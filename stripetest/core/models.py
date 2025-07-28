from django.db import models
from django.contrib.auth. models import AbstractUser

class AnonymousUser(models.Model):
    user_id = models.CharField(max_length=255, unique=True)

class Item(models.Model):
    class Currency(models.TextChoices):
        DOLLAR = "usd", "Dollar"
        ROUBLE = "rub", "Rouble"
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField(default=0)
    currency = models.CharField(max_length=10, choices=Currency.choices, default=Currency.DOLLAR)


    
    @property
    def price_display_dollar(self):
        return f"{self.price / 100}$"
    
    @property
    def price_display_rouble(self):
        return f"{self.price}₽"
    
    def __str__(self):
        if self.currency == self.Currency.DOLLAR:
            return f"{self.name}/{self.price_display_dollar}"
        if self.currency == self.Currency.ROUBLE:
            return f"{self.name}/{self.price_display_rouble}"

class Order(models.Model):
    items = models.ManyToManyField(Item)
    user = models.ForeignKey(AnonymousUser, on_delete=models.CASCADE, related_name="orders")
    
