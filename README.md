# Dreame Deshumidificador para Home Assistant

Versión experimental de solo lectura para el Dreame DD20 (`dreame.dehum.u2512`). La integración lee el estado mediante la nube de Dreamehome. La versión de laboratorio se verificó con Home Assistant Core 2026.11.3 y datos simulados.

## Instalación en Home Assistant de pruebas

1. En HACS, abre el menú **⋮ → Repositorios personalizados**.
2. Añade `https://github.com/Carbanog/dreame_dehum` con el tipo **Integración**.
3. Descarga **Dreame Dehumidifier** y reinicia Home Assistant de pruebas.
4. En **Ajustes → Dispositivos y servicios → Añadir integración**, selecciona **Dreame Dehumidifier**. Introduce las credenciales de Dreamehome en Home Assistant y elige la región de tu cuenta.

Esta copia y la integración de origen comparten el dominio `dreame_dehum`. Usa un entorno de pruebas donde no tengas instalada la integración de origen. Para una instalación manual o para retirar la copia, consulta [las instrucciones de laboratorio](LABORATORIO.md).

## Lecturas disponibles

- Humedad ambiente y consigna. La consigna se comprobó en Personalizado.
- Modo y velocidad del ventilador.
- Estado de la oscilación, plasma, tono de tecla y bloqueo infantil.
- Duración y estado del temporizador.
- Estado del secado de aire y ajuste de secado automático tras apagado.

El acceso local y el estado del prefiltro siguen pendientes.

## Privacidad y licencia

Home Assistant guarda las credenciales de Dreamehome en la entrada de configuración de la integración. Los diagnósticos solo incluyen el modelo y el estado del perfil. El repositorio contiene exclusivamente datos de prueba sintéticos.

Adaptado de [ha-dreame-dehum v0.1.7](https://github.com/vittorioallegra/ha-dreame-dehum/releases/tag/v0.1.7). Consulta [LICENSE](LICENSE), [NOTICE](NOTICE) y [la revisión de origen](REVISION_UPSTREAM).
