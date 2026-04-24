#!/usr/bin/env python3
"""
Wake Word Detector – Escuta continuamente a palavra "Luna" e,
ao detectar, captura o comando seguinte e o coloca numa fila.
Utiliza o SpeechListener (Google Speech-to-Text) para transcrição.
"""

import threading
import queue
import time
from microfone import SpeechListener


class WakeWordDetector:
    """
    Fica em loop ouvindo o microfone. Quando a palavra de ativação
    ("Luna" ou variações) é reconhecida, grava o comando seguinte
    e o disponibiliza na fila `fila_comandos`.
    """

    def __init__(self):
        # O mesmo listener usado no módulo microfone
        self.listener = SpeechListener()
        self.evento_acordar = threading.Event()
        self.fila_comandos = queue.Queue()
        self._executando = False
        self._thread = None
        self._pausa_apos_fala = False      # pausa temporária após Luna falar

    # ------------------------------------------------------------------
    # Controle de ciclo de vida
    # ------------------------------------------------------------------
    def iniciar(self):
        """Inicia a escuta em uma thread separada."""
        self._executando = True
        self._thread = threading.Thread(target=self._loop_escuta, daemon=True)
        self._thread.start()
        print("👂 Aguardando 'Luna'...")

    def parar(self):
        """Encerra a thread de escuta."""
        self._executando = False
        self.evento_acordar.set()          # libera qualquer wait

    def pausar(self, segundos: float = 3.0):
        """
        Pausa a escuta por alguns segundos (ex.: enquanto a Luna fala)
        para evitar que a própria voz da assistente ative o wake word.
        """
        self._pausa_apos_fala = True
        time.sleep(segundos)
        self._pausa_apos_fala = False

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------
    def _loop_escuta(self):
        """Fica ouvindo até o wake word ser detectado."""
        while self._executando:
            try:
                # Respeita pausa após fala
                if self._pausa_apos_fala:
                    time.sleep(0.5)
                    continue

                # Escuta um trecho curto (~4s de timeout)
                texto = self.listener.ouvir_transcrever(timeout=4)

                if not texto or len(texto) < 2:
                    continue

                texto_limpo = texto.lower().strip()
                print(f"🎤 Ouvi: {texto_limpo}")

                # Verifica se é a wake word
                if self._eh_wake_word(texto_limpo):
                    print("🌟 Luna acordou!")
                    self.evento_acordar.set()
                    self._ouvir_comando()

            except Exception as e:
                print(f"[WakeWord] Erro no loop: {e}")
                time.sleep(1)

    # ------------------------------------------------------------------
    # Verificação da wake word
    # ------------------------------------------------------------------
    def _eh_wake_word(self, texto: str) -> bool:
        """Retorna True se o texto contém a palavra de ativação."""
        wake_words = [
            "luna", "luna!", "ei luna", "ei luna!", "hey luna",
            "olá luna", "ola luna", "acorda luna", "luna acorda",
            "e aí luna", "e ai luna", "ó luna", "oh luna",
            "luna,"  # se a frase começar com "Luna, ..."
        ]
        for w in wake_words:
            if texto == w or texto.startswith(w):
                return True
        # Também aceita se a primeira palavra for "luna"
        primeira_palavra = texto.split()[0] if texto else ""
        return primeira_palavra.rstrip(",!?") == "luna"

    # ------------------------------------------------------------------
    # Captura do comando após wake word
    # ------------------------------------------------------------------
    def _ouvir_comando(self):
        """Após acordar, escuta o comando do papai."""
        print("🎙️  Pode falar! (7 segundos)")
        time.sleep(0.3)                    # pequeno delay para transição

        # Tenta até 3 vezes
        for tentativa in range(3):
            texto = self.listener.ouvir_transcrever(timeout=7)
            if texto and len(texto) > 2 and not self._eh_wake_word(texto):
                self.fila_comandos.put(texto)
                print(f"📝 Comando: {texto}")
                self.evento_acordar.clear()
                return
            print(f"⏰ Tentativa {tentativa+1} falhou, tentando de novo...")

        print("❌ Não entendi o comando.")
        self.evento_acordar.clear()


# ==============================================================================
# Teste rápido (executar diretamente)
# ==============================================================================
if __name__ == "__main__":
    print("🧪 Testando Wake Word 'Luna'...")
    print("   Fale 'Luna' e depois um comando.")
    print("   Pressione Ctrl+C para sair.\n")

    detector = WakeWordDetector()
    detector.iniciar()

    try:
        while True:
            detector.evento_acordar.wait(timeout=1)
            if detector.evento_acordar.is_set():
                try:
                    comando = detector.fila_comandos.get(timeout=5)
                    print(f"\n✅ Comando recebido: {comando}")
                    print("👂 Voltando a ouvir 'Luna'...\n")
                except queue.Empty:
                    pass
    except KeyboardInterrupt:
        print("\n👋 Até mais!")
        detector.parar()