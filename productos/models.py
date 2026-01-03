from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


class Categoria(models.Model):
    """
    Modelo para categorías de productos con soporte para jerarquía (subcategorías).
    """
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategorias',
        verbose_name="Categoría Padre"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']
    
    def __str__(self):
        if self.padre:
            return f"{self.padre.nombre} > {self.nombre}"
        return self.nombre


class Color(models.Model):
    """
    Modelo para colores de productos con código hexadecimal
    """
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del Color")
    codigo_hex = models.CharField(
        max_length=7, 
        verbose_name="Código Hexadecimal",
        help_text="Ej: #FF0000 para rojo"
    )
    orden = models.IntegerField(default=0, verbose_name="Orden de visualización")
    es_activo = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Color"
        verbose_name_plural = "Colores"
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """
    Modelo principal para productos. Contiene información común para todos los tipos.
    """
    # Identificación
    sku = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True,
        verbose_name="SKU (Código de Producto)"
    )
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción Detallada")
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='productos',
        verbose_name="Categoría"
    )
    
    # Precio
    precio_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Precio de Venta"
    )
    
    MONEDAS = [
        ('USD', 'Dólares USD'),
        ('EUR', 'Euros'),
        ('CUP', 'Pesos Cubanos'),
        ('MLC', 'Moneda Libremente Convertible')
    ]
    moneda = models.CharField(
        max_length=3,
        choices=MONEDAS,
        default='USD',
        verbose_name="Moneda"
    )
    
    # Colores disponibles (relación muchos a muchos)
    colores = models.ManyToManyField(
        Color,
        related_name='productos',
        blank=True,
        verbose_name="Colores Disponibles"
    )
    
    # Inventario
    stock_actual = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Stock Actual"
    )
    
    # Multimedia
    imagen_principal = models.ImageField(
        upload_to='productos/imagenes/',
        blank=True,
        null=True,
        verbose_name="Imagen Principal"
    )
    
    # Estado
    es_activo = models.BooleanField(default=True, verbose_name="Activo")
    
    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-fecha_creacion']
    
    def _redimensionar_imagen(self, imagen_field):
        """
        Redimensiona y recorta la imagen a 800x600px manteniendo la proporción
        """
        if not imagen_field:
            return None
            
        img = Image.open(imagen_field)
        
        # Convertir a RGB si es necesario (para PNGs con transparencia)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Dimensiones objetivo
        target_width = 800
        target_height = 600
        target_ratio = target_width / target_height
        
        # Calcular el ratio de la imagen original
        img_ratio = img.width / img.height
        
        # Redimensionar manteniendo aspecto y recortar
        if img_ratio > target_ratio:
            # Imagen más ancha - ajustar por altura
            new_height = target_height
            new_width = int(new_height * img_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            # Recortar el exceso de ancho
            left = (new_width - target_width) // 2
            img = img.crop((left, 0, left + target_width, target_height))
        else:
            # Imagen más alta - ajustar por ancho
            new_width = target_width
            new_height = int(new_width / img_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            # Recortar el exceso de altura
            top = (new_height - target_height) // 2
            img = img.crop((0, top, target_width, top + target_height))
        
        # Guardar en BytesIO
        output = BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        # Crear nuevo archivo
        return InMemoryUploadedFile(
            output, 'ImageField',
            f"{imagen_field.name.split('.')[0]}.jpg",
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
    
    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = self._generar_sku()
        
        # Redimensionar imagen principal si se ha cambiado
        if self.imagen_principal:
            try:
                # Verificar si la imagen ha sido modificada
                if not self.pk or (self.pk and Producto.objects.filter(pk=self.pk).exists()):
                    old_instance = Producto.objects.filter(pk=self.pk).first() if self.pk else None
                    if not old_instance or old_instance.imagen_principal != self.imagen_principal:
                        self.imagen_principal = self._redimensionar_imagen(self.imagen_principal)
            except Exception as e:
                print(f"Error al redimensionar imagen: {e}")
        
        super().save(*args, **kwargs)
    
    def _generar_sku(self):
        """
        Genera un SKU único basado en categoría y UUID.
        """
        prefijo = self.categoria.nombre[:3].upper()
        codigo_unico = str(uuid.uuid4())[:8].upper()
        return f"{prefijo}-{codigo_unico}"
    
    def __str__(self):
        return f"{self.nombre} ({self.sku})"
    
    @property
    def precio_formateado(self):
        """Retorna el precio con formato y moneda."""
        return f"{self.precio_venta} {self.moneda}"
    
    @property
    def en_stock(self):
        """Indica si hay stock disponible."""
        return self.stock_actual > 0
    
    @property
    def colores_disponibles(self):
        """Retorna lista de colores disponibles"""
        return self.colores.filter(es_activo=True)


class ImagenProducto(models.Model):
    """
    Modelo para galería de imágenes de productos.
    """
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='galeria_imagenes',
        verbose_name="Producto"
    )
    imagen = models.ImageField(upload_to='productos/galeria/', verbose_name="Imagen")
    descripcion = models.CharField(max_length=200, blank=True, null=True, verbose_name="Descripción")
    orden = models.IntegerField(default=0, verbose_name="Orden")
    fecha_subida = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Subida")
    
    class Meta:
        verbose_name = "Imagen de Producto"
        verbose_name_plural = "Imágenes de Productos"
        ordering = ['orden', 'fecha_subida']
    
    def _redimensionar_imagen(self, imagen_field):
        """
        Redimensiona y recorta la imagen a 800x600px manteniendo la proporción
        """
        if not imagen_field:
            return None
            
        img = Image.open(imagen_field)
        
        # Convertir a RGB si es necesario
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Dimensiones objetivo
        target_width = 800
        target_height = 600
        target_ratio = target_width / target_height
        
        # Calcular el ratio de la imagen original
        img_ratio = img.width / img.height
        
        # Redimensionar manteniendo aspecto y recortar
        if img_ratio > target_ratio:
            new_height = target_height
            new_width = int(new_height * img_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            left = (new_width - target_width) // 2
            img = img.crop((left, 0, left + target_width, target_height))
        else:
            new_width = target_width
            new_height = int(new_width / img_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            top = (new_height - target_height) // 2
            img = img.crop((0, top, target_width, top + target_height))
        
        # Guardar en BytesIO
        output = BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        return InMemoryUploadedFile(
            output, 'ImageField',
            f"{imagen_field.name.split('.')[0]}.jpg",
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
    
    def save(self, *args, **kwargs):
        # Redimensionar imagen de galería
        if self.imagen:
            try:
                if not self.pk or (self.pk and ImagenProducto.objects.filter(pk=self.pk).exists()):
                    old_instance = ImagenProducto.objects.filter(pk=self.pk).first() if self.pk else None
                    if not old_instance or old_instance.imagen != self.imagen:
                        self.imagen = self._redimensionar_imagen(self.imagen)
            except Exception as e:
                print(f"Error al redimensionar imagen: {e}")
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Imagen de {self.producto.nombre} (#{self.orden})"


class AtributoDinamico(models.Model):
    """
    Define atributos personalizables para productos (ej. Voltaje, Autonomía, Cilindrada).
    """
    TIPOS_PRODUCTO = [
        ('general', 'General (Todos)'),
        ('electrica', 'Motos Eléctricas'),
        ('combustion', 'Motos de Combustión'),
        ('triciclo', 'Triciclos')
    ]
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Atributo")
    tipo_producto = models.CharField(
        max_length=20,
        choices=TIPOS_PRODUCTO,
        default='general',
        verbose_name="Tipo de Producto"
    )
    unidad_medida = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Unidad de Medida",
        help_text="Ej: km, W, cc, L"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción"
    )
    orden = models.IntegerField(
        default=0,
        verbose_name="Orden de visualización"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Atributo Dinámico"
        verbose_name_plural = "Atributos Dinámicos"
        ordering = ['tipo_producto', 'orden', 'nombre']
        unique_together = ['nombre', 'tipo_producto']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_producto_display()})"


class ValorProducto(models.Model):
    """
    Relaciona productos con sus atributos dinámicos y valores específicos.
    """
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='valores_atributos',
        verbose_name="Producto"
    )
    atributo = models.ForeignKey(
        AtributoDinamico,
        on_delete=models.PROTECT,
        related_name='valores',
        verbose_name="Atributo"
    )
    valor = models.CharField(max_length=200, verbose_name="Valor")
    
    class Meta:
        verbose_name = "Valor de Atributo"
        verbose_name_plural = "Valores de Atributos"
        unique_together = ['producto', 'atributo']
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.atributo.nombre}: {self.valor}"
    
    @property
    def valor_formateado(self):
        """Retorna el valor con su unidad de medida si existe."""
        if self.atributo.unidad_medida:
            return f"{self.valor} {self.atributo.unidad_medida}"
        return self.valor

