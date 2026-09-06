from django.db import models
from django.conf import settings


class Category(models.Model):
    nombre = models.CharField(max_length=100)
    # muestra/oculta la categoría y sus productos del catálogo público
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Product(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    @property
    def imagen_principal(self):
        primera = self.images.first()
        if primera:
            return primera.imagen.url
        return "/static/img/producto_generico.png"


class ProductImage(models.Model):
    # CASCADE: si se borra el producto, sus imágenes no tienen sentido sin él
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    # upload_to: subcarpeta dentro de MEDIA_ROOT donde se guardan estos archivos
    imagen = models.ImageField(upload_to="productos/")

    def __str__(self):
        return f"Imagen de {self.product.nombre}"


class Order(models.Model):
    METODO_PAGO_CHOICES = [
        ("tarjeta", "Tarjeta"),
        ("transferencia", "Transferencia"),
        ("efectivo", "Efectivo"),
    ]
    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("pagado", "Pagado"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    fecha = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="pendiente"
    )
    # el total se calcula y se guarda al momento de crear el pedido
    # no se modifica aunque el precio del producto cambie luego
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Pedido #{self.pk} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField()
    # guarda el precio al momento de la orden
    # no se modifica aunque el precio del producto cambie luego
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.product}"
