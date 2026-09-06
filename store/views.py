from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    View,
    TemplateView,
    FormView,
)
from django.db.models import Count, Sum, Q
from django.contrib import messages

from .models import Category, Product, ProductImage, Order, OrderItem
from .forms import (
    CategoryForm,
    ProductForm,
    CheckoutForm,
    SignUpForm,
    ProfileForm,
    UserAdminForm,
)
from .cart import Cart

from django.http import HttpResponse
import openpyxl
from openpyxl.styles import Font

# ---- Mixins de permisos (mismo patrón usado en el CRM) ----


class LoginRequiredView(LoginRequiredMixin):
    login_url = "login"
    redirect_field_name = "next"


class AdminRequiredView(LoginRequiredView, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


# ==================== PÚBLICO ====================


class ProductListView(ListView):
    model = Product
    template_name = "store/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        # solo productos activos Y de categorías activas
        # si se desactiva una categoría, sus productos desaparecen del catálogo
        qs = Product.objects.filter(activo=True, category__activa=True)
        query = self.request.GET.get("q", "")
        categoria_id = self.request.GET.get("categoria", "")
        if query:
            qs = qs.filter(Q(nombre__icontains=query) | Q(descripcion__icontains=query))
        if categoria_id:
            qs = qs.filter(category_id=categoria_id)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        context["categoria_seleccionada"] = self.request.GET.get("categoria", "")
        # solo muestra categorías activas en el filtro público
        context["categories"] = Category.objects.filter(activa=True)
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "store/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.filter(activo=True)


class CategoryListView(ListView):
    model = Category
    template_name = "store/category_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.filter(activa=True)


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")


# ==================== CARRITO (usuarios registrados) ====================


class CartAddView(LoginRequiredView, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk, activo=True)
        cart = Cart(request)
        cantidad = int(request.POST.get("cantidad", 1))
        cart.add(product, cantidad)
        messages.success(request, f"{product.nombre} añadido al carrito.")
        return redirect("cart_detail")


class CartRemoveView(LoginRequiredView, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        Cart(request).remove(product)
        return redirect("cart_detail")


class CartDetailView(LoginRequiredView, TemplateView):
    template_name = "store/cart_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = Cart(self.request)
        return context


# ==================== CHECKOUT / PEDIDOS (usuarios registrados) ====================


class CheckoutView(LoginRequiredView, FormView):
    form_class = CheckoutForm
    template_name = "store/checkout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = Cart(self.request)
        return context

    def form_valid(self, form):
        cart = Cart(self.request)
        if len(cart) == 0:
            messages.error(self.request, "Tu carrito está vacío.")
            return redirect("cart_detail")

        # pasarela de pago simulada
        order = Order.objects.create(
            user=self.request.user,
            metodo_pago=form.cleaned_data["metodo_pago"],
            estado="pagado",
            total=cart.get_total(),
        )
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                cantidad=item["cantidad"],
                precio_unitario=item["precio"],  # recupera el precio actual
            )
            # descontamos stock al confirmar el pedido
            item["product"].stock = max(0, item["product"].stock - item["cantidad"])
            item["product"].save()

        cart.clear()
        self.order_id = order.pk
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("order_detail", kwargs={"pk": self.order_id})


class MyOrderListView(LoginRequiredView, ListView):
    model = Order
    template_name = "store/order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        # cada usuario solo ve sus propios pedidos
        return Order.objects.filter(user=self.request.user)


class MyOrderDetailView(LoginRequiredView, DetailView):
    model = Order
    template_name = "store/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        # doble seguridad por si alguien ingresa el pk de otro pedido en la URL
        return Order.objects.filter(user=self.request.user)


# ==================== PERFIL (usuarios registrados) ====================


class ProfileUpdateView(LoginRequiredView, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "store/profile_form.html"
    success_url = reverse_lazy("product_list")

    def get_object(self):
        # ignora cualquier pk de la url, editando siempre al usuario logueado
        return self.request.user


# ==================== ADMIN: productos y categorías ====================


class ProductCreateView(AdminRequiredView, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "store/product_form.html"
    success_url = reverse_lazy("admin_product_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        for imagen in self.request.FILES.getlist("imagenes"):
            ProductImage.objects.create(product=self.object, imagen=imagen)
        return response


class ProductUpdateView(AdminRequiredView, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "store/product_form.html"
    success_url = reverse_lazy("admin_product_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        for imagen in self.request.FILES.getlist("imagenes"):
            ProductImage.objects.create(product=self.object, imagen=imagen)
        return response


class AdminProductListView(AdminRequiredView, ListView):
    model = Product
    template_name = "store/admin_product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.all().order_by("-fecha_creacion")


class ProductImageManageView(AdminRequiredView, TemplateView):
    template_name = "store/product_images_manage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product"] = get_object_or_404(Product, pk=self.kwargs["pk"])
        return context


class ProductImageDeleteView(AdminRequiredView, View):
    def post(self, request, pk):
        # buscamos la imagen puntual, no el producto
        image = get_object_or_404(ProductImage, pk=pk)
        product_pk = (
            image.product.pk
        )  # guardamos el pk del producto ANTES de borrar la imagen
        image.delete()
        return redirect("product_images_manage", pk=product_pk)


class CategoryCreateView(AdminRequiredView, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "store/category_form.html"
    success_url = reverse_lazy("admin_category_list")


class CategoryUpdateView(AdminRequiredView, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "store/category_form.html"
    success_url = reverse_lazy("admin_category_list")


class AdminCategoryListView(AdminRequiredView, ListView):
    model = Category
    template_name = "store/admin_category_list.html"
    context_object_name = "categories"


# ==================== ADMIN: usuarios ====================


class AdminUserListView(AdminRequiredView, ListView):
    model = User
    template_name = "store/admin_user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        qs = User.objects.all().order_by("username")
        if query:
            qs = qs.filter(Q(username__icontains=query) | Q(email__icontains=query))
        return qs


class AdminUserUpdateView(AdminRequiredView, UpdateView):
    model = User
    form_class = UserAdminForm
    template_name = "store/admin_user_form.html"
    success_url = reverse_lazy("admin_user_list")


class AdminUserDeactivateView(AdminRequiredView, UpdateView):
    model = User
    fields = []
    template_name = "store/admin_user_confirm_deactivate.html"
    success_url = reverse_lazy("admin_user_list")

    def form_valid(self, form):
        form.instance.is_active = False
        return super().form_valid(form)


# ==================== ADMIN: todas las órdenes ====================


class AdminOrderListView(AdminRequiredView, ListView):
    model = Order
    template_name = "store/admin_order_list.html"
    context_object_name = "orders"


class AdminOrderDetailView(AdminRequiredView, DetailView):
    model = Order
    template_name = "store/order_detail.html"
    context_object_name = "order"


# ==================== ESTADÍSTICAS ====================


class MyStatsView(LoginRequiredView, TemplateView):
    template_name = "store/my_stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = Order.objects.filter(user=self.request.user)
        context["total_pedidos"] = orders.count()
        context["total_gastado"] = orders.aggregate(total=Sum("total"))["total"] or 0

        # producto más comprado por este usuario en particular
        top_productos = (
            OrderItem.objects.filter(order__user=self.request.user)
            .values("product__nombre")
            .annotate(total_comprado=Sum("cantidad"))
            .order_by("-total_comprado")[:5]
        )
        context["top_productos"] = top_productos
        return context


class AdminStatsView(AdminRequiredView, TemplateView):
    template_name = "store/admin_stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        import json

        # productos más vendidos (global)
        top_productos = (
            OrderItem.objects.values("product__nombre")
            .annotate(total=Sum("cantidad"))
            .order_by("-total")[:10]
        )
        context["labels_productos"] = json.dumps(
            [p["product__nombre"] for p in top_productos]
        )
        context["data_productos"] = json.dumps([p["total"] for p in top_productos])

        # pedidos por usuario
        top_usuarios = (
            User.objects.annotate(total_pedidos=Count("orders"))
            .filter(total_pedidos__gt=0)
            .order_by("-total_pedidos")
        )
        context["labels_usuarios"] = json.dumps([u.username for u in top_usuarios])
        context["data_usuarios"] = json.dumps([u.total_pedidos for u in top_usuarios])

        context["total_ventas"] = (
            Order.objects.aggregate(total=Sum("total"))["total"] or 0
        )
        context["total_pedidos_global"] = Order.objects.count()
        return context


class ToggleViewModeView(AdminRequiredView, View):
    def post(self, request):
        modo_actual = request.session.get("view_mode", "admin")
        request.session["view_mode"] = "cliente" if modo_actual == "admin" else "admin"

        next_url = request.POST.get("next", "/")
        return redirect(next_url)


# ==================== EXPORTAR A EXCEL ====================


class AdminProductExportView(AdminRequiredView, View):
    def get(self, request):
        products = Product.objects.all().order_by("-fecha_creacion")

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Productos"

        headers = [
            "Nombre",
            "Categoría",
            "Precio",
            "Stock",
            "Activo",
            "Fecha de creación",
        ]
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)

        for product in products:
            ws.append(
                [
                    product.nombre,
                    str(product.category) if product.category else "Sin categoría",
                    float(
                        product.precio
                    ),  # float en vez de Decimal: openpyxl no serializa Decimal directamente
                    product.stock,
                    "Sí" if product.activo else "No",
                    product.fecha_creacion.strftime("%d/%m/%Y"),
                ]
            )

        for col_cells in ws.columns:
            max_length = max(len(str(cell.value or "")) for cell in col_cells)
            ws.column_dimensions[col_cells[0].column_letter].width = max_length + 2

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="productos.xlsx"'
        wb.save(response)
        return response


class AdminCategoryExportView(AdminRequiredView, View):
    def get(self, request):
        categories = Category.objects.all()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Categorías"

        headers = ["Nombre", "Activa", "Cantidad de productos"]
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)

        for category in categories:
            ws.append(
                [
                    category.nombre,
                    "Sí" if category.activa else "No",
                    category.products.count(),  # related_name "products" definido en Product.category
                ]
            )

        for col_cells in ws.columns:
            max_length = max(len(str(cell.value or "")) for cell in col_cells)
            ws.column_dimensions[col_cells[0].column_letter].width = max_length + 2

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="categorias.xlsx"'
        wb.save(response)
        return response


class AdminUserExportView(AdminRequiredView, View):
    def get(self, request):
        # respeta el mismo filtro de búsqueda que la lista, igual que hicimos
        # con la exportación de Client en el CRM
        query = request.GET.get("q", "")
        users = User.objects.all().order_by("username")
        if query:
            users = users.filter(
                Q(username__icontains=query) | Q(email__icontains=query)
            )

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Usuarios"

        headers = [
            "Username",
            "Email",
            "Nombre",
            "Apellido",
            "Admin",
            "Activo",
            "Fecha de alta",
        ]
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)

        for u in users:
            ws.append(
                [
                    u.username,
                    u.email,
                    u.first_name,
                    u.last_name,
                    "Sí" if u.is_staff else "No",
                    "Sí" if u.is_active else "No",
                    u.date_joined.strftime("%d/%m/%Y"),
                ]
            )

        for col_cells in ws.columns:
            max_length = max(len(str(cell.value or "")) for cell in col_cells)
            ws.column_dimensions[col_cells[0].column_letter].width = max_length + 2

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="usuarios.xlsx"'
        wb.save(response)
        return response


class AdminOrderExportView(AdminRequiredView, View):
    def get(self, request):
        orders = Order.objects.select_related("user").all()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Pedidos"

        headers = ["ID", "Usuario", "Fecha", "Método de pago", "Estado", "Total"]
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)

        for order in orders:
            ws.append(
                [
                    order.pk,
                    order.user.username,
                    order.fecha.strftime("%d/%m/%Y %H:%M"),
                    order.get_metodo_pago_display(),
                    order.get_estado_display(),
                    float(order.total),
                ]
            )

        for col_cells in ws.columns:
            max_length = max(len(str(cell.value or "")) for cell in col_cells)
            ws.column_dimensions[col_cells[0].column_letter].width = max_length + 2

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="pedidos.xlsx"'
        wb.save(response)
        return response
