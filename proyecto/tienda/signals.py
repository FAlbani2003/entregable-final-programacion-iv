"""Observer: reacciona al guardar un producto y ajusta el estado según el stock."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Producto


@receiver(post_save, sender=Producto)
def sincronizar_estado_con_stock(sender, instance, **kwargs):
    nuevo_estado = None
    if instance.cantidad == 0 and instance.estado == Producto.Estado.ACTIVO:
        nuevo_estado = Producto.Estado.AGOTADO
    elif instance.cantidad > 0 and instance.estado == Producto.Estado.AGOTADO:
        nuevo_estado = Producto.Estado.ACTIVO

    if nuevo_estado is None:
        return

    # update() no vuelve a disparar post_save.
    Producto.objects.filter(pk=instance.pk).update(estado=nuevo_estado)
    instance.estado = nuevo_estado
