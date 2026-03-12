from django.core.management.base import BaseCommand
from django.db.models import Count
from productos.models import AtributoDinamico, ValorProducto


class Command(BaseCommand):
    help = 'Pobla la base de datos con atributos predefinidos para cada tipo de producto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la migración o eliminación de valores asociados',
        )

    def handle(self, *args, **options):

        atributos = [

            # === ATRIBUTOS GENERALES ===
            {'nombre': 'Garantía', 'tipo_producto': 'general', 'unidad_medida': '', 'orden': 99},
            {'nombre': 'Mensajería', 'tipo_producto': 'general', 'unidad_medida': '', 'orden': 100},

            # === MOTOS ELÉCTRICAS ===
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

            # === TRICICLOS ===
            {'nombre': 'Tipo de Energía', 'tipo_producto': 'triciclo', 'unidad_medida': '', 'orden': 30},
            {'nombre': 'Potencia/Cilindraje', 'tipo_producto': 'triciclo', 'unidad_medida': '', 'orden': 31},
            {'nombre': 'Voltaje de Batería', 'tipo_producto': 'triciclo', 'unidad_medida': 'V', 'orden': 32},
            {'nombre': 'Capacidad de Batería', 'tipo_producto': 'triciclo', 'unidad_medida': 'Ah', 'orden': 33},
            {'nombre': 'Autonomía', 'tipo_producto': 'triciclo', 'unidad_medida': 'km', 'orden': 34},
            {'nombre': 'Capacidad de Carga', 'tipo_producto': 'triciclo', 'unidad_medida': 'kg', 'orden': 35},
            {'nombre': 'Dimensiones de Caja', 'tipo_producto': 'triciclo', 'unidad_medida': 'm', 'orden': 36},
            {'nombre': 'Tipo de Estructura', 'tipo_producto': 'triciclo', 'unidad_medida': '', 'orden': 37},
            {'nombre': 'Tracción', 'tipo_producto': 'triciclo', 'unidad_medida': '', 'orden': 38},
            {'nombre': 'Sistema de Marchas', 'tipo_producto': 'triciclo', 'unidad_medida': '', 'orden': 39},
            {'nombre': 'Tipo de Cabina', 'tipo_producto': 'triciclo', 'unidad_medida': '', 'orden': 40},
            ]

        created_count = 0
        updated_count = 0
        migrated_count = 0
        deleted_count = 0

        self.stdout.write(self.style.SUCCESS('\n🔧 Iniciando sincronización de atributos...\n'))

        # =========================================================
        # PASO 1: ELIMINAR ATRIBUTOS QUE YA SON CAMPOS DEL MODELO
        # =========================================================

        atributos_a_eliminar = ['Precio', 'Cantidad en Stock']

        for nombre_attr in atributos_a_eliminar:

            atributo = AtributoDinamico.objects.filter(
                nombre=nombre_attr,
                tipo_producto='general'
            ).first()

            if atributo:

                valores = ValorProducto.objects.filter(atributo=atributo)

                if valores.exists():

                    if options['force']:
                        count = valores.count()
                        valores.delete()
                        atributo.delete()
                        migrated_count += count

                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Eliminado atributo "{nombre_attr}" con {count} valores'
                            )
                        )

                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'⚠ "{nombre_attr}" tiene valores. Usa --force'
                            )
                        )

                else:
                    atributo.delete()
                    deleted_count += 1

        # =========================================================
        # PASO 2: CREAR / ACTUALIZAR ATRIBUTOS
        # =========================================================

        self.stdout.write(self.style.SUCCESS('\n📝 Creando o actualizando atributos...\n'))

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
                    self.style.SUCCESS(f'✓ Creado: {atributo}')
                )

            else:

                atributo.unidad_medida = atributo_data.get('unidad_medida', '')
                atributo.orden = atributo_data.get('orden', 0)
                atributo.save()

                updated_count += 1

                self.stdout.write(
                    self.style.WARNING(f'↻ Actualizado: {atributo}')
                )

        # =========================================================
        # PASO 3: BUSCAR DUPLICADOS
        # =========================================================

        self.stdout.write(self.style.WARNING('\n🔍 Revisando duplicados...\n'))

        DUPLICADOS_PERMITIDOS = ['Velocidad Máxima']

        duplicados = AtributoDinamico.objects.values('nombre').annotate(
            count=Count('id')
        ).filter(count__gt=1)

        for dup in duplicados:

            if dup['nombre'] in DUPLICADOS_PERMITIDOS:
                continue

            attrs = AtributoDinamico.objects.filter(nombre=dup['nombre'])

            self.stdout.write(
                self.style.WARNING(
                    f'⚠ "{dup["nombre"]}" tiene {dup["count"]} versiones'
                )
            )

            for attr in attrs:
                valores_count = attr.valores.count()

                self.stdout.write(
                    self.style.NOTICE(
                        f' - {attr.get_tipo_producto_display()} ({valores_count} valores)'
                    )
                )

        # =========================================================
        # PASO 4: ELIMINAR ATRIBUTOS NO DEFINIDOS EN EL SCRIPT
        # =========================================================

        self.stdout.write(self.style.WARNING('\n🧹 Eliminando atributos obsoletos...\n'))

        atributos_validos = {
            (a['nombre'], a['tipo_producto'])
            for a in atributos
        }

        atributos_db = AtributoDinamico.objects.all()

        for attr in atributos_db:

            clave = (attr.nombre, attr.tipo_producto)

            if clave not in atributos_validos:

                valores = ValorProducto.objects.filter(atributo=attr)

                if valores.exists():

                    if options['force']:

                        count = valores.count()
                        valores.delete()
                        attr.delete()

                        deleted_count += 1

                        self.stdout.write(
                            self.style.SUCCESS(
                                f'🗑 Eliminado "{attr.nombre}" ({attr.tipo_producto}) con {count} valores'
                            )
                        )

                    else:

                        self.stdout.write(
                            self.style.WARNING(
                                f'⚠ "{attr.nombre}" ({attr.tipo_producto}) tiene valores. Usa --force'
                            )
                        )

                else:

                    attr.delete()
                    deleted_count += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'🗑 Eliminado "{attr.nombre}" ({attr.tipo_producto})'
                        )
                    )

        # =========================================================
        # RESUMEN
        # =========================================================

        self.stdout.write(

            self.style.SUCCESS(

                f'\n✅ Sincronización completada\n'
                f' - {created_count} creados\n'
                f' - {updated_count} actualizados\n'
                f' - {deleted_count} eliminados\n'
                f' - {migrated_count} valores migrados\n'

            )
        )