from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Producto, ImagenProducto, AtributoDinamico, ValorProducto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """
    Administración de Categorías con soporte para jerarquía.
    """
    list_display = ['nombre', 'padre', 'cantidad_productos', 'fecha_creacion']
    list_filter = ['padre', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion')
        }),
        ('Jerarquía', {
            'fields': ('padre',),
            'description': 'Selecciona una categoría padre para crear una subcategoría'
        }),
    )
    
    def cantidad_productos(self, obj):
        """Muestra la cantidad de productos en esta categoría."""
        return obj.productos.count()
    cantidad_productos.short_description = 'Productos'


class ImagenProductoInline(admin.TabularInline):
    """
    Inline para gestionar imágenes adicionales del producto.
    """
    model = ImagenProducto
    extra = 1
    fields = ['imagen', 'orden', 'descripcion', 'vista_previa']
    readonly_fields = ['vista_previa', 'fecha_subida']
    
    def vista_previa(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="max-height: 80px; max-width: 80px;" />',
                obj.imagen.url
            )
        return "Sin imagen"
    vista_previa.short_description = 'Vista Previa'


class ValorProductoInline(admin.TabularInline):
    """
    Inline para gestionar atributos dinámicos del producto.
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
        'precio_formateado', 
        'stock_actual', 
        'es_activo',
        'imagen_miniatura',
        'fecha_creacion'
    ]
    list_filter = ['categoria', 'es_activo', 'moneda', 'fecha_creacion']
    search_fields = ['nombre', 'sku', 'descripcion']
    list_editable = ['es_activo', 'stock_actual']
    readonly_fields = ['sku', 'fecha_creacion', 'fecha_actualizacion', 'imagen_preview']
    ordering = ['-fecha_creacion']
    date_hierarchy = 'fecha_creacion'
    
    inlines = [ImagenProductoInline, ValorProductoInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'categoria', 'descripcion')
        }),
        ('Pricing', {
            'fields': ('precio_venta', 'moneda'),
            'classes': ('wide',)
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
    
    def imagen_miniatura(self, obj):
        """Muestra miniatura de la imagen principal en el listado."""
        if obj.imagen_principal:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 4px;" />',
                obj.imagen_principal.url
            )
        return "Sin imagen"
    imagen_miniatura.short_description = 'Imagen'
    
    def imagen_preview(self, obj):
        """Muestra preview más grande en el formulario de edición."""
        if obj.imagen_principal:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px; border-radius: 8px;" />',
                obj.imagen_principal.url
            )
        return "Sin imagen cargada"
    imagen_preview.short_description = 'Vista Previa'
    
    def get_queryset(self, request):
        """Optimiza las consultas con select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('categoria')


@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    """
    Administración de Galería de Imágenes.
    """
    list_display = ['producto', 'orden', 'vista_previa_small', 'descripcion', 'fecha_subida']
    list_filter = ['producto__categoria', 'fecha_subida']
    search_fields = ['producto__nombre', 'descripcion']
    ordering = ['producto', 'orden']
    
    fieldsets = (
        ('Información', {
            'fields': ('producto', 'imagen', 'orden', 'descripcion')
        }),
        ('Vista Previa', {
            'fields': ('vista_previa',),
            'classes': ('wide',)
        }),
    )
    
    readonly_fields = ['vista_previa', 'fecha_subida']
    
    def vista_previa_small(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 60px;" />',
                obj.imagen.url
            )
        return "Sin imagen"
    vista_previa_small.short_description = 'Miniatura'
    
    def vista_previa(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="max-height: 300px; max-width: 400px;" />',
                obj.imagen.url
            )
        return "Sin imagen"
    vista_previa.short_description = 'Vista Previa Grande'


@admin.register(AtributoDinamico)
class AtributoDinamicoAdmin(admin.ModelAdmin):
    """
    Administración de Atributos Dinámicos (Especificaciones técnicas).
    """
    list_display = ['nombre', 'unidad_medida', 'cantidad_usos', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']
    
    fieldsets = (
        ('Definición del Atributo', {
            'fields': ('nombre', 'unidad_medida', 'descripcion')
        }),
    )
    
    def cantidad_usos(self, obj):
        """Muestra cuántos productos usan este atributo."""
        return obj.valores.count()
    cantidad_usos.short_description = 'Productos que lo usan'


@admin.register(ValorProducto)
class ValorProductoAdmin(admin.ModelAdmin):
    """
    Administración de Valores de Atributos asignados a productos.
    """
    list_display = ['producto', 'atributo', 'valor_formateado', 'fecha_creacion']
    list_filter = ['atributo', 'producto__categoria', 'fecha_creacion']
    search_fields = ['producto__nombre', 'atributo__nombre', 'valor']
    autocomplete_fields = ['producto', 'atributo']
    ordering = ['producto', 'atributo']
    
    fieldsets = (
        ('Asignación', {
            'fields': ('producto', 'atributo', 'valor')
        }),
    )


# Personalización del sitio de administración
admin.site.site_header = "Administración MotoLuxe"
admin.site.site_title = "Panel de Control MotoLuxe"
admin.site.index_title = "Gestión de Productos y Categorías"