from django.contrib import admin
from .models import Dish, Sale, SaleItem, Presentation


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_available")
    list_filter = ("is_available",)
    search_fields = ("name",)


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = ("name", "dish", "extra_price")
    list_filter = ("dish",)
    search_fields = ["name", "dish__name"]


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    autocomplete_fields = ["presentation"]
    exclude = ["price"]


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "total")
    readonly_fields = ("created_at", "total")
    inlines = [SaleItemInline]

    def save_model(self, request, obj, form, change):
        """
        Guarda la venta sin calcular el total aún
        (los items se guardan después)
        """
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        """
        Cuando ya existen los SaleItem,
        recalculamos el total
        """
        super().save_related(request, form, formsets, change)
        form.instance.calculate_total()
