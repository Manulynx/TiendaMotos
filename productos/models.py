from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


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


class Producto(models.Model):
    """
    Modelo principal para productos. Contiene información común para todos los tipos.
    """
    MONEDAS = [
        ('USD', 'Dólar Estadounidense'),
        ('CUP', 'Peso Cubano'),
        ('EUR', 'Euro'),
        ('MLC', 'Moneda Libremente Convertible'),
    ]
    
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Producto")
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='productos',
        verbose_name="Categoría"
    )
    precio_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Precio de Venta"
    )
    moneda = models.CharField(
        max_length=3,
        choices=MONEDAS,
        default='USD',
        verbose_name="Moneda"
    )
    sku = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name="SKU",
        help_text="Código único generado automáticamente"
    )
    stock_actual = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Stock Actual"
    )
    es_activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Desactiva el producto sin eliminarlo"
    )
    
    # Campos multimedia
    imagen_principal = models.ImageField(
        upload_to='productos/imagenes/',
        blank=True,
        null=True,
        verbose_name="Imagen Principal"
    )
    
    # Campos adicionales útiles
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-fecha_creacion']
    
    def save(self, *args, **kwargs):
        # Generar SKU automáticamente si no existe
        if not self.sku:
            self.sku = self._generar_sku()
        super().save(*args, **kwargs)
    
    def _generar_sku(self):
        """
        Genera un SKU único basado en categoría y UUID.
        """
        prefijo = self.categoria.nombre[:3].upper() if self.categoria else 'PRD'
        codigo_unico = str(uuid.uuid4().hex)[:8].upper()
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
    imagen = models.ImageField(
        upload_to='productos/galeria/',
        verbose_name="Imagen"
    )
    orden = models.IntegerField(
        default=0,
        verbose_name="Orden",
        help_text="Orden de visualización en la galería"
    )
    descripcion = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Descripción"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Subida")
    
    class Meta:
        verbose_name = "Imagen de Producto"
        verbose_name_plural = "Imágenes de Productos"
        ordering = ['producto', 'orden']
    
    def __str__(self):
        return f"Imagen de {self.producto.nombre} (#{self.orden})"


class AtributoDinamico(models.Model):
    """
    Define atributos personalizables para productos (ej. Voltaje, Autonomía, Cilindrada).
    """
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre del Atributo"
    )
    unidad_medida = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Unidad de Medida",
        help_text="Ej. V, Ah, km, cc, kg"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Atributo Dinámico"
        verbose_name_plural = "Atributos Dinámicos"
        ordering = ['nombre']
    
    def __str__(self):
        if self.unidad_medida:
            return f"{self.nombre} ({self.unidad_medida})"
        return self.nombre


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
    valor = models.CharField(
        max_length=255,
        verbose_name="Valor"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Valor de Atributo"
        verbose_name_plural = "Valores de Atributos"
        unique_together = ['producto', 'atributo']
        ordering = ['producto', 'atributo']
    
    def __str__(self):
        unidad = f" {self.atributo.unidad_medida}" if self.atributo.unidad_medida else ""
        return f"{self.producto.nombre} - {self.atributo.nombre}: {self.valor}{unidad}"
    
    @property
    def valor_formateado(self):
        """Retorna el valor con su unidad de medida si existe."""
        if self.atributo.unidad_medida:
            return f"{self.valor} {self.atributo.unidad_medida}"
        return self.valor

