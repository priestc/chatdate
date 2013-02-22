from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class UserEditForm(forms.ModelForm):
    # old_password = forms.CharField(required=False, widget=forms.widgets.PasswordInput)
    # new_password = forms.CharField(required=False, widget=forms.widgets.PasswordInput)
    # new_password2 = forms.CharField(required=False, widget=forms.widgets.PasswordInput)

    # def clean(self):
    #     cleaned_data = super(UserEditForm, self).clean()
    #     if cleaned_data['new_password'] and not cleaned_data['new_password2']:
    #         raise forms.ValidationError("Must type new password twice")

    #     if cleaned_data['new_password2'] != cleaned_data['new_password']:
    #         raise forms.ValidationError("Passwords must match")

    #     if cleaned_data['new_password'] and not cleaned_data['old_password']:


    class Meta:
        model = User
        widgets = {
            'full_name': forms.TextInput,
            'location': forms.HiddenInput,
            'sexual_preference': forms.RadioSelect,
            'gender': forms.RadioSelect}
        exclude = ['user_permissions', 'password', 'groups', 'is_superuser', 'hash',
                   'last_login', 'relationships', 'status', 'reputation', 'pics',
                   'email', 'nickname']

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
        exclude = ['user_permissions', 'groups', 'is_superuser', 'hash', 'pics',
                  'connection_distance', 'karma_threshold',
                   'last_login', 'relationships', 'status', 'reputation']