from django.db import models
from django.db.models import Sum, F


class Dish(models.Model):
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Platillo"
        verbose_name_plural = "Platillos"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Presentation(models.Model):
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name="presentations",
        verbose_name="Platillo",
    )

    name = models.CharField(max_length=150, verbose_name="Presentación")

    extra_price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, verbose_name="Precio extra"
    )

    class Meta:
        verbose_name = "Presentación"
        verbose_name_plural = "Presentaciones"
        unique_together = ("dish", "name")

    def __str__(self):
        return f"{self.dish.name} - {self.name}"

    @property
    def final_price(self):
        return self.dish.price + self.extra_price


class Sale(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")

    total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Total"
    )

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Venta #{self.id} - {self.created_at:%Y-%m-%d %H:%M}"

    def calculate_total(self):
        total = (
            self.items.aggregate(total=Sum(F("price") * F("quantity")))["total"] or 0
        )

        self.total = total
        self.save()


class SaleItem(models.Model):
    sale = models.ForeignKey(
        Sale, on_delete=models.CASCADE, related_name="items", verbose_name="Venta"
    )

    presentation = models.ForeignKey(
        Presentation, on_delete=models.PROTECT, verbose_name="Presentación"
    )

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Precio unitario",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Detalle de venta"
        verbose_name_plural = "Detalles de venta"

    def __str__(self):
        return f"{self.quantity} x {self.presentation}"

    def save(self, *args, **kwargs):
        if self.price is None:
            self.price = self.presentation.final_price
        super().save(*args, **kwargs)
