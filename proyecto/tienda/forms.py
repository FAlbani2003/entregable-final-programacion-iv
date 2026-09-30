from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from .models import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
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
        ]
        widgets = {
            "codigo": forms.TextInput(attrs={"placeholder": "Ej: FIL-ACE-001"}),
            "nombre": forms.TextInput(
                attrs={"placeholder": "Ej: Filtro de aceite universal"}
            ),
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "categoria": forms.TextInput(
                attrs={"placeholder": "Filtros, Frenos, Aceites, Luces..."}
            ),
            "precio": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "cantidad": forms.NumberInput(attrs={"min": "0"}),
            "stock_minimo": forms.NumberInput(attrs={"min": "0"}),
            "imagen": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            "imagen_url": forms.URLInput(
                attrs={"placeholder": "https://… si no vas a subir un archivo"}
            ),
        }

    def clean_codigo(self):
        codigo = (self.cleaned_data.get("codigo") or "").strip().upper()
        if not codigo:
            raise ValidationError("El código es obligatorio.")
        qs = Producto.objects.filter(codigo__iexact=codigo)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un producto con ese código.")
        return codigo

    def clean_nombre(self):
        nombre = (self.cleaned_data.get("nombre") or "").strip()
        if not nombre:
            raise ValidationError("El nombre es obligatorio.")
        return nombre

    def clean_categoria(self):
        categoria = (self.cleaned_data.get("categoria") or "").strip()
        if not categoria:
            raise ValidationError("La categoría es obligatoria.")
        return categoria

    def clean_precio(self):
        precio = self.cleaned_data.get("precio")
        if precio is None:
            raise ValidationError("El precio es obligatorio.")
        if precio < Decimal("0"):
            raise ValidationError("El precio no puede ser negativo.")
        return precio

    def clean_cantidad(self):
        return self._entero_no_negativo("cantidad", "La cantidad")

    def clean_stock_minimo(self):
        return self._entero_no_negativo("stock_minimo", "El stock mínimo")

    def _entero_no_negativo(self, campo, etiqueta):
        valor = self.cleaned_data.get(campo)
        if valor is None:
            raise ValidationError(f"{etiqueta} es obligatorio.")
        if valor < 0:
            raise ValidationError(f"{etiqueta} no puede ser negativo.")
        return valor


class ConsultaOllamaForm(forms.Form):
    pregunta = forms.CharField(
        label="Pregunta",
        max_length=500,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Ej.: ¿Cuál es el repuesto más caro en stock?",
            }
        ),
    )

    def clean_pregunta(self):
        pregunta = (self.cleaned_data.get("pregunta") or "").strip()
        if not pregunta:
            raise ValidationError("Escribe una pregunta.")
        return pregunta
