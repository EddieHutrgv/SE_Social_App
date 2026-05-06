from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import UserProfile, StudySession, SessionMembership, Notification
from .forms import UserProfileForm, StudySessionForm, SessionFilterForm, UserUpdateForm

def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html', {'user': request.user})

def login_page(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

def signup_page(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Check for .edu email
        if not email.endswith('.edu'):
            return render(request, 'signup.html', {'error': 'Only .edu email addresses are allowed to register.'})

        if password1 != password2:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already taken'})
        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'Email already registered'})

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        login(request, user)
        return redirect('dashboard')

    return render(request, 'signup.html')

def logout_page(request):
    """User logout view"""
    logout(request)
    return redirect('/')


@login_required(login_url='login')
def dashboard(request):
    """User dashboard showing available sessions and user's sessions"""
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    # Get filter form
    filter_form = SessionFilterForm(request.GET)
    
    # Get all active sessions
    sessions = StudySession.objects.filter(is_active=True, date__gte=timezone.now().date())
    
    # Apply filters
    if filter_form.is_valid():
        course_name = filter_form.cleaned_data.get('course_name')
        location = filter_form.cleaned_data.get('location')
        date = filter_form.cleaned_data.get('date')
        time_slot = filter_form.cleaned_data.get('time_slot')
        
        if course_name:
            sessions = sessions.filter(
                Q(course_name__icontains=course_name) | 
                Q(course_code__icontains=course_name)
            )
        
        if location:
            sessions = sessions.filter(location=location)
        
        if date:
            sessions = sessions.filter(date=date)
        
        if time_slot:
            sessions = filter_by_time_slot(sessions, time_slot)
    
    # Get user's joined sessions
    joined_sessions = request.user.joined_sessions.filter(is_active=True)
    
    # Get user's created sessions
    created_sessions = request.user.created_sessions.filter(is_active=True)
    
    # Get unread notifications count
    unread_notifications = request.user.notifications.filter(is_read=False).count()
    
    context = {
        'filter_form': filter_form,
        'sessions': sessions,
        'joined_sessions': joined_sessions,
        'created_sessions': created_sessions,
        'unread_notifications': unread_notifications,
        'user_profile': user_profile,
    }
    return render(request, 'dashboard.html', context)


def filter_by_time_slot(sessions, time_slot):
    """Filter sessions by time slot"""
    from datetime import time
    
    if time_slot == 'morning':
        return sessions.filter(start_time__gte=time(8, 0), start_time__lt=time(12, 0))
    elif time_slot == 'afternoon':
        return sessions.filter(start_time__gte=time(12, 0), start_time__lt=time(16, 0))
    elif time_slot == 'evening':
        return sessions.filter(start_time__gte=time(16, 0), start_time__lt=time(20, 0))
    elif time_slot == 'night':
        return sessions.filter(start_time__gte=time(20, 0))
    return sessions


@login_required(login_url='login')
def user_profile(request):
    """User profile view"""
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('user_profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    
    # Get user's created sessions
    created_sessions = request.user.created_sessions.all()
    
    # Get user's joined sessions
    joined_sessions = request.user.joined_sessions.all()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'created_sessions': created_sessions,
        'joined_sessions': joined_sessions,
        'user_profile': user_profile,
    }
    return render(request, 'user_profile.html', context)


@login_required(login_url='login')
def create_session(request):
    """Create a new study session"""
    if request.method == 'POST':
        form = StudySessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.creator = request.user
            session.save()
            
            # Add creator as a member
            SessionMembership.objects.create(user=request.user, session=session)
            
            messages.success(request, 'Study session created successfully!')
            return redirect('session_detail', pk=session.pk)
    else:
        form = StudySessionForm()
    
    return render(request, 'create_session.html', {'form': form})


@login_required(login_url='login')
def edit_session(request, pk):
    """Edit an existing study session"""
    session = get_object_or_404(StudySession, pk=pk)
    
    if request.user != session.creator:
        messages.error(request, 'You can only edit your own sessions!')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = StudySessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, 'Study session updated successfully!')
            return redirect('session_detail', pk=session.pk)
    else:
        form = StudySessionForm(instance=session)
    
    return render(request, 'edit_session.html', {'form': form, 'session': session})


@login_required(login_url='login')
def delete_session(request, pk):
    """Delete a study session"""
    session = get_object_or_404(StudySession, pk=pk)
    
    if request.user != session.creator:
        messages.error(request, 'You can only delete your own sessions!')
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Create notification for all members
        members = session.current_members.exclude(pk=request.user.pk)
        for member in members:
            Notification.objects.create(
                user=member,
                notification_type='session_canceled',
                session=session,
                title='Study Session Canceled',
                message=f'The study session for {session.course_name} on {session.date} has been canceled.',
            )
        
        session.delete()
        messages.success(request, 'Study session deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'confirm_delete_session.html', {'session': session})


@login_required(login_url='login')
def session_detail(request, pk):
    """View detailed information about a study session"""
    session = get_object_or_404(StudySession, pk=pk)
    members = session.current_members.all()
    is_member = request.user in members
    is_creator = request.user == session.creator
    
    context = {
        'session': session,
        'members': members,
        'is_member': is_member,
        'is_creator': is_creator,
        'member_count': session.get_member_count(),
        'is_full': session.is_full(),
    }
    return render(request, 'session_detail.html', context)


@login_required(login_url='login')
def join_session(request, pk):
    """Join a study session"""
    session = get_object_or_404(StudySession, pk=pk)
    
    if session.is_full():
        messages.error(request, 'This session is full!')
        return redirect('session_detail', pk=pk)
    
    if request.user in session.current_members.all():
        messages.error(request, 'You are already a member of this session!')
        return redirect('session_detail', pk=pk)
    
    SessionMembership.objects.create(user=request.user, session=session)
    
    # Create notification for session creator
    Notification.objects.create(
        user=session.creator,
        notification_type='session_join',
        session=session,
        title='New Member Joined',
        message=f'{request.user.username} joined your study session for {session.course_name}.',
        related_user=request.user,
    )
    
    messages.success(request, f'You have successfully joined {session.course_name}!')
    return redirect('session_detail', pk=pk)


@login_required(login_url='login')
def leave_session(request, pk):
    """Leave a study session"""
    session = get_object_or_404(StudySession, pk=pk)
    
    try:
        membership = SessionMembership.objects.get(user=request.user, session=session)
        membership.status = 'left'
        membership.save()
        messages.success(request, 'You have left the session.')
    except SessionMembership.DoesNotExist:
        messages.error(request, 'You are not a member of this session.')
    
    return redirect('dashboard')


@login_required(login_url='login')
def notifications(request):
    """View all notifications"""
    user_notifications = request.user.notifications.all().order_by('-created_at')
    
    # Mark as read
    if request.method == 'POST':
        user_notifications.filter(is_read=False).update(is_read=True)
    
    context = {
        'notifications': user_notifications,
    }
    return render(request, 'notifications.html', context)


@login_required(login_url='login')
def mark_notification_as_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')

