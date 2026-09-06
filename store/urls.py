from django.urls import path
from . import views

urlpatterns = [
    # exportar
    path(
        "admin-tienda/productos/exportar/",
        views.AdminProductExportView.as_view(),
        name="admin_product_export",
    ),
    path(
        "admin-tienda/categorias/exportar/",
        views.AdminCategoryExportView.as_view(),
        name="admin_category_export",
    ),
    path(
        "admin-tienda/usuarios/exportar/",
        views.AdminUserExportView.as_view(),
        name="admin_user_export",
    ),
    path(
        "admin-tienda/pedidos/exportar/",
        views.AdminOrderExportView.as_view(),
        name="admin_order_export",
    ),
    # público
    path("", views.ProductListView.as_view(), name="product_list"),
    path(
        "productos/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"
    ),
    path("categorias/", views.CategoryListView.as_view(), name="category_list"),
    path("registro/", views.SignUpView.as_view(), name="signup"),
    # carrito
    path("carrito/", views.CartDetailView.as_view(), name="cart_detail"),
    path("carrito/agregar/<int:pk>/", views.CartAddView.as_view(), name="cart_add"),
    path(
        "carrito/quitar/<int:pk>/", views.CartRemoveView.as_view(), name="cart_remove"
    ),
    # checkout y pedidos propios
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("mis-pedidos/", views.MyOrderListView.as_view(), name="order_list"),
    path(
        "mis-pedidos/<int:pk>/", views.MyOrderDetailView.as_view(), name="order_detail"
    ),
    path("mis-estadisticas/", views.MyStatsView.as_view(), name="my_stats"),
    # perfil propio
    path("perfil/", views.ProfileUpdateView.as_view(), name="profile_edit"),
    # admin: productos
    path(
        "admin-tienda/productos/",
        views.AdminProductListView.as_view(),
        name="admin_product_list",
    ),
    path(
        "admin-tienda/productos/nuevo/",
        views.ProductCreateView.as_view(),
        name="product_create",
    ),
    path(
        "admin-tienda/productos/<int:pk>/editar/",
        views.ProductUpdateView.as_view(),
        name="product_update",
    ),
    # admin: categorías
    path(
        "admin-tienda/categorias/",
        views.AdminCategoryListView.as_view(),
        name="admin_category_list",
    ),
    path(
        "admin-tienda/categorias/nueva/",
        views.CategoryCreateView.as_view(),
        name="category_create",
    ),
    path(
        "admin-tienda/categorias/<int:pk>/editar/",
        views.CategoryUpdateView.as_view(),
        name="category_update",
    ),
    # admin: usuarios
    path(
        "admin-tienda/usuarios/",
        views.AdminUserListView.as_view(),
        name="admin_user_list",
    ),
    path(
        "admin-tienda/usuarios/<int:pk>/editar/",
        views.AdminUserUpdateView.as_view(),
        name="admin_user_update",
    ),
    path(
        "admin-tienda/usuarios/<int:pk>/desactivar/",
        views.AdminUserDeactivateView.as_view(),
        name="admin_user_deactivate",
    ),
    # admin: pedidos y estadísticas
    path(
        "admin-tienda/pedidos/",
        views.AdminOrderListView.as_view(),
        name="admin_order_list",
    ),
    path(
        "admin-tienda/pedidos/<int:pk>/",
        views.AdminOrderDetailView.as_view(),
        name="admin_order_detail",
    ),
    path(
        "admin-tienda/estadisticas/", views.AdminStatsView.as_view(), name="admin_stats"
    ),
    # cambar vista
    path("cambiar-vista/", views.ToggleViewModeView.as_view(), name="toggle_view_mode"),
    # eliminar imágenes de producto
    path(
        "admin-tienda/productos/<int:pk>/imagenes/",
        views.ProductImageManageView.as_view(),
        name="product_images_manage",
    ),
    path(
        "admin-tienda/imagenes/<int:pk>/borrar/",
        views.ProductImageDeleteView.as_view(),
        name="product_image_delete",
    ),
]
