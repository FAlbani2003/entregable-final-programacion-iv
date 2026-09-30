# Wagtail RAG Chatbot (localizado al español)

Chatbot RAG (Retrieval-Augmented Generation) para **Wagtail CMS**, ejecutado con
**Ollama** en local. Este repositorio es una adaptación académica del proyecto
open source [awais786/wagtail-ai-chat](https://github.com/awais786/wagtail-ai-chat)
(última actualización del original: mayo 2026).

## Qué hace

Administra el inventario de repuestos (CRUD), muestra cinco reportes y responde
preguntas en español con un modelo local de Ollama, usando solo los productos
guardados en SQLite. El sitio también conserva el chatbot RAG de Wagtail.

## Instalación del inventario (entregable)

Desde esta carpeta `proyecto/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_productos
python manage.py test tienda
python manage.py runserver 0.0.0.0:8000
```

Ollama tiene que estar en marcha y el modelo creado:

```bash
ollama serve
ollama pull qwen2.5:1.5b
ollama create productos-qwen2.5 -f ollama/Modelfile-productos
```

- Catálogo (inicio): http://127.0.0.1:8000/tienda/catalogo/
- Inventario: http://127.0.0.1:8000/tienda/
- Reportes: http://127.0.0.1:8000/tienda/reportes/
- Consulta: http://127.0.0.1:8000/tienda/consulta/
- Admin de productos: http://127.0.0.1:8000/django-admin/

Las variables `SECRET_KEY`, `DEBUG`, `OLLAMA_URL` y `OLLAMA_MODEL` están en
`.env.example`. La app `tienda` (modelos, vistas, reportes y servicio) viaja
con esta carpeta; no depende de otra ruta del equipo.

Decisiones de diseño: [`DOCUMENTACION.md`](DOCUMENTACION.md).
Interacciones del cierre: [`OPENCODE.md`](OPENCODE.md).

## Requisitos

- Python 3.11+
- Ollama instalado y en ejecución (`ollama serve`)
- Modelo: `ollama pull qwen2.5:1.5b`

## Instalación rápida (demo)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# desarrollo del paquete:
# pip install -e ".[local]"

python manage.py migrate
python manage.py createsuperuser   # opcional
python manage.py rag index
python manage.py runserver 0.0.0.0:8000
```

- Sitio: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- Chatbox: http://127.0.0.1:8000/chatbox/

Credenciales demo usadas en la práctica: usuario `admin` / contraseña `admin123`.

## Configuración RAG

En `demo/settings/base.py`:

```python
WAGTAIL_RAG = {
    "embedding": {"provider": "sentence-transformers", "model": "all-MiniLM-L6-v2"},
    "llm": {
        "provider": "ollama",
        "model": "qwen2.5:1.5b",
        "system_prompt": "… Responde SIEMPRE en español …",
    },
    "vector_store": {"backend": "faiss", "path": ".../faiss_index"},
}
```

## Funcionalidades añadidas en esta adaptación

1. **Modo oscuro** del widget de chat (preferencia en `localStorage`).
2. **Exportar conversación** a Markdown (`.md`) o CSV (`.csv`).
3. Interfaz, mensajes de API y prompts del sistema **en español**.

Ver detalle en [`CAMBIOS.md`](CAMBIOS.md).

## Comandos útiles

```bash
python manage.py rag index          # construir índice
python manage.py rag index --clear  # vaciar colección
python manage.py rag chat -q "¿…?"  # pregunta por CLI
python manage.py rag test           # smoke test del pipeline
make runserver
```

## Licencia

El proyecto original mantiene su licencia; ver `LICENSE`.
