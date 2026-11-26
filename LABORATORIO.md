# Laboratorio del DD20

Copia separada de [ha-dreame-dehum v0.1.7](https://github.com/vittorioallegra/ha-dreame-dehum/releases/tag/v0.1.7), revisión `2f67f6266328d2b3ef1da28579fe6fce38fc16fe`. Conserva `LICENSE` y `NOTICE`.

## Cambios de privacidad

- Las peticiones de autenticación e inventario/RPC rechazan redirecciones. Se valida la región y el formato de la ruta del dispositivo antes de construirla.
- Los errores de transporte, autenticación y RPC usan mensajes controlados. El cliente evita mostrar el texto de error enviado por el servidor.
- Los diagnósticos incluyen solo el modelo conocido y el estado del perfil. Las nuevas entradas dejan de guardar el MAC y el sondeo DD20 excluye el número de serie, la ubicación y las propiedades desconocidas.

## Instalación manual de la copia de solo lectura

1. Descomprime el ZIP en el equipo de trabajo. Copia `custom_components/dreame_dehum` al directorio `custom_components` de la configuración del Home Assistant de pruebas. Si ya existe otra carpeta `dreame_dehum` en ese entorno, deja la instalación pendiente para evitar reemplazarla.
2. Reinicia únicamente el Core de pruebas. En Ajustes → Dispositivos y servicios → Añadir integración, selecciona «Dreame Dehumidifier».
3. Introduce las credenciales de Dreamehome directamente en ese Home Assistant y elige Europa. Las credenciales se guardan en la entrada de configuración de ese Home Assistant.
4. Comprueba los sensores de humedad, consigna, modo, velocidad y temporizador, y los sensores binarios de las opciones. Cambia los ajustes de prueba en Dreamehome y espera la siguiente actualización del sondeo.

Para retirar la copia, elimina la entrada de integración en el Home Assistant de pruebas, retira la carpeta que copiaste y reinicia ese Core.

## Alcance del paquete

El paquete monta únicamente las plataformas `sensor` y `binary_sensor`. El cliente acepta solo `get_properties`. El perfil incluye las 12 propiedades comprobadas con el DD20. El estado del prefiltro y la conexión local siguen pendientes.

## Prueba aislada

Las pruebas de esta versión usan una cuenta y un dispositivo simulados con Home Assistant Core 2026.11.3, `pytest-homeassistant` 2026.11.3 y Python 3.14.10, en un contenedor sin red. Comprueban la instalación mediante config entry, la actualización de los sensores, la descarga de la integración y que el adaptador no presente entidades de control. También comprueban que el cliente rechaza escrituras, redirecciones y rutas inesperadas, y que los diagnósticos no exportan datos de la entrada.

Resultado del 26/11/2026 para `0.1.7+lab.1`: 23 pruebas superadas. Ruff, el formato, mypy y `pip check` también pasaron. Las cinco advertencias de deprecación proceden de Home Assistant y la dependencia `backoff`. Queda pendiente instalar esta copia en el Home Assistant de pruebas y comprobar una sesión autorizada de Dreamehome.

Comandos en un entorno desechable con las dependencias de desarrollo instaladas:

```bash
python -m pip install -r requirements_dev.txt
python -m ruff check .
python -m ruff format --check .
python -m mypy custom_components
python -m pytest -q
```
