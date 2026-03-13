from django.shortcuts import render
from productos.models import Producto, ConfiguracionHome

# Create your views here.

def home(request):
    # Obtener los 3 productos más recientes que estén activos
    productos_destacados = Producto.objects.filter(
        es_activo=True
    ).select_related('categoria').order_by('-fecha_creacion')[:3]

    # Obtener configuración del hero
    config_home = ConfiguracionHome.get_config()
    
    context = {
        'productos_destacados': productos_destacados,
        'config_home': config_home,
    }
    return render(request, 'home.html', context)


def contacto(request):
    """Vista de la página de contacto"""
    return render(request, 'contacto.html')

