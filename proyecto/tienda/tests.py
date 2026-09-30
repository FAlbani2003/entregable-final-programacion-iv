from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from tienda.forms import ProductoForm
from tienda.models import Producto
from tienda.reportes import (
    ReporteMasBarato,
    ReporteMasCaro,
    ReporteStockBajo,
    ReporteTotal,
)
from tienda.services.ollama_service import (
    MENSAJE_FUERA_DE_TEMA,
    MENSAJE_SIN_DATOS,
    OllamaNoDisponible,
    OllamaService,
)


def producto(**kwargs):
    datos = {
        "codigo": "FIL-001",
        "nombre": "Filtro",
        "categoria": "Filtros",
        "precio": Decimal("10.00"),
        "cantidad": 4,
        "stock_minimo": 2,
    }
    datos.update(kwargs)
    return Producto.objects.create(**datos)


class CatalogoTests(TestCase):
    def test_inicio_muestra_la_foto_por_enlace(self):
        producto(
            codigo="CAT-1",
            nombre="Filtro visible",
            imagen_url="https://example.com/filtro.jpg",
        )
        respuesta = self.client.get("/tienda/catalogo/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Filtro visible")
        self.assertContains(respuesta, "https://example.com/filtro.jpg")
        # El inicio del sitio redirige al catalogo, no a la tabla.
        inicio = self.client.get("/")
        self.assertRedirects(inicio, "/tienda/catalogo/", fetch_redirect_response=False)

    def test_foto_del_archivo_gana_sobre_el_enlace(self):
        item = producto(imagen_url="https://example.com/vieja.jpg")
        item.imagen = "productos/nueva.jpg"
        self.assertEqual(item.foto, "/media/productos/nueva.jpg")


class ValidacionCodigoTests(TestCase):
    def test_rechaza_codigo_duplicado(self):
        producto(codigo="FIL-001")
        form = ProductoForm(
            data={
                "codigo": "fil-001",
                "nombre": "Otro filtro",
                "categoria": "Filtros",
                "precio": "8.00",
                "cantidad": 1,
                "stock_minimo": 1,
                "estado": Producto.Estado.ACTIVO,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("codigo", form.errors)

    def test_rechaza_precio_negativo(self):
        form = ProductoForm(
            data={
                "codigo": "ACE-002",
                "nombre": "Aceite",
                "categoria": "Aceites",
                "precio": "-1",
                "cantidad": 1,
                "stock_minimo": 1,
                "estado": Producto.Estado.ACTIVO,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("precio", form.errors)


class ReporteTests(TestCase):
    def test_total_y_mas_caro(self):
        producto(codigo="A-1", nombre="Barato", precio=Decimal("5.00"), cantidad=2)
        producto(codigo="A-2", nombre="Caro", precio=Decimal("40.00"), cantidad=1)
        total = ReporteTotal().calcular(Producto.objects.all())
        self.assertIn("Productos registrados: 2", total[0])
        self.assertIn("50.00", total[1])
        caro = ReporteMasCaro().calcular(Producto.objects.all())
        self.assertIn("A-2", caro[0])
        self.assertIn("40.00", caro[0])

    def test_mas_barato(self):
        producto(codigo="C-1", nombre="Caro", precio=Decimal("40.00"), cantidad=1)
        producto(codigo="C-2", nombre="Barato", precio=Decimal("3.50"), cantidad=1)
        lineas = ReporteMasBarato().calcular(Producto.objects.all())
        self.assertIn("C-2", lineas[0])
        self.assertIn("3.50", lineas[0])

    def test_stock_bajo(self):
        producto(codigo="B-1", cantidad=1, stock_minimo=5)
        producto(codigo="B-2", cantidad=10, stock_minimo=2)
        lineas = ReporteStockBajo().calcular(Producto.objects.all())
        self.assertEqual(len(lineas), 1)
        self.assertIn("B-1", lineas[0])


class ObserverStockTests(TestCase):
    def test_cantidad_cero_pasa_a_agotado(self):
        item = producto(cantidad=0, stock_minimo=1)
        item.refresh_from_db()
        self.assertEqual(item.estado, Producto.Estado.AGOTADO)


class OllamaServiceTests(TestCase):
    def test_sin_productos_no_llama_a_ollama(self):
        servicio = OllamaService("http://127.0.0.1:11434", "productos-qwen2.5")
        with patch("tienda.services.ollama_service.requests.post") as post:
            texto = servicio.responder("¿Cuál es el precio del filtro?", [])
        self.assertEqual(texto, MENSAJE_SIN_DATOS)
        post.assert_not_called()

    def test_pregunta_ajena_no_inventa(self):
        servicio = OllamaService("http://127.0.0.1:11434", "productos-qwen2.5")
        with patch("tienda.services.ollama_service.requests.post") as post:
            texto = servicio.responder("¿Quién ganó el mundial?", [producto()])
        self.assertEqual(texto, MENSAJE_FUERA_DE_TEMA)
        post.assert_not_called()

    def test_rechaza_codigo_que_no_esta_en_el_catalogo(self):
        servicio = OllamaService("http://127.0.0.1:11434", "productos-qwen2.5")
        respuesta = patch("tienda.services.ollama_service.requests.post")
        with respuesta as post:
            post.return_value.raise_for_status.return_value = None
            post.return_value.json.return_value = {
                "response": "El código es XYZ-999."
            }
            texto = servicio.responder("¿Cuál es el código del filtro?", [producto()])
        self.assertEqual(texto, MENSAJE_SIN_DATOS)

    def test_acepta_codigo_del_catalogo(self):
        servicio = OllamaService("http://127.0.0.1:11434", "productos-qwen2.5")
        with patch("tienda.services.ollama_service.requests.post") as post:
            post.return_value.raise_for_status.return_value = None
            post.return_value.json.return_value = {
                "response": "FIL-001 — Filtro: 10.00"
            }
            texto = servicio.responder("¿Cuál es el precio del filtro?", [producto()])
        self.assertIn("FIL-001", texto)

    def test_ollama_caido(self):
        import requests

        servicio = OllamaService("http://127.0.0.1:11434", "productos-qwen2.5")
        with patch(
            "tienda.services.ollama_service.requests.post",
            side_effect=requests.ConnectionError("caído"),
        ):
            with self.assertRaises(OllamaNoDisponible):
                servicio.responder("¿Cuál es el precio del filtro?", [producto()])
