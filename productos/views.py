from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from .models import Producto, Categoria, ImagenProducto, AtributoDinamico, ValorProducto
import json

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

@staff_member_required
def admin_dashboard(request):
    """Dashboard principal del panel de administración"""
    total_productos = Producto.objects.count()
    productos_activos = Producto.objects.filter(es_activo=True).count()
    categorias_count = Categoria.objects.count()
    productos_sin_stock = Producto.objects.filter(stock_actual=0).count()
    
    productos_recientes = Producto.objects.select_related('categoria').order_by('-fecha_creacion')[:5]
    
    context = {
        'total_productos': total_productos,
        'productos_activos': productos_activos,
        'categorias_count': categorias_count,
        'productos_sin_stock': productos_sin_stock,
        'productos_recientes': productos_recientes,
    }
    return render(request, 'admin_custom/dashboard.html', context)


@staff_member_required
def admin_productos_lista(request):
    """Lista de productos con filtros y búsqueda"""
    productos = Producto.objects.select_related('categoria').order_by('-fecha_creacion')
    
    # Filtros
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    estado = request.GET.get('estado', '')
    
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | 
            Q(sku__icontains=query)
        )
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if estado == 'activo':
        productos = productos.filter(es_activo=True)
    elif estado == 'inactivo':
        productos = productos.filter(es_activo=False)
    
    # Paginación
    paginator = Paginator(productos, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    categorias = Categoria.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categorias': categorias,
        'query': query,
        'categoria_seleccionada': categoria_id,
        'estado_seleccionado': estado,
    }
    return render(request, 'admin_custom/productos_lista.html', context)


@staff_member_required
def admin_producto_crear(request):
    """Crear nuevo producto"""
    if request.method == 'POST':
        # Procesar formulario
        nombre = request.POST.get('nombre')
        categoria_id = request.POST.get('categoria')
        precio = request.POST.get('precio')
        moneda = request.POST.get('moneda', 'USD')
        stock = request.POST.get('stock', 0)
        descripcion = request.POST.get('descripcion', '')
        imagen = request.FILES.get('imagen')
        
        producto = Producto.objects.create(
            nombre=nombre,
            categoria_id=categoria_id,
            precio_venta=precio,
            moneda=moneda,
            stock_actual=stock,
            descripcion=descripcion,
            imagen_principal=imagen,
            es_activo=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Producto creado exitosamente',
            'redirect': f'/admin-custom/productos/{producto.id}/editar/'
        })
    
    categorias = Categoria.objects.all()
    context = {'categorias': categorias}
    return render(request, 'admin_custom/producto_crear.html', context)


@staff_member_required
def admin_producto_editar(request, producto_id):
    """Editar producto existente"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.categoria_id = request.POST.get('categoria')
        producto.precio_venta = request.POST.get('precio')
        producto.moneda = request.POST.get('moneda', 'USD')
        producto.stock_actual = request.POST.get('stock', 0)
        producto.descripcion = request.POST.get('descripcion', '')
        
        if 'imagen' in request.FILES:
            producto.imagen_principal = request.FILES['imagen']
        
        producto.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Producto actualizado exitosamente'
        })
    
    categorias = Categoria.objects.all()
    imagenes_galeria = producto.galeria_imagenes.all()
    atributos = producto.valores_atributos.select_related('atributo').all()
    atributos_disponibles = AtributoDinamico.objects.all()
    
    context = {
        'producto': producto,
        'categorias': categorias,
        'imagenes_galeria': imagenes_galeria,
        'atributos': atributos,
        'atributos_disponibles': atributos_disponibles,
    }
    return render(request, 'admin_custom/producto_editar.html', context)


@staff_member_required
@require_POST
def admin_producto_toggle_estado(request, producto_id):
    """Toggle del estado activo/inactivo del producto (AJAX)"""
    producto = get_object_or_404(Producto, id=producto_id)
    producto.es_activo = not producto.es_activo
    producto.save()
    
    return JsonResponse({
        'success': True,
        'es_activo': producto.es_activo,
        'message': f'Producto {"activado" if producto.es_activo else "desactivado"} exitosamente'
    })


@staff_member_required
@require_POST
def admin_producto_eliminar(request, producto_id):
    """Eliminar producto (AJAX)"""
    producto = get_object_or_404(Producto, id=producto_id)
    nombre = producto.nombre
    producto.delete()
    
    return JsonResponse({
        'success': True,
        'message': f'Producto "{nombre}" eliminado exitosamente'
    })


@staff_member_required
@require_POST
def admin_imagen_subir(request, producto_id):
    """Subir imagen a la galería del producto (AJAX)"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    if 'imagen' not in request.FILES:
        return JsonResponse({'success': False, 'message': 'No se proporcionó imagen'})
    
    imagen = request.FILES['imagen']
    descripcion = request.POST.get('descripcion', '')
    orden = request.POST.get('orden', 0)
    
    imagen_producto = ImagenProducto.objects.create(
        producto=producto,
        imagen=imagen,
        descripcion=descripcion,
        orden=orden
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Imagen subida exitosamente',
        'imagen': {
            'id': imagen_producto.id,
            'url': imagen_producto.imagen.url,
            'descripcion': imagen_producto.descripcion
        }
    })


@staff_member_required
@require_POST
def admin_imagen_eliminar(request, imagen_id):
    """Eliminar imagen de la galería (AJAX)"""
    imagen = get_object_or_404(ImagenProducto, id=imagen_id)
    imagen.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Imagen eliminada exitosamente'
    })


@staff_member_required
def admin_categorias_lista(request):
    """Lista de categorías"""
    categorias = Categoria.objects.prefetch_related('productos').order_by('nombre')
    
    context = {'categorias': categorias}
    return render(request, 'admin_custom/categorias_lista.html', context)


@staff_member_required
@require_POST
def admin_categoria_crear(request):
    """Crear categoría (AJAX)"""
    nombre = request.POST.get('nombre')
    descripcion = request.POST.get('descripcion', '')
    padre_id = request.POST.get('padre', None)
    
    categoria = Categoria.objects.create(
        nombre=nombre,
        descripcion=descripcion,
        padre_id=padre_id if padre_id else None
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Categoría creada exitosamente',
        'categoria': {
            'id': categoria.id,
            'nombre': categoria.nombre,
            'descripcion': categoria.descripcion
        }
    })


@staff_member_required
@require_POST
def admin_categoria_editar(request, categoria_id):
    """Editar categoría (AJAX)"""
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    categoria.nombre = request.POST.get('nombre')
    categoria.descripcion = request.POST.get('descripcion', '')
    padre_id = request.POST.get('padre', None)
    categoria.padre_id = padre_id if padre_id else None
    categoria.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Categoría actualizada exitosamente'
    })


@staff_member_required
@require_POST
def admin_categoria_eliminar(request, categoria_id):
    """Eliminar categoría (AJAX)"""
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    if categoria.productos.exists():
        return JsonResponse({
            'success': False,
            'message': 'No se puede eliminar la categoría porque tiene productos asociados'
        })
    
    nombre = categoria.nombre
    categoria.delete()
    
    return JsonResponse({
        'success': True,
        'message': f'Categoría "{nombre}" eliminada exitosamente'
    })

