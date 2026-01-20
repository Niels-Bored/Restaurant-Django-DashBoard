from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Dish, Presentation
from django.views.decorators.http import require_POST


def menu_view(request):
    dishes = Dish.objects.prefetch_related("presentations")
    cart = request.session.get("cart", {})
    return render(request, "restaurant/menu.html", {"dishes": dishes, "cart": cart})


def add_to_cart(request):
    presentation_id = request.POST.get("presentation_id")
    quantity = int(request.POST.get("quantity", 1))

    presentation = get_object_or_404(Presentation, id=presentation_id)

    cart = request.session.get("cart", {})

    key = str(presentation.id)

    if key in cart:
        cart[key]["quantity"] += quantity
    else:
        cart[key] = {
            "dish": presentation.dish.name,
            "presentation": presentation.name,
            "price": float(presentation.final_price),
            "quantity": quantity,
        }

    request.session["cart"] = cart

    return JsonResponse({"ok": True, "cart": cart})


@require_POST
def remove_from_cart(request):
    presentation_id = request.POST.get("presentation_id")

    cart = request.session.get("cart", {})

    key = str(presentation_id)

    if key in cart:
        del cart[key]
        request.session["cart"] = cart

    return JsonResponse({"ok": True, "cart": cart})
