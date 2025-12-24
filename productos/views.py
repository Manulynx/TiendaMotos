from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from .models import Producto, Categoria

def lista(request):
    """
    Vista de listado de productos con filtros avanzados:
    - Búsqueda por nombre
    - Filtro por categoría
    - Filtro por rango de precio
    - Filtro por disponibilidad en stock
    - Ordenamiento
    """
    productos = Producto.objects.filter(es_activo=True).select_related('categoria').prefetch_related('valores_atributos')
    
    # Obtener todas las categorías para el sidebar
    categorias = Categoria.objects.all().prefetch_related('productos')
    
    # Filtro de búsqueda por nombre o descripción
    query = request.GET.get('q', '').strip()
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | 
            Q(descripcion__icontains=query) |
            Q(sku__icontains=query)
        )
    
    # Filtro por categoría
    categoria_id = request.GET.get('categoria')
    categoria_seleccionada = None
    if categoria_id:
        try:
            categoria_seleccionada = Categoria.objects.get(id=categoria_id)
            productos = productos.filter(categoria_id=categoria_id)
        except Categoria.DoesNotExist:
            pass
    
    # Filtro por rango de precio
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    
    if precio_min:
        try:
            productos = productos.filter(precio_venta__gte=float(precio_min))
        except ValueError:
            pass
    
    if precio_max:
        try:
            productos = productos.filter(precio_venta__lte=float(precio_max))
        except ValueError:
            pass
    
    # Filtro por disponibilidad en stock
    en_stock = request.GET.get('en_stock')
    if en_stock:
        productos = productos.filter(stock_actual__gt=0)
    
    # Ordenamiento
    ordenar = request.GET.get('ordenar', '')
    if ordenar == 'precio_asc':
        productos = productos.order_by('precio_venta')
    elif ordenar == 'precio_desc':
        productos = productos.order_by('-precio_venta')
    elif ordenar == 'nombre':
        productos = productos.order_by('nombre')
    else:
        productos = productos.order_by('-fecha_creacion')
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada,
    }
    return render(request, 'productos/lista.html', context)


def detalle(request, producto_id):
    producto = get_object_or_404(
        Producto.objects.select_related('categoria').prefetch_related(
            'valores_atributos__atributo',
            'galeria_imagenes'
        ),
        id=producto_id,
        es_activo=True
    )
    
    # Obtener productos relacionados de la misma categoría
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        es_activo=True
    ).exclude(id=producto.id).select_related('categoria')[:3]
    
    # Número de WhatsApp (puedes configurar esto en settings.py)
    whatsapp_numero = '5355513196'  # Cambia este número
    mensaje_whatsapp = f'Hola, estoy interesado en el producto: {producto.nombre}'
    
    context = {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
        'whatsapp_numero': whatsapp_numero,
        'mensaje_whatsapp': mensaje_whatsapp,
    }
    return render(request, 'productos/detalles.html', context)


def buscar_productos(request):
    """Vista AJAX para buscar productos en tiempo real"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'productos': []})
    
    # Buscar productos que coincidan con la consulta
    productos = Producto.objects.filter(
        Q(nombre__icontains=query) |
        Q(descripcion__icontains=query) |
        Q(sku__icontains=query),
        es_activo=True
    ).select_related('categoria')[:5]  # Limitar a 5 resultados
    
    # Formatear resultados para JSON
    resultados = []
    for producto in productos:
        resultado = {
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': str(producto.precio_venta),
            'precio_formateado': producto.precio_formateado,
            'categoria': producto.categoria.nombre if producto.categoria else '',
            'imagen': producto.imagen_principal.url if producto.imagen_principal else '/static/images/hero.webp',
            'url': f'/productos/{producto.id}/'
        }
        resultados.append(resultado)
    
    return JsonResponse({'productos': resultados})

