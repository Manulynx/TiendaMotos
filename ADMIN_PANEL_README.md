# Panel de Administración de Lujo - MotoLuxe

## 🎨 Características del Panel

### ✨ Diseño Premium

- **UI Moderna**: Diseño minimalista y elegante con Tailwind CSS
- **Responsive**: Adaptable a todos los dispositivos
- **Animaciones Suaves**: Transiciones y efectos visuales de alta calidad
- **Tema Oscuro en Sidebar**: Contraste profesional

### 🚀 Funcionalidades Principales

#### Dashboard

- Estadísticas generales del inventario
- Contadores en tiempo real
- Vista rápida de productos recientes
- Accesos rápidos a acciones principales

#### Gestión de Productos (CRUD Completo)

- ✅ **Crear**: Formulario intuitivo con vista previa
- ✅ **Leer**: Lista con filtros avanzados y búsqueda
- ✅ **Actualizar**: Edición inline con AJAX
- ✅ **Eliminar**: Confirmación y eliminación suave

#### Características Especiales de Productos

- **Toggle AJAX**: Activar/desactivar productos sin recargar
- **Galería de Imágenes**: Subir múltiples imágenes por producto
- **Gestión de Imágenes**: Eliminar imágenes con un click
- **Vista Previa**: Preview de imágenes antes de subir
- **Imagen Principal**: Cambio de imagen principal del producto
- **Validaciones en Tiempo Real**: Feedback instantáneo

#### Gestión de Categorías (CRUD Completo)

- ✅ **Modal de Creación**: Crear categorías sin salir de la página
- ✅ **Edición Inline**: Modificar desde la misma vista
- ✅ **Eliminación Segura**: No permite borrar si tiene productos
- ✅ **Contador de Productos**: Ver cuántos productos por categoría

### 🔒 Seguridad

- **Autenticación Requerida**: Solo staff puede acceder
- **CSRF Protection**: Tokens de seguridad en todas las operaciones
- **Validaciones**: Backend y frontend
- **Permisos**: Decorador `@staff_member_required`

### 💡 Tecnologías Utilizadas

- Django 5.2.4
- Tailwind CSS 3.0
- JavaScript Vanilla (AJAX)
- HTML5
- Font Awesome Icons (via SVG)

## 📍 Rutas de Acceso

### URL Principal

```
http://localhost:8000/productos/admin-custom/
```

### Rutas Disponibles

- **Dashboard**: `/productos/admin-custom/`
- **Lista Productos**: `/productos/admin-custom/productos/`
- **Crear Producto**: `/productos/admin-custom/productos/crear/`
- **Editar Producto**: `/productos/admin-custom/productos/{id}/editar/`
- **Lista Categorías**: `/productos/admin-custom/categorias/`

### Rutas AJAX (POST)

- Toggle Estado: `/productos/admin-custom/productos/{id}/toggle/`
- Eliminar Producto: `/productos/admin-custom/productos/{id}/eliminar/`
- Subir Imagen: `/productos/admin-custom/productos/{id}/imagen/subir/`
- Eliminar Imagen: `/productos/admin-custom/imagenes/{id}/eliminar/`
- Crear Categoría: `/productos/admin-custom/categorias/crear/`
- Editar Categoría: `/productos/admin-custom/categorias/{id}/editar/`
- Eliminar Categoría: `/productos/admin-custom/categorias/{id}/eliminar/`

## 🎯 Cómo Usar

### 1. Acceder al Panel

1. Asegúrate de ser usuario staff/superuser
2. Visita: `http://localhost:8000/productos/admin-custom/`
3. Serás redirigido al login si no estás autenticado

### 2. Crear un Producto

1. Click en "Nuevo Producto" (botón rojo)
2. Completa el formulario
3. Sube una imagen (opcional)
4. Click en "Crear Producto"
5. Serás redirigido a la página de edición

### 3. Editar un Producto

1. En la lista, click en "Editar" en cualquier producto
2. Modifica los campos necesarios
3. Sube/elimina imágenes de la galería
4. Click en "Guardar Cambios"

### 4. Toggle de Estado

- Click directo en el botón "ACTIVO/INACTIVO" en las cards
- Cambio instantáneo sin recargar
- Notificación de éxito

### 5. Gestionar Categorías

1. Click en "Categorías" en el sidebar
2. Click en "Nueva Categoría" (botón morado)
3. Completa el modal y guarda
4. Editar: Click en el ícono de lápiz
5. Eliminar: Click en el ícono de basura

## 🎨 Paleta de Colores

```css
- Blue Dark: #0F172A (Títulos principales)
- Red Accent: #C52233 (Acciones principales)
- Purple: #9333EA (Categorías)
- Green: #10B981 (Estados activos)
- Gray: #F8F9FA (Fondos)
```

## ⚡ Funcionalidades AJAX

Todas estas operaciones se realizan sin recargar la página:

- ✅ Toggle de estado de productos
- ✅ Subida de imágenes a galería
- ✅ Eliminación de imágenes
- ✅ Creación de categorías
- ✅ Edición de categorías
- ✅ Eliminación de productos
- ✅ Eliminación de categorías

## 🔔 Sistema de Notificaciones

Toast notifications con 4 tipos:

- **Success** (Verde): Operaciones exitosas
- **Error** (Rojo): Errores y problemas
- **Warning** (Amarillo): Advertencias
- **Info** (Azul): Información general

Auto-dismiss después de 5 segundos.

## 📱 Responsive Design

- **Mobile**: Vista optimizada para smartphones
- **Tablet**: Grid adaptativo
- **Desktop**: Vista completa con sidebar

## 🎭 Elementos de UI

### Cards

- Hover effects con elevación
- Animaciones de entrada
- Bordes sutiles

### Botones

- Gradientes en principales
- Estados hover/active
- Iconos SVG integrados

### Modales

- Backdrop con blur
- Animaciones de entrada/salida
- Click fuera para cerrar

### Formularios

- Focus rings personalizados
- Validación en tiempo real
- Placeholders descriptivos

## 🐛 Solución de Problemas

### El panel no carga

- Verifica que el usuario sea staff: `user.is_staff = True`
- Revisa que las URLs estén correctamente configuradas
- Verifica que las vistas tengan el decorador `@staff_member_required`

### Las imágenes no se suben

- Verifica configuración de MEDIA_URL en settings.py
- Asegúrate que la carpeta media existe
- Revisa permisos de escritura

### Los toggles no funcionan

- Verifica el token CSRF en las cookies
- Revisa la consola del navegador para errores
- Asegúrate que las rutas AJAX estén correctas

## 📊 Estadísticas del Código

- **Templates**: 5 archivos HTML
- **Vistas**: 12 funciones
- **Rutas**: 11 URLs
- **Líneas de Código**: ~2000
- **Funciones AJAX**: 8

## 🚀 Mejoras Futuras

- [ ] Drag & drop para imágenes
- [ ] Búsqueda en tiempo real
- [ ] Exportar a CSV/Excel
- [ ] Gestión de atributos dinámicos
- [ ] Historial de cambios
- [ ] Múltiples imágenes en creación
- [ ] Editor WYSIWYG para descripciones
- [ ] Gestión de inventario avanzada

---

**Desarrollado con ❤️ para MotoLuxe**
_Panel de Administración Premium v1.0_
