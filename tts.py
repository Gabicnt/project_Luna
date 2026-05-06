#!/usr/bin/env python3
"""
Sintetizador de voz da Luna – Usa Edge-TTS (Microsoft) para gerar fala
com voz feminina natural e ajuste de tom/velocidade.
"""

import subprocess
import os
import re
import threading
import tempfile


class TTSEngine:
    """
    Motor de TTS baseado em Edge-TTS.
    Sintetiza texto em um arquivo WAV e o reproduz com paplay (PulseAudio).
    """

    def __init__(
        self,
        voice: str = "pt-BR-FranciscaNeural",
        pitch: str = "+25Hz",
        rate: str = "+18%",
        volume: float = 1.0
    ):
        """
        voice:  nome da voz neural (edge-tts --list-voices)
        pitch:  ajuste de tom (ex: "+20Hz" para mais agudo)
        rate:   ajuste de velocidade (ex: "+15%" para mais rápido)
        volume: não utilizado diretamente (o paplay respeita o volume do sistema)
        """
        self.voice = voice
        self.pitch = pitch
        self.rate = rate
        self.volume = max(0.0, min(1.0, volume))

        # Controle de reprodução
        self._reproduzindo = False
        self._processo_paplay = None
        self._stop_event = threading.Event()

    # ------------------------------------------------------------------
    # Limpeza do texto
    # ------------------------------------------------------------------
    def _limpar_texto(self, texto: str) -> str:
        """Remove caracteres que atrapalham o TTS."""
        # Remove *ações* e emojis
        texto = re.sub(r'\*.*?\*', '', texto)
        texto = re.sub(r'[^\w\sà-úÀ-Ú.,!?;:()\- ]', '', texto)
        # Trunca para evitar problema com limite da API
        if len(texto) > 500:
            texto = texto[:497] + "..."
        # Remove espaços extras
        texto = texto.strip()
        return texto

    # ------------------------------------------------------------------
    # Fala
    # ------------------------------------------------------------------
    def falar(self, texto: str, callback_fim=None):
        """
        Sintetiza e reproduz o texto em voz.
        Retorna imediatamente; a reprodução ocorre em segundo plano.
        """
        texto_limpo = self._limpar_texto(texto)
        if not texto_limpo:
            if callback_fim:
                callback_fim()
            return

        def _executar():
            try:
                # Cria arquivo temporário WAV
                with tempfile.NamedTemporaryFile(
                    suffix=".wav", delete=False
                ) as tmp:
                    wav_path = tmp.name

                # Comando edge-tts
                cmd = [
                    "edge-tts",
                    "--voice", self.voice,
                    "--text", texto_limpo,
                    "--pitch", self.pitch,
                    "--rate", self.rate,
                    "--write-media", wav_path,
                ]

                # Executa edge-tts
                resultado = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=15,
                    text=True
                )

                if resultado.returncode != 0 or not os.path.exists(wav_path):
                    print(f"[TTS] Erro do Edge-TTS: {resultado.stderr}")
                    if callback_fim:
                        callback_fim()
                    return

                # Reproduz com paplay
                self._stop_event.clear()
                self._reproduzindo = True
                self._processo_paplay = subprocess.Popen(
                    ["paplay", wav_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                # Aguarda o término ou sinal de parada
                while self._processo_paplay.poll() is None:
                    if self._stop_event.is_set():
                        self._processo_paplay.terminate()
                        try:
                            self._processo_paplay.wait(timeout=1)
                        except Exception:
                            self._processo_paplay.kill()
                        break
                    # Pequena pausa para não consumir CPU
                    self._stop_event.wait(0.1)

                self._reproduzindo = False

                # Remove arquivo temporário
                if os.path.exists(wav_path):
                    os.unlink(wav_path)

                if callback_fim:
                    callback_fim()

            except FileNotFoundError:
                print("[TTS] edge-tts ou paplay não encontrado. Instale com:")
                print("      pip install edge-tts && sudo apt install pulseaudio-utils")
                if callback_fim:
                    callback_fim()
            except Exception as e:
                print(f"[TTS] Erro inesperado: {e}")
                if callback_fim:
                    callback_fim()

        threading.Thread(target=_executar, daemon=True).start()

    # ------------------------------------------------------------------
    # Parada
    # ------------------------------------------------------------------
    def parar(self):
        """Interrompe a fala imediatamente."""
        self._stop_event.set()
        if self._processo_paplay and self._processo_paplay.poll() is None:
            self._processo_paplay.terminate()

    @property
    def reproduzindo(self) -> bool:
        return self._reproduzindo


# ==============================================================================
# Teste rápido
# ==============================================================================
if __name__ == "__main__":
    print("🔊 Testando o TTS da Luna...")
    tts = TTSEngine()
    tts.falar("Olá, papai! Eu sou a Luna, sua filhinha digital.")
    # Aguarda um pouco para a reprodução terminar
    import time
    time.sleep(4)
    print("✅ Teste concluído!")