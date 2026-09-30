from decimal import Decimal

from django.core.management.base import BaseCommand

from tienda.models import Producto

# Imágenes públicas de Wikimedia Commons (productos de auto / repuestos)
IMG = {
    "filtro": (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/"
        "5/52/Bosch_Oil_Filter.JPG/500px-Bosch_Oil_Filter.JPG"
    ),
    "frenos": (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/"
        "f/f0/L05A-RF_Shimano_Disc_Brake_Pads_packaging.jpg/"
        "500px-L05A-RF_Shimano_Disc_Brake_Pads_packaging.jpg"
    ),
    "aceite": (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/"
        "4/4a/LUBTROL_JSE_EDGE_5W-40_Motor_Oil_4L_Bottle.jpg/"
        "500px-LUBTROL_JSE_EDGE_5W-40_Motor_Oil_4L_Bottle.jpg"
    ),
    "luces": (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/"
        "d/dc/Bosch_H7.JPG/500px-Bosch_H7.JPG"
    ),
    "bateria": (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/"
        "4/4c/Car_battery.jpg/500px-Car_battery.jpg"
    ),
}


PRODUCTOS_DEMO = [
    {
        "codigo": "FIL-ACE-001",
        "nombre": "Filtro de aceite universal",
        "descripcion": "Filtro de aceite para motores 1.6–2.0 L. Rosca M20.",
        "categoria": "Filtros",
        "precio": Decimal("12.50"),
        "cantidad": 40,
        "stock_minimo": 10,
        "estado": Producto.Estado.ACTIVO,
        "imagen_url": IMG["filtro"],
    },
    {
        "codigo": "PAD-FRE-220",
        "nombre": "Pastillas de freno delanteras",
        "descripcion": "Juego de pastillas cerámicas para sedán compacto.",
        "categoria": "Frenos",
        "precio": Decimal("45.00"),
        "cantidad": 8,
        "stock_minimo": 10,
        "estado": Producto.Estado.ACTIVO,
        "imagen_url": IMG["frenos"],
    },
    {
        "codigo": "ACE-5W30-4L",
        "nombre": "Aceite sintético 5W-30 4L",
        "descripcion": "Aceite de motor sintético API SN/CF.",
        "categoria": "Aceites",
        "precio": Decimal("32.90"),
        "cantidad": 25,
        "stock_minimo": 8,
        "estado": Producto.Estado.ACTIVO,
        "imagen_url": IMG["aceite"],
    },
    {
        "codigo": "LED-H7-PAR",
        "nombre": "Bombillos LED H7 (par)",
        "descripcion": "Par de bombillos LED 6000K para faros delanteros.",
        "categoria": "Luces",
        "precio": Decimal("28.00"),
        "cantidad": 0,
        "stock_minimo": 5,
        "estado": Producto.Estado.AGOTADO,
        "imagen_url": IMG["luces"],
    },
    {
        "codigo": "BAT-12V-60",
        "nombre": "Batería 12V 60Ah",
        "descripcion": "Batería de arranque libre de mantenimiento.",
        "categoria": "Eléctrico",
        "precio": Decimal("95.00"),
        "cantidad": 6,
        "stock_minimo": 3,
        "estado": Producto.Estado.ACTIVO,
        "imagen_url": IMG["bateria"],
    },
]


class Command(BaseCommand):
    help = "Carga productos de demostración para la tienda de repuestos."

    def handle(self, *args, **options):
        creados = 0
        for data in PRODUCTOS_DEMO:
            _, created = Producto.objects.update_or_create(
                codigo=data["codigo"],
                defaults={k: v for k, v in data.items() if k != "codigo"},
            )
            if created:
                creados += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Listo. {creados} nuevos, {Producto.objects.count()} en total."
            )
        )
