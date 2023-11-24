from django import forms
from .models import role_master

class LoginForm(forms.Form):
    email = forms.CharField(required=True)
    password = forms.CharField(required=True)

class createUserForm(forms.Form):

    ROLES = role_master.objects.filter(status = 1).values_list('id', 'name')

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    role_master = forms.ChoiceField(choices=ROLES, required=True)
    phone_number = forms.IntegerField()
    email = forms.CharField(required=True)
    bln_active = forms.ChoiceField(label='Status', choices=[
        (True, 'Active'),
        (False, 'Inactive')
    ])
    password = forms.CharField(required=True)

class updateUserForm(forms.Form):

    ROLES = role_master.objects.filter(status = 1).values_list('id', 'name')

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    role_master = forms.ChoiceField(label='Role', choices=ROLES, required=True)
    phone_number = forms.IntegerField()
    email = forms.CharField(required=True)
    bln_active = forms.ChoiceField(label='Status', choices=[
        (True, 'Active'),
        (False, 'Inactive')
    ])