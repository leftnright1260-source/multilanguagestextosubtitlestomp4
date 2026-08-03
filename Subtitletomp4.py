import sys
import time
import textwrap
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# --- Configuración por Grupos Lingüísticos ---
CONFIG_IDIOMAS = {
    "CJK": {"fuente": "msyh.ttc", "size": 32, "width": 18, "idiomas": ["Chinese", "Japanese", "Korean"]},
    "RTL": {"fuente": "segoeui.ttf", "size": 32, "width": 38, "idiomas": ["Arabic", "Persian", "Urdu", "Pastún", "Hebreo"]},
    "INDICO_ASIA": {
        "fuente": "Nirmala.ttf", "size": 30, "width": 32,
        "idiomas": ["Bengali", "Panyabí-Pakistán", "Panyabí-India", "Télugu", "Tamil", "Tailandés", "Birmano", "Nepalí", "Hindi", "Sundanés"]
    },
    "AMHARICO": {"fuente": "ebrima.ttf", "size": 30, "width": 35, "idiomas": ["Amhárico"]},
    "OTROS_ALFABETOS": {"fuente": "segoeui.ttf", "size": 30, "width": 38, "idiomas": ["Armenio", "Mongol"]},
    "LATINO_CIRILICO": {"fuente": "segoeui.ttf", "size": 28, "width": 45, "idiomas": []}
}

LISTA_IDIOMAS = [
    "Spanish", "English", "Italian", "French", "Portuguese", "German", "Polish", "Ukrainian", 
    "Russian", "Dutch", "Chinese", "Japanese", "Korean", "Arabic", "Turkish", "Persian", 
    "Indonesian", "Bengali", "Urdu", "Filipino", "Vietnamese", "Hindi", "Swahili", "Romanian", 
    "Panyabí-Pakistán", "Panyabí-India", "Télugu", "Tamil", "Malayo", "Hausa", "Tailandés", 
    "Yoruba", "Pastún", "Sundanés", "Kurdo", "Birmano", "Amhárico", "Nepalí", "Zulú", 
    "Afrikaans", "Húngaro", "Griego", "Serbio", "Checo", "Sueco", "Catalán", "Hebreo", 
    "Búlgaro", "Albanés", "Bielorruso", "Armenio", "Croata", "Danés", "Mongol", "Eslovaco", 
    "Noruego", "Finlandés", "Lombardo", "Bosnio", "Lituano", "Irlandés", "Esloveno", 
    "Gallego", "Macedonio", "Pangasinán", "Latín", "Estonio"
]

FPS = 30

SIGNOS_PUNTO = ['.', '?', '!', ':', '。', '？', '！', '।', '؟']
SIGNOS_COMA = [',', ';', '，', '；', '،', '、']

class SimuladorSubtitulos:
    def __init__(self, root):
        self.root = root
        self.root.title("Panel de Control - Subtítulos Pro")
        self.root.geometry("520x610")
        self.root.resizable(False, False)

        self.escribiendo = False
        self.pausado = False
        self.arrastrando_slider = False
        self.ruta_archivo = ""
        self.bloques_subtitulos = []
        self.tiempos_bloques = []
        self.tiempo_total_segundos = 0
        self.tiempo_original_base = 0
        self.indice_bloque_actual = 0

        # Tiempos base por defecto
        self.vel_base = 0.050
        self.pausa_punto = 0.600
        self.pausa_coma = 0.300
        self.tiempo_lectura = 3.0

        self.font_family = "segoeui.ttf"
        self.font_size = 28
        self.ancho_linea = 45

        # Integración Menú Superior
        self.crear_menu_superior()

        # Ventana Externa de Proyección
        self.ventana_proyeccion = tk.Toplevel(self.root)
        self.ventana_proyeccion.title("PANTALLA DE PREVISUALIZACIÓN")
        self.ventana_proyeccion.geometry("1000x400")
        self.ventana_proyeccion.configure(bg="#126e47")

        self.canvas = tk.Canvas(
            self.ventana_proyeccion,
            bg=self.ventana_proyeccion["bg"],
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Panel GUI
        frame = ttk.Frame(self.root, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Idioma del texto:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.combo_idioma = ttk.Combobox(frame, values=LISTA_IDIOMAS, state="readonly")
        self.combo_idioma.set("Spanish")
        self.combo_idioma.pack(fill="x", pady=(2, 6))
        self.combo_idioma.bind("<<ComboboxSelected>>", self.al_cambiar_idioma)

        self.lbl_archivo = ttk.Label(frame, text="Ningún archivo seleccionado", wraplength=480)
        self.lbl_archivo.pack(fill="x", pady=2)

        self.btn_cargar = ttk.Button(frame, text="📂 Seleccionar Archivo TXT", command=self.seleccionar_archivo)
        self.btn_cargar.pack(fill="x", pady=4)

        # SLIDER DE AJUSTE DE RITMO (AMPLIADO A ±50%)
        self.frame_tiempo_adj = ttk.LabelFrame(frame, text=" Reajuste de Duración Final (±50%) ", padding=8)
        self.frame_tiempo_adj.pack(fill="x", pady=6)

        self.lbl_ritmo_info = ttk.Label(self.frame_tiempo_adj, text="Carga un archivo TXT para habilitar el ajuste", font=("Segoe UI", 9))
        self.lbl_ritmo_info.pack(anchor="center", pady=(0, 4))

        self.slider_ritmo_var = tk.DoubleVar(value=0) # De -50 a +50
        self.slider_ritmo = ttk.Scale(
            self.frame_tiempo_adj, 
            from_=-50, 
            to=50, 
            orient="horizontal", 
            variable=self.slider_ritmo_var,
            command=self.al_mover_slider_ritmo,
            state="disabled"
        )
        self.slider_ritmo.pack(fill="x")

        frame_marcas = ttk.Frame(self.frame_tiempo_adj)
        frame_marcas.pack(fill="x", pady=(2, 0))
        ttk.Label(frame_marcas, text="-50% (Muy Rápido)", font=("Segoe UI", 8)).pack(side="left")
        ttk.Label(frame_marcas, text="0% (Original)", font=("Segoe UI", 8, "bold")).pack(side="left", expand=True)
        ttk.Label(frame_marcas, text="+50% (Muy Lento)", font=("Segoe UI", 8)).pack(side="right")

        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=6)

        # BARRA DE TIEMPO / NAVEGACIÓN
        frame_slider = ttk.LabelFrame(frame, text=" Control de Tiempo y Avance ", padding=8)
        frame_slider.pack(fill="x", pady=4)

        self.slider_var = tk.DoubleVar(value=0)
        self.slider = ttk.Scale(
            frame_slider, 
            from_=0, 
            to=100, 
            orient="horizontal", 
            variable=self.slider_var,
            command=self.al_mover_slider
        )
        self.slider.pack(fill="x")
        self.slider.bind("<ButtonPress-1>", self.al_iniciar_arrastre)
        self.slider.bind("<ButtonRelease-1>", self.al_soltar_arrastre)

        self.lbl_tiempo = ttk.Label(frame_slider, text="00:00 / 00:00 (0%)", font=("Segoe UI", 10, "bold"))
        self.lbl_tiempo.pack(anchor="center", pady=(5, 0))

        self.lbl_progreso = ttk.Label(frame_slider, text="Bloque: 0 / 0")
        self.lbl_progreso.pack(anchor="e")

        # CONTROLES Y RENDERIZADO
        self.btn_iniciar = ttk.Button(frame, text="▶ Previsualizar en Vivo", command=self.iniciar, state="disabled")
        self.btn_iniciar.pack(fill="x", pady=3)

        frame_ctrl = ttk.Frame(frame)
        frame_ctrl.pack(fill="x", pady=3)
        
        self.btn_pausar = ttk.Button(frame_ctrl, text="⏸ Pausar", command=self.alternar_pausa, state="disabled")
        self.btn_pausar.pack(side="left", fill="x", expand=True, padx=(0,4))

        self.btn_reiniciar = ttk.Button(frame_ctrl, text="🔄 Reiniciar", command=self.reiniciar, state="disabled")
        self.btn_reiniciar.pack(side="left", fill="x", expand=True)

        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=6)

        # BOTÓN EXPORTAR MP4
        self.btn_exportar = ttk.Button(frame, text="🎬 EXPORTAR A ARCHIVO MP4", command=self.exportar_mp4, state="disabled")
        self.btn_exportar.pack(fill="x", ipady=4)

        self.al_cambiar_idioma()

    def crear_menu_superior(self):
        barra_menu = tk.Menu(self.root)
        menu_ayuda = tk.Menu(barra_menu, tearoff=0)
        menu_ayuda.add_command(label="Acerca de / Créditos", command=self.mostrar_acerca_de)
        barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)
        self.root.config(menu=barra_menu)

    def mostrar_acerca_de(self):
        ventana_about = tk.Toplevel(self.root)
        ventana_about.title("Acerca de - Subtítulos Pro")
        ventana_about.geometry("380x250")
        ventana_about.resizable(False, False)
        ventana_about.configure(bg="#1a202c")
        
        # Centrar la ventana respecto a la principal
        ventana_about.transient(self.root)
        ventana_about.grab_set()

        tk.Label(
            ventana_about, 
            text="Subtítulos Pro Generator", 
            font=("Segoe UI", 14, "bold"), 
            fg="#ffffff", 
            bg="#1a202c"
        ).pack(pady=(20, 5))

        tk.Label(
            ventana_about, 
            text="Desarrollado por José Galindo", 
            font=("Segoe UI", 11, "bold"), 
            fg="#319795", 
            bg="#1a202c"
        ).pack(pady=2)

        tk.Label(
            ventana_about, 
            text="Herramienta Pro de Automatización de Contenido", 
            font=("Segoe UI", 9, "italic"), 
            fg="#a0aec0", 
            bg="#1a202c"
        ).pack(pady=(0, 15))

        def abrir_website():
            webbrowser.open("https://gabriels.work")

        btn_web = tk.Button(
            ventana_about, 
            text="🌐 Visitar GABRIELS.WORK", 
            font=("Segoe UI", 10, "bold"), 
            bg="#319795", 
            fg="white", 
            activebackground="#2b6cb0", 
            activeforeground="white",
            relief="flat", 
            padx=12, 
            pady=6, 
            command=abrir_website, 
            cursor="hand2"
        )
        btn_web.pack(pady=10)

        tk.Label(
            ventana_about, 
            text="© All rights reserved", 
            font=("Segoe UI", 8), 
            fg="#718096", 
            bg="#1a202c"
        ).pack(side="bottom", pady=10)

    def al_cambiar_idioma(self, event=None):
        idioma = self.combo_idioma.get()
        config_encontrada = CONFIG_IDIOMAS["LATINO_CIRILICO"]
        for grupo, datos in CONFIG_IDIOMAS.items():
            if idioma in datos["idiomas"]:
                config_encontrada = datos
                break

        self.font_family = config_encontrada["fuente"]
        self.font_size = config_encontrada["size"]
        self.ancho_linea = config_encontrada["width"]

        if self.ruta_archivo:
            self.preprocesar_texto()

    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de texto",
            filetypes=[("Archivos de texto (*.txt)", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            self.ruta_archivo = archivo
            nombre = os.path.basename(archivo)
            self.lbl_archivo.configure(text=f"Archivo: {nombre}")
            
            # Resetear slider de ritmo
            self.slider_ritmo_var.set(0)
            self.slider_ritmo.configure(state="normal")
            
            self.vel_base = 0.050
            self.pausa_punto = 0.600
            self.pausa_coma = 0.300
            self.tiempo_lectura = 3.0
            
            self.preprocesar_texto()
            self.tiempo_original_base = self.tiempo_total_segundos
            
            self.actualizar_texto_ritmo(0)

            self.btn_iniciar.configure(state="normal")
            self.btn_exportar.configure(state="normal")

    def preprocesar_texto(self):
        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as file:
                texto_completo = file.read()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")
            return

        lineas_limpias = [l.strip() for l in texto_completo.splitlines() if l.strip() != ""]
        texto_unificado = " ".join(lineas_limpias)
        renglones = textwrap.wrap(texto_unificado, width=self.ancho_linea)

        self.bloques_subtitulos = []
        for i in range(0, len(renglones), 2):
            bloque = renglones[i:i+2]
            self.bloques_subtitulos.append("\n".join(bloque))

        self.recalcular_tiempos()

    def recalcular_tiempos(self):
        self.tiempos_bloques = []
        frames_acumulados = 0

        for bloque in self.bloques_subtitulos:
            for car in bloque:
                if car in SIGNOS_PUNTO:
                    duracion = self.pausa_punto
                elif car in SIGNOS_COMA:
                    duracion = self.pausa_coma
                elif car == '\n':
                    duracion = 0.1
                else:
                    duracion = self.vel_base
                
                num_f = int(round(duracion * FPS))
                frames_acumulados += max(1, num_f)
            
            frames_acumulados += int(round(self.tiempo_lectura * FPS))
            self.tiempos_bloques.append(frames_acumulados / float(FPS))

        self.tiempo_total_segundos = frames_acumulados / float(FPS) if FPS > 0 else 0
        total = len(self.bloques_subtitulos)
        self.slider.configure(to=max(total - 1, 0))
        self.actualizar_etiqueta_progreso(0)

    def al_mover_slider_ritmo(self, val):
        if not self.ruta_archivo or self.tiempo_original_base == 0:
            return

        porcentaje_variacion = float(val) # Rango de -50.0 a +50.0
        # Convertir porcentaje a factor (ej: +50% -> factor 1.50 | -50% -> factor 0.50)
        delta = 1.0 + (porcentaje_variacion / 100.0)

        self.vel_base = 0.050 * delta
        self.pausa_punto = 0.600 * delta
        self.pausa_coma = 0.300 * delta
        self.tiempo_lectura = 3.0 * delta

        self.recalcular_tiempos()
        self.actualizar_texto_ritmo(porcentaje_variacion)

    def actualizar_texto_ritmo(self, pct):
        fmt_total = self.formatear_tiempo(self.tiempo_total_segundos)
        signo = "+" if pct > 0 else ""
        self.lbl_ritmo_info.configure(
            text=f"Ajuste: {signo}{pct:.1f}%  |  Duración Final: {fmt_total}",
            font=("Segoe UI", 9, "bold")
        )

    def formatear_tiempo(self, segundos):
        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        segs = int(segundos % 60)
        if horas > 0:
            return f"{horas:02d}:{minutos:02d}:{segs:02d}"
        else:
            return f"{minutos:02d}:{segs:02d}"

    def actualizar_etiqueta_progreso(self, indice):
        total = len(self.bloques_subtitulos)
        if total == 0:
            self.lbl_tiempo.configure(text="00:00 / 00:00 (0%)")
            self.lbl_progreso.configure(text="Bloque: 0 / 0")
            return

        tiempo_actual = self.tiempos_bloques[indice] if indice < len(self.tiempos_bloques) else self.tiempo_total_segundos
        porcentaje = int((tiempo_actual / max(self.tiempo_total_segundos, 1)) * 100)
        
        t_actual_fmt = self.formatear_tiempo(tiempo_actual)
        t_total_fmt = self.formatear_tiempo(self.tiempo_total_segundos)

        self.lbl_tiempo.configure(text=f"{t_actual_fmt} / {t_total_fmt} ({porcentaje}%)")
        self.lbl_progreso.configure(text=f"Bloque: {indice + 1} / {total}")

    def al_iniciar_arrastre(self, event):
        self.arrastrando_slider = True

    def al_soltar_arrastre(self, event):
        self.arrastrando_slider = False
        if self.bloques_subtitulos:
            nuevo_idx = int(round(self.slider_var.get()))
            self.indice_bloque_actual = nuevo_idx
            bloque_texto = self.bloques_subtitulos[self.indice_bloque_actual]
            self.actualizar_pantalla_con_sombra(bloque_texto)

    def al_mover_slider(self, val):
        if self.arrastrando_slider and self.bloques_subtitulos:
            idx = int(round(float(val)))
            self.actualizar_etiqueta_progreso(idx)
            bloque_texto = self.bloques_subtitulos[idx]
            self.actualizar_pantalla_con_sombra(bloque_texto)

    def actualizar_pantalla_con_sombra(self, texto):
        self.canvas.delete("all")
        if not texto: return

        x = self.canvas.winfo_width() / 2
        y = self.canvas.winfo_height() / 2

        fuente_config = (self.font_family, self.font_size, "bold")
        d = 3

        self.canvas.create_text(x-d, y-d, text=texto, font=fuente_config, fill="black", justify="center", anchor="center")
        self.canvas.create_text(x+d, y-d, text=texto, font=fuente_config, fill="black", justify="center", anchor="center")
        self.canvas.create_text(x-d, y+d, text=texto, font=fuente_config, fill="black", justify="center", anchor="center")
        self.canvas.create_text(x+d, y+d, text=texto, font=fuente_config, fill="black", justify="center", anchor="center")
        self.canvas.create_text(x, y, text=texto, font=fuente_config, fill="white", justify="center", anchor="center")

    def iniciar(self):
        if not self.escribiendo and self.bloques_subtitulos:
            self.escribiendo = True
            self.pausado = False
            self.combo_idioma.configure(state="disabled")
            self.btn_cargar.configure(state="disabled")
            self.slider_ritmo.configure(state="disabled")
            self.btn_iniciar.configure(state="disabled")
            self.btn_exportar.configure(state="disabled")
            self.btn_pausar.configure(state="normal", text="⏸ Pausar")
            self.btn_reiniciar.configure(state="normal")
            
            self.ventana_proyeccion.update_idletasks()
            self.hilo_escritura = threading.Thread(target=self.bucle_escritura, daemon=True)
            self.hilo_escritura.start()

    def alternar_pausa(self):
        self.pausado = not self.pausado
        self.btn_pausar.configure(text="▶ Continuar" if self.pausado else "⏸ Pausar")

    def reiniciar(self):
        self.escribiendo = False
        self.pausado = False
        self.indice_bloque_actual = 0
        self.slider_var.set(0)
        self.actualizar_etiqueta_progreso(0)
        self.actualizar_pantalla_con_sombra("")
        
        self.combo_idioma.configure(state="readonly")
        self.btn_cargar.configure(state="normal")
        self.slider_ritmo.configure(state="normal" if self.ruta_archivo else "disabled")
        self.btn_iniciar.configure(state="normal" if self.ruta_archivo else "disabled")
        self.btn_exportar.configure(state="normal" if self.ruta_archivo else "disabled")
        self.btn_pausar.configure(state="disabled", text="⏸ Pausar")
        self.btn_reiniciar.configure(state="disabled")

    def bucle_escritura(self):
        while self.indice_bloque_actual < len(self.bloques_subtitulos):
            if not self.escribiendo: break

            bloque = self.bloques_subtitulos[self.indice_bloque_actual]
            texto_acumulado = ""

            if not self.arrastrando_slider:
                self.root.after(0, self.slider_var.set, self.indice_bloque_actual)
                self.root.after(0, self.actualizar_etiqueta_progreso, self.indice_bloque_actual)

            for caracter in bloque:
                while self.pausado or self.arrastrando_slider:
                    if not self.escribiendo: break
                    time.sleep(0.1)

                if not self.escribiendo: break

                texto_acumulado += caracter
                self.root.after(0, self.actualizar_pantalla_con_sombra, texto_acumulado)

                if caracter in SIGNOS_PUNTO:
                    pausa = self.pausa_punto
                elif caracter in SIGNOS_COMA:
                    pausa = self.pausa_coma
                elif caracter == '\n':
                    pausa = 0.1
                else:
                    pausa = self.vel_base

                time.sleep(pausa)

            if self.escribiendo:
                time.sleep(self.tiempo_lectura)

            self.indice_bloque_actual += 1

        self.root.after(0, self.reiniciar)

    # --- RENDERIZADO Y EXPORTACIÓN A MP4 ---
    def exportar_mp4(self):
        if not self.bloques_subtitulos: return

        ruta_salida = filedialog.asksaveasfilename(
            title="Guardar archivo MP4",
            defaultextension=".mp4",
            filetypes=[("Video MP4", "*.mp4")]
        )
        if not ruta_salida: return

        self.btn_exportar.configure(state="disabled")
        self.btn_iniciar.configure(state="disabled")
        self.btn_cargar.configure(state="disabled")
        self.slider_ritmo.configure(state="disabled")

        threading.Thread(target=self._proceso_render_mp4, args=(ruta_salida,), daemon=True).start()

    def _proceso_render_mp4(self, ruta_salida):
        ANCHO, ALTO = 1920, 1080
        COLOR_FONDO = (18, 110, 71)
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            out = cv2.VideoWriter(ruta_salida, fourcc, float(FPS), (ANCHO, ALTO))
            if not out.isOpened():
                raise Exception("avc1 no soportado")
        except:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(ruta_salida, fourcc, float(FPS), (ANCHO, ALTO))

        try:
            fuente = ImageFont.truetype(self.font_family, 60)
        except:
            fuente = ImageFont.load_default()

        d_sombra = 4

        for idx, bloque in enumerate(self.bloques_subtitulos):
            texto_acumulado = ""

            for caracter in bloque:
                texto_acumulado += caracter
                
                img = Image.new("RGB", (ANCHO, ALTO), COLOR_FONDO)
                draw = ImageDraw.Draw(img)

                bbox = draw.multiline_textbbox((0, 0), texto_acumulado, font=fuente, align="center")
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
                x = (ANCHO - text_w) // 2
                y = (ALTO - text_h) // 2

                for dx, dy in [(-d_sombra,-d_sombra), (d_sombra,-d_sombra), (-d_sombra,d_sombra), (d_sombra,d_sombra)]:
                    draw.multiline_text((x+dx, y+dy), texto_acumulado, font=fuente, fill="black", align="center")

                draw.multiline_text((x, y), texto_acumulado, font=fuente, fill="white", align="center")

                frame_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

                if caracter in SIGNOS_PUNTO:
                    duracion = self.pausa_punto
                elif caracter in SIGNOS_COMA:
                    duracion = self.pausa_coma
                elif caracter == '\n':
                    duracion = 0.1
                else:
                    duracion = self.vel_base

                num_frames = int(round(duracion * FPS))
                if num_frames < 1:
                    num_frames = 1

                for _ in range(num_frames):
                    out.write(frame_cv)

            num_frames_espera = int(round(self.tiempo_lectura * FPS))
            for _ in range(num_frames_espera):
                out.write(frame_cv)

            self.root.after(0, self.slider_var.set, idx)
            self.root.after(0, self.actualizar_etiqueta_progreso, idx)

        out.release()
        
        self.root.after(0, lambda: messagebox.showinfo("¡Completado!", f"El archivo MP4 se exportó exitosamente en:\n{ruta_salida}"))
        self.root.after(0, self.reiniciar)

if __name__ == "__main__":
    root = tk.Tk()
    try:
        style = ttk.Style()
        style.theme_use('clam')
    except:
        pass
        
    app = SimuladorSubtitulos(root)
    root.mainloop()
