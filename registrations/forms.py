from django.contrib.auth.models import User
from django import forms
from .models import *



cities = (
	('a','a'),
	('Delhi','Delhi')
	)

states = (
	('a','a'),
	('Rajasthan','Rajasthan')
	)

colleges = (
	('a','a'),
	('Bits','Bits')
	)

genders = (

			('M', 'MALE'),
			('F', 'FEMALE'),
		)

class UserForm(forms.ModelForm):
	
	class Meta:
		model = User
		fields = ('username', 'password')
		 widgets = {
            'username':forms.TextInput(attrs={'placeholder':'Username'}),
            'password': forms.PasswordInput(attrs={'placeholder':'Password'}), 
        }

class GroupLeaderForm(forms.ModelForm):
	
	phone = forms.RegexField(regex=r'^\d{10}$')

	class Meta:
		model = GroupLeader
		fields = ('email', 'city', 'name', 'college', 'state', 'phone', 'gender',)

		widgets = {
		'email':forms.TextInput(attrs={'placeholder':'Email'}),
		'city':forms.Select(choices = cities),
		'state':forms.Select(choices = states),
		'college':forms.Select(choices = college),
		'gender':forms.Select(choices = gender),
		'name':forms.TextInput(attrs='placeholder':'FullName')
		}

class TeamCaptainForm(models.ModelForm):
	phone = forms.RegexField(regex=r'^\d{10}$')

	class Meta:
		model = TeamCaptain
		fields = ('email', 'name', 'phone', 'gender')

		widgets = {
		'email':forms.TextInput(attrs={'placeholder':'Email'}),
		'name':forms.TextInput(attrs='placeholder':'FullName')
		}