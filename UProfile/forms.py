from django import forms
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm, UsernameField
from django.core.validators import MaxValueValidator, MinValueValidator
from inv.models import InventoryType
from django.contrib.auth.models import User
from .models import QrParameters
from .serializers import QrParametersSerializer
from django.utils.translation import gettext_lazy as _


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
    error_messages = {'inactive': "Аккаунт неактивний",
                      'invalid_login': "Хибне ім'я користувача або пароль"}
    username = UsernameField(required=True, label='Ім\'я користувача',
                             widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}))
    password = forms.CharField(required=True, label='Пароль', strip=False,
                               widget=forms.PasswordInput(attrs={'autocomplete': 'current-password',
                                                                 'class': 'form-control'}),)

# TODO: перевірку введених значень, на перше "більше" другого
class QrRangeForm(forms.Form):
    less = _("Введене значення має бути більше або рівне %(limit_value)s.")
    more = _("Введене значення має бути менше або рівне %(limit_value)s.")
    CHOICES = ((i.short_name, i.full_name) for i in InventoryType.objects.all())
    inv_type = forms.ChoiceField(label='Тип', widget=forms.Select(attrs={'class': 'form-control'}), choices=CHOICES)
    index_from = forms.IntegerField(label='Початковий', validators=[MaxValueValidator(100, less), MinValueValidator(1, more)],
                                    widget=forms.NumberInput(attrs={'class': 'form-control', 'value': 1}))
    index_to = forms.IntegerField(label='Кінцевий', validators=[MaxValueValidator(100, less), MinValueValidator(1, more)],
                                  widget=forms.NumberInput(attrs={'class': 'form-control', 'value': 1}))


class QrParametersForm(forms.Form):
    fonts = [('arial', 'Arial'), (2, 'Test')]
    weight = forms.IntegerField(label='Ширина', initial=30, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    height = forms.IntegerField(label='Висота', initial=50, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    font = forms.ChoiceField(label='Шрифт', initial=fonts[0], widget=forms.Select(attrs={'class': 'form-control'}), choices=fonts)
    font_size = forms.IntegerField(label='Розмір шрифту', initial=14, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    description_logo = forms.BooleanField(label='Додати логотип', initial=True, required=False)
    logo_size = forms.IntegerField(label='Розмір логотипу', initial=30, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, user=None, *args, **kwargs):
        qrp = user.qr
        super(QrParametersForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['weight'].initial = qrp.weight
            self.fields['height'].initial = qrp.height
            self.fields['font'].initial = (qrp.font, str(qrp.font).title())
            self.fields['font_size'].initial = qrp.font_size
            self.fields['description_logo'].initial = qrp.description_logo
            self.fields['logo_size'].initial = qrp.logo_size


