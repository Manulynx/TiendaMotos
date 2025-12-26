from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter para obtener un item de un diccionario usando una key.
    Uso: {{ valores_actuales|get_item:atributo.id }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def color_hex(color_name):
    """
    Convierte un nombre de color en español a código hexadecimal.
    Uso: {{ color|lower|color_hex }}
    """
    colores_map = {
        # Colores básicos
        'negro': '#000000',
        'blanco': '#FFFFFF',
        'gris': '#808080',
        'plata': '#C0C0C0',
        'plateado': '#C0C0C0',
        'rojo': '#DC143C',
        'azul': '#0047AB',
        'verde': '#228B22',
        'amarillo': '#FFD700',
        'naranja': '#FF8C00',
        'morado': '#800080',
        'rosa': '#FF69B4',
        'marrón': '#8B4513',
        'marron': '#8B4513',
        'café': '#8B4513',
        'beige': '#F5F5DC',
        'dorado': '#FFD700',
        'oro': '#FFD700',
        
        # Colores compuestos
        'gris oscuro': '#404040',
        'gris claro': '#D3D3D3',
        'azul oscuro': '#00008B',
        'azul claro': '#87CEEB',
        'azul marino': '#000080',
        'rojo oscuro': '#8B0000',
        'verde oscuro': '#006400',
        'verde claro': '#90EE90',
        'verde lima': '#32CD32',
        'amarillo claro': '#FFFFE0',
        
        # Colores metálicos
        'cromado': '#E5E4E2',
        'bronce': '#CD7F32',
        'cobre': '#B87333',
    }
    
    color_lower = str(color_name).lower().strip()
    return colores_map.get(color_lower, '#808080')  # Por defecto gris si no encuentra el color
