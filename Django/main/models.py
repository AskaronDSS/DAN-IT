from django.contrib.auth.models import User
from django.db import models

class PredictHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_date = models.DateTimeField(auto_now_add=True)

    leading_pf = models.FloatField()
    lagging_pf = models.FloatField()
    leading_reactive = models.FloatField()
    load_type = models.CharField(max_length=50)
    result_predict = models.FloatField()
