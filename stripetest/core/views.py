from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.generic import ListView, DetailView
from django.views import View
from core.models import *
import stripe
import uuid
from django.conf import settings


stripe.api_key = settings.STRIPE_SECRET_KEY

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
        return render(request, "core/order.html", {"order":order, "end_sum":end_sum, "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY})
        
class CreateCheckoutSession(View):
    
    def get(self, request, *args, **kwargs):
        item_id = self.kwargs["pk"]
        item = Item.objects.get(pk = item_id)
        item_price = item.price
        item_currency = item.currency
        if item_currency == "rub":
            item_price *= 100
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    "price_data":{
                        "currency":item_currency,
                        "unit_amount":item_price,
                        'product_data':{
                            "name":item.name
                        },
                    },
                    "quantity":1,
                },
            ],
            metadata={
                "product_id": item.id
            },
            mode="payment",
            success_url = DOMAIN + "/success/",
            cancel_url = DOMAIN + "/cancel/",
        )
        return JsonResponse({"id":checkout_session.id})
    
    def post(self, request, *args, **kwargs):
        user_id = request.session["user_id"]
        user = get_object_or_404(AnonymousUser, user_id=user_id)
        order = Order.objects.filter(user=user).first()

        line_items = []

        for item in order.items.all():
            if item.currency == Item.Currency.DOLLAR:
                amount = item.price
            elif item.currency == Item.Currency.ROUBLE:
                amount = item.price * 0.01 * 100
            line_items.append({
                "price_data":{
                    "currency":"usd",
                    "unit_amount":amount,
                    "product_data":{"name":item.name},
                        
                },
                "quantity":1
            })
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url = DOMAIN + "/success/",
            cancel_url = DOMAIN + "/cancel/",
        )
        return JsonResponse({"id":checkout_session.id})



class ItemDetailView(DetailView):
    template_name = "core/detailed.html"
    model = Item

    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        context.update({"STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY})
        return context
    
class ItemListView(ListView):
    queryset = Item.objects.all()
    context_object_name = "items"
    paginate_by = 3
    template_name = "core/index.html"

def success(request):
    return HttpResponse(200)

def cancel(request):
    return HttpResponseBadRequest(400)
