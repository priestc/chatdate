from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class UserEditForm(forms.ModelForm):
    old_password = forms.CharField(widget=forms.widgets.PasswordInput)
    new_password = forms.CharField(widget=forms.widgets.PasswordInput)
    new_password2 = forms.CharField(widget=forms.widgets.PasswordInput)

    class Meta:
        model = User
        exclude = ['user_permissions', 'groups', 'is_superuser', 'hash',
                   'last_login', 'relationships', 'status', 'reputation']

class RegisterForm(forms.ModelForm):
    password_again = forms.CharField(widget=forms.widgets.PasswordInput)
    class Meta:
        widgets = {
            'password': forms.PasswordInput,
            'full_name': forms.TextInput,
            'location': forms.HiddenInput,
            'sexual_preference': forms.RadioSelect,
            'gender': forms.RadioSelect}
        model = User
        exclude = ['user_permissions', 'groups', 'is_superuser', 'hash',
                   'last_login', 'relationships', 'status', 'reputation']