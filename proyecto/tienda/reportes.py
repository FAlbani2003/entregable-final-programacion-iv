"""Reportes del inventario.

Cada reporte es una Strategy: misma interfaz, distinto cálculo.
"""

from abc import ABC, abstractmethod
from decimal import Decimal

from django.db.models import Count, Sum


class Reporte(ABC):
    titulo = ""
    descripcion = ""

    @abstractmethod
    def calcular(self, queryset):
        """Devuelve una lista de líneas de texto con el resultado."""


class ReporteTotal(Reporte):
    titulo = "Total de registros"
    descripcion = "Cuántos productos hay y cuál es el valor del inventario."

    def calcular(self, queryset):
        total = queryset.count()
        if total == 0:
            return ["No hay productos registrados."]
        valor = Decimal("0")
        for producto in queryset:
            valor += producto.precio * producto.cantidad
        return [
            f"Productos registrados: {total}",
            f"Valor del inventario (precio × cantidad): ${valor:.2f}",
        ]


class ReporteMasCaro(Reporte):
    titulo = "Producto más caro"
    descripcion = "El registro con el mayor precio."

    def calcular(self, queryset):
        producto = queryset.order_by("-precio", "nombre").first()
        if producto is None:
            return ["No hay productos registrados."]
        return [f"{producto.codigo} — {producto.nombre}: ${producto.precio}"]


class ReporteMasBarato(Reporte):
    titulo = "Producto más barato"
    descripcion = "El registro con el menor precio."

    def calcular(self, queryset):
        producto = queryset.order_by("precio", "nombre").first()
        if producto is None:
            return ["No hay productos registrados."]
        return [f"{producto.codigo} — {producto.nombre}: ${producto.precio}"]


class ReporteStockBajo(Reporte):
    titulo = "Stock bajo o agotado"
    descripcion = "Productos cuya cantidad es menor o igual al stock mínimo."

    def calcular(self, queryset):
        bajos = [
            producto
            for producto in queryset.order_by("cantidad", "nombre")
            if producto.cantidad <= producto.stock_minimo
        ]
        if not bajos:
            return ["Ningún producto está en stock bajo."]
        return [
            f"{p.codigo} — {p.nombre}: {p.cantidad} (mínimo {p.stock_minimo})"
            for p in bajos
        ]


class ReportePorCategoria(Reporte):
    titulo = "Resumen por categoría"
    descripcion = "Cantidad de productos y unidades en cada categoría."

    def calcular(self, queryset):
        filas = (
            queryset.values("categoria")
            .annotate(productos=Count("id"), unidades=Sum("cantidad"))
            .order_by("categoria")
        )
        if not filas:
            return ["No hay productos registrados."]
        return [
            f"{fila['categoria']}: {fila['productos']} productos, {fila['unidades']} unidades"
            for fila in filas
        ]


def reportes_disponibles():
    """Devuelve las estrategias de reporte en el orden de la vista."""
    return [
        ReporteTotal(),
        ReporteMasCaro(),
        ReporteMasBarato(),
        ReporteStockBajo(),
        ReportePorCategoria(),
    ]


def ejecutar_reportes(queryset):
    return [
        {
            "titulo": reporte.titulo,
            "descripcion": reporte.descripcion,
            "lineas": reporte.calcular(queryset),
        }
        for reporte in reportes_disponibles()
    ]
