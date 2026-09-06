from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Category, Product, Order


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["nombre", "activa"]


class ProductForm(forms.ModelForm):
    # campo extra que no pertenece al modelo Product directamente:
    # se procesa a mano en la vista para crear varios ProductImage
    imagenes = MultipleFileField(required=False, label="Imágenes del producto")

    class Meta:
        model = Product
        fields = ["nombre", "descripcion", "precio", "stock", "category", "activo"]


class CheckoutForm(forms.Form):
    # form simple (no ModelForm) porque no mapea 1 a 1 con el modelo Order;
    # solo pide el método de pago, el resto lo arma la vista
    metodo_pago = forms.ChoiceField(
        choices=Order.METODO_PAGO_CHOICES, label="Método de pago"
    )


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class ProfileForm(forms.ModelForm):
    # formulario para que un usuario edite su propio perfil
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class UserAdminForm(forms.ModelForm):
    # formulario que usa el admin para editar cualquier usuario,
    # incluyendo si es staff y si está activo
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
        ]
