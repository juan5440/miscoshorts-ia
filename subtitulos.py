from moviepy import TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip

def generar_subtitulos(video_clip, segmentos_whisper, tiempo_inicio_recorte):
    print("📝 Generando capas de subtítulos (fragmentados)...")

    # 1. Extraer todas las palabras con sus tiempos
    all_words = []
    for segmento in segmentos_whisper:
        if 'words' in segmento:
            all_words.extend(segmento['words'])
        else:
            # Fallback por si no hay words (no debería pasar con la configuración actual)
            all_words.append({
                'word': segmento['text'], 
                'start': segmento['start'], 
                'end': segmento['end']
            })

    # 2. Agrupar palabras en fragmentos cortos
    subs = []
    MAX_CHARS = 25  # Máximo de caracteres por subtítulo
    MAX_DURATION = 2.5 # Duración máxima para forzar corte
    
    grupo_words = []
    
    def procesar_grupo(grupo):
        if not grupo: return
        
        # Calcular tiempos del grupo relative al recorte
        # El start del grupo es el start de la primera palabra
        # El end del grupo es el end de la última palabra
        
        g_start_abs = grupo[0]['start']
        g_end_abs = grupo[-1]['end']
        
        start = g_start_abs - tiempo_inicio_recorte
        end = g_end_abs - tiempo_inicio_recorte

        # Validar visibilidad en el clip
        if end > 0 and start < video_clip.duration:
            start = max(0, start)
            end = min(video_clip.duration, end)
            
            # Construir texto
            texto_lista = [w['word'].strip() for w in grupo]
            texto_final = " ".join(texto_lista).upper() # Mayúsculas impactan más
            
            subs.append(((start, end), texto_final))

    for word in all_words:
        word_text = word['word'].strip()
        if not word_text: continue
        
        # Si el grupo está vacío, añadimos directamente
        if not grupo_words:
            grupo_words.append(word)
            continue
            
        # Evaluar si añadir la palabra excede límites
        texto_actual = " ".join([w['word'].strip() for w in grupo_words])
        nuevo_texto_len = len(texto_actual) + 1 + len(word_text)
        
        tiempo_actual = grupo_words[-1]['end'] - grupo_words[0]['start']
        
        # Criterios de corte: longitud de texto o mucho tiempo acumulado
        if nuevo_texto_len > MAX_CHARS or tiempo_actual > MAX_DURATION:
            procesar_grupo(grupo_words)
            grupo_words = [word] # Iniciar nuevo grupo
        else:
            grupo_words.append(word)
            
    # Procesar lo que quede
    procesar_grupo(grupo_words)

    # 3. Configurar estilo (Fuente más grande, amarillo, borde negro)
    # Posición: ('center', 0.75) coloca el centro del subtítulo al 75% de la altura (parte inferior)
    
    estilo_texto = lambda txt: TextClip(text=txt, 
                                        font=r'C:\Windows\Fonts\arial.ttf', 
                                        font_size=30, # Ajustado a petición del usuario (antes 50)
                                        color='#FFFF00', # Amarillo brillante
                                        stroke_color='black', 
                                        stroke_width=4, 
                                        method='caption',
                                        # Ancho máximo del 90% del video para evitar desbordes
                                        size=(int(video_clip.w * 0.90), None), 
                                        text_align='center')

    # Crear el clip de subtítulos
    # IMPORTANTE: SubtitlesClip a veces da problemas si la lista 'subs' está vacía.
    if not subs:
        print("⚠️ No se generaron subtítulos para este fragmento.")
        return video_clip

    subtitles = SubtitlesClip(subtitles=subs, make_textclip=estilo_texto)
    
    # Posicionamiento en el tercio inferior
    subtitles = subtitles.with_position(('center', 0.80), relative=True)
    
    final_clip = CompositeVideoClip([video_clip, subtitles])
    
    return final_clip