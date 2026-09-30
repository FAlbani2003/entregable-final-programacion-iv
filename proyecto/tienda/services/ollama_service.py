"""Integración con Ollama.

Factory crea el servicio a partir de la configuración.
El servicio arma un contexto solo con filas reales de Producto, pide
al modelo que no invente datos y descarta respuestas que citan un código
que no está en el catálogo.
"""

import re

import requests
from django.conf import settings

# Códigos del inventario: prefijo en letras y al menos un tramo con guion.
_CODIGO_EN_TEXTO = re.compile(r"\b[A-Z]{2,}(?:-[A-Z0-9]+)+\b")

MENSAJE_SIN_DATOS = "No tengo ese dato disponible."
MENSAJE_FUERA_DE_TEMA = (
    "Solo puedo responder consultas sobre repuestos y accesorios "
    "de la tienda AutoRepuestos."
)
MENSAJE_OLLAMA_CAIDO = (
    "Ollama no está disponible. Comprueba que el servicio esté en "
    "ejecución (ollama serve) e inténtalo de nuevo."
)

_TEMAS_TIENDA = (
    "producto",
    "productos",
    "repuesto",
    "repuestos",
    "accesorio",
    "accesorios",
    "inventario",
    "precio",
    "precios",
    "stock",
    "cantidad",
    "codigo",
    "código",
    "categoria",
    "categoría",
    "caro",
    "barato",
    "filtro",
    "freno",
    "aceite",
    "bateria",
    "batería",
    "luz",
    "luces",
    "agotado",
    "activo",
    "catalogo",
    "catálogo",
)


class OllamaNoDisponible(Exception):
    """Ollama no respondió o no está en ejecución."""


class OllamaService:
    def __init__(self, base_url, model, timeout=90):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def responder(self, pregunta, productos):
        filas = list(productos)
        if not filas:
            return MENSAJE_SIN_DATOS
        if not self._es_consulta_de_tienda(pregunta):
            return MENSAJE_FUERA_DE_TEMA

        prompt = self._prompt(pregunta, filas)
        try:
            respuesta = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 300},
                },
                timeout=self.timeout,
            )
            respuesta.raise_for_status()
        except requests.RequestException as exc:
            raise OllamaNoDisponible(MENSAJE_OLLAMA_CAIDO) from exc

        texto = (respuesta.json().get("response") or "").strip()
        if not texto or not self._respeta_catalogo(texto, filas):
            return MENSAJE_SIN_DATOS
        return texto

    def _respeta_catalogo(self, texto, filas):
        """True si cada código citado en la respuesta existe en las filas."""
        permitidos = {p.codigo.upper() for p in filas}
        citados = _CODIGO_EN_TEXTO.findall(texto.upper())
        return all(codigo in permitidos for codigo in citados)

    def _es_consulta_de_tienda(self, pregunta):
        texto = pregunta.casefold()
        return any(tema in texto for tema in _TEMAS_TIENDA)

    def _prompt(self, pregunta, filas):
        lineas = []
        for p in filas:
            lineas.append(
                " | ".join(
                    [
                        f"Código: {p.codigo}",
                        f"Nombre: {p.nombre}",
                        f"Descripción: {p.descripcion or '—'}",
                        f"Categoría: {p.categoria}",
                        f"Precio: {p.precio}",
                        f"Cantidad: {p.cantidad}",
                        f"Stock mínimo: {p.stock_minimo}",
                        f"Estado: {p.get_estado_display()}",
                        f"Fecha: {p.fecha_registro:%d/%m/%Y}",
                    ]
                )
            )
        catalogo = "\n".join(lineas)
        return (
            "Eres el asistente de AutoRepuestos. Responde siempre en español.\n"
            "Usa únicamente el catálogo que aparece debajo. No inventes códigos, "
            "precios ni cantidades.\n"
            f'Si el dato no está en el catálogo, responde exactamente: "{MENSAJE_SIN_DATOS}"\n'
            f'Si la pregunta no es del inventario, responde exactamente: "{MENSAJE_FUERA_DE_TEMA}"\n\n'
            f"CATÁLOGO:\n{catalogo}\n\n"
            f"PREGUNTA: {pregunta}\n"
            "RESPUESTA:"
        )


class OllamaServiceFactory:
    """Factory: construye el servicio con la URL y el modelo configurados."""

    @staticmethod
    def crear():
        return OllamaService(
            base_url=settings.OLLAMA_URL,
            model=settings.OLLAMA_MODEL,
        )
