from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, UserProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'}))

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            
        # Customize password field placeholders
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs['placeholder'] = 'Create a strong password'
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'
        if 'username' in self.fields:
            self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'DATA_SCIENTIST'  # Full features & unlimited upload quota by default
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}))


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'education', 'company', 'github', 'linkedin', 'photo', 'dark_mode']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'education': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'github': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'dark_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
