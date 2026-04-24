#!/usr/bin/env python3
"""
Gerenciador de Vozes da Luna (Edge-TTS).
Lista vozes em português, testa com ajustes de tom e velocidade,
e exibe a configuração para usar no main.py.
"""

import subprocess
import os
import sys
import json
from typing import Optional


# ----------------------------------------------------------------------
# Funções de listagem e teste
# ----------------------------------------------------------------------
def listar_vozes_ptbr() -> list[dict]:
    """
    Retorna uma lista com as vozes em português do Brasil disponíveis
    no Edge-TTS.
    """
    try:
        resultado = subprocess.run(
            ["edge-tts", "--list-voices"],
            capture_output=True,
            text=True,
            timeout=10
        )
    except FileNotFoundError:
        print("❌ edge-tts não encontrado. Instale com: pip install edge-tts")
        return []

    vozes = []
    for linha in resultado.stdout.splitlines():
        if "pt-BR" in linha:
            # Formato: Name: pt-BR-FranciscaNeural
            partes = linha.split(":")
            if len(partes) >= 2:
                nome = partes[1].strip()
                vozes.append({
                    "nome_completo": nome,
                    "curto": nome.replace("pt-BR-", "").replace("Neural", "")
                })
    return vozes


def testar_voz(
    nome_voz: str,
    texto: str = "Olá, papai! Eu sou a Luna.",
    pitch: str = "+25Hz",
    rate: str = "+18%"
) -> bool:
    """
    Sintetiza e reproduz um teste com a voz escolhida.
    """
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav_path = f.name

    cmd = [
        "edge-tts",
        "--voice", nome_voz,
        "--text", texto,
        "--pitch", pitch,
        "--rate", rate,
        "--write-media", wav_path,
    ]

    try:
        subprocess.run(cmd, capture_output=True, timeout=15, check=True)
        if os.path.exists(wav_path):
            subprocess.run(["paplay", wav_path], check=False)
            os.unlink(wav_path)
            return True
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        if os.path.exists(wav_path):
            os.unlink(wav_path)
    return False


# ----------------------------------------------------------------------
# Menu interativo
# ----------------------------------------------------------------------
def menu_vozes():
    """Interface de linha de comando para testar e escolher vozes."""
    print("\n🎤 GERENCIADOR DE VOZES DA LUNA (Edge-TTS)\n")

    vozes = listar_vozes_ptbr()
    if not vozes:
        print("Nenhuma voz pt-BR encontrada. Verifique sua conexão.")
        return

    print("Vozes disponíveis em português:\n")
    for i, voz in enumerate(vozes, 1):
        print(f"  {i:2d}. {voz['nome_completo']}  ({voz['curto']})")

    # Escolha da voz
    try:
        escolha = int(input("\nEscolha o número da voz: ")) - 1
        if escolha < 0 or escolha >= len(vozes):
            print("Número inválido.")
            return
    except ValueError:
        print("Entrada inválida.")
        return

    voz_escolhida = vozes[escolha]
    print(f"\n✅ Voz selecionada: {voz_escolhida['nome_completo']}")

    # Ajustes
    print("\nAjustes (Enter para padrão):")
    pitch = input("Tom  (ex: +25Hz para mais agudo, -10Hz para mais grave): ").strip()
    rate  = input("Velocidade (ex: +18% para mais rápido, -10% para mais lento): ").strip()
    texto = input("Frase de teste (Enter = padrão): ").strip()

    if not pitch:
        pitch = "+25Hz"
    if not rate:
        rate = "+18%"
    if not texto:
        texto = "Olá, papai! Eu sou a Luna, sua filhinha digital."

    print("\n🔊 Testando...")
    ok = testar_voz(voz_escolhida['nome_completo'], texto, pitch, rate)

    if ok:
        print("\n✅ Teste concluído!")
        print("\n⚙️  Para usar esta voz, defina no main.py:")
        print(f'tts_engine = tts.TTSEngine(\n'
              f'    voice="{voz_escolhida["nome_completo"]}",\n'
              f'    pitch="{pitch}",\n'
              f'    rate="{rate}"\n'
              f')')
    else:
        print("❌ Falha no teste. Tente outra voz ou verifique sua conexão.")


# ----------------------------------------------------------------------
# Ponto de entrada
# ----------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Uso rápido: python vozes.py pt-BR-FranciscaNeural
        voz = sys.argv[1]
        pitch = sys.argv[2] if len(sys.argv) > 2 else "+25Hz"
        rate  = sys.argv[3] if len(sys.argv) > 3 else "+18%"
        testar_voz(voz, pitch=pitch, rate=rate)
    else:
        menu_vozes()