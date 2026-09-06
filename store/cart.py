from decimal import Decimal
from .models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("cart")
        if cart is None:
            cart = self.session["cart"] = {}
        self.cart = cart

    def add(self, product, cantidad=1):
        product_id = str(product.id)
        if product_id not in self.cart:
            # guarda el precio como string directamente a JSON
            self.cart[product_id] = {"cantidad": 0, "precio": str(product.precio)}
        self.cart[product_id]["cantidad"] += cantidad
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        # marca la sesión como modificada para que Django la guarde
        self.session.modified = True

    def clear(self):
        self.session["cart"] = {}
        self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            data = self.cart[str(product.id)]
            precio = Decimal(data["precio"])
            yield {
                "product": product,
                "cantidad": data["cantidad"],
                "precio": precio,
                "subtotal": precio * data["cantidad"],
            }

    def __len__(self):
        return sum(item["cantidad"] for item in self.cart.values())

    def get_total(self):
        return sum(
            Decimal(item["precio"]) * item["cantidad"] for item in self.cart.values()
        )
