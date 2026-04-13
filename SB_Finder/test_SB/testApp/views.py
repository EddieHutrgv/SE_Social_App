from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from testApp.models import StudySession

def home(request):
    return render(request, 'home.html', {'user': request.user})

def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/dashboard/')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

def signup_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if not email.endswith('.edu'):
            return render(request, 'signup.html', {'error': 'Only .edu email addresses are allowed.'})
        if password1 != password2:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already taken'})
        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'Email already registered'})

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        login(request, user)
        return redirect('/dashboard/')

    return render(request, 'signup.html')

def logout_page(request):
    logout(request)
    return redirect('/')

@login_required(login_url='/login/')
def dashboard(request):
    sessions = StudySession.objects.all().order_by('date', 'time')
    return render(request, 'dashboard.html', {'sessions': sessions, 'user': request.user})

@login_required(login_url='/login/')
def create_session(request):
    if request.method == 'POST':
        course = request.POST['course']
        subject = request.POST['subject']
        location = request.POST['location']
        date = request.POST['date']
        time = request.POST['time']
        max_students = request.POST['max_students']

        session = StudySession.objects.create(
            creator=request.user,
            course=course,
            subject=subject,
            location=location,
            date=date,
            time=time,
            max_students=max_students
        )
        session.members.add(request.user)
        return redirect('/dashboard/')

    return render(request, 'create_session.html')

@login_required(login_url='/login/')
def session_detail(request, pk):
    session = get_object_or_404(StudySession, pk=pk)
    is_member = request.user in session.members.all()
    is_creator = request.user == session.creator
    return render(request, 'session_detail.html', {
        'session': session,
        'is_member': is_member,
        'is_creator': is_creator
    })

@login_required(login_url='/login/')
def join_session(request, pk):
    session = get_object_or_404(StudySession, pk=pk)
    if not session.is_full() and request.user not in session.members.all():
        session.members.add(request.user)
    return redirect(f'/session/{pk}/')

@login_required(login_url='/login/')
def leave_session(request, pk):
    session = get_object_or_404(StudySession, pk=pk)
    if request.user in session.members.all() and request.user != session.creator:
        session.members.remove(request.user)
    return redirect(f'/session/{pk}/')

@login_required(login_url='/login/')
def edit_session(request, pk):
    session = get_object_or_404(StudySession, pk=pk)
    if request.user != session.creator:
        return redirect(f'/session/{pk}/')

    if request.method == 'POST':
        session.course = request.POST['course']
        session.subject = request.POST['subject']
        session.location = request.POST['location']
        session.date = request.POST['date']
        session.time = request.POST['time']
        session.max_students = request.POST['max_students']
        session.save()
        return redirect(f'/session/{pk}/')

    return render(request, 'edit_session.html', {'session': session})

@login_required(login_url='/login/')
def delete_session(request, pk):
    session = get_object_or_404(StudySession, pk=pk)
    if request.user == session.creator:
        session.delete()
    return redirect('/dashboard/')
