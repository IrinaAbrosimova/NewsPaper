from django.core.exceptions import ValidationError
from .models import Post
from django.forms import ModelForm, TextInput, Textarea, SelectMultiple, Select


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('category', 'author', 'title', 'text')

        widgets = {
            'title': TextInput(attrs={'class': 'form-control', 'placeholder': 'Название'}),
            'text': Textarea(attrs={'class': 'form-control', 'placeholder': 'Содержание'}),
            'category': SelectMultiple(attrs={'class': 'form-control'}),
            'author': Select(attrs={'class': 'form-control', 'placeholder': 'Автор'}),


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
