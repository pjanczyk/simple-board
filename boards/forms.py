from django import forms
from django.contrib.auth.models import User

from boards.models import Post, Thread


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text']


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['category', 'title']
        widgets = {
            'title': forms.TextInput()
        }


class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
