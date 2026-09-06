from django.contrib import admin
from .models import Category, Product, ProductImage, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activa")
    list_filter = ("activa",)
    search_fields = ("nombre",)


class ProductImageInline(admin.TabularInline):
    # permite editar las imágenes de un producto en la misma pantalla del producto
    model = ProductImage
    extra = 1  # cuántos formularios vacíos extra mostrar para cargar imágenes nuevas


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("nombre", "category", "precio", "stock", "activo")
    list_filter = ("category", "activo")
    search_fields = ("nombre",)
    inlines = [ProductImageInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "cantidad", "precio_unitario")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False  # impide agregar items a un pedido ya creado


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "fecha", "metodo_pago", "estado", "total")
    list_filter = ("estado", "metodo_pago")
    readonly_fields = ("user", "fecha", "metodo_pago", "estado", "total")
    inlines = [OrderItemInline]

    def has_add_permission(self, request):
        return False  # los pedidos se crean solo desde el checkout, no desde el admin

    def has_delete_permission(self, request, obj=None):
        return False  # impide que las órdenes se puedan eliminar

    def has_change_permission(self, request, obj=None):
        return False  # impide que las órdenes se puedan editar
