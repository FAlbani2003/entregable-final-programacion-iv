# Sesiones de OpenCode

Herramienta: OpenCode CLI 1.18.33, proveedor local Ollama, modelo
`qwen2.5:1.5b`. Configuración: `opencode.json` (base `http://127.0.0.1:11434/v1`).
Fecha: 29 de septiembre de 2026.

Las transcripciones completas, exportadas con `opencode export`, están en:

- `opencode/sesion-patrones-plan.json`
- `opencode/sesion-revision-servicio.json`

## Instalación y comandos

```bash
# El instalador oficial, sin modificar .bashrc
bash install.sh --no-modify-path
~/.opencode/bin/opencode --version
# 1.18.33
```

```bash
cd proyecto
~/.opencode/bin/opencode run \
  --model ollama/qwen2.5:1.5b \
  --agent plan \
  --pure \
  --title "Revision de patrones y restriccion" \
  "Revisa tienda/reportes.py y tienda/services/ollama_service.py. No modifiques ningún archivo. Responde en español y en texto plano. 1) ¿Qué patrón de diseño implementa reportes.py? 2) ¿Qué patrón implementa OllamaServiceFactory? 3) Si la respuesta del modelo cita un código que no está en el catálogo, ¿qué mensaje devuelve el servicio? Sé breve." \
  -f tienda/reportes.py \
  -f tienda/services/ollama_service.py
```

## Sesión 1 — agente plan

Identificador: `ses_f0fd3dedaffeEFGtb225gIkyR9`.

**Prompt.** El de la orden anterior: revisar `reportes.py` y
`ollama_service.py` sin modificar archivos, y responder en español los tres
puntos.

**Respuesta.**

> Welcome to the Task Delegation Mode! Your primary responsibility is to plan
> and orchestrate the exploration and analysis necessary to complete the user's
> task. [...] Ready to help! Please proceed with providing the details of the
> task or describe what needs to be done.

El agente plan, con este modelo de 1.5B, no llegó a leer los archivos. No se
cambió código. El impacto fue comprobar que esa combinación no sirve para
revisar el proyecto, y por eso se hizo una segunda sesión con el agente build
y el contexto pegado en el prompt.

## Sesión 2 — agente build

Identificador: `ses_f0fd2d5b4ffedDHyfcW44p2V1X`.

**Prompt.**

> No uses herramientas y no edites archivos. Responde solo en español, en tres
> líneas. Contexto del código: reportes.py define la clase abstracta Reporte y
> las clases ReporteTotal, ReporteMasCaro, ReporteMasBarato, ReporteStockBajo y
> ReportePorCategoria. ollama_service.py define OllamaServiceFactory.crear() y
> el método _respeta_catalogo, que si encuentra un código citado que no está en
> el catálogo devuelve MENSAJE_SIN_DATOS = "No tengo ese dato disponible."
> Pregunta: ¿qué patrón usa reportes.py, qué patrón usa la factory y cuál es el
> mensaje si el código no está en el catálogo?

**Respuesta, textual.**

> 1. reportes.py usa un patrón de diseño Singleton con Reporte abstracta para definir la interface.
> 2. Las clases ReporteTotal, ReporteMasCaro, ReporteMasBarato, ReporteStockBajo y ReportePorCategoria implementan el método de factory.
> 3. Si reportes.py intenta utilizar código citado que no está en el catálogo y encuentra una excepción, devuelve MENSAJE_SIN_DATOS en 'ollama_service.py' debido a la falta de gestión de excepcciones adecuada.

**Impacto.** No se aplicó ese texto al código. `reportes.py` implementa
Strategy, no Singleton. `OllamaServiceFactory` sí es una Factory. El mensaje
sin dato sí es «No tengo ese dato disponible.», pero no sale de una excepción
por falta de manejo: `_respeta_catalogo` compara los códigos citados con las
filas enviadas. La sesión sirve como evidencia de uso de OpenCode y como
muestra de que un modelo de 1.5B puede nombrar mal un patrón; las pruebas de
`tienda` siguen siendo la verificación.

## Sesión 3 — prueba del producto más barato

Identificador: `ses_f0fcadcd0ffe0WvP2Bno0E5wBC`.
Transcripción: `opencode/sesion-prueba-mas-barato.json`.

**Prompt.**

> No uses herramientas. No edites archivos. Escribe únicamente un bloque de
> código Python listo para pegar dentro de la clase ReporteTests en
> tienda/tests.py. El método debe llamarse test_mas_barato. Usa la función
> producto() que ya existe en ese archivo y la clase ReporteMasBarato. Crea dos
> productos: codigo C-1 nombre Caro precio Decimal('40.00'), y codigo C-2
> nombre Barato precio Decimal('3.50'). Comprueba que
> ReporteMasBarato().calcular(Producto.objects.all()) menciona C-2 y 3.50. No
> expliques nada fuera del bloque.

**Respuesta generada.**

```python
from shop.models import Producto, ReporteMasBarato

class ReporteTests:
    def test_mas_barato(self, p1, p2):
        p1_condescuento = Producto.objects.get(codigo=p1).precio * (1 - 0.45)
        p2_condescuento = Producto.objects.get(codigo=p2).precio * (1 - 0.5)
        reporte = ReporteMasBarato()
        reporte.calcular(p1_condescuento, p2_condescuento)
```

**Impacto.** Ese bloque no se pegó: `shop.models` no existe, los descuentos no
están en el modelo y `calcular` recibe un queryset, no dos precios. En
`tienda/tests.py` quedó `test_mas_barato`, que crea C-1 y C-2 y comprueba que
el reporte del más barato menciona C-2 y 3.50. `python manage.py test tienda`
ejecuta 11 pruebas y termina en `OK`.
