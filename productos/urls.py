from django.urls import path
from productos import views

app_name = 'productos'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('<int:producto_id>/', views.detalle, name='detalle'),
    path('buscar/', views.buscar_productos, name='buscar'),
    
    # Auth URLs
    path('admin-custom/login/', views.admin_login, name='admin_login'),
    path('admin-custom/logout/', views.admin_logout, name='admin_logout'),
    
    # Admin Custom URLs
    path('admin-custom/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-custom/productos/', views.admin_productos_lista, name='admin_productos_lista'),
    path('admin-custom/productos/crear/', views.admin_producto_crear, name='admin_producto_crear'),
    path('admin-custom/productos/<int:producto_id>/editar/', views.admin_producto_editar, name='admin_producto_editar'),
    path('admin-custom/productos/<int:producto_id>/toggle/', views.admin_producto_toggle_estado, name='admin_producto_toggle'),
    path('admin-custom/productos/<int:producto_id>/eliminar/', views.admin_producto_eliminar, name='admin_producto_eliminar'),
    path('admin-custom/productos/<int:producto_id>/imagen/subir/', views.admin_imagen_subir, name='admin_imagen_subir'),
    path('admin-custom/imagenes/<int:imagen_id>/eliminar/', views.admin_imagen_eliminar, name='admin_imagen_eliminar'),
    path('admin-custom/categorias/', views.admin_categorias_lista, name='admin_categorias_lista'),
    path('admin-custom/categorias/crear/', views.admin_categoria_crear, name='admin_categoria_crear'),
    path('admin-custom/categorias/<int:categoria_id>/editar/', views.admin_categoria_editar, name='admin_categoria_editar'),
    path('admin-custom/categorias/<int:categoria_id>/eliminar/', views.admin_categoria_eliminar, name='admin_categoria_eliminar'),
]