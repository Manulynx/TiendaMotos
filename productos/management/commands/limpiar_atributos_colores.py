from django.core.management.base import BaseCommand
from productos.models import AtributoDinamico, ValorProducto, Color


class Command(BaseCommand):
    help = 'Elimina todos los atributos dinámicos y colores poblados por script para crearlos desde el admin'

    def add_arguments(self, parser):
        parser.add_argument(
            '--atributos',
            action='store_true',
            help='Eliminar solo atributos dinámicos y sus valores',
        )
        parser.add_argument(
            '--colores',
            action='store_true',
            help='Eliminar solo colores (desvinculándolos de productos)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='No pedir confirmación',
        )

    def handle(self, *args, **options):
        limpiar_atributos = options['atributos']
        limpiar_colores = options['colores']
        force = options['force']

        # Si no se especifica ninguno, limpiar ambos
        if not limpiar_atributos and not limpiar_colores:
            limpiar_atributos = True
            limpiar_colores = True

        if limpiar_atributos:
            self._limpiar_atributos(force)

        if limpiar_colores:
            self._limpiar_colores(force)

        self.stdout.write(self.style.SUCCESS('\nLimpieza completada. Ahora puedes crear atributos y colores desde el panel de administración.'))

    def _limpiar_atributos(self, force):
        total_atributos = AtributoDinamico.objects.count()
        total_valores = ValorProducto.objects.count()

        if total_atributos == 0:
            self.stdout.write(self.style.WARNING('No hay atributos que eliminar.'))
            return

        self.stdout.write(f'\nAtributos encontrados: {total_atributos}')
        self.stdout.write(f'Valores de producto asociados: {total_valores}')

        if not force:
            confirm = input('\n¿Eliminar TODOS los atributos y sus valores asociados? (si/no): ')
            if confirm.lower() not in ('si', 'sí', 's', 'yes', 'y'):
                self.stdout.write(self.style.WARNING('Operación cancelada.'))
                return

        # Eliminar valores primero, luego atributos
        ValorProducto.objects.all().delete()
        AtributoDinamico.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(f'Eliminados {total_atributos} atributos y {total_valores} valores.'))

    def _limpiar_colores(self, force):
        total_colores = Color.objects.count()

        if total_colores == 0:
            self.stdout.write(self.style.WARNING('No hay colores que eliminar.'))
            return

        # Contar productos con colores asignados
        productos_con_colores = 0
        for color in Color.objects.all():
            productos_con_colores += color.productos.count()

        self.stdout.write(f'\nColores encontrados: {total_colores}')
        self.stdout.write(f'Asignaciones color-producto: {productos_con_colores}')

        if not force:
            confirm = input('\n¿Eliminar TODOS los colores? Se desvincularán de los productos. (si/no): ')
            if confirm.lower() not in ('si', 'sí', 's', 'yes', 'y'):
                self.stdout.write(self.style.WARNING('Operación cancelada.'))
                return

        # Limpiar relaciones M2M y eliminar colores
        for color in Color.objects.all():
            color.productos.clear()
        Color.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(f'Eliminados {total_colores} colores y {productos_con_colores} asignaciones.'))
