from django import forms
from django.core.exceptions import ValidationError
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('category', 'author', 'title', 'text')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'author': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get("text")
        title = cleaned_data.get("title")
        if title is not None and len(title) > 100:
            raise ValidationError({
                "title": "Заголовок не может быть более 100 символов."
            })
        if title == text:
            raise ValidationError(
                "Заголовок не должен быть идентичным тексту статьи."
            )
        if title[0].islower():
            raise ValidationError(
                "Заголовок должен начинаться с заглавной буквы.")
        if text[0].islower():
            raise ValidationError(
                "Текст статьи должен начинаться с заглавной буквы.")
        return cleaned_data
