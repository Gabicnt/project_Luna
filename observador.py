#!/usr/bin/env python3
"""
Observador da Casa da Luna – Monitora o diretório ~/Casa_da_Luna/ usando Watchdog.
Detecta criação de arquivos em subpastas específicas (Presentes, Lembretes, Armario)
e gera eventos que são processados pelo loop principal no main.py.
"""

import os
import queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class CasaHandler(FileSystemEventHandler):
    """
    Manipulador de eventos do Watchdog.
    Reage apenas a arquivos criados (não diretórios) nas subpastas monitoradas.
    """

    def __init__(self, fila_comandos: queue.Queue):
        super().__init__()
        self.fila_comandos = fila_comandos

    def on_created(self, event):
        """Chamado quando um arquivo ou diretório é criado."""
        # Ignora diretórios
        if event.is_directory:
            return

        caminho = event.src_path
        pasta = os.path.dirname(caminho)
        nome = os.path.basename(caminho)

        # Detecta a subpasta afetada
        if pasta.endswith("Presentes"):
            mensagem = f"🎁 Oba! Ganhei um presente: {nome}!"
            self.fila_comandos.put({"acao": "presente", "texto": mensagem})
            print(f"[Casa] Presente detectado: {nome}")

        elif pasta.endswith("Lembretes"):
            mensagem = f"📌 Papai deixou um lembrete: {nome}. Vou ler!"
            self.fila_comandos.put({"acao": "lembrete", "texto": mensagem})
            print(f"[Casa] Lembrete detectado: {nome}")

        elif pasta.endswith("Armario"):
            mensagem = f"🗄️ Hmm, algo novo no armário: {nome}."
            self.fila_comandos.put({"acao": "item", "texto": mensagem})
            print(f"[Casa] Item no armário: {nome}")

        elif pasta.endswith("Mochila"):
            mensagem = f"🎒 Colocaram algo na minha mochila: {nome}!"
            self.fila_comandos.put({"acao": "item", "texto": mensagem})
            print(f"[Casa] Item na mochila: {nome}")

        elif pasta.endswith("Mesa"):
            mensagem = f"📄 Tem algo novo na minha mesa: {nome}."
            self.fila_comandos.put({"acao": "item", "texto": mensagem})
            print(f"[Casa] Item na mesa: {nome}")


class ObservadorCasa:
    """
    Inicia e gerencia o observador da Casa da Luna.
    Cria as subpastas automaticamente, se necessário.
    """

    def __init__(self, caminho: str = "~/Casa_da_Luna"):
        self.caminho = os.path.expanduser(caminho)
        self.fila_eventos = queue.Queue()
        self.observer = Observer()

    def iniciar(self):
        """Inicia o monitoramento da Casa."""
        # Garante que a casa e suas subpastas existam
        if not os.path.exists(self.caminho):
            os.makedirs(self.caminho)
            print(f"🏠 Criando a Casa da Luna em: {self.caminho}")

        subpastas = ["Armario", "Cama", "Mochila", "Mesa", "Lembretes", "Presentes"]
        for sub in subpastas:
            os.makedirs(os.path.join(self.caminho, sub), exist_ok=True)

        # Configura o manipulador e inicia o observador
        event_handler = CasaHandler(self.fila_eventos)
        self.observer.schedule(event_handler, self.caminho, recursive=True)
        self.observer.start()
        print(f"🏠 Observando a casa em: {self.caminho}")

    def parar(self):
        """Para o monitoramento da Casa."""
        self.observer.stop()
        self.observer.join()
        print("🏠 Observador da casa parado.")


# ==============================================================================
# Teste rápido
# ==============================================================================
if __name__ == "__main__":
    import time
    print("🧪 Testando o Observador da Casa...")
    print("   Coloque um arquivo em ~/Casa_da_Luna/Presentes/ para ver a reação.")
    obs = ObservadorCasa()
    obs.iniciar()
    try:
        while True:
            try:
                evento = obs.fila_eventos.get(timeout=1)
                print(f"Evento recebido: {evento}")
            except queue.Empty:
                pass
    except KeyboardInterrupt:
        print("\n👋 Encerrando teste.")
        obs.parar()