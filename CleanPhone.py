import os
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, ttk

# Importamos los datos estructurados desde el módulo dedicado
from bloatware_data import CARRIER_BLOATWARE, SYSTEM_BLOATWARE


class CollapsiblePane(ttk.LabelFrame):
    """Componente ultra-compacto para secciones desplegables (Acordeón) con encabezado a la izquierda."""
    def __init__(self, parent, title, *args, **kwargs):
        super().__init__(parent, text="", *args, **kwargs)
        self.is_open = False

        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=1, pady=0)

        self.toggle_btn = ttk.Button(header_frame, text=f"▶ {title}", command=self.toggle, style="TButton")
        self.toggle_btn.pack(side="left", padx=1, fill="x", expand=True)

        self.btn_select_all = ttk.Button(header_frame, text="Marcar Todo", command=self.select_all, width=10)
        self.btn_deselect_all = ttk.Button(header_frame, text="Desmarcar Todo", command=self.deselect_all, width=12)
        
        self.title_text = title
        self.content_frame = ttk.Frame(self, padding=1)

    def toggle(self):
        if self.is_open:
            self.content_frame.pack_forget()
            self.btn_select_all.pack_forget()
            self.btn_deselect_all.pack_forget()
            self.toggle_btn.config(text=f"▶ {self.title_text}")
            self.is_open = False
        else:
            self.content_frame.pack(fill="x", expand=True, padx=2, pady=1)
            self.btn_select_all.pack(side="left", padx=2)
            self.btn_deselect_all.pack(side="left", padx=1)
            self.toggle_btn.config(text=f"▼ {self.title_text}")
            self.is_open = True

    def select_all(self):
        for widget in self.content_frame.winfo_children():
            if isinstance(widget, tk.Checkbutton):
                widget.select()

    def deselect_all(self):
        for widget in self.content_frame.winfo_children():
            if isinstance(widget, tk.Checkbutton):
                widget.deselect()


class CleanPhoneApp:

    def __init__(self, root):
        self.root = root
        self.root.title("CleanPhone Pro - Limpieza Inteligente By Wolkelyn")
        
        window_width = 720
        window_height = 740

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))

        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.root.resizable(True, True)
        self.root.minsize(580, 550)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", anchor="w")

        self.device_id = None
        self.device_brand = ""
        self.check_vars = {}
        self.chk_widgets = {}
        self.carrier_sections = {}
        self.system_sections = {}

        lbl_title = tk.Label(root, text="CleanPhone - Optimizador Inteligente", font=("Arial", 11, "bold"))
        lbl_title.pack(pady=2)

        # Panel de Estado del Dispositivo
        info_frame = tk.LabelFrame(root, text=" Dispositivo Detectado ", padx=6, pady=2, font=("Arial", 9, "bold"))
        info_frame.pack(fill="x", padx=8, pady=2)

        self.lbl_info = tk.Label(
            info_frame, text="Esperando conexion USB...", justify="left", fg="gray", font=("Consolas", 9)
        )
        self.lbl_info.pack(anchor="w", pady=0)

        btn_frame = tk.Frame(info_frame)
        btn_frame.pack(anchor="e", pady=0)

        btn_detect = tk.Button(btn_frame, text="Detectar Equipo", command=self.detect_device, bg="#007bff", fg="white", font=("Arial", 8, "bold"))
        btn_detect.pack(side="left", padx=2)

        btn_rescan = tk.Button(btn_frame, text="Redetectar Apps", command=self.scan_installed_apps, bg="#17a2b8", fg="white", font=("Arial", 8, "bold"))
        btn_rescan.pack(side="left", padx=2)

        # Contenedor principal con Scroll compacto
        frame_container = tk.Frame(root)
        frame_container.pack(fill="both", expand=True, padx=8, pady=2)

        self.canvas = tk.Canvas(frame_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_container, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.build_all_sections()

        # --- SECCIÓN DE PROGRESO (BARRA Y PORCENTAJE) ---
        progress_frame = tk.Frame(root)
        progress_frame.pack(fill="x", padx=10, pady=2)

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate", variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", side="top", padx=2, pady=1)

        self.lbl_progress_status = tk.Label(progress_frame, text="Estado: Listo", font=("Arial", 8), fg="gray")
        self.lbl_progress_status.pack(anchor="w", padx=2)

        # --- MONITOR DE PROCESOS (CUADRO DE REGISTRO) ---
        monitor_frame = tk.LabelFrame(root, text=" Monitor de Procesos ", padx=6, pady=2, font=("Arial", 9, "bold"))
        monitor_frame.pack(fill="x", padx=8, pady=2)

        self.log_text = tk.Text(monitor_frame, height=4, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 8), state="disabled")
        log_scroll = ttk.Scrollbar(monitor_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        log_scroll.pack(side="right", fill="y")

        # --- PANEL INFERIOR CON LOS BOTONES PRINCIPALES Y MODO GAMER ---
        exec_frame = tk.Frame(root)
        exec_frame.pack(pady=6)

        self.btn_cache = tk.Button(
            exec_frame, text="LIMPIEZA CACHÉ", bg="#17a2b8", fg="white", font=("Arial", 8, "bold"),
            command=self.execute_cache_cleaning, width=16, pady=5
        )
        self.btn_cache.pack(side="left", padx=3)

        self.btn_optimize = tk.Button(
            exec_frame, text="OPTIMIZAR SISTEMA", bg="#fd7e14", fg="white", font=("Arial", 8, "bold"),
            command=self.execute_system_optimization, width=17, pady=5
        )
        self.btn_optimize.pack(side="left", padx=3)

        self.btn_gamer = tk.Button(
            exec_frame, text="MODO GAMER", bg="#6f42c1", fg="white", font=("Arial", 8, "bold"),
            command=self.open_gamer_modal, width=16, pady=5
        )
        self.btn_gamer.pack(side="left", padx=3)

        self.btn_debloat = tk.Button(
            exec_frame, text="DESINSTALAR APP", bg="#28a745", fg="white", font=("Arial", 8, "bold"),
            command=self.execute_debloat, width=16, pady=5
        )
        self.btn_debloat.pack(side="left", padx=3)

        self.detect_device()

    def log(self, message):
        """Agrega un mensaje al monitor de procesos en tiempo real."""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"> {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def update_progress(self, val, text=""):
        """Actualiza la barra de progreso y el texto descriptivo de manera segura para hilos."""
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
            self.lbl_info.config(
                text="Estado: Ningun dispositivo detectado. Conecta el USB y activa Depuracion.", fg="red"
            )
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
        self.lbl_info.config(text=info_text, fg="darkblue")
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
                    self.chk_widgets[pkg].config(fg="black")
            else:
                var.set(False)
                if pkg in self.chk_widgets:
                    self.chk_widgets[pkg].config(fg="gray")
        self.log(f"Escaneo finalizado. Se detectaron {count} apps de la lista instaladas.")

    def build_all_sections(self):
        for carrier, items in CARRIER_BLOATWARE.items():
            pane = CollapsiblePane(self.scrollable_frame, f"Operadora: {carrier} ({len(items)} apps)")
            self.carrier_sections[carrier] = pane
            for name, pkg in items:
                var = tk.BooleanVar(value=False)
                chk = tk.Checkbutton(pane.content_frame, text=f"{name} [{pkg}]", variable=var, anchor="w", justify="left")
                chk.pack(fill="x", anchor="w", padx=4, pady=0)
                self.check_vars[pkg] = var
                self.chk_widgets[pkg] = chk

        for cat_name, items in SYSTEM_BLOATWARE.items():
            pane = CollapsiblePane(self.scrollable_frame, f"Sistema: {cat_name} ({len(items)} apps)")
            self.system_sections[cat_name] = pane
            for name, pkg in items:
                var = tk.BooleanVar(value=False)
                chk = tk.Checkbutton(pane.content_frame, text=f"{name} [{pkg}]", variable=var, anchor="w", justify="left")
                chk.pack(fill="x", anchor="w", padx=4, pady=0)
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
                pane.pack(fill="x", expand=True, pady=1)

            if carrier and carrier in self.carrier_sections:
                self.carrier_sections[carrier].pack(fill="x", expand=True, pady=1)

    def execute_cache_cleaning(self):
        if not self.device_id:
            messagebox.showerror("Error", "No hay ningún teléfono conectado por USB.")
            return

        advertencia = (
            "⚠️ ADVERTENCIA: LIMPIEZA DE CACHÉ\n\n"
            "• Qué realizará: Liberará la caché general del sistema, borrará datos/caché de Google Chrome, "
            "detendrá procesos secundarios en segundo plano y reiniciará el Launcher principal.\n"
            "• Tiempo aproximado: 15 a 30 segundos.\n\n"
            "¿Desea continuar con este proceso?"
        )
        if not messagebox.askyesno("Confirmar Limpieza de Caché", advertencia):
            return

        self.log("--- INICIANDO LIMPIEZA DE CACHÉ Y MANTENIMIENTO ---")
        self.update_progress(10, "Limpiando caché de sistema")
        
        self.run_adb(f"-s {self.device_id} shell pm trim-caches 999999999G")
        self.update_progress(40, "Limpiando Google Chrome")

        self.run_adb(f"-s {self.device_id} shell pm clear com.android.chrome")
        self.update_progress(70, "Cerrando aplicaciones en segundo plano")

        packages_out = self.run_adb(f"-s {self.device_id} shell pm list packages -3")
        for line in packages_out.splitlines():
            if line.startswith("package:"):
                pkg = line.replace("package:", "").strip()
                self.run_adb(f"-s {self.device_id} shell am force-stop {pkg}")

        self.update_progress(100, "Limpieza de caché completada")
        self.log("--- LIMPIEZA DE CACHÉ FINALIZADA ---")
        messagebox.showinfo("Proceso Completado", "Limpieza de caché finalizada con éxito.")
        self.root.after(2000, lambda: self.update_progress(0, "Listo"))

    def execute_system_optimization(self):
        if not self.device_id:
            messagebox.showerror("Error", "No hay ningún teléfono conectado por USB.")
            return

        advertencia = (
            "⚠️ ADVERTENCIA: OPTIMIZACIÓN INTEGRAL Y ACELERACIÓN\n\n"
            "• Qué realizará: Analizará el estado y salud de la batería, re-compilará los perfiles de velocidad "
            "de todas las aplicaciones (Runtime ART), aplicará ahorro profundo (Doze) y acelerará las "
            "animaciones del sistema un 15% más rápido (escala 0.85).\n"
            "• Tiempo aproximado: 1 a 3 minutos (dependiendo de la cantidad de apps instaladas).\n\n"
            "¿Desea iniciar la optimización?"
        )
        if not messagebox.askyesno("Confirmar Optimización del Sistema", advertencia):
            return

        self.btn_optimize.config(state=tk.DISABLED)
        threading.Thread(target=self._run_optimization_worker, daemon=True).start()

    def _run_optimization_worker(self):
        self.log("--- INICIANDO OPTIMIZACIÓN INTEGRAL Y ACELERACIÓN ---")
        summary = []

        # 1. Batería (10%)
        self.root.after(0, lambda: self.update_progress(10, "Leyendo estado de batería"))
        battery_out = self.run_adb(f"-s {self.device_id} shell dumpsys battery")
        batt_level, batt_health = "N/A", "N/A"
        for line in battery_out.splitlines():
            if "level:" in line:
                batt_level = line.split(":")[1].strip() + "%"
            elif "health:" in line:
                h_val = line.split(":")[1].strip()
                batt_health = "Buena (Good)" if h_val == "2" else f"Código {h_val}"
        summary.append(f"🔋 Batería -> Nivel: {batt_level} | Salud: {batt_health}")
        self.log(f"🔋 Batería: Nivel {batt_level} | Estado: {batt_health}")

        # 2. Aceleración de Animaciones un 15% más rápido (20%)
        self.root.after(0, lambda: self.update_progress(20, "Acelerando animaciones (15% más rápido)"))
        self.run_adb(f"-s {self.device_id} shell settings put global window_animation_scale 0.85")
        self.run_adb(f"-s {self.device_id} shell settings put global transition_animation_scale 0.85")
        self.run_adb(f"-s {self.device_id} shell settings put global animator_duration_scale 0.85")
        summary.append("⚡ Animaciones aceleradas (Escala 0.85).")
        self.log("✔ Animaciones del sistema aceleradas un 15% más rápido.")

        # 3. Optimización ART App por App (30% al 85%)
        self.root.after(0, lambda: self.update_progress(30, "Obteniendo lista de paquetes para compilar"))
        pkgs_out = self.run_adb(f"-s {self.device_id} shell pm list packages")
        packages = [line.replace("package:", "").strip() for line in pkgs_out.splitlines() if line.startswith("package:")]
        
        total_pkgs = len(packages)
        if total_pkgs > 0:
            self.log(f"Optimizando perfiles de velocidad para {total_pkgs} aplicaciones...")
            for index, pkg in enumerate(packages):
                self.run_adb(f"-s {self.device_id} shell cmd package compile -m speed-profile {pkg}")
                
                progress_pct = 30 + int((index + 1) / total_pkgs * 55)
                if index % 5 == 0 or index == total_pkgs - 1:
                    self.root.after(0, lambda p=progress_pct, i=index+1, t=total_pkgs: self.update_progress(p, f"Optimizando app {i}/{t}"))
        
        summary.append(f"⚡ {total_pkgs} aplicaciones optimizadas (ART Runtime).")
        self.log("⚡ Compilación de perfiles ART finalizada con éxito.")

        # 4. Modo Doze (95%)
        self.root.after(0, lambda: self.update_progress(95, "Aplicando Modo Doze (Ahorro Profundo)"))
        self.run_adb(f"-s {self.device_id} shell dumpsys deviceidle force-idle")
        summary.append("💤 Modo de ahorro profundo (Doze) aplicado.")
        self.log("💤 Modo Doze activado.")

        # Finalizado (100%)
        self.root.after(0, lambda: self.update_progress(100, "¡Optimización Completa!"))
        self.log("--- OPTIMIZACIÓN INTEGRAL Y ACELERACIÓN COMPLETADA ---")
        
        report_text = "Reporte de Optimización del Sistema:\n\n" + "\n".join(summary)
        self.root.after(0, lambda: messagebox.showinfo("Optimización Completa", report_text))
        self.root.after(0, lambda: self.btn_optimize.config(state=tk.NORMAL))
        self.root.after(3000, lambda: self.update_progress(0, "Listo"))

    # ==========================================
    # --- MÓDULO GAMER / ACELERADOR DE JUEGOS ---
    # ==========================================
    def open_gamer_modal(self):
        if not self.device_id:
            messagebox.showerror("Error", "No hay ningún teléfono conectado por USB.")
            return

        gamer_win = tk.Toplevel(self.root)
        gamer_win.title("Modo Gamer - CleanPhone Pro")
        
        # Dimensiones y centrado absoluto en pantalla
        win_width = 400
        win_height = 320
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int((screen_width / 2) - (win_width / 2))
        center_y = int((screen_height / 2) - (win_height / 2))

        gamer_win.geometry(f"{win_width}x{win_height}+{center_x}+{center_y}")
        gamer_win.resizable(False, False)
        gamer_win.transient(self.root)
        gamer_win.grab_set()

        lbl_header = tk.Label(gamer_win, text="🎮 Selector de Perfil Gamer (ADB)", font=("Arial", 10, "bold"))
        lbl_header.pack(pady=10)

        lbl_desc = tk.Label(
            gamer_win, 
            text="Selecciona el perfil de rendimiento que deseas aplicar\nal dispositivo conectado para mejorar tu experiencia en juegos:", 
            font=("Arial", 8), justify="center", fg="gray"
        )
        lbl_desc.pack(pady=5)

        btn_turbo = tk.Button(
            gamer_win, text="🚀 Velocidad y FPS Máximos (Turbo)", bg="#d9534f", fg="white", 
            font=("Arial", 9, "bold"), width=35, pady=6,
            command=lambda: [self.apply_gamer_profile("turbo"), gamer_win.destroy()]
        )
        btn_turbo.pack(pady=6)

        btn_balanced = tk.Button(
            gamer_win, text="⚖️ Rendimiento Equilibrado", bg="#f0ad4e", fg="white", 
            font=("Arial", 9, "bold"), width=35, pady=6,
            command=lambda: [self.apply_gamer_profile("balanced"), gamer_win.destroy()]
        )
        btn_balanced.pack(pady=6)

        btn_factory = tk.Button(
            gamer_win, text="🏭 Rendimiento de Fábrica (Original)", bg="#5bc0de", fg="white", 
            font=("Arial", 9, "bold"), width=35, pady=6,
            command=lambda: [self.apply_gamer_profile("factory"), gamer_win.destroy()]
        )
        btn_factory.pack(pady=6)

    def apply_gamer_profile(self, profile):
        self.btn_gamer.config(state=tk.DISABLED)
        threading.Thread(target=self._run_gamer_worker, args=(profile,), daemon=True).start()

    def _run_gamer_worker(self, profile):
        if profile == "turbo":
            self.log("--- APLICANDO MODO TURBO (VELOCIDAD Y FPS MÁXIMOS) ---")
            self.root.after(0, lambda: self.update_progress(20, "Activando rendimiento fijo"))
            self.run_adb(f"-s {self.device_id} shell cmd power set-fixed-performance-mode-enabled true")
            
            self.root.after(0, lambda: self.update_progress(60, "Forzando tasa de refresco máxima"))
            self.run_adb(f"-s {self.device_id} shell settings put system peak_refresh_rate 120.0")
            self.run_adb(f"-s {self.device_id} shell settings put system min_refresh_rate 120.0")
            
            self.root.after(0, lambda: self.update_progress(90, "Eliminando animaciones de interfaz"))
            self.run_adb(f"-s {self.device_id} shell settings put global window_animation_scale 0")
            self.run_adb(f"-s {self.device_id} shell settings put global transition_animation_scale 0")
            self.run_adb(f"-s {self.device_id} shell settings put global animator_duration_scale 0")
            
            self.log("✔ ¡Modo Turbo aplicado con éxito en el dispositivo!")
            self.root.after(0, lambda: messagebox.showinfo("Modo Gamer", "🚀 Modo Turbo aplicado correctamente."))

        elif profile == "balanced":
            self.log("--- APLICANDO MODO EQUILIBRADO ---")
            self.root.after(0, lambda: self.update_progress(30, "Restaurando gestión inteligente"))
            self.run_adb(f"-s {self.device_id} shell cmd power set-fixed-performance-mode-enabled false")
            
            self.root.after(0, lambda: self.update_progress(70, "Configurando refresco dinámico"))
            self.run_adb(f"-s {self.device_id} shell settings put system peak_refresh_rate 120.0")
            self.run_adb(f"-s {self.device_id} shell settings put system min_refresh_rate 60.0")
            
            self.run_adb(f"-s {self.device_id} shell settings put global window_animation_scale 1.0")
            self.run_adb(f"-s {self.device_id} shell settings put global transition_animation_scale 1.0")
            self.run_adb(f"-s {self.device_id} shell settings put global animator_duration_scale 1.0")
            
            self.log("✔ ¡Modo Equilibrado aplicado con éxito!")
            self.root.after(0, lambda: messagebox.showinfo("Modo Gamer", "⚖️ Rendimiento equilibrado aplicado."))

        elif profile == "factory":
            self.log("--- RESTAURANDO RENDIMIENTO DE FÁBRICA ---")
            self.root.after(0, lambda: self.update_progress(50, "Restaurando valores originales"))
            self.run_adb(f"-s {self.device_id} shell cmd power set-fixed-performance-mode-enabled false")
            self.run_adb(f"-s {self.device_id} shell settings put system peak_refresh_rate 120.0")
            self.run_adb(f"-s {self.device_id} shell settings put system min_refresh_rate 60.0")
            self.run_adb(f"-s {self.device_id} shell settings put global window_animation_scale 1.0")
            self.run_adb(f"-s {self.device_id} shell settings put global transition_animation_scale 1.0")
            self.run_adb(f"-s {self.device_id} shell settings put global animator_duration_scale 1.0")
            
            self.log("✔ ¡Valores de fábrica restaurados con éxito!")
            self.root.after(0, lambda: messagebox.showinfo("Modo Gamer", "🏭 Valores originales del sistema restaurados."))

        self.root.after(0, lambda: self.update_progress(100, "Modo Gamer Actualizado"))
        self.root.after(0, lambda: self.btn_gamer.config(state=tk.NORMAL))
        self.root.after(2500, lambda: self.update_progress(0, "Listo"))

    def execute_debloat(self):
        if not self.device_id:
            messagebox.showerror("Error", "No hay ningun telefono detectado por USB.")
            return

        selected_pkgs = [pkg for pkg, var in self.check_vars.items() if var.get() and self.chk_widgets[pkg].winfo_ismapped()]
        if not selected_pkgs:
            messagebox.showwarning("Atencion", "No has seleccionado ningun paquete visible para desinstalar.")
            return

        cant_apps = len(selected_pkgs)
        advertencia = (
            f"⚠️ ADVERTENCIA: DESINSTALACIÓN DE BLOATWARE ({cant_apps} apps seleccionadas)\n\n"
            f"• Qué realizará: Desinstalará mediante ADB (--user 0) y/o deshabilitará las aplicaciones "
            f"que has marcado en las listas, liberando espacio en el almacenamiento interno.\n"
            f"• Tiempo aproximado: 10 a 30 segundos.\n\n"
            f"¿Estás seguro de procesar estas {cant_apps} aplicaciones?"
        )
        if not messagebox.askyesno("Confirmar Desinstalación", advertencia):
            return

        self.log("--- INICIANDO DESINSTALACIÓN DE APPS SELECCIONADAS ---")
        self.update_progress(10, "Iniciando desinstalación")
        
        success_count = 0
        total_sel = len(selected_pkgs)
        for index, pkg in enumerate(selected_pkgs):
            self.log(f"Desinstalando / Deshabilitando: {pkg}")
            res = self.run_adb(f"-s {self.device_id} shell pm uninstall --user 0 {pkg}")
            if "Failure" in res or "not installed" not in res:
                self.run_adb(f"-s {self.device_id} shell pm disable-user --user 0 {pkg}")
            success_count += 1
            
            pct = 10 + int((index + 1) / total_sel * 80)
            self.update_progress(pct, f"Procesando {index+1}/{total_sel} apps")

        self.run_adb(f"-s {self.device_id} shell pm trim-caches 10G")
        self.update_progress(100, "Desinstalación finalizada")
        self.log(f"--- PROCESO FINALIZADO: {success_count} apps procesadas ---")
        messagebox.showinfo("Proceso Completado", f"Se procesaron {success_count} aplicaciones en el dispositivo {self.device_id}.")
        self.root.after(2000, lambda: self.update_progress(0, "Listo"))


if __name__ == "__main__":
    root = tk.Tk()
    app = CleanPhoneApp(root)
    root.mainloop()
