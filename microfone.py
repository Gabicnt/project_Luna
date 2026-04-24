import speech_recognition as sr

class SpeechListener:
    def __init__(self, language="pt-BR"):
        self.recognizer = sr.Recognizer()
        self.microfone = sr.Microphone()
        self.language = language
        
        # Ajusta automaticamente para o ruído ambiente ao iniciar
        print("🎤 Calibrando microfone... Por favor, fique em silêncio.")
        with self.microfone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Microfone pronto!")

    def ouvir_transcrever(self, timeout=5):
        """
        Escuta o microfone e transcreve usando o Google.
        Retorna o texto ou None se não entender.
        """
        with self.microfone as source:
            print("🎙️ Ouvindo...")
            try:
                # Escuta até o tempo limite
                audio = self.recognizer.listen(source, timeout=timeout)
                print("📝 Transcrevendo...")
                texto = self.recognizer.recognize_google(audio, language=self.language)
                return texto
            except sr.WaitTimeoutError:
                print("⏰ Tempo esgotado.")
                return None
            except sr.UnknownValueError:
                print("❓ Não entendi o que foi dito.")
                return None
            except sr.RequestError as e:
                print(f"🌐 Erro de conexão com o serviço: {e}")
                return None

# Um pequeno teste para rodar diretamente
if __name__ == "__main__":
    print("🧪 Testando o novo SpeechListener...")
    listener = SpeechListener()
    texto = listener.ouvir_transcrever(timeout=5)
    if texto:
        print(f"Você disse: {texto}")
    else:
        print("Falha na transcrição.")