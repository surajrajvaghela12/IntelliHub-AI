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


from django.contrib.auth import authenticate

class UserLoginForm(forms.Form):
    username = forms.CharField(label="Username or Email", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username or email address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}))

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        username_or_email = self.cleaned_data.get('username', '').strip()
        password = self.cleaned_data.get('password', '')

        if username_or_email and password:
            # Look up registered user by username OR email (case-insensitive)
            user_obj = User.objects.filter(email__iexact=username_or_email).first() or User.objects.filter(username__iexact=username_or_email).first()
            actual_username = user_obj.username if user_obj else username_or_email

            self.user_cache = authenticate(self.request, username=actual_username, password=password)

            if self.user_cache is None:
                raise forms.ValidationError("Invalid username/email or password. Please check your credentials.")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("This account has been deactivated.")

        return self.cleaned_data

    def get_user(self):
        return self.user_cache


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
