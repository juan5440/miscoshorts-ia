import yt_dlp
from moviepy import VideoFileClip
import os
import whisper
import warnings
import imageio_ffmpeg

import shutil

# Configurar FFmpeg explícitamente para evitar WinError 2
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_exe

# Whisper necesita llamar a "ffmpeg", pero imageio-ffmpeg trae un binario con otro nombre.
# Solución: Copiarlo como ffmpeg.exe a la carpeta actual y agregarla al PATH.
project_dir = os.path.dirname(os.path.abspath(__file__))
target_ffmpeg = os.path.join(project_dir, "ffmpeg.exe")

if not os.path.exists(target_ffmpeg):
    print(f"🔧 Configurando FFmpeg por primera vez...")
    try:
        shutil.copyfile(ffmpeg_exe, target_ffmpeg)
        print(f"✅ FFmpeg copiado a: {target_ffmpeg}")
    except Exception as e:
        print(f"⚠️ No se pudo copiar FFmpeg: {e}")

if project_dir not in os.environ["PATH"]:
    os.environ["PATH"] = project_dir + os.pathsep + os.environ["PATH"]

# own modules
import cerebro_gemini as cerebro
import subtitulos

warnings.filterwarnings("ignore")

URL_VIDEO = "TU_URL_DE_VIDEO_AQUI" 
NOMBRE_SALIDA = "short_con_subs.mp4"

def descargar_video(url_or_path, callback=None):
    # Si es un archivo local existente, usarlo directamente
    if os.path.isfile(url_or_path):
        if callback: callback(f"📂 Usando archivo local: {url_or_path}")
        else: print(f"📂 Usando archivo local: {url_or_path}")
        return url_or_path

    # Si no, asumir que es URL
    if callback: callback(f"📥 Descargando video: {url_or_path}...")
    else: print(f"📥 Descargando video: {url_or_path}...")
    
    ydl_opts = {'format': 'best[ext=mp4]', 'outtmpl': 'video_temp.%(ext)s', 'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url_or_path])
    return "video_temp.mp4"

def transcribir_audio(video_path, callback=None):
    if callback: callback("🔍 Transcribiendo audio para obtener tiempos...")
    else: print("🔍 Transcribiendo audio para obtener tiempos...")
    
    model = whisper.load_model("base")
    resultado = model.transcribe(video_path, word_timestamps=True)
    
    # Save transcript optionally or return it
    with open("transcripcion_completa.txt", "w", encoding="utf-8") as f:
        f.write(resultado['text'])
        
    return resultado

def analizar_contenido(segmentos, callback=None):
    if callback: callback("✨ Consultando a Gemini (con timestamps)...")
    analisis = cerebro.encontrar_clip_viral(segmentos)
    return parsear_respuesta_gemini(analisis)

def parsear_respuesta_gemini(texto):
    """Extrae los datos limpios de la respuesta de texto de Gemini"""
    datos = {}
    lines = texto.split('\n')
    for line in lines:
        if "TITULO:" in line: datos['titulo'] = line.split("TITULO:")[1].strip()
        if "INICIO:" in line: datos['inicio'] = float(line.split("INICIO:")[1].strip())
        if "FIN:" in line: datos['fin'] = float(line.split("FIN:")[1].strip())
        if "RAZON:" in line: datos['razon'] = line.split("RAZON:")[1].strip()
    return datos

def crear_clip_final(video_path, start, end, segmentos, output_name="short_con_subs.mp4", callback=None):
    if callback: callback(f"🚀 Cocinando el Short ({start}s a {end}s)...")
    else: print(f"🚀 Cocinando el Short ({start}s a {end}s)...")
    
    clip = VideoFileClip(video_path).subclipped(start, end)

    w, h = clip.size
    new_width = h * (9/16)
    clip_vertical = clip.cropped(x1=w/2 - new_width/2, y1=0, x2=w/2 + new_width/2, y2=h)
    
    clip_final = subtitulos.generar_subtitulos(clip_vertical, segmentos, start)
    clip_final.write_videofile(output_name, 
                               codec='libx264', 
                               audio_codec='aac', 
                               fps=24,
                               threads=4)
    
    clip.close()
    return output_name

def cleanup(video_path):
    if os.path.exists(video_path):
        os.remove(video_path)

def main():
    video_path = descargar_video(URL_VIDEO)
    
    resultado = transcribir_audio(video_path)
    with open("transcripcion_completa_cli.txt", "w", encoding="utf-8") as f:
         f.write(f"URL: {URL_VIDEO}\n")
         f.write(resultado['text'])

    clip_data = analizar_contenido(resultado['segments'])

    print(f"🤖 PROPUESTA DE SHORT:")
    print(f"📌 Título: {clip_data.get('titulo')}")
    print(f"⏱️ Tiempo: {clip_data.get('inicio')}s --> {clip_data.get('fin')}s")
    print(f"💡 Razón: {clip_data.get('razon')}")
    confirmacion = input("¿Te mola? Escribe 's' para crearlo, o introduce nuevos tiempos (ej: 120-140): ")
    
    start = 0
    end = 0
    if confirmacion.lower() == 's':
        start = clip_data['inicio']
        end = clip_data['fin']
    elif '-' in confirmacion:
        partes = confirmacion.split('-')
        start = float(partes[0])
        end = float(partes[1])
    else:
        print("Cancelado.")
        cleanup(video_path)
        return

    crear_clip_final(video_path, start, end, resultado['segments'], NOMBRE_SALIDA)
    
    cleanup(video_path)
    print(f"🎉 ¡Video listo: {NOMBRE_SALIDA}!")

if __name__ == "__main__":
    main()