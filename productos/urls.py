from django.urls import path
from productos import views

app_name = 'productos'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('<int:producto_id>/', views.detalle, name='detalle'),    path('buscar/', views.buscar_productos, name='buscar'),]