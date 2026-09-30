# CAMBIOS.md — Wagtail RAG Chatbot (Actividad 4)

Documento de modificaciones aplicadas sobre el proyecto open source
[wagtail-ai-chat](https://github.com/awais786/wagtail-ai-chat) (última actualización del repo: mayo 2026).

## Resumen

Se implementó el proyecto en local con Ollama (`qwen2.5:1.5b`), se localizó la
interfaz y los prompts al español, se añadió contenido demo indexable y se
incorporaron **dos funcionalidades nuevas** en el widget de chat.

Además se creó el modelo restringido `productos-qwen2.5` (Modelfile en
`~/ollama/Modelfile-productos` y copia en `proyecto/ollama/`) para limitar la IA
a consultas de productos e inventario.

## 1. Traducciones y localización

| Área | Archivos | Cambio |
|------|----------|--------|
| Widget de chat | `wagtail_rag/templates/wagtail_rag/chatbox.html` | Textos UI al español (títulos, placeholders, aria-labels, fuentes, errores) |
| API | `wagtail_rag/views.py` | Mensajes de error de la API en español |
| Prompts LLM | `wagtail_rag/llm_providers/generation.py` | System prompt y plantilla RAG en español (“Responde siempre en español”) |
| Config | `wagtail_rag/conf.py`, `demo/settings/base.py` | Soporte de `system_prompt` / `prompt_template` y valores en español |
| Sitio demo | `demo/templates/base.html` | `lang="es"` |
| Modelos | `home/models.py` | `search_fields` para indexar `body` / `introduction` |

## 2. Funcionalidades nuevas

### 2.1 Modo oscuro

- Botón en la cabecera del chat para alternar tema claro/oscuro.
- Preferencia persistida en `localStorage` (`ragChatDarkMode`).
- Variables CSS específicas bajo `#rag-chatbox-root.dark`.

### 2.2 Exportar conversación

- Botones **Exportar .md** y **Exportar .csv** en el pie del chat.
- Se guarda un transcript en memoria del navegador y se descarga el archivo.
- Incluye rol, contenido, fuentes y marca de tiempo.

## 3. Contenido e índice RAG

- Páginas demo en español: Inicio, Servicios, Política de IA, FAQ.
- Configuración de indexación explícita de campos de contenido.
- Índice FAISS generado con `python manage.py rag index`.

## 4. Archivos creados / tocados (lista)

- `wagtail_rag/templates/wagtail_rag/chatbox.html` (reescrito)
- `wagtail_rag/views.py`
- `wagtail_rag/llm_providers/generation.py`
- `wagtail_rag/conf.py`
- `demo/settings/base.py`
- `demo/templates/base.html`
- `home/models.py`
- `README.md` (versión en español)
- `CAMBIOS.md` (este archivo)
- `requirements.txt` (`pip freeze`)

## 5. Comandos de instalación y ejecución

```bash
cd proyecto
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# o, en desarrollo del paquete:
# pip install -e ".[local]"

# Modelo Ollama base + modelo restringido a productos
ollama serve   # si no está corriendo
ollama pull qwen2.5:1.5b
ollama create productos-qwen2.5 -f ~/ollama/Modelfile-productos
# Probar: ollama run productos-qwen2.5

python manage.py migrate
python manage.py createsuperuser   # si hace falta
python manage.py rag index
python manage.py runserver 0.0.0.0:8000
```

Modelo activo en `demo/settings/base.py`: `productos-qwen2.5`.

## 6. Restricciones del modelo Ollama (productos)

- Carpeta: `~/ollama/` (copia en `proyecto/ollama/`)
- Archivo: `Modelfile-productos` (base `qwen2.5:1.5b` + SYSTEM de productos/inventario)
- Modelo creado: `productos-qwen2.5`
- Prompts de `WAGTAIL_RAG` alineados con las mismas reglas

## 7. Actividad 5 — CRUD, reportes y consulta directa a Ollama

- Validaciones de código único, campos obligatorios y valores no negativos en `tienda/forms.py`.
- Cinco reportes (Strategy) en `tienda/reportes.py` y vista `/tienda/reportes/`.
- Chat de Django en `/tienda/consulta/` que envía el catálogo real a `http://127.0.0.1:11434` mediante `tienda/services/ollama_service.py` (Factory).
- Señal `post_save` (Observer) que marca un producto activo como agotado cuando la cantidad llega a cero.
- Pruebas en `tienda/tests.py`. Variables de entorno en `.env.example`.

URLs útiles:

- Sitio: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- Chatbox: http://127.0.0.1:8000/chatbox/

## 8. Entregable final

- `OllamaService` descarta una respuesta si cita un código con guion que no está en las filas enviadas a Ollama.
- `requirements.txt` ya no apunta a `file:///home/felipe/wagtail-ai-chat`; el código de la app viaja dentro de `proyecto/`.
- Documentación de cierre: `OPENCODE.md`, `informe.md` e `informe.pdf` en la raíz del ZIP.
- OpenCode CLI 1.18.33, `opencode.json` y las transcripciones en `opencode/`.
