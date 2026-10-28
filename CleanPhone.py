import os
import subprocess
import threading
import json
import urllib.request
import tkinter as tk
from tkinter import messagebox, ttk

# Importamos los datos estructurados desde el módulo dedicado
from bloatware_data import CARRIER_BLOATWARE, SYSTEM_BLOATWARE

CURRENT_VERSION = "1.1.0"
VERSION_URL = "https://raw.githubusercontent.com/zerocoolrd/CleanPhone/main/version.json"


class CollapsiblePane(tk.Frame):
    """Componente tipo acordeón totalmente limpio y sin barras blancas."""
    def __init__(self, parent, title, app_instance, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app = app_instance
        self.is_open = False
        self.config(bg=self.app.theme["bg_main"])

        # Marco de cabecera del acordeón
        self.header_frame = tk.Frame(self, bg=self.app.theme["bg_pane"], padx=4, pady=2)
        self.header_frame.pack(fill="x", padx=0, pady=1)

        self.toggle_btn = tk.Button(
            self.header_frame, text=f"▶  {title}", command=self.toggle, 
            bg=self.app.theme["bg_pane"], fg=self.app.theme["fg_text"], 
            activebackground=self.app.theme["btn_hover"], activeforeground=self.app.theme["fg_text"],
            relief="flat", anchor="w", font=("Arial", 9, "bold")
        )
        self.toggle_btn.pack(side="left", fill="x", expand=True)

        self.btn_select_all = tk.Button(
            self.header_frame, text="Marcar", command=self.select_all, 
            bg=self.app.theme["bg_pane"], fg=self.app.theme["accent_blue"], 
            activebackground=self.app.theme["btn_hover"], activeforeground=self.app.theme["accent_blue"],
            relief="flat", font=("Arial", 8, "bold"), width=8
        )
        self.btn_select_all.pack(side="left", padx=1)

        self.btn_deselect_all = tk.Button(
            self.header_frame, text="Desmarcar", command=self.deselect_all, 
            bg=self.app.theme["bg_pane"], fg=self.app.theme["accent_red"], 
            activebackground=self.app.theme["btn_hover"], activeforeground=self.app.theme["accent_red"],
            relief="flat", font=("Arial", 8, "bold"), width=9
        )
        self.btn_deselect_all.pack(side="left", padx=1)
        
        self.title_text = title
        self.content_frame = tk.Frame(self, bg=self.app.theme["bg_main"], padx=6, pady=4)

    def toggle(self):
        if self.is_open:
            self.content_frame.pack_forget()
            self.toggle_btn.config(text=f"▶  {self.title_text}")
            self.is_open = False
        else:
            self.content_frame.pack(fill="x", expand=True, padx=2, pady=2)
            self.toggle_btn.config(text=f"▼  {self.title_text}")
            self.is_open = True

    def select_all(self):
        for widget in self.content_frame.winfo_children():
            if isinstance(widget, tk.Checkbutton):
                widget.select()

    def deselect_all(self):
        for widget in self.content_frame.winfo_children():
            if isinstance(widget, tk.Checkbutton):
                widget.deselect()

    def update_theme(self):
        self.config(bg=self.app.theme["bg_main"])
        self.header_frame.config(bg=self.app.theme["bg_pane"])
        self.toggle_btn.config(
            bg=self.app.theme["bg_pane"], fg=self.app.theme["fg_text"],
            activebackground=self.app.theme["btn_hover"], activeforeground=self.app.theme["fg_text"]
        )
        self.btn_select_all.config(
            bg=self.app.theme["bg_pane"], fg=self.app.theme["accent_blue"],
            activebackground=self.app.theme["btn_hover"]
        )
        self.btn_deselect_all.config(
            bg=self.app.theme["bg_pane"], fg=self.app.theme["accent_red"],
            activebackground=self.app.theme["btn_hover"]
        )
        self.content_frame.config(bg=self.app.theme["bg_main"])
        for widget in self.content_frame.winfo_children():
            if isinstance(widget, tk.Checkbutton):
                widget.config(
                    bg=self.app.theme["bg_main"], fg=self.app.theme["fg_text"],
                    selectcolor=self.app.theme["bg_pane"], activebackground=self.app.theme["bg_main"],
                    activeforeground=self.app.theme["fg_text"]
                )


class CleanPhoneApp:

    def __init__(self, root):
        self.root = root
        self.root.title(f"CleanPhone Pro v{CURRENT_VERSION} - By Wolkelyn")
        
        # Temas perfeccionados (Oscuro y Claro)
        self.dark_theme = {
            "bg_main": "#0b0f19",
            "bg_pane": "#1e293b",
            "bg_header": "#0f172a",
            "fg_text": "#f8fafc",
            "fg_sub": "#94a3b8",
            "fg_info": "#cbd5e1",
            "btn_hover": "#334155",
            "accent_blue": "#38bdf8",
            "accent_red": "#f43f5e",
            "log_bg": "#020617",
            "log_fg": "#22c55e"
        }

        self.light_theme = {
            "bg_main": "#f1f5f9",
            "bg_pane": "#e2e8f0",
            "bg_header": "#ffffff",
            "fg_text": "#0f172a",
            "fg_sub": "#475569",
            "fg_info": "#334155",
            "btn_hover": "#cbd5e1",
            "accent_blue": "#0284c7",
            "accent_red": "#e11d48",
            "log_bg": "#ffffff",
            "log_fg": "#15803d"
        }

        self.is_dark_mode = True
        self.theme = self.dark_theme

        window_width = 540
        window_height = 700

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))

        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.root.resizable(True, True)
        self.root.minsize(580, 550)
        self.root.config(bg=self.theme["bg_main"])

        style = ttk.Style()
        style.theme_use("clam")

        self.device_id = None
        self.device_brand = ""
        self.check_vars = {}
        self.chk_widgets = {}
        self.carrier_sections = {}
        self.system_sections = {}

        # --- CABECERA SUPERIOR ---
        self.header_container = tk.Frame(root, bg=self.theme["bg_header"], pady=6, padx=10)
        self.header_container.pack(fill="x", padx=10, pady=6)

        self.lbl_logo_title = tk.Label(
            self.header_container, text="🐐 CleanPhone Pro", 
            font=("Arial", 11, "bold"), bg=self.theme["bg_header"], fg=self.theme["accent_blue"]
        )
        self.lbl_logo_title.pack(side="left")

        # Botón compacto para Modo Claro/Oscuro
        self.btn_theme_toggle = tk.Button(
            self.header_container, text="☀️ Claro", command=self.toggle_theme, 
            bg="#334155", fg="#f8fafc", activebackground="#475569", activeforeground="#ffffff",
            relief="flat", font=("Arial", 7, "bold"), padx=6, pady=2
        )
        self.btn_theme_toggle.pack(side="right", padx=2)

        # Botón compacto para Actualizar
        self.btn_update_check = tk.Button(
            self.header_container, text="🔄 Actualizar", command=self.check_for_updates, 
            bg="#334155", fg="#f8fafc", activebackground="#475569", activeforeground="#ffffff",
            relief="flat", font=("Arial", 7, "bold"), padx=6, pady=2
        )
        self.btn_update_check.pack(side="right", padx=2)

        # --- PANEL DE ESTADO DEL DISPOSITIVO ---
        self.info_frame = tk.LabelFrame(
            root, text=" Dispositivo Detectado ", padx=8, pady=4, 
            font=("Arial", 9, "bold"), bg=self.theme["bg_header"], fg=self.theme["fg_sub"], relief="flat"
        )
        self.info_frame.pack(fill="x", padx=10, pady=2)

        self.lbl_info = tk.Label(
            self.info_frame, text="Esperando conexion USB...", justify="left", 
            bg=self.theme["bg_header"], fg=self.theme["fg_info"], font=("Consolas", 9)
        )
        self.lbl_info.pack(anchor="w", pady=1)

        self.btn_frame = tk.Frame(self.info_frame, bg=self.theme["bg_header"])
        self.btn_frame.pack(anchor="e", pady=1)

        self.btn_detect = tk.Button(
            self.btn_frame, text="Detectar Equipo", command=self.detect_device, 
            bg="#2563eb", fg="white", activebackground="#1d4ed8", activeforeground="white",
            relief="flat", font=("Arial", 8, "bold"), padx=8, pady=2
        )
        self.btn_detect.pack(side="left", padx=3)

        self.btn_rescan = tk.Button(
            self.btn_frame, text="Redetectar Apps", command=self.scan_installed_apps, 
            bg="#0ea5e9", fg="white", activebackground="#0284c7", activeforeground="white",
            relief="flat", font=("Arial", 8, "bold"), padx=8, pady=2
        )
        self.btn_rescan.pack(side="left", padx=3)

        # --- CONTENEDOR PRINCIPAL CON SCROLL ---
        self.frame_container = tk.Frame(root, bg=self.theme["bg_main"])
        self.frame_container.pack(fill="both", expand=True, padx=10, pady=2)

        self.canvas = tk.Canvas(self.frame_container, highlightthickness=0, bg=self.theme["bg_main"])
        scrollbar = ttk.Scrollbar(self.frame_container, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.theme["bg_main"])
        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.build_all_sections()

        # --- SECCIÓN DE PROGRESO ---
        self.progress_frame = tk.Frame(root, bg=self.theme["bg_main"])
        self.progress_frame.pack(fill="x", padx=10, pady=2)

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, orient="horizontal", mode="determinate", 
            variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(fill="x", side="top", padx=2, pady=1)

        self.lbl_progress_status = tk.Label(
            self.progress_frame, text="Estado: Listo", font=("Arial", 8), 
            bg=self.theme["bg_main"], fg=self.theme["fg_sub"]
        )
        self.lbl_progress_status.pack(anchor="w", padx=2)

        # --- MONITOR DE PROCESOS ---
        self.monitor_frame = tk.LabelFrame(
            root, text=" Monitor de Procesos ", padx=8, pady=4, 
            font=("Arial", 9, "bold"), bg=self.theme["bg_header"], fg=self.theme["fg_sub"], relief="flat"
        )
        self.monitor_frame.pack(fill="x", padx=10, pady=2)

        self.log_text = tk.Text(
            self.monitor_frame, height=4, bg=self.theme["log_bg"], fg=self.theme["log_fg"], 
            font=("Consolas", 8), state="disabled", relief="flat", highlightthickness=0
        )
        log_scroll = ttk.Scrollbar(self.monitor_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        log_scroll.pack(side="right", fill="y")

        # --- PANEL INFERIOR DE ACCIONES ---
        self.exec_frame = tk.Frame(root, bg=self.theme["bg_main"], pady=4)
        self.exec_frame.pack(fill="x", padx=10, pady=4)

        self.btn_cache = tk.Button(
            self.exec_frame, text="LIMPIEZA CACHÉ", bg="#0ea5e9", fg="white", 
            activebackground="#0284c7", activeforeground="white", relief="flat",
            font=("Arial", 8, "bold"), command=self.execute_cache_cleaning, width=16, pady=6
        )
        self.btn_cache.pack(side="left", expand=True, padx=2)

        self.btn_optimize = tk.Button(
            self.exec_frame, text="OPTIMIZAR SISTEMA", bg="#f97316", fg="white", 
            activebackground="#ea580c", activeforeground="white", relief="flat",
            font=("Arial", 8, "bold"), command=self.execute_system_optimization, width=17, pady=6
        )
        self.btn_optimize.pack(side="left", expand=True, padx=2)

        self.btn_gamer = tk.Button(
            self.exec_frame, text="MODO GAMER 🐐", bg="#8b5cf6", fg="white", 
            activebackground="#7c3aed", activeforeground="white", relief="flat",
            font=("Arial", 8, "bold"), command=self.open_gamer_modal, width=16, pady=6
        )
        self.btn_gamer.pack(side="left", expand=True, padx=2)

        self.btn_debloat = tk.Button(
            self.exec_frame, text="DESINSTALAR APP", bg="#10b981", fg="white", 
            activebackground="#059669", activeforeground="white", relief="flat",
            font=("Arial", 8, "bold"), command=self.execute_debloat, width=16, pady=6
        )
        self.btn_debloat.pack(side="left", expand=True, padx=2)

        self.detect_device()

    def toggle_theme(self):
        """Alterna dinámicamente entre Modo Oscuro y Modo Claro."""
        if self.is_dark_mode:
            self.theme = self.light_theme
            self.is_dark_mode = False
            self.btn_theme_toggle.config(text="🌙 Oscuro")
        else:
            self.theme = self.dark_theme
            self.is_dark_mode = True
            self.btn_theme_toggle.config(text="☀️ Claro")

        # Aplicar colores sincronizados
        self.root.config(bg=self.theme["bg_main"])
        self.header_container.config(bg=self.theme["bg_header"])
        self.lbl_logo_title.config(bg=self.theme["bg_header"], fg=self.theme["accent_blue"])
        self.info_frame.config(bg=self.theme["bg_header"], fg=self.theme["fg_sub"])
        self.lbl_info.config(bg=self.theme["bg_header"], fg=self.theme["fg_info"])
        self.btn_frame.config(bg=self.theme["bg_header"])
        self.frame_container.config(bg=self.theme["bg_main"])
        self.canvas.config(bg=self.theme["bg_main"])
        self.scrollable_frame.config(bg=self.theme["bg_main"])
        self.progress_frame.config(bg=self.theme["bg_main"])
        self.lbl_progress_status.config(bg=self.theme["bg_main"], fg=self.theme["fg_sub"])
        self.monitor_frame.config(bg=self.theme["bg_header"], fg=self.theme["fg_sub"])
        self.log_text.config(bg=self.theme["log_bg"], fg=self.theme["log_fg"])
        self.exec_frame.config(bg=self.theme["bg_main"])

        for pane in list(self.carrier_sections.values()) + list(self.system_sections.values()):
            pane.update_theme()

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"> {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def update_progress(self, val, text=""):
        self.progress_var.set(val)
        if text:
            self.lbl_progress_status.config(text=f"Estado: {text} ({int(val)}%)")

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def run_adb(self, cmd):
        try:
            adb_path = os.path.join(os.getcwd(), "adb.exe")
            if not os.path.exists(adb_path):
                adb_path = "adb"
            res = subprocess.run(f'"{adb_path}" {cmd}', capture_output=True, text=True, shell=True)
            return res.stdout.strip()
        except Exception:
            return ""

    def detect_device(self):
        self.log("Buscando dispositivos conectados...")
        devices_out = self.run_adb("devices")
        lines = [l for l in devices_out.split("\n")[1:] if "device" in l]

        if not lines:
            self.device_id = None
            self.lbl_info.config(text="Estado: Ningun dispositivo detectado. Conecta el USB y activa Depuracion.", fg="#f43f5e")
            self.log("Ningún dispositivo detectado.")
            self.update_visible_sections("", "")
            return

        self.device_id = lines[0].split()[0]
        self.log(f"Dispositivo detectado: {self.device_id}")

        model = self.run_adb(f"-s {self.device_id} shell getprop ro.product.model")
        brand = self.run_adb(f"-s {self.device_id} shell getprop ro.product.brand")
        self.device_brand = brand.lower()
        android_ver = self.run_adb(f"-s {self.device_id} shell getprop ro.build.version.release")
        carrier_csc = self.run_adb(f"-s {self.device_id} shell getprop ro.csc.sales_code").upper()

        csc_map = {
            "ATT": "AT&T", "CWH": "AT&T",
            "TMO": "T-Mobile / Sprint", "TMK": "T-Mobile / Sprint", "SPR": "T-Mobile / Sprint",
            "VZW": "Verizon",
            "DOR": "Claro", "CTM": "Claro", "CLO": "Claro", "AMX": "Claro",
            "TDR": "Altice", "TCN": "Altice"
        }
        detected_carrier = csc_map.get(carrier_csc, "")

        mem_info = self.run_adb(f"-s {self.device_id} shell cat /proc/meminfo")
        ram_total, ram_free = "N/A", "N/A"
        try:
            for line in mem_info.splitlines():
                if "MemTotal:" in line:
                    val_kb = int(line.split()[1])
                    ram_total = f"{val_kb // 1024 // 1024} GB"
                elif "MemAvailable:" in line:
                    val_kb = int(line.split()[1])
                    ram_free = f"{val_kb // 1024} MB"
        except Exception:
            pass

        df_out = self.run_adb(f"-s {self.device_id} shell df -h /data")
        storage_info = "Almacenamiento: N/A"
        try:
            lines_df = df_out.splitlines()
            if len(lines_df) > 1:
                parts = lines_df[1].split()
                if len(parts) >= 4:
                    storage_info = f"Libre: {parts[3]} / Total: {parts[1]}"
        except Exception:
            pass

        info_text = (
            f"Equipo: {brand.upper()} {model} | Android: {android_ver} | CSC: {carrier_csc} ({detected_carrier or 'Libre/Otro'})\n"
            f"RAM Libre: {ram_free} ({ram_total}) | Almacenamiento {storage_info}"
        )
        self.lbl_info.config(text=info_text, fg=self.theme["accent_blue"])
        self.log(f"Equipo conectado: {brand.upper()} {model} (CSC: {carrier_csc})")

        self.update_visible_sections(self.device_brand, detected_carrier)
        self.scan_installed_apps()

    def get_installed_packages(self):
        if not self.device_id:
            return set()
        output = self.run_adb(f"-s {self.device_id} shell pm list packages")
        return {line.replace("package:", "").strip() for line in output.splitlines() if line.startswith("package:")}

    def scan_installed_apps(self):
        if not self.device_id:
            return
        self.log("Escaneando aplicaciones instaladas en el dispositivo...")
        installed_packages = self.get_installed_packages()
        count = 0
        for pkg, var in self.check_vars.items():
            if pkg in installed_packages:
                var.set(True)
                count += 1
                if pkg in self.chk_widgets:
                    self.chk_widgets[pkg].config(fg=self.theme["fg_text"])
            else:
                var.set(False)
                if pkg in self.chk_widgets:
                    self.chk_widgets[pkg].config(fg=self.theme["fg_sub"])
        self.log(f"Escaneo finalizado. Se detectaron {count} apps de la lista instaladas.")

    def build_all_sections(self):
        for carrier, items in CARRIER_BLOATWARE.items():
            pane = CollapsiblePane(self.scrollable_frame, f"Operadora: {carrier} ({len(items)} apps)", self)
            self.carrier_sections[carrier] = pane
            for name, pkg in items:
                var = tk.BooleanVar(value=False)
                chk = tk.Checkbutton(
                    pane.content_frame, text=f"{name} [{pkg}]", variable=var, anchor="w", justify="left",
                    bg=self.theme["bg_main"], fg=self.theme["fg_text"], selectcolor=self.theme["bg_pane"], 
                    activebackground=self.theme["bg_main"], activeforeground=self.theme["fg_text"], relief="flat"
                )
                chk.pack(fill="x", anchor="w", padx=4, pady=1)
                self.check_vars[pkg] = var
                self.chk_widgets[pkg] = chk

        for cat_name, items in SYSTEM_BLOATWARE.items():
            pane = CollapsiblePane(self.scrollable_frame, f"Sistema: {cat_name} ({len(items)} apps)", self)
            self.system_sections[cat_name] = pane
            for name, pkg in items:
                var = tk.BooleanVar(value=False)
                chk = tk.Checkbutton(
                    pane.content_frame, text=f"{name} [{pkg}]", variable=var, anchor="w", justify="left",
                    bg=self.theme["bg_main"], fg=self.theme["fg_text"], selectcolor=self.theme["bg_pane"], 
                    activebackground=self.theme["bg_main"], activeforeground=self.theme["fg_text"], relief="flat"
                )
                chk.pack(fill="x", anchor="w", padx=4, pady=1)
                self.check_vars[pkg] = var
                self.chk_widgets[pkg] = chk

    def update_visible_sections(self, brand, carrier):
        for pane in self.carrier_sections.values():
            pane.pack_forget()
        for pane in self.system_sections.values():
            pane.pack_forget()

        if not brand:
            return

        if "samsung" in brand:
            for cat_name, pane in self.system_sections.items():
                pane.pack(fill="x", expand=True, pady=2)

            if carrier and carrier in self.carrier_sections:
                self.carrier_sections[carrier].pack(fill="x", expand=True, pady=2)

    def execute_cache_cleaning(self):
        if not self.device_id:
            messagebox.showerror("Error", "No hay ningún teléfono conectado por USB.")
            return

        if not messagebox.askyesno("Confirmar Limpieza de Caché", "⚠️ ADVERTENCIA: ¿Desea continuar con la limpieza de caché?"):
            return

        self.log("--- INICIANDO LIMPIEZA DE CACHÉ ---")
        self.update_progress(10, "Limpiando caché de sistema")
        self.run_adb(f"-s {self.device_id} shell pm trim-caches 999999999G")
        self.update_progress(40, "Limpiando Google Chrome")
        self.run_adb(f"-s {self.device_id} shell pm clear com.android.chrome")
        self.update_progress(100, "Limpieza completada")
        messagebox.showinfo("Proceso Completado", "Limpieza de caché finalizada con éxito.")
        self.root.after(2000, lambda: self.update_progress(0, "Listo"))

    def execute_system_optimization(self):
        if not self.device_id:
            messagebox.showerror("Error", "No hay ningún teléfono conectado por USB.")
            return
        if not messagebox.askyesno("Confirmar Optimización", "¿Desea iniciar la optimización integral del sistema?"):
            return
        self.btn_optimize.config(state=tk.DISABLED)
        threading.Thread(target=self._run_optimization_worker, daemon=True).start()

    def _run_optimization_worker(self):
        self.log("--- OPTIMIZACIÓN INTEGRAL EN CURSO ---")
        self.root.after(0, lambda: self.update_progress(20, "Acelerando animaciones"))
        self.run_adb(f"-s {self.device_id} shell settings put global window_animation_scale 0.85")
        self.run_adb(f"-s {self.device_id} shell settings put global transition_animation_scale 0.85")
        self.run_adb(f"-s {self.device_id} shell settings put global animator_duration_scale 0.85")
        self.root.after(0, lambda: self.update_progress(100, "Optimización Completa"))
        messagebox.showinfo("Optimización Completa", "El sistema se ha optimizado correctamente.")
        self.root.after(0, lambda: self.btn_optimize.config(state=tk.NORMAL))

    def check_for_updates(self):
        try:
            req = urllib.request.urlopen(VERSION_URL, timeout=5)
            data = json.loads(req.read().decode("utf-8"))
            if data.get("version") and data.get("version") != CURRENT_VERSION:
                if messagebox.askyesno("Actualización", f"Nueva versión {data.get('version')} disponible. ¿Descargar?"):
                    self.download_and_apply_update(data.get("download_url"))
            else:
                messagebox.showinfo("Actualizado", f"Ya tienes la última versión (v{CURRENT_VERSION}).")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo comprobar actualizaciones: {e}")

    def download_and_apply_update(self, url):
        try:
            current_script_path = os.path.abspath(__file__)
            temp_script_path = current_script_path + ".tmp"
            urllib.request.urlretrieve(url, temp_script_path)
            os.replace(temp_script_path, current_script_path)
            messagebox.showinfo("Éxito", "Actualización aplicada. Reiniciando aplicación.")
            os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al actualizar: {e}")

    def open_gamer_modal(self):
        if not self.device_id:
            messagebox.showerror("Error", "No hay ningún teléfono conectado por USB.")
            return

        gamer_win = tk.Toplevel(self.root)
        gamer_win.title("Modo Gamer - By Wolkelyn")
        win_width, win_height = 420, 350
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int((screen_width / 2) - (win_width / 2))
        center_y = int((screen_height / 2) - (win_height / 2))

        gamer_win.geometry(f"{win_width}x{win_height}+{center_x}+{center_y}")
        gamer_win.resizable(False, False)
        gamer_win.transient(self.root)
        gamer_win.grab_set()
        gamer_win.config(bg=self.theme["bg_header"])

        tk.Label(
            gamer_win, text="🐐 MODO GAMER 🐐", 
            font=("Arial", 11, "bold"), bg=self.theme["bg_header"], fg="#a78bfa"
        ).pack(pady=12)
        
        tk.Label(
            gamer_win, text="Selecciona el perfil de rendimiento extremo:", 
            font=("Arial", 8), bg=self.theme["bg_header"], fg=self.theme["fg_sub"]
        ).pack(pady=4)

        tk.Button(
            gamer_win, text="🚀 Velocidad y FPS Máximos (Turbo)", bg="#ef4444", fg="white", 
            activebackground="#dc2626", activeforeground="white", relief="flat",
            font=("Arial", 9, "bold"), width=36, pady=8, 
            command=lambda: [self.apply_gamer_profile("turbo"), gamer_win.destroy()]
        ).pack(pady=6)

        tk.Button(
            gamer_win, text="⚖️ Rendimiento Equilibrado", bg="#f59e0b", fg="white", 
            activebackground="#d97706", activeforeground="white", relief="flat",
            font=("Arial", 9, "bold"), width=36, pady=8, 
            command=lambda: [self.apply_gamer_profile("balanced"), gamer_win.destroy()]
        ).pack(pady=6)

        tk.Button(
            gamer_win, text="🏭 Rendimiento de Fábrica (Original)", bg="#0ea5e9", fg="white", 
            activebackground="#0284c7", activeforeground="white", relief="flat",
            font=("Arial", 9, "bold"), width=36, pady=8, 
            command=lambda: [self.apply_gamer_profile("factory"), gamer_win.destroy()]
        ).pack(pady=6)

    def apply_gamer_profile(self, profile):
        self.btn_gamer.config(state=tk.DISABLED)
        threading.Thread(target=self._run_gamer_worker, args=(profile,), daemon=True).start()

    def _run_gamer_worker(self, profile):
        if profile == "turbo":
            self.run_adb(f"-s {self.device_id} shell cmd power set-fixed-performance-mode-enabled true")
            self.run_adb(f"-s {self.device_id} shell settings put system peak_refresh_rate 120.0")
            self.run_adb(f"-s {self.device_id} shell settings put system min_refresh_rate 120.0")
            self.run_adb(f"-s {self.device_id} shell settings put global window_animation_scale 0")
            messagebox.showinfo("Gamer", "🚀 ¡Modo Turbo activado al máximo rendimiento!")
        elif profile == "balanced":
            self.run_adb(f"-s {self.device_id} shell cmd power set-fixed-performance-mode-enabled false")
            self.run_adb(f"-s {self.device_id} shell settings put system peak_refresh_rate 120.0")
            self.run_adb(f"-s {self.device_id} shell settings put system min_refresh_rate 60.0")
            messagebox.showinfo("Gamer", "⚖️ Rendimiento equilibrado aplicado.")
        elif profile == "factory":
            self.run_adb(f"-s {self.device_id} shell cmd power set-fixed-performance-mode-enabled false")
            self.run_adb(f"-s {self.device_id} shell settings put system peak_refresh_rate 120.0")
            self.run_adb(f"-s {self.device_id} shell settings put system min_refresh_rate 60.0")
            messagebox.showinfo("Gamer", "🏭 Valores originales restaurados con éxito.")
        self.root.after(0, lambda: self.btn_gamer.config(state=tk.NORMAL))

    def execute_debloat(self):
        if not self.device_id:
            messagebox.showerror("Error", "No hay ningún teléfono conectado.")
            return
        selected_pkgs = [pkg for pkg, var in self.check_vars.items() if var.get() and self.chk_widgets[pkg].winfo_ismapped()]
        if not selected_pkgs:
            messagebox.showwarning("Atención", "No has seleccionado ninguna aplicación.")
            return
        if not messagebox.askyesno("Confirmar", f"¿Desinstalar {len(selected_pkgs)} aplicaciones?"):
            return
        for pkg in selected_pkgs:
            self.run_adb(f"-s {self.device_id} shell pm uninstall --user 0 {pkg}")
        messagebox.showinfo("Completado", "Proceso de desinstalación finalizado.")


if __name__ == "__main__":
    import sys
    root = tk.Tk()
    app = CleanPhoneApp(root)
    root.mainloop()
