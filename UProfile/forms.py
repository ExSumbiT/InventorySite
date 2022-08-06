from django import forms
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm, UsernameField


class ChangePasswordForm(PasswordChangeForm):
    error_css_class = 'has-error'
    error_messages = {'password_incorrect': "Невірний пароль користувача",
                      'password_mismatch': "Паролі не співпадають"}
    old_password = forms.CharField(required=True, label='Пароль користувача',
                                   widget=forms.PasswordInput(attrs={
                                       'class': 'form-control'}),
                                   error_messages={
                                       'required': 'Введіть пароль користувача!'})

    new_password1 = forms.CharField(required=True, label='Новий пароль',
                                    widget=forms.PasswordInput(attrs={
                                        'class': 'form-control'}),
                                    error_messages={
                                        'required': 'Введіть новий пароль!'})
    new_password2 = forms.CharField(required=True, label='Новий пароль (підтвердження)',
                                    widget=forms.PasswordInput(attrs={
                                        'class': 'form-control'}),
                                    error_messages={
                                        'required': 'Введіть підтвердження паролю!'})

    def clean_new_password2(self):
        old_password = self.cleaned_data.get("old_password")
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError('Паролі не співпадають')
        elif old_password and new_password1 and old_password == new_password1:
            raise forms.ValidationError("Новий пароль відповідає старому!")
        return new_password1


class LoginForm(AuthenticationForm):
    error_messages = {'password_incorrect': "Хибний пароль",
                      'invalid_login': "Хибне ім'я користувача"}
    username = UsernameField(required=True, label='Ім\'я користувача',
                             widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}))
    password = forms.CharField(required=True, label='Пароль', strip=False,
                               widget=forms.PasswordInput(attrs={'autocomplete': 'current-password',
                                                                 'class': 'form-control'}),)
