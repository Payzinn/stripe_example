from django.db import models
from django.contrib.auth. models import AbstractUser

class AnonymousUser(models.Model):
    user_id = models.CharField(max_length=255, unique=True)

class Discount(models.Model):
    amount = models.IntegerField()

    def __str__(self):
        return f"{self.amount}"


class Tax(models.Model):
    amount = models.IntegerField()
    
    def __str__(self):
        return f"{self.amount}"

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
        return "{:,}$".format(self.price).replace(",", ".")
    
    @property
    def price_display_rouble(self):
        return "{:,}₽".format(self.price).replace(",", ".")
    
    def __str__(self):
        if self.currency == self.Currency.DOLLAR:
            return f"{self.name}/{self.price_display_dollar}"
        if self.currency == self.Currency.ROUBLE:
            return f"{self.name}/{self.price_display_rouble}"

class Order(models.Model):
    items = models.ManyToManyField(Item)
    user = models.ForeignKey(AnonymousUser, on_delete=models.CASCADE, related_name="orders")
    tax = models.ForeignKey(Tax, on_delete=models.SET_DEFAULT, default=1)
    discount = models.ForeignKey(Discount, on_delete=models.SET_DEFAULT, default=1)
