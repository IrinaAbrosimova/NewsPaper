import django_filters
from django.forms import DateInput
from django_filters import FilterSet, DateFilter, CharFilter
from .models import Post, Category
from django import forms


class PostFilter(FilterSet):
    time_in = DateFilter(
        field_name='time_in',
        label='Дата (позже)',
        lookup_expr='gt',
        widget=DateInput(
            attrs={
                'type': 'date',
            }
        ),
    )
    title = CharFilter(
        field_name='title',
        label='Название',
        lookup_expr='icontains',
    )
    author = CharFilter(
        field_name='author__username',
        label='Автор',
        lookup_expr='icontains',
    )
    category = django_filters.ModelMultipleChoiceFilter(queryset=Category.objects.all(),
                                                        widget=forms.CheckboxSelectMultiple(
                                                            attrs={'category': 'category'}), label='Category')

    class Meta:
        model = Post
        fields = [

            'title',
            'author',
        ]
