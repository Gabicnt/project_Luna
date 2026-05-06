#!/usr/bin/env python3
"""
Módulo de microfone da Luna.
Fornece a classe SpeechListener para captura de áudio e transcrição
usando a API gratuita do Google Speech Recognition.
"""

import speech_recognition as sr
from typing import Optional


class SpeechListener:
    """
    Gerencia a captura de áudio do microfone e a transcrição usando
    o reconhecimento de fala do Google (gratuito e rápido).

    Uso típico:
        listener = SpeechListener()
        texto = listener.ouvir_transcrever(timeout=5)
        if texto:
            print("Você disse:", texto)
    """

    def __init__(
        self,
        language: str = "pt-BR",
        device_index: Optional[int] = None
    ):
        """
        Inicializa o ouvinte.

        Parâmetros:
            language:      código do idioma (pt-BR, en-US etc.)
            device_index:  índice do microfone (None = padrão do sistema)
        """
        self.recognizer = sr.Recognizer()
        self.language = language
        self.device_index = device_index

        # Configura o microfone
        try:
            self.microfone = sr.Microphone(device_index=device_index)
        except OSError:
            # Fallback: tenta sem device_index
            self.microfone = sr.Microphone()

        # Calibra automaticamente para o ruído ambiente
        self._calibrar()

    # ------------------------------------------------------------------
    # Calibração
    # ------------------------------------------------------------------
    def _calibrar(self) -> None:
        """Ajusta o reconhecedor para o ruído ambiente."""
        print("🎤 Calibrando microfone... Por favor, fique em silêncio.")
        try:
            with self.microfone as source:
                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=1.0
                )
            print("✅ Microfone pronto!")
        except Exception as e:
            print(f"⚠️  Aviso na calibração: {e}")
            print("   Usando configuração padrão do microfone.")

    # ------------------------------------------------------------------
    # Captura e transcrição
    # ------------------------------------------------------------------
    def ouvir_transcrever(self, timeout: int = 5) -> Optional[str]:
        """
        Escuta o microfone e transcreve a fala.

        Parâmetros:
            timeout: segundos máximos de gravação

        Retorna:
            Texto transcrito, ou None se nada foi detectado ou houve erro.
        """
        with self.microfone as source:
            print("🎙️  Ouvindo...")
            try:
                audio = self.recognizer.listen(source, timeout=timeout)
                print("📝 Transcrevendo...")
                return self._transcrever_google(audio)
            except sr.WaitTimeoutError:
                print("⏰ Tempo esgotado (ninguém falou).")
                return None
            except Exception as e:
                print(f"❌ Erro na captura: {e}")
                return None

    def _transcrever_google(self, audio) -> Optional[str]:
        """Envia o áudio para o Google Speech-to-Text."""
        try:
            texto = self.recognizer.recognize_google(
                audio,
                language=self.language
            )
            return texto
        except sr.UnknownValueError:
            print("❓ Não entendi o que foi dito.")
            return None
        except sr.RequestError as e:
            print(f"🌐 Erro de rede na transcrição: {e}")
            return None

    # ------------------------------------------------------------------
    # Utilitários
    # ------------------------------------------------------------------
    @staticmethod
    def listar_dispositivos() -> list:
        """Lista os dispositivos de áudio disponíveis (para debug)."""
        dispositivos = []
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    dispositivos.append((i, info['name']))
            p.terminate()
        except Exception:
            pass
        return dispositivos


# ==============================================================================
# Teste rápido
# ==============================================================================
if __name__ == "__main__":
    print("🧪 Testando o SpeechListener...")
    print("Dispositivos disponíveis:")
    for idx, nome in SpeechListener.listar_dispositivos():
        print(f"  {idx}: {nome}")
    print()

    listener = SpeechListener()
    texto = listener.ouvir_transcrever(timeout=5)
    if texto:
        print(f"Você disse: {texto}")
    else:
        print("Falha na transcrição.")