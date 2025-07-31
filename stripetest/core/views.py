from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.generic import ListView, DetailView
from django.views import View
from core.models import *
from django.urls import reverse
import stripe
import uuid
from django.conf import settings


DOLLAR = stripe.api_key = settings.STRIPE_SECRET_KEY_DOLLAR
ROUBLE = stripe.api_key = settings.STRIPE_SECRET_KEY_ROUBLE


DOMAIN = "http://127.0.0.1:8000"

class OrderView(View):
    def post(self, request, *args, **kwargs):
        item_id = self.kwargs["pk"]
        item = Item.objects.get(pk=item_id)
        if "user_id" not in request.session:
            request.session["user_id"] = str(uuid.uuid4())
        user_id = request.session["user_id"]
        user, _ = AnonymousUser.objects.get_or_create(user_id = user_id)
        order, _ = Order.objects.get_or_create(user = user)
        order.items.add(item)
        order.update(tax=2, discount=2)
        return JsonResponse({"status":"ok"})

    def get(self, request, *args, **kwargs):
        if "user_id" not in request.session:
            request.session["user_id"] = str(uuid.uuid4())
        user_id = request.session["user_id"]
        user, _ = AnonymousUser.objects.get_or_create(user_id=user_id)
        order = Order.objects.filter(user=user).first()
        # Конечная сумма в корзине всегда в долларах
        end_sum = 0
        if order:
            for item in order.items.all():
                if item.currency == Item.Currency.DOLLAR:
                    end_sum += item.price / 100
                if item.currency == Item.Currency.ROUBLE:
                    end_sum += item.price * 0.01
        return render(request, "core/order.html", {"order":order, "end_sum":end_sum, "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY_DOLLAR})
        
class CreateCheckoutSession(View):
    
    def get(self, request, *args, **kwargs):
        item_id = self.kwargs["pk"]
        item = Item.objects.get(pk = item_id)
        item_price = item.price
        item_currency = item.currency
        
        if item_currency == "rub":
            stripe.api_key = settings.STRIPE_SECRET_KEY_ROUBLE
        elif item_currency == "usd":
            stripe.api_key = settings.STRIPE_SECRET_KEY_DOLLAR

        if item_currency == "usd":
            item_price *= 100

        elif item_currency == "rub":
            item_price *= 100
        
        intent = stripe.PaymentIntent.create(
            automatic_payment_methods={"enabled": True},
            amount = item_price,
            currency = item_currency,
            metadata={
                "product_id": item.id
            }
        )
        return JsonResponse({"client_secret":intent.client_secret}) # Так как в бонусных заданиях было указано использовать Payment Intent приходится возвращать именно это
    
    def post(self, request, *args, **kwargs):
        user_id = request.session["user_id"]
        user = get_object_or_404(AnonymousUser, user_id=user_id)
        order = Order.objects.filter(user=user).first()
        tax = order.tax.amount
        discount = order.discount.amount

        metadata = {}
        amount = 0

        for idx, item in enumerate(order.items.all()):
            if item.currency == Item.Currency.DOLLAR:
                amount += int(item.price * 100)
            elif item.currency == Item.Currency.ROUBLE:
                amount += int(item.price)
            metadata[f"item_{idx}_id"] = str(item.id)

        tax_amount = (tax / 100) * amount
        discount_amount = (discount / 100) * amount
        final_amount = (amount + tax_amount) - discount_amount

        stripe.api_key = settings.STRIPE_SECRET_KEY_DOLLAR
        intent = stripe.PaymentIntent.create(
            automatic_payment_methods={"enabled": True},
            metadata = metadata,
            amount = final_amount,
            currency = "usd"
        )
        return JsonResponse({"client_secret":intent.client_secret}) # Так как в бонусных заданиях было указано использовать Payment Intent приходится возвращать именно это



class ItemDetailView(DetailView):
    template_name = "core/detailed.html"
    model = Item

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.get_object()

        if item.currency == Item.Currency.DOLLAR:
            context["stripe_public_key"] = settings.STRIPE_PUBLIC_KEY_DOLLAR
        elif item.currency == Item.Currency.ROUBLE:
            context["stripe_public_key"] = settings.STRIPE_PUBLIC_KEY_ROUBLE

        return context
    
class ItemListView(ListView):
    queryset = Item.objects.all()
    context_object_name = "items"
    paginate_by = 3
    template_name = "core/index.html"

def delete_item(request, pk):
    user_id = request.session["user_id"]
    user = get_object_or_404(AnonymousUser, user_id=user_id)
    order = Order.objects.filter(user = user).first()
    if order:
        order.items.remove(pk)
    return redirect("/order/")

def success(request):
    return HttpResponse(200)

def cancel(request):
    return HttpResponseBadRequest(400)
