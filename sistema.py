import psutil
import os

def temperatura_cpu():
    """Retorna temperatura da CPU em graus Celsius, se disponível."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read().strip()) / 1000.0
            return f"{temp:.1f}°C"
    except:
        return "desconhecida"

def status_bateria():
    """Retorna porcentagem e status da bateria."""
    try:
        bat = psutil.sensors_battery()
        if bat:
            status = "carregando" if bat.power_plugged else "descarregando"
            return f"{bat.percent}% ({status})"
    except:
        pass
    return "desconhecida"

def uso_cpu_ram():
    """Retorna uso da CPU e RAM em porcentagem."""
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().percent
    return f"CPU: {cpu}%, RAM: {ram}%"

def obter_contexto_sistema():
    """Contexto para inserir no prompt."""
    return f"Temperatura da CPU: {temperatura_cpu()}. Bateria: {status_bateria()}. Uso: {uso_cpu_ram()}."