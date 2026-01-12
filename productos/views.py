from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Max
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Producto, Categoria, ImagenProducto, AtributoDinamico, ValorProducto, Color
import json

def lista(request):
    """
    Vista de listado de productos con filtros avanzados
    """
    productos = Producto.objects.filter(es_activo=True).select_related('categoria').prefetch_related('valores_atributos', 'colores')
    
    # Obtener todas las categorías y colores para el sidebar
    categorias = Categoria.objects.all().prefetch_related('productos')
    colores_disponibles = Color.objects.filter(es_activo=True, productos__es_activo=True).distinct().order_by('orden')
    
    # Obtener precio máximo para el slider
    precio_max_db = Producto.objects.filter(es_activo=True).aggregate(
        max_precio=Max('precio_venta')
    )['max_precio'] or 10000
    
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
        productos = productos.filter(categoria_id=categoria_id)
        try:
            categoria_seleccionada = Categoria.objects.get(id=categoria_id)
        except Categoria.DoesNotExist:
            pass
    
    # Filtro por colores (múltiple)
    colores_ids = request.GET.getlist('color')
    colores_seleccionados = []
    if colores_ids:
        productos = productos.filter(colores__id__in=colores_ids).distinct()
        colores_seleccionados = Color.objects.filter(id__in=colores_ids)
    
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
    elif ordenar == 'popular':
        productos = productos.order_by('-vistas', '-fecha_creacion')
    elif ordenar == 'mas_vendido':
        productos = productos.order_by('-ventas', '-fecha_creacion')
    else:
        productos = productos.order_by('-fecha_creacion')
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'colores_disponibles': colores_disponibles,
        'categoria_seleccionada': categoria_seleccionada,
        'colores_seleccionados': colores_seleccionados,
        'precio_max_db': precio_max_db,
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
    """Vista para búsqueda AJAX de productos"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'productos': []})
    
    productos = Producto.objects.filter(
        Q(nombre__icontains=query) | 
        Q(descripcion__icontains=query) |
        Q(sku__icontains=query),
        es_activo=True
    ).select_related('categoria')[:5]
    
    resultados = [{
        'id': p.id,
        'nombre': p.nombre,
        'categoria': p.categoria.nombre,
        'precio': str(p.precio_venta),
        'moneda': p.moneda,
        'imagen': p.imagen_principal.url if p.imagen_principal else None,
        'url': reverse('productos:detalle', kwargs={'producto_id': p.id})
    } for p in productos]
    
    return JsonResponse({'productos': resultados})


def admin_login(request):
    """Vista de login personalizada para el panel de administración"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('productos:admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff:
                login(request, user)
                next_url = request.GET.get('next', 'productos:admin_dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'No tienes permisos de administrador')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'admin_custom/login.html')


def admin_logout(request):
    """Cerrar sesión del panel de administración"""
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('home')


@staff_member_required(login_url='/productos/admin-custom/login/')
def admin_dashboard(request):
    """Dashboard principal del panel de administración"""
    total_productos = Producto.objects.count()
    productos_activos = Producto.objects.filter(es_activo=True).count()
    total_categorias = Categoria.objects.count()
    total_atributos = AtributoDinamico.objects.count()
    productos_sin_stock = Producto.objects.filter(stock_actual=0).count()
    
    # Últimos 5 productos agregados/editados
    productos_recientes = Producto.objects.select_related('categoria').order_by('-fecha_actualizacion', '-fecha_creacion')[:5]
    
    context = {
        'total_productos': total_productos,
        'productos_activos': productos_activos,
        'total_categorias': total_categorias,
        'total_atributos': total_atributos,
        'productos_sin_stock': productos_sin_stock,
        'productos_recientes': productos_recientes,
    }
    return render(request, 'admin_custom/dashboard.html', context)


@staff_member_required(login_url='/productos/admin-custom/login/')
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


@staff_member_required(login_url='/productos/admin-custom/login/')
def admin_producto_crear(request):
    """Crear nuevo producto"""
    if request.method == 'POST':
        try:
            # Procesar formulario
            nombre = request.POST.get('nombre')
            categoria_id = request.POST.get('categoria')
            precio = request.POST.get('precio')
            moneda = request.POST.get('moneda', 'USD')
            stock = request.POST.get('stock', 0)
            descripcion = request.POST.get('descripcion', '')
            imagen = request.FILES.get('imagen')
            colores_ids = request.POST.getlist('colores')  # Obtener colores seleccionados
            
            # Validaciones básicas
            if not nombre or not categoria_id or not precio:
                return JsonResponse({
                    'success': False,
                    'message': 'Campos obligatorios faltantes'
                })
            
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
            
            # Asignar colores al producto
            if colores_ids:
                producto.colores.set(colores_ids)
            
            # Guardar imágenes de galería
            for key in request.FILES:
                if key.startswith('galeria_'):
                    imagen_file = request.FILES[key]
                    ImagenProducto.objects.create(
                        producto=producto,
                        imagen=imagen_file,
                        orden=0  # El orden se puede ajustar después en editar
                    )
            
            # Guardar atributos dinámicos
            atributos = AtributoDinamico.objects.all()
            for atributo in atributos:
                valor = request.POST.get(f'atributo_{atributo.id}', '').strip()
                if valor:
                    ValorProducto.objects.create(
                        producto=producto,
                        atributo=atributo,
                        valor=valor
                    )
            
            return JsonResponse({
                'success': True,
                'message': f'Producto "{nombre}" creado exitosamente',
                'redirect': reverse('productos:admin_producto_editar', kwargs={'producto_id': producto.id})
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al crear producto: {str(e)}'
            })
    
    categorias = Categoria.objects.all()
    colores = Color.objects.filter(es_activo=True).order_by('orden')
    
    # Obtener atributos generales para el formulario inicial
    atributos_disponibles = AtributoDinamico.objects.filter(
        tipo_producto='general'
    ).order_by('orden', 'nombre')
    
    context = {
        'categorias': categorias,
        'colores': colores,
        'atributos_disponibles': atributos_disponibles
    }
    return render(request, 'admin_custom/producto_crear.html', context)


@staff_member_required(login_url='/productos/admin-custom/login/')
def admin_producto_editar(request, producto_id):
    """Editar producto existente"""
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        try:
            producto.nombre = request.POST.get('nombre')
            producto.categoria_id = request.POST.get('categoria')
            producto.precio_venta = request.POST.get('precio')
            producto.moneda = request.POST.get('moneda', 'USD')
            producto.stock_actual = request.POST.get('stock', 0)
            producto.descripcion = request.POST.get('descripcion', '')
            producto.es_activo = request.POST.get('es_activo') == 'true'
            
            if 'imagen' in request.FILES:
                producto.imagen_principal = request.FILES['imagen']
            
            producto.save()
            
            # Actualizar colores
            colores_ids = request.POST.getlist('colores')
            producto.colores.set(colores_ids)
            
            # Actualizar atributos dinámicos
            producto.valores_atributos.all().delete()
            
            atributos = AtributoDinamico.objects.all()
            for atributo in atributos:
                valor = request.POST.get(f'atributo_{atributo.id}', '').strip()
                if valor:
                    ValorProducto.objects.create(
                        producto=producto,
                        atributo=atributo,
                        valor=valor
                    )
            
            return JsonResponse({
                'success': True,
                'message': 'Producto actualizado exitosamente',
                'redirect': reverse('productos:admin_productos_lista')
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar el producto: {str(e)}'
            }, status=400)
    
    categorias = Categoria.objects.all()
    colores = Color.objects.filter(es_activo=True).order_by('orden')
    imagenes_galeria = producto.galeria_imagenes.all()
    
    # Determinar el tipo de producto basado en la categoría
    categoria_nombre = producto.categoria.nombre.lower()
    
    tipo_filtro = 'general'
    
    # Agrupar todas las categorías eléctricas
    if any(keyword in categoria_nombre for keyword in ['electrica', 'eléctrica', 'e-bike', 'ebike', 'bicimoto', 'bici']):
        tipo_filtro = 'electrica'
    elif any(keyword in categoria_nombre for keyword in ['combustion', 'combustión', 'moto', 'gasolina']):
        tipo_filtro = 'combustion'
    elif 'triciclo' in categoria_nombre:
        tipo_filtro = 'triciclo'
    
    # Obtener atributos generales + específicos del tipo
    atributos_disponibles = AtributoDinamico.objects.filter(
        Q(tipo_producto='general') | Q(tipo_producto=tipo_filtro)
    ).order_by('orden', 'nombre')
    
    valores_actuales = {v.atributo_id: v.valor for v in producto.valores_atributos.all()}
    
    context = {
        'producto': producto,
        'categorias': categorias,
        'colores': colores,
        'imagenes_galeria': imagenes_galeria,
        'atributos_disponibles': atributos_disponibles,
        'valores_actuales': valores_actuales,
        'tipo_producto': tipo_filtro,
    }
    return render(request, 'admin_custom/producto_editar.html', context)
        

@staff_member_required(login_url='/productos/admin-custom/login/')
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


@staff_member_required(login_url='/productos/admin-custom/login/')
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


@staff_member_required(login_url='/productos/admin-custom/login/')
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


@staff_member_required(login_url='/productos/admin-custom/login/')
@require_POST
def admin_imagen_eliminar(request, imagen_id):
    """Eliminar imagen de la galería (AJAX)"""
    imagen = get_object_or_404(ImagenProducto, id=imagen_id)
    imagen.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Imagen eliminada exitosamente'
    })


# Nueva vista para obtener atributos por categoría (AJAX)
@staff_member_required(login_url='/productos/admin-custom/login/')
def admin_obtener_atributos(request):
    """Obtiene los atributos correspondientes según la categoría seleccionada (AJAX)"""
    categoria_id = request.GET.get('categoria_id')
    
    if not categoria_id:
        return JsonResponse({'atributos': []})
    
    try:
        categoria = Categoria.objects.get(id=categoria_id)
        categoria_nombre = categoria.nombre.lower()
        
        # Determinar tipo de producto
        tipo_filtro = 'general'
        
        # Agrupar todas las categorías eléctricas (Motos Eléctricas, E-Bikes, Bicimotos)
        if any(keyword in categoria_nombre for keyword in ['electrica', 'eléctrica', 'e-bike', 'ebike', 'bicimoto', 'bici']):
            tipo_filtro = 'electrica'
        elif any(keyword in categoria_nombre for keyword in ['combustion', 'combustión', 'moto', 'gasolina']):
            tipo_filtro = 'combustion'
        elif 'triciclo' in categoria_nombre:
            tipo_filtro = 'triciclo'
        
        # Obtener atributos generales + específicos
        atributos = AtributoDinamico.objects.filter(
            Q(tipo_producto='general') | Q(tipo_producto=tipo_filtro)
        ).order_by('orden', 'nombre')
        
        atributos_data = [{
            'id': attr.id,
            'nombre': attr.nombre,
            'unidad_medida': attr.unidad_medida or '',
            'tipo_producto': attr.get_tipo_producto_display()
        } for attr in atributos]
        
        return JsonResponse({
            'success': True,
            'atributos': atributos_data,
            'tipo_producto': tipo_filtro
        })
        
    except Categoria.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Categoría no encontrada'})


# ===== VISTAS PARA CATEGORÍAS =====

@staff_member_required(login_url='/productos/admin-custom/login/')
def admin_categorias_lista(request):
    """Lista de categorías"""
    categorias = Categoria.objects.prefetch_related('productos').order_by('nombre')
    
    context = {'categorias': categorias}
    return render(request, 'admin_custom/categorias_lista.html', context)


@staff_member_required(login_url='/productos/admin-custom/login/')
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


@staff_member_required(login_url='/productos/admin-custom/login/')
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


@staff_member_required(login_url='/productos/admin-custom/login/')
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


# ===== VISTAS PARA ATRIBUTOS DINÁMICOS =====

@staff_member_required(login_url='/productos/admin-custom/login/')
def admin_atributos_lista(request):
    """Lista de atributos dinámicos"""
    atributos = AtributoDinamico.objects.all().order_by('tipo_producto', 'orden', 'nombre')
    
    context = {'atributos': atributos}
    return render(request, 'admin_custom/atributos_lista.html', context)


@staff_member_required(login_url='/productos/admin-custom/login/')
def admin_atributo_crear(request):
    """Crear atributo dinámico"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        tipo_producto = request.POST.get('tipo_producto')
        unidad_medida = request.POST.get('unidad_medida', '')
        descripcion = request.POST.get('descripcion', '')
        orden = request.POST.get('orden', 0)
        
        AtributoDinamico.objects.create(
            nombre=nombre,
            tipo_producto=tipo_producto,
            unidad_medida=unidad_medida,
            descripcion=descripcion,
            orden=orden
        )
        
        messages.success(request, f'Atributo "{nombre}" creado exitosamente')
        return redirect('productos:admin_atributos_lista')
    
    return render(request, 'admin_custom/atributo_crear.html')


@staff_member_required(login_url='/productos/admin-custom/login/')
def admin_atributo_editar(request, atributo_id):
    """Editar atributo dinámico"""
    atributo = get_object_or_404(AtributoDinamico, id=atributo_id)
    
    if request.method == 'POST':
        atributo.nombre = request.POST.get('nombre')
        atributo.tipo_producto = request.POST.get('tipo_producto')
        atributo.unidad_medida = request.POST.get('unidad_medida', '')
        atributo.descripcion = request.POST.get('descripcion', '')
        atributo.orden = request.POST.get('orden', 0)
        atributo.save()
        
        messages.success(request, 'Atributo actualizado exitosamente')
        return redirect('productos:admin_atributos_lista')
    
    context = {'atributo': atributo}
    return render(request, 'admin_custom/atributo_editar.html', context)


@staff_member_required(login_url='/productos/admin-custom/login/')
@require_POST
def admin_atributo_eliminar(request, atributo_id):
    """Eliminar atributo dinámico (AJAX)"""
    atributo = get_object_or_404(AtributoDinamico, id=atributo_id)
    
    # Verificar si hay productos usando este atributo
    if atributo.valores.exists():
        return JsonResponse({
            'success': False,
            'message': f'No se puede eliminar. {atributo.valores.count()} productos usan este atributo'
        })
    
    nombre = atributo.nombre
    atributo.delete()
    
    return JsonResponse({
        'success': True,
        'message': f'Atributo "{nombre}" eliminado exitosamente'
    })


@staff_member_required(login_url='/productos/admin-custom/login/')
def admin_categoria_atributos(request, categoria_id):
    """Obtener atributos según la categoría (AJAX)"""
    try:
        categoria = get_object_or_404(Categoria, id=categoria_id)
        categoria_nombre = categoria.nombre.lower()
        
        # Determinar el tipo de producto basado en la categoría
        tipo_filtro = 'general'
        
        # Agrupar todas las categorías eléctricas
        if any(keyword in categoria_nombre for keyword in ['electrica', 'eléctrica', 'e-bike', 'ebike', 'bicimoto', 'bici']):
            tipo_filtro = 'electrica'
        elif any(keyword in categoria_nombre for keyword in ['combustion', 'combustión', 'moto', 'gasolina']):
            tipo_filtro = 'combustion'
        elif 'triciclo' in categoria_nombre:
            tipo_filtro = 'triciclo'
        
        # Obtener atributos generales + específicos del tipo
        atributos = AtributoDinamico.objects.filter(
            Q(tipo_producto='general') | Q(tipo_producto=tipo_filtro)
        ).order_by('orden', 'nombre')
        
        atributos_data = [{
            'id': attr.id,
            'nombre': attr.nombre,
            'unidad_medida': attr.unidad_medida or '',
            'tipo_producto': attr.tipo_producto,
            'tipo_producto_display': attr.get_tipo_producto_display(),
        } for attr in atributos]
        
        return JsonResponse({
            'success': True,
            'atributos': atributos_data,
            'tipo_producto': tipo_filtro,
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener atributos: {str(e)}'
        }, status=400)
