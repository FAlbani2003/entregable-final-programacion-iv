from django.contrib import admin

from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nombre",
        "categoria",
        "precio",
        "cantidad",
        "stock_minimo",
        "estado",
        "fecha_registro",
    )
    fields = (
        "codigo",
        "nombre",
        "descripcion",
        "categoria",
        "precio",
        "cantidad",
        "stock_minimo",
        "imagen",
        "imagen_url",
        "estado",
        "fecha_registro",
    )
    readonly_fields = ("fecha_registro",)
    list_filter = ("estado", "categoria")
    search_fields = ("codigo", "nombre", "categoria")
