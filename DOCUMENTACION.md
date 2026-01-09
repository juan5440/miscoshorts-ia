# Miscoshorts - Generador de Shorts con Inteligencia Artificial

Este proyecto automatiza la creación de YouTube Shorts virales a partir de videos largos, utilizando Inteligencia Artificial para el análisis de contenido, transcripción de audio y generación de subtítulos.

## 📋 Descripción del Proyecto

**Miscoshorts** es una herramienta de escritorio que permite a los creadores de contenido:

1.  **Descargar** videos de YouTube o utilizar archivos locales.
2.  **Transcribir** el audio automáticamente a texto.
3.  **Analizar** el contenido con IA (Google Gemini) para encontrar los segmentos con mayor potencial viral.
4.  **Generar** un video vertical (9:16) optimizado para Shorts/Reels/TikTok.
5.  **Añadir subtítulos** dinámicos y estilizados automáticamente.

## 🛠️ Herramientas y Tecnologías Utilizadas

El proyecto combina varias tecnologías potentes:

- **Python 3.12+**: Lenguaje principal.
- **CustomTkinter**: Para la Interfaz Gráfica de Usuario (GUI) moderna y modo oscuro.
- **OpenAI Whisper**: Para la transcripción de audio de alta precisión.
- **Google Gemini (API)**: Como "cerebro" para analizar el texto, detectar momentos virales y sugerir títulos.
- **MoviePy**: Para la edición de video (recorte, redimensionado 9:16).
- **FFmpeg**: Motor de procesamiento de video y audio subyacente.
- **yt-dlp**: Para la descarga robusta de videos de YouTube.
- **Pillow (PIL)**: Para el procesamiento de gráficos en los subtítulos.

## ⚙️ Requisitos Previos

Antes de instalar, asegúrate de tener:


# DOCUMENTACIÓN - Miscoshorts

Este documento recoge la descripción técnica, las instrucciones de instalación y el uso del proyecto "Miscoshorts" —una herramienta para generar YouTube Shorts automáticos a partir de vídeos largos usando transcripción y análisis por IA.

## 1. Resumen rápido

-+- Propósito: detectar el fragmento más viral de un vídeo largo, recortarlo a formato vertical 9:16, añadir subtítulos y generar un MP4 listo para publicar.
-+- Modo de uso: CLI (`maker.py`) o GUI (`gui_app.py` / `iniciar.bat`).

## 2. Requisitos

-+- Python 3.12+
-+- FFmpeg (binario en PATH o `ffmpeg.exe` en la carpeta del proyecto)
-+- Clave de API de Google Gemini (no subirla a repositorios públicos)
-+- Dependencias Python listadas en [requirements.txt](requirements.txt)

Instala dependencias:

```bash
pip install -r requirements.txt
```

## 3. Instalación (Windows - pasos recomendados)

1. Clona el repositorio y sitúate en la carpeta:

```bash
git clone <repo-url>
cd miscoshorts-ai
```

2. Crea un entorno virtual (opcional pero recomendado):

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Instala dependencias:

```bash
pip install -r requirements.txt
```

4. Instala o copia `ffmpeg.exe`:

- Si usas Windows, descarga FFmpeg y coloca `ffmpeg.exe` en la carpeta del proyecto o agrega FFmpeg al PATH.
- El script `maker.py` intenta copiar el binario proporcionado por `imageio-ffmpeg` a `ffmpeg.exe` en la carpeta del proyecto si no lo encuentra.

5. Configura la API Key de Gemini:

- Abre [cerebro_gemini.py](cerebro_gemini.py) y reemplaza `GEMINI_API_KEY` por tu clave.
- Alternativa más segura: modificar el código para leer la clave desde una variable de entorno y evitar hardcodearla.

Ejemplo (recomendado):

```python
import os
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
```

## 4. Uso

4.1 Desde la GUI

- Ejecuta `iniciar.bat` o `python gui_app.py` para abrir la interfaz.
- Pega la URL de YouTube o selecciona un archivo local.
- Pulsa "Analizar Video" para transcribir y pedir la selección al modelo Gemini.
- Ajusta tiempos si quieres y pulsa "Generar Short".

4.2 Desde CLI (flujo principal)

- Edita `URL_VIDEO` en [maker.py](maker.py) o pasa un archivo local a la función `descargar_video`.
- Ejecuta:

```bash
python maker.py
```

- Flujo que realiza `maker.py`:
  1. Descarga el vídeo (`yt-dlp`) o usa archivo local.
  2. Transcribe con `whisper` (modelo `base`).
  3. Envía segmentos a `cerebro_gemini.encontrar_clip_viral()` para obtener título, inicio, fin y razón.
  4. El usuario confirma o ajusta tiempos.
  5. Se recorta el clip, se centra para formato vertical y se añaden subtítulos (`subtitulos.py`).
  6. Genera `short_con_subs.mp4`.

## 5. Arquitectura y módulos (tareas principales)

- [maker.py](maker.py): Orquestador principal. Descarga, transcribe (Whisper), consulta a Gemini, y genera el clip final.
- [cerebro_gemini.py](cerebro_gemini.py): Encapsula la llamada al modelo generativo de Google Gemini y construye el prompt para elegir el clip viral.
- [subtitulos.py](subtitulos.py): Agrupa palabras en subtítulos, formatea texto y compone el clip final con `MoviePy`.
- [gui_app.py](gui_app.py): Interfaz gráfica (CustomTkinter) — atajos para cargar URL/archivo, analizar y generar.
- [verify_fix.py](verify_fix.py): Script auxiliar para comprobar/corregir el manejo de `ffmpeg.exe` en Windows.
- [verify_subs_standalone.py](verify_subs_standalone.py): Prueba local para comprobar el render de subtítulos.
- [requirements.txt](requirements.txt): Dependencias Python.
- `ffmpeg.exe`: (opcional) se puede incluir en la carpeta para evitar problemas en Windows.

## 6. Detalle técnico del flujo

1. Descarga y preparación

- `yt-dlp` descarga el vídeo (si se proporciona URL).
- `imageio-ffmpeg` proporciona un binario que `maker.py` copia como `ffmpeg.exe` para compatibilidad con `whisper`.

2. Transcripción

- Se carga el modelo `whisper` con `whisper.load_model("base")` y se obtiene `resultado['segments']` que contienen palabras con timestamps.

3. Análisis por Gemini

- `cerebro_gemini.encontrar_clip_viral()` construye un prompt con la transcripción timestamped y genera una respuesta con formato:

  TITULO: ...
  INICIO: ...
  FIN: ...
  RAZON: ...

- `maker.parsear_respuesta_gemini()` extrae esos valores para su uso.

4. Render y subtítulos

- `maker.crear_clip_final()` recorta y centra el frame para formato vertical.
- `subtitulos.generar_subtitulos()` agrupa palabras en bloques (por caracteres y duración), crea `TextClip`s estilizados y los superpone con `CompositeVideoClip`.

## 7. Dependencias clave

- yt-dlp
- moviepy
- google-generativeai
- openai-whisper
- customtkinter
- imageio-ffmpeg

Instala todo con `pip install -r requirements.txt`.

## 8. Solución de problemas

- Problema: `Whisper` no encuentra `ffmpeg` → Asegúrate de que `ffmpeg.exe` está en la carpeta del proyecto o que FFmpeg está en tu PATH.
- Problema: errores de fuente en `moviepy.TextClip` → cambia la ruta de `font` en [subtitulos.py](subtitulos.py) a una fuente instalada (ej. `C:\Windows\Fonts\arial.ttf`).
- Problema: clave de Gemini incluida en el repo → reemplaza uso hardcodeado por variable de entorno y regenera la clave si fue comprometida.

## 9. Seguridad y buenas prácticas

- Nunca subir claves API a repositorios públicos. Usa variables de entorno (`GEMINI_API_KEY`) o un archivo `.env` (ignorarlo en `.gitignore`).
- Revisa y limita permisos y cuotas de la API de Gemini.

## 10. Cómo contribuir

1. Crea un fork.
2. Añade tests y documentación para cambios grandes.
3. Abre un Pull Request explicando el cambio.

## 11. Recursos y referencias

- Tutorial en YouTube (si aplica) — enlace en [README.md](README.md).
- Documentación de `moviepy`, `yt-dlp`, `whisper` y `google-generativeai`.

---

Si quieres, puedo:
- actualizar también el `README.md` con un resumen reducido, o
- convertir instrucciones de configuración para usar variables de entorno en lugar de claves hardcodeadas.
