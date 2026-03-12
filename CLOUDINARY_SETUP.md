# 🖼️ Configuración de Cloudinary para TiendaMotos

## ✅ Cambios Realizados

### 1. **Settings.py actualizado**

- ✅ Agregado import `cloudinary.utils.cloudinary_url`
- ✅ `SECRET_KEY` ahora se lee desde variable de entorno
- ✅ `DEBUG` por defecto es `False` (más seguro en producción)
- ✅ Cloudinary Storage solo se configura en producción
- ✅ `MEDIA_ROOT` solo existe en desarrollo (no en producción)
- ✅ Agregados headers de seguridad HTTPS (SSL, HSTS, etc.)

### 2. **Estructura de configuración**

```python
# Producción (ENVIRONMENT='production')
- Static files: Cloudinary (StaticHashedCloudinaryStorage)
- Media files: Cloudinary (MediaCloudinaryStorage)
- MEDIA_ROOT: NO configurado
- DEBUG: False
- SSL: Activado

# Desarrollo
- Static files: WhiteNoise (CompressedManifestStaticFilesStorage)
- Media files: Carpeta local `media/`
- MEDIA_ROOT: BASE_DIR / 'media'
- DEBUG: True
```

---

## 🚀 Variables de Entorno Requeridas en Railway

### **Vars Cloudinary (obtén de https://cloudinary.com/console)**

```
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
```

### **Vars Django**

```
SECRET_KEY=tu_secret_key_super_segura
DEBUG=False
ENVIRONMENT=production
```

### **Vars Admin (para crear superuser)**

```
ADMIN_USERNAME=tu_usuario_admin
ADMIN_EMAIL=tu_email@example.com
ADMIN_PASSWORD=contraseña_super_segura
```

---

## 📝 Pasos para Configurar en Railway

### 1. **Ir al Proyecto en Railway**

- Railway.app → Tu proyecto TiendaMotos

### 2. **Agregar Variables de Entorno**

- Settings → Environment → Variables
- Agregar todas las variables del listado anterior

### 3. **Ejecutar Migraciones y Crear Superuser** (primera vez)

```bash
# En Railway CLI o web terminal:
python manage.py migrate
python manage.py createsuperuserenv
```

### 4. **Recolectar static files** (primera vez)

```bash
python manage.py collectstatic --noinput
```

---

## 🔧 Configuración por Defecto (ya incluida)

### **Seguridad SSL/TLS**

```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_SECONDS = 31536000  # 1 año
```

### **URL de Cloudinary**

Las URLs de imágenes se generan automáticamente cuando subas a Cloudinary. Ejemplo:

```
https://res.cloudinary.com/[cloud_name]/image/upload/produktos/imagenes/xxx.jpg
```

---

## ⚠️ ADVERTENCIAS IMPORTANTES

### **1. MEDIA_ROOT en Producción:**

- ❌ NO habrá carpeta `media/` en producción
- ✅ Cloudinary maneja todo automáticamente
- Cualquier imagen subida irá directamente a Cloudinary

### 2. SECRET_KEY:\*\*

- 🔐 NUNCA exponer en código
- ✅ Usar variable de entorno en Railway
- Generar una segura: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

### 3. DEBUG = False:\*\*

- ⚠️ En producción DEBE ser False
- Evita exponer información sensible
- Sistema de errores es más seguro

---

## 🧪 Verificar Configuración

### **En desarrollo local:**

```bash
# Verificar que todo está bien
python manage.py check

# Ver que archivos estáticos se van a servir
python manage.py collectstatic --clear --noinput
```

### **En Railway (ver logs):**

```bash
# Ver logs de la app
railway logs application

# SSH a la app
railway shell

# Luego en el shell:
python manage.py check
```

---

## 📸 Cómo Funciona en las Plantillas

### **Imágenes de Productos (Cloudinary automático)**

```django
<!-- En lista.html, detalles.html, home.html -->
{% if producto.imagen_principal %}
  <img src="{{ producto.imagen_principal.url }}" alt="{{ producto.nombre }}">
  <!-- La URL es generada por Cloudinary Storage automáticamente -->
  <!-- Ejemplo: https://res.cloudinary.com/xxx/image/upload/productos/imagenes/xxx.jpg -->
{% endif %}
```

### **Archivos estáticos (CSS, JS)**

```django
<!-- En base.html, admin_custom/base.html -->
<link rel="stylesheet" href="{% static 'css/admin_custom.css' %}">
<!-- En producción: Cloudinary StaticHashedCloudinaryStorage lleva estos archivos a Cloudinary -->
<!-- En desarrollo: WhiteNoise los sirve localmente -->
```

---

## 🎯 Optimizaciones Recomendadas

### **1. Transformaciones de Cloudinary en Modelos (futuro)**

```python
# Dentro del modelo Producto
def get_thumbnail_url(self):
    """Retorna URL optimizada para thumbnail"""
    if self.imagen_principal:
        # Redimensionar a 300x300 con calidad automática
        from cloudinary.utils import cloudinary_url
        url, options = cloudinary_url(
            self.imagen_principal.name,
            width=300,
            height=300,
            crop="fill",
            quality="auto",
            fetch_format="auto"
        )
        return url
    return None
```

### **2. Cache Headers en Cloudinary**

Las imágenes en Cloudinary son cacheadas por 1 año automáticamente (header configurado por defecto).

### **3. Versioning de Static Files**

En producción, los static files se versionan automáticamente con `StaticHashedCloudinaryStorage`.

---

## ❌ Problemas Comunes y Soluciones

### **1. "ImproperlyConfigured: Invalid MEDIA_ROOT"**

- **Causa:** DEBUG=False sin ENVIRONMENT=production
- **Solución:** Agregar `ENVIRONMENT=production` en Railway

### **2. "Cloudinary credentials not found"**

- **Causa:** Faltan variables de entorno Cloudinary
- **Solución:** Verificar que estén en Railway → Variables → Environment

### **3. Las imágenes no cargan**

- **Causa:** URLs no son HTTPS o están bloqueadas por CSP
- **Solución:** Verificar que SECURE_SSL_REDIRECT=True y CSP permite cloudinary.com

### **4. Static files sirven 404**

- **Causa:** collectstatic no se ejecutó
- **Solución:** Ejecutar `python manage.py collectstatic --noinput`

---

## 📚 Referencias

- [Cloudinary Django Storage](https://github.com/cloudinary/pycloudinary)
- [Django Static Files](https://docs.djangoproject.com/en/5.2/howto/static-files/)
- [Railway Documentation](https://docs.railway.app/)
- [Security in Django Production](https://docs.djangoproject.com/en/5.2/topics/security/)

---

## ✅ Checklist Final

- [ ] Variables de entorno agregadas en Railway
- [ ] `ENVIRONMENT=production` configurado
- [ ] `SECRET_KEY` en variable de entorno
- [ ] `DEBUG=False` en Railway
- [ ] Primera ejecución: `python manage.py migrate`
- [ ] Primera ejecución: `python manage.py createsuperuserenv`
- [ ] Primera ejecución: `python manage.py collectstatic --noinput`
- [ ] Verificar logs de Railway sin errores
- [ ] Subir images a productos desde admin
- [ ] Verificar que aparecen URLs de Cloudinary en inspector
- [ ] Verificar que HTTPS funciona correctamente
