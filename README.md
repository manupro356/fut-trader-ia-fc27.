# FUT Trader IA FC 27 — modo automático (beta)

## Qué hace
- Sirve la app web y un backend Python desde el mismo sitio.
- Busca cartas FC 27 en FUTBIN y muestra el precio de consola/PlayStation cuando está disponible.
- Permite vincular una carta y actualizar los precios de cartas vinculadas con el botón de la app.
- Mantiene recomendaciones, límites de compra/venta y cálculos en el navegador.

## Importante
Esta integración depende de un SDK comunitario no oficial que consulta endpoints web no documentados de FUTBIN. FUTBIN no ofrece una API pública oficial; las rutas pueden cambiar, bloquear solicitudes o dejar de funcionar. Los precios pueden tener retraso y no se garantiza que cada carta tenga cotización.
No usa credenciales de EA ni realiza operaciones dentro del juego. Nunca pongas tu contraseña de EA en esta aplicación.
La actualización es manual mediante un botón, no una vigilancia en segundo plano: la web debe estar abierta para usarla. No se puede automatizar el mercado dentro del juego.

## Despliegue gratuito de prueba con Render
1. Subí el contenido de esta carpeta a un repositorio de GitHub.
2. En Render, creá un nuevo **Web Service** desde ese repositorio.
3. Render detectará `render.yaml` o podés poner:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. Esperá a que termine el despliegue y abrí la URL `https://...onrender.com`.
5. La primera carga puede tardar si el servicio gratuito estuvo inactivo. Probá `/api/health` para verificar que el backend esté funcionando.

## Probar localmente (computadora)
Python 3.11+ recomendado:
```bash
pip install -r requirements.txt
uvicorn app:app --host 127.0.0.1 --port 8000
```
Abrí `http://127.0.0.1:8000`.

## Si falla
- Revisá los logs del servicio: la fuente externa puede cambiar.
- Si aparece un error de SDK, revisá que el repositorio comunitario siga disponible.
- Los precios faltantes se muestran como no disponibles, nunca como cero inventado.
