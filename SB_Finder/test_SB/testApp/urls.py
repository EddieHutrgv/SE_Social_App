from django.urls import path
from testApp import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('signup/', views.signup_page, name='signup'),
    path('logout/', views.logout_page, name='logout'),
    
    # Dashboard and Profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.user_profile, name='user_profile'),
    path('user/<int:user_id>/', views.view_user_profile, name='view_user_profile'),
    
    # Study Sessions
    path('session/create/', views.create_session, name='create_session'),
    path('session/<int:pk>/', views.session_detail, name='session_detail'),
    path('session/<int:pk>/edit/', views.edit_session, name='edit_session'),
    path('session/<int:pk>/delete/', views.delete_session, name='delete_session'),
    path('session/<int:pk>/join/', views.join_session, name='join_session'),
    path('session/<int:pk>/leave/', views.leave_session, name='leave_session'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notification/<int:notification_id>/read/', views.mark_notification_as_read, name='mark_notification_read'),
]
