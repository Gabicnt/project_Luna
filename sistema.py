#!/usr/bin/env python3
"""
Sensores do Sistema – Fornece leituras de temperatura da CPU, bateria
e uso de CPU/RAM. Esses dados são injetados no contexto da conversa
para que a Luna possa reagir ao estado do computador.
"""

import os
import psutil


def temperatura_cpu() -> str:
    """
    Retorna a temperatura da CPU em graus Celsius.
    Caminho padrão do kernel Linux; pode variar conforme o hardware.
    """
    zonas = [
        "/sys/class/thermal/thermal_zone0/temp",
        "/sys/class/thermal/thermal_zone1/temp",
    ]
    for zona in zonas:
        try:
            with open(zona, "r") as f:
                temp = int(f.read().strip()) / 1000.0
                return f"{temp:.1f}°C"
        except (FileNotFoundError, ValueError):
            continue
    return "desconhecida"


def status_bateria() -> str:
    """Retorna a porcentagem e o status da bateria (carregando/descarregando)."""
    try:
        bat = psutil.sensors_battery()
        if bat is not None:
            status = "carregando" if bat.power_plugged else "descarregando"
            return f"{bat.percent:.0f}% ({status})"
    except Exception:
        pass
    return "desconhecida"


def uso_cpu_ram() -> str:
    """Retorna o uso percentual da CPU e da memória RAM."""
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        return f"CPU: {cpu:.0f}%, RAM: {ram:.0f}%"
    except Exception:
        return "CPU: ?, RAM: ?"


def uptime() -> str:
    """Retorna há quanto tempo o sistema está ligado (formato humano)."""
    try:
        with open("/proc/uptime", "r") as f:
            segundos = float(f.readline().split()[0])
        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        if horas > 0:
            return f"{horas}h{minutos}m"
        return f"{minutos} minutos"
    except Exception:
        return "desconhecido"


def obter_contexto_sistema() -> str:
    """
    Junta todas as leituras em uma única string pronta para ser
    inserida no prompt do sistema.
    """
    return (
        f"Temperatura da CPU: {temperatura_cpu()}. "
        f"Bateria: {status_bateria()}. "
        f"Uso: {uso_cpu_ram()}. "
        f"Ligado há: {uptime()}."
    )


# ==============================================================================
# Teste rápido
# ==============================================================================
if __name__ == "__main__":
    print("🧪 Teste dos sensores do sistema:\n")
    print(f"🌡️  Temperatura CPU: {temperatura_cpu()}")
    print(f"🔋 Bateria:         {status_bateria()}")
    print(f"💻 Uso CPU/RAM:     {uso_cpu_ram()}")
    print(f"⏱️  Uptime:          {uptime()}")
    print(f"\n📋 Contexto completo:\n{obter_contexto_sistema()}")