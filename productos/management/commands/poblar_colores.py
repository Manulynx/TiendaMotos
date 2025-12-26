from django.core.management.base import BaseCommand
from productos.models import Color

class Command(BaseCommand):
    help = 'Pobla la base de datos con colores predefinidos'

    def handle(self, *args, **options):
        colores = [
            {'nombre': 'Negro', 'codigo_hex': '#000000', 'orden': 1},
            {'nombre': 'Blanco', 'codigo_hex': '#FFFFFF', 'orden': 2},
            {'nombre': 'Rojo', 'codigo_hex': '#DC2626', 'orden': 3},
            {'nombre': 'Azul', 'codigo_hex': '#2563EB', 'orden': 4},
            {'nombre': 'Verde', 'codigo_hex': '#16A34A', 'orden': 5},
            {'nombre': 'Amarillo', 'codigo_hex': '#EAB308', 'orden': 6},
            {'nombre': 'Naranja', 'codigo_hex': '#EA580C', 'orden': 7},
            {'nombre': 'Gris', 'codigo_hex': '#6B7280', 'orden': 8},
            {'nombre': 'Plateado', 'codigo_hex': '#C0C0C0', 'orden': 9},
            {'nombre': 'Dorado', 'codigo_hex': '#D4AF37', 'orden': 10},
            {'nombre': 'Azul Marino', 'codigo_hex': '#1E3A8A', 'orden': 11},
            {'nombre': 'Verde Militar', 'codigo_hex': '#4B5320', 'orden': 12},
        ]
        
        created_count = 0
        updated_count = 0
        
        self.stdout.write(
            self.style.SUCCESS('\n🎨 Iniciando población de colores...\n')
        )
        
        for color_data in colores:
            color, created = Color.objects.get_or_create(
                nombre=color_data['nombre'],
                defaults={
                    'codigo_hex': color_data['codigo_hex'],
                    'orden': color_data['orden']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Creado: {color.nombre} ({color.codigo_hex})')
                )
            else:
                # Actualizar si ya existe
                color.codigo_hex = color_data['codigo_hex']
                color.orden = color_data['orden']
                color.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'  ↻ Actualizado: {color.nombre} ({color.codigo_hex})')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Proceso completado: {created_count} creados, {updated_count} actualizados\n'
            )
        )