from django.core.management.base import BaseCommand
from django.db.models import Count
from productos.models import AtributoDinamico, ValorProducto

class Command(BaseCommand):
    help = 'Pobla la base de datos con atributos predefinidos para cada tipo de producto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la migración de valores de atributos duplicados',
        )

    def handle(self, *args, **options):
        atributos = [
            # === ATRIBUTOS GENERALES (TODOS) ===
            {'nombre': 'Color', 'tipo_producto': 'general', 'unidad_medida': '', 'orden': 2},
            {'nombre': 'Garantía', 'tipo_producto': 'general', 'unidad_medida': '', 'orden': 99},
            {'nombre': 'Mensajería', 'tipo_producto': 'general', 'unidad_medida': '', 'orden': 100},
            
            # === MOTOS ELÉCTRICAS (También para E-Bikes y Bicimotos) ===
            {'nombre': 'Potencia del Motor', 'tipo_producto': 'electrica', 'unidad_medida': 'W', 'orden': 10},
            {'nombre': 'Voltaje de Batería', 'tipo_producto': 'electrica', 'unidad_medida': 'V', 'orden': 11},
            {'nombre': 'Capacidad de Batería', 'tipo_producto': 'electrica', 'unidad_medida': 'Ah', 'orden': 12},
            {'nombre': 'Tipo de Batería', 'tipo_producto': 'electrica', 'unidad_medida': '', 'orden': 13},
            {'nombre': 'Velocidad Máxima', 'tipo_producto': 'electrica', 'unidad_medida': 'km/h', 'orden': 14},
            {'nombre': 'Autonomía', 'tipo_producto': 'electrica', 'unidad_medida': 'km', 'orden': 15},
            {'nombre': 'Tiempo de Carga', 'tipo_producto': 'electrica', 'unidad_medida': 'horas', 'orden': 16},
            {'nombre': 'Incluye', 'tipo_producto': 'electrica', 'unidad_medida': '', 'orden': 17},
            
            # === MOTOS DE COMBUSTIÓN ===
            {'nombre': 'Cilindraje', 'tipo_producto': 'combustion', 'unidad_medida': 'cc', 'orden': 20},
            {'nombre': 'Tipo de Motor', 'tipo_producto': 'combustion', 'unidad_medida': '', 'orden': 21},
            {'nombre': 'Sistema de Enfriamiento', 'tipo_producto': 'combustion', 'unidad_medida': '', 'orden': 22},
            {'nombre': 'Capacidad del Tanque', 'tipo_producto': 'combustion', 'unidad_medida': 'L', 'orden': 23},
            {'nombre': 'Velocidad Máxima', 'tipo_producto': 'combustion', 'unidad_medida': 'km/h', 'orden': 24},
            {'nombre': 'Rendimiento', 'tipo_producto': 'combustion', 'unidad_medida': 'km/L', 'orden': 25},
            {'nombre': 'Sistema de Arranque', 'tipo_producto': 'combustion', 'unidad_medida': '', 'orden': 26},
            {'nombre': 'Transmisión', 'tipo_producto': 'combustion', 'unidad_medida': '', 'orden': 27},
            {'nombre': 'Tipo de Frenos', 'tipo_producto': 'combustion', 'unidad_medida': '', 'orden': 28},
            
            # === TRICICLOS (Eléctricos o de Combustión) ===
            {'nombre': 'Tipo de Energía', 'tipo_producto': 'triciclo', 'unidad_medida': '', 'orden': 30},
            {'nombre': 'Potencia/Cilindraje', 'tipo_producto': 'triciclo', 'unidad_medida': '', 'orden': 31},
            {'nombre': 'Voltaje de Batería', 'tipo_producto': 'triciclo', 'unidad_medida': 'V', 'orden': 32},
            {'nombre': 'Capacidad de Batería', 'tipo_producto': 'triciclo', 'unidad_medida': 'Ah', 'orden': 33},
            {'nombre': 'Capacidad de Carga', 'tipo_producto': 'triciclo', 'unidad_medida': 'kg', 'orden': 34},
            {'nombre': 'Dimensiones de Caja', 'tipo_producto': 'triciclo', 'unidad_medida': 'm', 'orden': 35},
            {'nombre': 'Tipo de Estructura', 'tipo_producto': 'triciclo', 'unidad_medida': '', 'orden': 36},
            {'nombre': 'Tracción', 'tipo_producto': 'triciclo', 'unidad_medida': '', 'orden': 37},
            {'nombre': 'Sistema de Marchas', 'tipo_producto': 'triciclo', 'unidad_medida': '', 'orden': 38},
            {'nombre': 'Tipo de Cabina', 'tipo_producto': 'triciclo', 'unidad_medida': '', 'orden': 39},
            
        ]
        
        created_count = 0
        updated_count = 0
        migrated_count = 0
        
        self.stdout.write(
            self.style.SUCCESS('\n🔧 Iniciando población de atributos...\n')
        )
        
        # === PASO 1: Detectar y migrar atributos problemáticos ===
        self.stdout.write(
            self.style.WARNING('\n📋 PASO 1: Detectando atributos duplicados...\n')
        )
        
        # Lista de atributos a eliminar (ya están en campos del modelo)
        atributos_a_eliminar = ['Precio', 'Cantidad en Stock']
        
        for nombre_attr in atributos_a_eliminar:
            atributo = AtributoDinamico.objects.filter(
                nombre=nombre_attr,
                tipo_producto='general'
            ).first()
            
            if atributo:
                valores = ValorProducto.objects.filter(atributo=atributo)
                
                if valores.exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠️  Encontrado "{nombre_attr}" en general con {valores.count()} valores'
                        )
                    )
                    
                    if options['force']:
                        count = valores.count()
                        valores.delete()
                        atributo.delete()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ Eliminados {count} valores de "{nombre_attr}" (se usa campo del modelo)'
                            )
                        )
                        migrated_count += count
                    else:
                        self.stdout.write(
                            self.style.NOTICE(
                                '  ℹ️  Usa --force para eliminar estos valores automáticamente'
                            )
                        )
                elif atributo:
                    # Si no tiene valores, eliminar directamente
                    atributo.delete()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Eliminado "{nombre_attr}" sin valores'
                        )
                    )
        
        # Diccionario de atributos duplicados a migrar
        # nombre_variaciones: [lista de nombres similares] -> tipo_destino
        duplicados_a_migrar = {
            'Autonomía': {
                'variaciones': ['Autonomia', 'Autonomía', 'autonomia', 'autonomía'],
                'tipo_destino': 'electrica',
                'unidad': 'km',
                'orden': 15
            },
            'Capacidad de Batería': {
                'variaciones': ['Capacidad de la bateria', 'Capacidad de bateria', 'Capacidad de Batería', 'Capacidad de la Batería'],
                'tipo_destino': 'electrica',
                'unidad': 'Ah',
                'orden': 12
            },
            'Potencia del Motor': {
                'variaciones': ['Potencia del motor', 'Potencia del Motor', 'potencia del motor'],
                'tipo_destino': 'electrica',
                'unidad': 'W',
                'orden': 10
            },
            'Peso de carga': {
                'variaciones': ['Peso de carga', 'Peso de Carga', 'peso de carga'],
                'tipo_destino': 'triciclo',
                'unidad': 'kg',
                'orden': 32
            }
        }
        
        for nombre_base, config in duplicados_a_migrar.items():
            for variacion in config['variaciones']:
                atributo_general = AtributoDinamico.objects.filter(
                    nombre=variacion,
                    tipo_producto='general'
                ).first()
                
                if atributo_general:
                    valores = ValorProducto.objects.filter(atributo=atributo_general)
                    
                    if valores.exists():
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ⚠️  Encontrado "{variacion}" en general con {valores.count()} valores'
                            )
                        )
                        
                        if options['force']:
                            # Migrar a tipo específico
                            atributo_especifico, created = AtributoDinamico.objects.get_or_create(
                                nombre=nombre_base,
                                tipo_producto=config['tipo_destino'],
                                defaults={
                                    'unidad_medida': config['unidad'],
                                    'orden': config['orden']
                                }
                            )
                            
                            # Migrar valores
                            count = 0
                            for valor in valores:
                                valor.atributo = atributo_especifico
                                valor.save()
                                count += 1
                            
                            # Eliminar el atributo general
                            atributo_general.delete()
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'  ✓ Migrados {count} valores de "{variacion}" → "{nombre_base}" ({config["tipo_destino"]})'
                                )
                            )
                            migrated_count += count
                        else:
                            self.stdout.write(
                                self.style.NOTICE(
                                    '  ℹ️  Usa --force para migrar estos valores automáticamente'
                                )
                            )
                    elif atributo_general:
                        # Si no tiene valores, eliminar directamente
                        atributo_general.delete()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ Eliminado "{variacion}" general sin valores'
                            )
                        )
        
        # === PASO 2: Crear/Actualizar atributos definidos ===
        self.stdout.write(
            self.style.SUCCESS('\n📝 PASO 2: Creando/actualizando atributos...\n')
        )
        
        for atributo_data in atributos:
            atributo, created = AtributoDinamico.objects.get_or_create(
                nombre=atributo_data['nombre'],
                tipo_producto=atributo_data['tipo_producto'],
                defaults={
                    'unidad_medida': atributo_data.get('unidad_medida', ''),
                    'orden': atributo_data.get('orden', 0)
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Creado: {atributo}')
                )
            else:
                # Actualizar si ya existe
                atributo.unidad_medida = atributo_data.get('unidad_medida', '')
                atributo.orden = atributo_data.get('orden', 0)
                atributo.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'  ↻ Actualizado: {atributo}')
                )
        
        # === PASO 3: Detectar otros duplicados ===
        self.stdout.write(
            self.style.WARNING('\n🔍 PASO 3: Buscando otros duplicados...\n')
        )
        
        # Lista de duplicados permitidos (mismo nombre, diferentes tipos)
        DUPLICADOS_PERMITIDOS = ['Velocidad Máxima']
        
        duplicados = AtributoDinamico.objects.values('nombre').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        if duplicados.exists():
            duplicados_reales = False
            for dup in duplicados:
                # Saltar duplicados permitidos
                if dup['nombre'] in DUPLICADOS_PERMITIDOS:
                    continue
                    
                attrs = AtributoDinamico.objects.filter(nombre=dup['nombre'])
                duplicados_reales = True
                self.stdout.write(
                    self.style.WARNING(
                        f'  ⚠️  "{dup["nombre"]}" tiene {dup["count"]} versiones:'
                    )
                )
                for attr in attrs:
                    valores_count = attr.valores.count()
                    self.stdout.write(
                        self.style.NOTICE(
                            f'     - {attr.get_tipo_producto_display()} ({valores_count} valores)'
                        )
                    )
            
            if not duplicados_reales:
                self.stdout.write(
                    self.style.SUCCESS('  ✓ Solo duplicados permitidos (ej: Velocidad Máxima para diferentes tipos)')
                )
        else:
            self.stdout.write(
                self.style.SUCCESS('  ✓ No se encontraron duplicados adicionales')
            )
        
        # === RESUMEN FINAL ===
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Proceso completado:\n'
                f'   - {created_count} atributos creados\n'
                f'   - {updated_count} atributos actualizados\n'
                f'   - {migrated_count} valores migrados\n'
            )
        )
        
        if not options['force'] and duplicados.exists():
            self.stdout.write(
                self.style.NOTICE(
                    '\n💡 Consejo: Ejecuta con --force para migrar valores automáticamente:\n'
                    '   python manage.py poblar_atributos --force\n'
                )
            )
        
        self.stdout.write(
            self.style.NOTICE(
                '\n📚 Categorización de atributos:\n'
                '   • "general" → Todos los productos (Color, Garantía, Mensajería)\n'
                '   • "electrica" → Motos Eléctricas, E-Bikes, Bicimotos\n'
                '   • "combustion" → Motos de Gasolina\n'
                '   • "triciclo" → Triciclos de Carga\n\n'
                '⚠️  Atributos NO incluidos (campos del modelo):\n'
                '   • Precio → Se usa el campo "precio_venta"\n'
                '   • Cantidad en Stock → Se usa el campo "stock_actual"\n'
            )
        )