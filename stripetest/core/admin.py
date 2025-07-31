from django.contrib import admin
from core.models import *
# Register your models here.
admin.site.register(Item)
admin.site.register(Order)
admin.site.register(AnonymousUser)
admin.site.register(Tax)
admin.site.register(Discount)