from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Dish, Presentation, Sale, SaleItem
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from django.contrib import messages


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


@require_POST
def save_sale(request):
    cart = request.session.get("cart", {})

    if not cart:
        return redirect("menu")

    sale = Sale.objects.create()

    for presentation_id, item in cart.items():
        presentation = Presentation.objects.get(id=presentation_id)

        SaleItem.objects.create(
            sale=sale,
            presentation=presentation,
            quantity=item["quantity"],
            price=item["price"],  # precio congelado
        )

    sale.calculate_total()

    messages.success(request, f"Venta #{sale.id} guardada correctamente")

    # Limpiar carrito
    request.session["cart"] = {}

    return redirect("menu")
