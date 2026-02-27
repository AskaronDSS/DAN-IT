from django.db import models
from django.contrib.auth.models import User

class PredictHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    leading_pf = models.FloatField()
    lagging_pf = models.FloatField()
    leading_reactive = models.FloatField()

    day_num = models.IntegerField(default=0)
    load_type = models.CharField(max_length=100)
    result_predict = models.FloatField()
    variance = models.FloatField(default=0)

    def get_day_name(self):
        days = ['Понедельник', 'Вторник', 'Среда', 'Четверг',
                'Пятница', 'Суббота', 'Воскресенье']
        return days[self.day_num]