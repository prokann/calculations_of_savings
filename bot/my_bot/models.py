from django.db import models


class User(models.Model):
    # id = models.AutoField(primary_key=True)
    chat_id = models.CharField(max_length=30)


class SavingsType(models.Model):
    user_id = models.CharField(max_length=30, default='1')
    name = models.CharField(max_length=50)
    amount = models.IntegerField()
