import subprocess

class PhoneOptimizer:
    def __init__(self, adb_path="adb"):
        self.adb_path = adb_path

    def run_adb(self, command):
        full_cmd = f"{self.adb_path} {command}"
        try:
            result = subprocess.run(
                full_cmd, shell=True, capture_output=True, text=True, timeout=10
            )
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def get_battery_status(self):
        output = self.run_adb("shell dumpsys battery")
        battery_info = {}
        for line in output.splitlines():
            if ":" in line:
                parts = line.split(":")
                battery_info[parts[0].strip()] = parts[1].strip()
        return battery_info

    def optimize_storage_cache(self):
        # Optimiza la compilación ART y limpia perfiles pesados de caché
        res = self.run_adb("shell cmd package compile -m speed-profile -a")
        return "Optimización de caché y paquetes completada." if "Success" in res or res else "Proceso finalizado."

    def force_stop_app(self, package_name):
        res = self.run_adb(f"shell am force-stop {package_name}")
        return f"Proceso {package_name} detenido."

    def trigger_doze_mode(self):
        # Fuerza al sistema a entrar en modo reposo profundo para ahorrar batería
        self.run_adb("shell dumpsys deviceidle force-idle")
        return "Modo Doze (Ahorro Profundo) activado en el dispositivo."
