from django.apps import AppConfig


class TiendaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tienda"
    verbose_name = "Tienda de accesorios y repuestos"

    def ready(self):
        from . import signals  # noqa: F401
