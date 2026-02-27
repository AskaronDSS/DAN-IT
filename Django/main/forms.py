from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm



class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class PredictionForm(forms.Form):
    LOAD_CHOICES = [
        ('Light_Load', 'Легкая загрузка'),
        ('Medium_Load', 'Средняя загрузка'),
        ('Maximum_Load', 'Максимальная загрузка'),
    ]
    WEEK_STATUS_CHOICES = [
        ('Weekday', 'Будний день'),
        ('Weekend', 'Выходной'),
    ]
    DAY_CHOICES = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье')
    ]

    Leading_Power_Factor = forms.FloatField(min_value=0, max_value=100)
    Lagging_Power_Factor = forms.FloatField(min_value=0, max_value=100)
    leading_reactive = forms.FloatField()

    time = forms.TimeField(
        label="Время (для расчета NSM)",
        widget=forms.TimeInput(attrs={'type': 'time'}),
        help_text="Мы сами переведем это в секунды (NSM)"
    )

    week_status = forms.ChoiceField(choices=WEEK_STATUS_CHOICES)
    day_of_week = forms.ChoiceField(choices=DAY_CHOICES)
    load_type = forms.ChoiceField(choices=LOAD_CHOICES )