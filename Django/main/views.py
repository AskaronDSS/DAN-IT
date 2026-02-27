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
    """
    Регистрирует нового пользователя в системе.

    Создает запись в таблице пользователей Django на основе данных из UserRegisterForm.
    После успешной регистрации автоматически авторизует пользователя.

    Args:
        request: Объект запроса Django.
    Returns:
        Рендер страницы регистрации или перенаправление на главную при успехе.
    """
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
    """
    Авторизует существующего пользователя.

    Проверяет соответствие логина и пароля. При успешном совпадении создает
    сессию пользователя. Перед входом принудительно завершает текущую сессию (logout).

    Args:
        request: Объект запроса Django.
    Returns:
        Рендер страницы входа или перенаправление на главную.
    """
    my_logout(request)
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
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
    """
    Завершает текущую сессию пользователя.

    Args:
        request: Объект запроса Django.
    Returns:
        Перенаправление на страницу логина.
    """
    logout(request)
    return redirect('login')


def predict_view(request):
    """
        Обрабатывает ввод технических параметров и возвращает прогноз энергопотребления.

        Функция выполняет следующие действия:
        1. Получает данные из PredictionForm (коэффициенты мощности, нагрузку, время).
        2. Рассчитывает NSM (количество секунд с начала дня).
        3. Формирует DataFrame для подачи в модель ML.
        4. Рассчитывает прогноз и дисперсию (погрешность 5%).
        5. Сохраняет результат в базу данных (PredictHistory), если пользователь авторизован.

        Args:
            request: Объект запроса Django.
        Returns:
            Рендер страницы прогноза с результатом и формой.
        """
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
                'DayOfWeek': int(data['day_of_week']),
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
                    day_num=int(data['day_of_week']),
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
    """Отображает главную страницу сайта."""
    return render(request, 'main/home.html')

def forecast(request):
    """Отображает страницу с формой для прогноза энергопотребления."""
    return render(request, 'main/forecast.html')

def history(request):
    """
    Отображает историю прогнозов, сделанных текущим пользователем.

    Извлекает все записи из PredictHistory, связанные с авторизованным пользователем.

    Args:
        request: Объект запроса Django.
    Returns:
        Рендер страницы истории с набором данных (QuerySet).
    """
    my_history = PredictHistory.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/history.html',{'history': my_history})

def clear_history(request):
    """
    Удаляет все записи из истории прогнозов текущего пользователя.

    Выполняется только при POST-запросе для защиты от случайного удаления через URL.

    Args:
        request: Объект запроса Django.
    Returns:
        Перенаправление на пустую страницу истории.
    """
    if request.method == 'POST':
        PredictHistory.objects.filter(user=request.user).delete()
    return redirect('history')

def statistics(request):
    """Отображает страницу с аналитическими данными и статистикой."""
    return render(request, 'main/analise.html')