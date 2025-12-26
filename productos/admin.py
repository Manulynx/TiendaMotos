from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Producto, ImagenProducto, AtributoDinamico, ValorProducto, Color


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    """
    Administración de Colores
    """
    list_display = ['nombre', 'muestra_color', 'codigo_hex', 'orden', 'productos_count', 'es_activo']
    list_filter = ['es_activo']
    search_fields = ['nombre', 'codigo_hex']
    list_editable = ['orden', 'es_activo']
    ordering = ['orden', 'nombre']
    
    fieldsets = (
        ('Información del Color', {
            'fields': ('nombre', 'codigo_hex', 'orden')
        }),
        ('Estado', {
            'fields': ('es_activo',)
        }),
    )
    
    def muestra_color(self, obj):
        """Muestra un círculo con el color"""
        return format_html(
            '<span style="display: inline-block; width: 30px; height: 30px; background-color: {}; border: 2px solid #ddd; border-radius: 50%;"></span>',
            obj.codigo_hex
        )
    muestra_color.short_description = 'Color'
    
    def productos_count(self, obj):
        """Cuenta productos con este color"""
        return obj.productos.count()
    productos_count.short_description = 'Productos'


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """
    Administración de Categorías con jerarquía.
    """
    list_display = ['nombre', 'padre', 'cantidad_productos', 'fecha_creacion']
    list_filter = ['padre', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']
    date_hierarchy = 'fecha_creacion'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion')
        }),
        ('Jerarquía', {
            'fields': ('padre',),
            'description': 'Selecciona una categoría padre para crear subcategorías'
        }),
    )
    
    def cantidad_productos(self, obj):
        """Cuenta la cantidad de productos en esta categoría."""
        return obj.productos.count()
    cantidad_productos.short_description = 'Productos'


class ImagenProductoInline(admin.TabularInline):
    """
    Inline para gestionar imágenes de galería desde el admin de Producto.
    """
    model = ImagenProducto
    extra = 1
    fields = ['imagen', 'descripcion', 'orden']
    ordering = ['orden']


class ValorProductoInline(admin.TabularInline):
    """
    Inline para gestionar atributos dinámicos desde el admin de Producto.
    """
    model = ValorProducto
    extra = 1
    fields = ['atributo', 'valor']
    autocomplete_fields = ['atributo']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """
    Administración completa de Productos con inlines y filtros avanzados.
    """
    list_display = [
        'nombre', 
        'sku', 
        'categoria', 
        'colores_html',
        'precio_formateado', 
        'stock_actual', 
        'es_activo',
        'imagen_miniatura',
        'fecha_creacion'
    ]
    list_filter = ['categoria', 'colores', 'es_activo', 'moneda', 'fecha_creacion']
    search_fields = ['nombre', 'sku', 'descripcion']
    list_editable = ['es_activo', 'stock_actual']
    readonly_fields = ['sku', 'fecha_creacion', 'fecha_actualizacion', 'imagen_preview']
    ordering = ['-fecha_creacion']
    date_hierarchy = 'fecha_creacion'
    filter_horizontal = ['colores']  # Interfaz mejorada para seleccionar colores
    
    inlines = [ImagenProductoInline, ValorProductoInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'categoria', 'descripcion')
        }),
        ('Pricing', {
            'fields': ('precio_venta', 'moneda'),
            'classes': ('wide',)
        }),
        ('Colores Disponibles', {
            'fields': ('colores',),
            'description': 'Selecciona todos los colores disponibles para este producto'
        }),
        ('Inventario', {
            'fields': ('stock_actual', 'es_activo'),
        }),
        ('Multimedia', {
            'fields': ('imagen_principal', 'imagen_preview'),
            'description': 'Imagen principal del producto'
        }),
        ('Información del Sistema', {
            'fields': ('sku', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def colores_html(self, obj):
        """Muestra los colores como círculos"""
        if obj.colores.exists():
            html = ''.join([
                f'<span style="display: inline-block; width: 20px; height: 20px; background-color: {color.codigo_hex}; border: 1px solid #ddd; border-radius: 50%; margin-right: 3px;" title="{color.nombre}"></span>'
                for color in obj.colores.all()
            ])
            return format_html(html)
        return '-'
    colores_html.short_description = 'Colores'
    
    def imagen_miniatura(self, obj):
        """Muestra una miniatura de la imagen principal."""
        if obj.imagen_principal:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.imagen_principal.url
            )
        return '-'
    imagen_miniatura.short_description = 'Imagen'
    
    def imagen_preview(self, obj):
        """Vista previa grande de la imagen principal."""
        if obj.imagen_principal:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 8px;" />',
                obj.imagen_principal.url
            )
        return 'Sin imagen'
    imagen_preview.short_description = 'Vista Previa'


@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    """
    Administración de imágenes de galería de productos.
    """
    list_display = ['producto', 'descripcion', 'orden', 'imagen_miniatura', 'fecha_subida']
    list_filter = ['producto__categoria', 'fecha_subida']
    search_fields = ['producto__nombre', 'descripcion']
    ordering = ['producto', 'orden']
    readonly_fields = ['fecha_subida', 'imagen_preview']
    
    fieldsets = (
        ('Información de la Imagen', {
            'fields': ('producto', 'imagen', 'imagen_preview', 'descripcion', 'orden')
        }),
        ('Metadata', {
            'fields': ('fecha_subida',),
            'classes': ('collapse',)
        }),
    )
    
    def imagen_miniatura(self, obj):
        """Muestra una miniatura de la imagen."""
        if obj.imagen:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.imagen.url
            )
        return '-'
    imagen_miniatura.short_description = 'Miniatura'
    
    def imagen_preview(self, obj):
        """Vista previa grande de la imagen."""
        if obj.imagen:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 400px; border-radius: 8px;" />',
                obj.imagen.url
            )
        return 'Sin imagen'
    imagen_preview.short_description = 'Vista Previa'


@admin.register(AtributoDinamico)
class AtributoDinamicoAdmin(admin.ModelAdmin):
    """
    Administración de atributos dinámicos para productos.
    """
    list_display = ['nombre', 'tipo_producto', 'unidad_medida', 'orden', 'cantidad_productos', 'fecha_creacion']
    list_filter = ['tipo_producto', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['orden']
    ordering = ['tipo_producto', 'orden', 'nombre']
    
    fieldsets = (
        ('Información del Atributo', {
            'fields': ('nombre', 'tipo_producto', 'unidad_medida', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('orden',)
        }),
    )
    
    def cantidad_productos(self, obj):
        """Cuenta productos que usan este atributo."""
        return obj.valores.count()
    cantidad_productos.short_description = 'Productos usando'


@admin.register(ValorProducto)
class ValorProductoAdmin(admin.ModelAdmin):
    """
    Administración de valores de atributos de productos.
    """
    list_display = ['producto', 'atributo', 'valor', 'valor_con_unidad']
    list_filter = ['atributo__tipo_producto', 'atributo']
    search_fields = ['producto__nombre', 'atributo__nombre', 'valor']
    autocomplete_fields = ['producto', 'atributo']
    ordering = ['producto', 'atributo']
    
    fieldsets = (
        ('Relación', {
            'fields': ('producto', 'atributo')
        }),
        ('Valor', {
            'fields': ('valor',)
        }),
    )
    
    def valor_con_unidad(self, obj):
        """Muestra el valor con su unidad de medida."""
        return obj.valor_formateado
    valor_con_unidad.short_description = 'Valor Formateado'


# Personalización del sitio de administración
admin.site.site_header = "Administración MotoLuxe"
admin.site.site_title = "Panel de Control MotoLuxe"
admin.site.index_title = "Gestión de Productos y Categorías"