from statistics import variance

from django.shortcuts import redirect
from .forms import UserRegisterForm
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import logout
import joblib

import pandas as pd
from django.shortcuts import render
from .forms import PredictionForm
from .models import PredictHistory

my_model = joblib.load('my_model.joblib')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'main/register.html', {'form': form})

def my_login(request):
    my_logout(request)
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user() 
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Неверное имя пользователя или пароль.")
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})
def my_logout(request):
    logout(request)
    return redirect('login')


def predict_view(request):
    result = None
    variance = None
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            nsm_value = (data['time'].hour * 3600) + (data['time'].minute * 60)
            input_df = pd.DataFrame([{
                'Leading_Current_Reactive_Power_kVarh': data['leading_reactive'],
                'Lagging_Current_Power_Factor': data['Lagging_Power_Factor'],
                'Leading_Current_Power_Factor': data['Leading_Power_Factor'],
                'NSM': nsm_value,
                'DayOfWeek': data['day_num'],
                'WeekStatus': data['week_status'],
                'Day_Of_Week': data['day_of_week'],
                'Load_Type': data['load_type']
            }])
            prediction = my_model.predict(input_df)
            result = round(prediction[0], 4)

            variance = round(result * 0.05, 2)
            if request.user.is_authenticated:
                PredictHistory.objects.create(
                    user=request.user,
                    day_num=data['day_num'],
                    leading_pf=data['Leading_Power_Factor'],
                    lagging_pf=data['Lagging_Power_Factor'],
                    leading_reactive=data['leading_reactive'],
                    load_type=data['load_type'],
                    result_predict=result,
                    variance = variance
                )
    else:
        form = PredictionForm()

    return render(request, 'main/forecast.html', {'form': form,
                                                  'result': result,
                                                  'variance': variance})


def home(request):
    return render(request, 'main/home.html')
def forecast(request):
    return render(request, 'main/forecast.html')
def history(request):
    my_history = PredictHistory.objects.filter(user=request.user)
    return render(request, 'main/history.html',{'history': my_history})

def clear_history(request):
    if request.method == 'POST':
        my_history = PredictHistory.objects.filter(user=request.user).delete()
    return redirect('history')

def statistics(request):
    return render(request, 'main/analise.html')