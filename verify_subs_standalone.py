import os
import imageio_ffmpeg
from moviepy import ColorClip
import subtitulos

# 1. Configurar FFmpeg
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_exe

# 2. Mock de datos
video_duration = 5.0
dummy_clip = ColorClip(size=(720, 1280), color=(0, 0, 255), duration=video_duration)

mock_segments = [
    {
        'text': "Prueba de tamaño de fuente reducido",
        'start': 0.0,
        'end': 4.0,
        'words': [
            {'word': 'Prueba', 'start': 0.0, 'end': 1.0},
            {'word': 'de', 'start': 1.0, 'end': 1.5},
            {'word': 'tamaño', 'start': 1.5, 'end': 2.5},
            {'word': 'de', 'start': 2.5, 'end': 3.0},
            {'word': 'fuente', 'start': 3.0, 'end': 3.5},
            {'word': 'reducido', 'start': 3.5, 'end': 4.0},
        ]
    }
]

# 3. Ejecutar función
try:
    print("Generando clip de prueba para verificar fuente...")
    final_clip = subtitulos.generar_subtitulos(dummy_clip, mock_segments, 0.0)
    output_filename = "test_subs_font_size.mp4"
    final_clip.write_videofile(output_filename, fps=10, codec='libx264', audio_codec=None)
    print(f"✅ Éxito! Video de prueba generado en {output_filename}")
except Exception as e:
    print(f"❌ Error durante la generación: {e}")
    import traceback
    traceback.print_exc()
