from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Template filter para obtener valores de diccionarios"""
    return dictionary.get(key, '')

@register.filter
def tipo_categoria(categoria_nombre):
    """
    Determina el tipo de producto basado en el nombre de la categoría
    """
    nombre = categoria_nombre.lower()
    
    # Todas las categorías eléctricas
    if any(keyword in nombre for keyword in ['electrica', 'eléctrica', 'e-bike', 'ebike', 'bicimoto', 'bici']):
        return 'electrica'
    
    # Motos de combustión
    elif any(keyword in nombre for keyword in ['combustion', 'combustión', 'moto', 'gasolina']):
        return 'combustion'
    
    # Triciclos
    elif 'triciclo' in nombre:
        return 'triciclo'
    
    return 'general'