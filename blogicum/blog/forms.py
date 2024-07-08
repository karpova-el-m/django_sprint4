from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('is_published',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }
    
    def clean(self):
        super().clean()