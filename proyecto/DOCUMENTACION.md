# Documentación técnica — inventario AutoRepuestos

La entidad del sistema es **Producto** (repuestos y accesorios). Vive en la app
`tienda`, aparte del sitio Wagtail. La base de datos es SQLite.

## Modelo

| Campo | Tipo | Regla |
|-------|------|--------|
| código | texto, único | obligatorio, se guarda en mayúsculas |
| nombre | texto | obligatorio |
| descripción | texto | opcional |
| categoría | texto | obligatoria |
| precio | decimal | obligatorio, no negativo |
| cantidad | entero | no negativo |
| stock mínimo | entero | no negativo |
| estado | activo / inactivo / agotado | si la cantidad es 0 y estaba activo, pasa a agotado |
| fecha de registro | fecha y hora | se asigna al crear |

El catálogo de inicio muestra la foto del producto. `imagen` es el archivo
que se sube en el formulario. `imagen_url` (migración `0002`) sirve cuando
no hay archivo, como en los productos de demostración. Si existen las dos,
`Producto.foto` usa el archivo.

## Patrones

### Strategy — reportes

`tienda/reportes.py` define la interfaz `Reporte.calcular()`. Cada informe
(total, más caro, más barato, stock bajo, resumen por categoría) es una clase
distinta. La vista solo llama a `ejecutar_reportes()` y no conoce el cálculo.

### Factory — servicio de Ollama

`OllamaServiceFactory.crear()` lee `OLLAMA_URL` y `OLLAMA_MODEL` (de `.env` o
de los valores por defecto) y devuelve un `OllamaService`. La vista de consulta
no construye la URL ni elige el modelo.

### Observer — señal de stock

`tienda/signals.py` escucha `post_save` de `Producto`. Si un producto activo
queda con cantidad 0, el estado pasa a agotado. Si un agotado vuelve a tener
unidades, pasa a activo. La actualización usa `QuerySet.update()` para no
volver a disparar la señal.

## Consulta a Ollama

`POST /tienda/consulta/` toma la pregunta y todas las filas de `Producto`.
El servicio arma un texto con código, nombre, descripción, categoría, precio,
cantidad, stock mínimo, estado y fecha, y lo envía a
`{OLLAMA_URL}/api/generate`.

- Sin productos: responde «No tengo ese dato disponible.» y no llama a Ollama.
- Pregunta ajena al inventario: responde la frase fija de restricción y no llama a Ollama.
- Si la respuesta cita un código con guion que no está en las filas enviadas, se descarta y se muestra el mensaje de dato no disponible.
- Si el proceso de Ollama no responde: la vista muestra un mensaje de error.

La app corre sobre Django 6.1 porque el proyecto base usa Wagtail 8. La app
`tienda` no depende del índice FAISS: el CRUD, los reportes y la consulta
funcionan con SQLite y con la API local de Ollama.

## Pruebas

```bash
python manage.py test tienda
```

Cubren el código duplicado, el precio negativo, el total y el producto más caro,
el stock bajo, la señal de agotado y el servicio de Ollama (sin datos, pregunta
ajena y servicio caído).
