from inv.forms import LoginForm
from django import template

register = template.Library()


@register.filter
def login_form(string):
    return LoginForm()
