"""Forms used by Study Buddy Finder.

This module contains Django forms for profile management,
study session creation, session filtering, and user updates.
"""

from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, StudySession

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    class Meta:
        model = UserProfile
        fields = ['major', 'year', 'interests', 'bio', 'availability_morning', 
                  'availability_afternoon', 'availability_evening', 'availability_night']
        widgets = {
            'major': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Computer Science'
            }),
            'year': forms.Select(attrs={'class': 'form-control'}),
            'interests': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Web Development, Machine Learning, AI',
                'rows': 3
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell other students about yourself',
                'rows': 3
            }),
            'availability_morning': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'availability_afternoon': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'availability_evening': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'availability_night': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StudySessionForm(forms.ModelForm):
    """Form for creating and editing study sessions"""
    class Meta:
        model = StudySession
        fields = ['course_name', 'course_code', 'description', 'location', 'other_location',
                  'date', 'start_time', 'end_time', 'max_capacity', 'subject_tags']
        widgets = {
            'course_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Data Structures'
            }),
            'course_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., CS 2401'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the study session...',
                'rows': 4
            }),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'other_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Specify location'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'max_capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100
            }),
            'subject_tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., algorithms, programming, interview prep'
            }),
        }


class SessionFilterForm(forms.Form):
    """Form for filtering study sessions"""
    course_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by course name'
        })
    )
    location = forms.ChoiceField(
        required=False,
        choices=[('', 'All Locations')] + StudySession._meta.get_field('location').choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    time_slot = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Times'),
            ('morning', 'Morning (8 AM - 12 PM)'),
            ('afternoon', 'Afternoon (12 PM - 4 PM)'),
            ('evening', 'Evening (4 PM - 8 PM)'),
            ('night', 'Night (8 PM - 12 AM)'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class UserUpdateForm(forms.ModelForm):
    """Form for updating basic user information"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@utrgv.edu'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
        }
