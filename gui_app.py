import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import maker

# Configuración inicial de CustomTkinter
ctk.set_appearance_mode("Dark")  # Modos: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Temas: "blue", "green", "dark-blue"

class ShortsMakerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Shorts Creator")
        self.geometry("600x650")

        # Variables de estado
        self.video_path = None
        self.transcript_segments = None
        self.clip_data = None
        self.selected_file_path = None # Para almacenar la ruta local

        self._init_ui()

    def _init_ui(self):
        # Título
        self.lbl_title = ctk.CTkLabel(self, text="YouTube Shorts AI Creator", font=("Roboto", 24))
        self.lbl_title.pack(pady=20)

        # Entrada de URL
        self.frame_input = ctk.CTkFrame(self)
        self.frame_input.pack(pady=10, padx=20, fill="x")
        
        self.entry_url = ctk.CTkEntry(self.frame_input, placeholder_text="Pega URL de YouTube o selecciona archivo local")
        self.entry_url.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_file = ctk.CTkButton(self.frame_input, text="📁", width=40, command=self.select_file)
        self.btn_file.pack(side="left", padx=(0, 10))

        self.btn_analyze = ctk.CTkButton(self.frame_input, text="Analizar Video", command=self.start_analysis)
        self.btn_analyze.pack(side="right")

        # Area de Logs/Estado
        self.log_box = ctk.CTkTextbox(self, height=100)
        self.log_box.pack(pady=10, padx=20, fill="x")
        self.log_box.insert("0.0", "Esperando URL o archivo...\n")
        self.log_box.configure(state="disabled")

        # Resultados del análisis
        self.frame_results = ctk.CTkFrame(self)
        self.frame_results.pack(pady=10, padx=20, fill="x")
        
        self.lbl_short_title = ctk.CTkLabel(self.frame_results, text="Título Propuesto: ---")
        self.lbl_short_title.pack(anchor="w", padx=10, pady=5)
        
        self.lbl_reason = ctk.CTkLabel(self.frame_results, text="Razón: ---", wraplength=500)
        self.lbl_reason.pack(anchor="w", padx=10, pady=5)

        # Edición de tiempos
        self.frame_times = ctk.CTkFrame(self)
        self.frame_times.pack(pady=10, padx=20, fill="x")
        
        self.lbl_start = ctk.CTkLabel(self.frame_times, text="Inicio (s):")
        self.lbl_start.pack(side="left", padx=5)
        self.entry_start = ctk.CTkEntry(self.frame_times, width=80)
        self.entry_start.pack(side="left", padx=5)
        
        self.lbl_end = ctk.CTkLabel(self.frame_times, text="Fin (s):")
        self.lbl_end.pack(side="left", padx=5)
        self.entry_end = ctk.CTkEntry(self.frame_times, width=80)
        self.entry_end.pack(side="left", padx=5)

        # Botón Generar
        self.btn_generate = ctk.CTkButton(self, text="Generar Short", command=self.start_generation, state="disabled")
        self.btn_generate.pack(pady=20)

    def select_file(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar video",
            filetypes=(("Archivos de video", "*.mp4 *.mov *.avi *.mkv"), ("Todos los archivos", "*.*"))
        )
        if filename:
            self.selected_file_path = filename
            self.entry_url.delete(0, "end")
            self.entry_url.insert(0, filename)
            self.log(f"📂 Archivo seleccionado: {filename}")

    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def start_analysis(self):
        input_val = self.entry_url.get()
        if not input_val:
            self.log("❌ Error: Ingresa una URL o selecciona un archivo.")
            return
        
        # Determine if it's a URL or path (basic check)
        target = input_val
        if self.selected_file_path and os.path.normpath(input_val) == os.path.normpath(self.selected_file_path):
             target = self.selected_file_path

        self.btn_analyze.configure(state="disabled")
        self.btn_generate.configure(state="disabled")
        self.log("-" * 30)
        
        # Ejecutar en hilo separado
        threading.Thread(target=self.run_analysis, args=(target,), daemon=True).start()

    def run_analysis(self, target):
        try:
            # 1. Obtener video (descargar o usar local)
            self.video_path = maker.descargar_video(target, callback=self.log)
            
            # 2. Transcribir
            resultado = maker.transcribir_audio(self.video_path, callback=self.log)
            self.transcript_segments = resultado['segments']
            
            # 3. Analizar (Gemini)
            self.clip_data = maker.analizar_contenido(resultado['segments'], callback=self.log)
            
            # Actualizar GUI en el hilo principal
            self.after(0, self.update_ui_with_results)
            
        except Exception as e:
            self.log(f"❌ Error durante el análisis: {str(e)}")
            self.after(0, lambda: self.btn_analyze.configure(state="normal"))

    def update_ui_with_results(self):
        if self.clip_data:
            self.lbl_short_title.configure(text=f"Título Propuesto: {self.clip_data.get('titulo')}")
            self.lbl_reason.configure(text=f"Razón: {self.clip_data.get('razon')}")
            
            self.entry_start.delete(0, "end")
            self.entry_start.insert(0, str(self.clip_data.get('inicio')))
            
            self.entry_end.delete(0, "end")
            self.entry_end.insert(0, str(self.clip_data.get('fin')))
            
            self.log("✅ Análisis completado. Revisa los tiempos y genera el short.")
            self.btn_generate.configure(state="normal")
            self.btn_analyze.configure(state="normal")

    def start_generation(self):
        try:
            start = float(self.entry_start.get())
            end = float(self.entry_end.get())
        except ValueError:
            self.log("❌ Error: Los tiempos deben ser números.")
            return

        self.btn_generate.configure(state="disabled")
        self.btn_analyze.configure(state="disabled")
        
        threading.Thread(target=self.run_generation, args=(start, end), daemon=True).start()

    def run_generation(self, start, end):
        try:
            output_name = maker.crear_clip_final(
                self.video_path, 
                start, 
                end, 
                self.transcript_segments, 
                callback=self.log
            )
            self.log(f"🎉 ¡Short creado exitosamente!: {output_name}")
            # Solo borrar si era temporal (descarga), no si es local.
            # maker.descargar_video retorna "video_temp.mp4" o el path original.
            # Una logica simple es checkear si nombre == "video_temp.mp4"
            if "video_temp.mp4" in self.video_path:
                maker.cleanup(self.video_path)
            
        except Exception as e:
            self.log(f"❌ Error al generar el short: {str(e)}")
        
        finally:
            self.after(0, lambda: self.btn_generate.configure(state="normal"))
            self.after(0, lambda: self.btn_analyze.configure(state="normal"))

if __name__ == "__main__":
    app = ShortsMakerApp()
    app.mainloop()
