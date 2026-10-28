import subprocess
import sys

class GamerOptimizer:
    def __init__(self):
        """Verifica si hay un dispositivo conectado por ADB antes de iniciar."""
        pass

    def _run_adb_command(self, command):
        """Ejecuta un comando ADB y maneja errores básicos."""
        full_command = ["adb"] + command
        try:
            result = subprocess.run(
                full_command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                check=True
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip()
        except FileNotFoundError:
            return False, "ADB no está instalado o no se encuentra en el PATH del sistema."

    def set_turbo_mode(self):
        """🚀 Velocidad y FPS Máximos (Modo Turbo)"""
        commands = [
            ["shell", "cmd", "power", "set-fixed-performance-mode-enabled", "true"],
            ["shell", "settings", "put", "system", "peak_refresh_rate", "120.0"],
            ["shell", "settings", "put", "system", "min_refresh_rate", "120.0"],
            ["shell", "settings", "put", "global", "window_animation_scale", "0"],
            ["shell", "settings", "put", "global", "transition_animation_scale", "0"],
            ["shell", "settings", "put", "global", "animator_duration_scale", "0"]
        ]
        
        print("[*] Aplicando Modo Turbo...")
        for cmd in commands:
            success, output = self._run_adb_command(cmd)
            if not success:
                print(f"[!] Advertencia en comando {' '.join(cmd)}: {output}")
        print("[+] ¡Modo Turbo aplicado con éxito!")

    def set_balanced_mode(self):
        """⚖️ Rendimiento Equilibrado"""
        commands = [
            ["shell", "cmd", "power", "set-fixed-performance-mode-enabled", "false"],
            ["shell", "settings", "put", "system", "peak_refresh_rate", "120.0"],
            ["shell", "settings", "put", "system", "min_refresh_rate", "60.0"],
            ["shell", "settings", "put", "global", "window_animation_scale", "1.0"],
            ["shell", "settings", "put", "global", "transition_animation_scale", "1.0"],
            ["shell", "settings", "put", "global", "animator_duration_scale", "1.0"]
        ]
        
        print("[*] Aplicando Modo Equilibrado...")
        for cmd in commands:
            success, output = self._run_adb_command(cmd)
            if not success:
                print(f"[!] Advertencia en comando {' '.join(cmd)}: {output}")
        print("[+] ¡Modo Equilibrado aplicado con éxito!")

    def set_factory_mode(self):
        """🏭 Rendimiento de Fábrica (Original)"""
        commands = [
            ["shell", "cmd", "power", "set-fixed-performance-mode-enabled", "false"],
            ["shell", "settings", "put", "system", "peak_refresh_rate", "120.0"],
            ["shell", "settings", "put", "system", "min_refresh_rate", "60.0"],
            ["shell", "settings", "put", "global", "window_animation_scale", "1.0"],
            ["shell", "settings", "put", "global", "transition_animation_scale", "1.0"],
            ["shell", "settings", "put", "global", "animator_duration_scale", "1.0"]
        ]
        
        print("[*] Restaurando valores de fábrica...")
        for cmd in commands:
            success, output = self._run_adb_command(cmd)
            if not success:
                print(f"[!] Advertencia en comando {' '.join(cmd)}: {output}")
        print("[+] ¡Valores de fábrica restaurados con éxito!")


# Ejemplo de integración en el menú principal de tu CleanPhone Pro
if __name__ == "__main__":
    optimizer = GamerOptimizer()
    
    while True:
        print("\n==================================")
        print("     CLEANPHONE PRO - GAMER     ")
        print("==================================")
        print("[1] 🚀 Velocidad y FPS Máximos (Turbo)")
        print("[2] ⚖️ Rendimiento Equilibrado")
        print("[3] 🏭 Rendimiento de Fábrica")
        print("[4] Salir")
        
        opcion = input("\nSelecciona una opción (1-4): ").strip()
        
        if opcion == "1":
            optimizer.set_turbo_mode()
        elif opcion == "2":
            optimizer.set_balanced_mode()
        elif opcion == "3":
            optimizer.set_factory_mode()
        elif opcion == "4":
            print("Saliendo del módulo Gamer...")
            break
        else:
            print("[!] Opción inválida, intenta de nuevo.")
