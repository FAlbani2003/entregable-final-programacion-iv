from django.db import models
from django.urls import reverse


class Producto(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        INACTIVO = "inactivo", "Inactivo"
        AGOTADO = "agotado", "Agotado"

    codigo = models.CharField("Código", max_length=40, unique=True)
    nombre = models.CharField("Nombre", max_length=200)
    descripcion = models.TextField("Descripción", blank=True)
    categoria = models.CharField("Categoría", max_length=100)
    precio = models.DecimalField("Precio", max_digits=12, decimal_places=2)
    cantidad = models.PositiveIntegerField("Cantidad existente", default=0)
    stock_minimo = models.PositiveIntegerField("Stock mínimo", default=5)
    estado = models.CharField(
        "Estado del producto",
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVO,
    )
    # Archivo que sube la persona desde el formulario. El enlace de abajo
    # queda para los productos de prueba que ya traian foto por URL.
    imagen = models.ImageField(
        "Imagen del producto",
        upload_to="productos/",
        blank=True,
    )
    imagen_url = models.URLField(
        "URL de imagen",
        max_length=500,
        blank=True,
        help_text="Enlace a imagen del producto (estilo tienda online).",
    )
    fecha_registro = models.DateTimeField("Fecha de registro", auto_now_add=True)

    class Meta:
        ordering = ["-fecha_registro"]
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.codigo} — {self.nombre}"

    def get_absolute_url(self):
        return reverse("tienda:detalle", kwargs={"pk": self.pk})

    @property
    def stock_bajo(self):
        return self.cantidad <= self.stock_minimo

    @property
    def foto(self):
        # Si subio un archivo, ese gana. Si no, uso el enlace (o nada).
        if self.imagen:
            return self.imagen.url
        return self.imagen_url or ""
