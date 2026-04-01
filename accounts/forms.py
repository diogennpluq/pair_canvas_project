from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, max_length=500)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'bio')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('avatar', 'bio', 'email')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'required': True,
            'autofocus': True,
            'placeholder': 'your@email.com'
        })
    )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'required': True,
            'autofocus': True
        }),
    )
    new_password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'required': True
        }),
    )