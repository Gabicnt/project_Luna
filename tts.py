import subprocess
import os
import re

class TTSEngine:
    def __init__(self, voice="pt_BR-FranciscaNeural", pitch="+25Hz", rate="+18%"):
        self.voice = voice
        self.pitch = pitch
        self.rate = rate

    def _limpar_texto(self, texto):
        texto = re.sub(r'\*.*?\*', '', texto)
        texto = texto.split("MEMORIA:")[0].strip()
        if len(texto) > 400:
            texto = texto[:400] + "..."
        return texto

    def falar(self, texto):
        texto_limpo = self._limpar_texto(texto)
        if not texto_limpo:
            return

        wav_path = "/tmp/luna_fala.wav"
        
        cmd = [
            "edge-tts",
            "--voice", self.voice,
            "--text", texto_limpo,
            "--pitch", self.pitch,
            "--rate", self.rate,
            "--write-media", wav_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=15)
            if result.returncode == 0 and os.path.exists(wav_path):
                subprocess.run(["paplay", wav_path], capture_output=True, timeout=15)
                os.unlink(wav_path)
            else:
                print(f"[TTS] Erro: {result.stderr.decode()}")
        except Exception as e:
            print(f"[TTS] Erro: {e}")

    def parar(self):
        subprocess.run(["pkill", "-f", "paplay"], capture_output=True)