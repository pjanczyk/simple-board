from django import forms

from app.models import Post, Thread


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'textarea-autosize', 'rows': 5})
        }


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['category', 'title']
        widgets = {
            'title': forms.TextInput()
        }
