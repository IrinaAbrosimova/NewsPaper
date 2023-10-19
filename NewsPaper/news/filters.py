import django_filters
from django.forms import DateInput
from django_filters import FilterSet, DateFilter, CharFilter
from .models import Post, Category
from django import forms


class PostFilter(FilterSet):
    title = django_filters.Filter(field_name='title', lookup_expr='icontains', label='Название')
    time_in = django_filters.DateFilter(field_name='time_in', lookup_expr='gte', widget=DateInput(attrs={'type': 'date'}), label='Дата (позже)')
    category = django_filters.ModelMultipleChoiceFilter(queryset=Category.objects.all(), widget=forms.CheckboxSelectMultiple(attrs={'category': 'category'}), label = 'Категория')

    class Meta:
        model = Post
        fields = [
            'category',
            'author',
            'title',
            'time_in'
        ]
