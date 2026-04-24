#!/usr/bin/env python3
"""
Luna - IA pessoal completa com personalidade orgânica, voz, corpo, casa, ações autônomas
      e ALMA (autonomia, necessidades, XP, ações espontâneas).
A detecção de pedidos de ação é FEITA NATURALMENTE, sem comandos especiais.
Memória de curto prazo incluída para evitar perda de contexto.
"""

import sys
import signal
import re
import os
import queue
import time
import io
import warnings
from datetime import date
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Módulos da Luna
import config
import memoria
import groq_client
import tts
import microfone
import wakeword
import corpo
import sistema
import observador
import cerebro
import personalidade
import executor
import alma                                 # Fase 5 – Autonomia e vida

# ==============================================================================
# Silencia os irritantes avisos do ALSA/JACK (não afetam o funcionamento)
# ==============================================================================
warnings.filterwarnings("ignore")
os.environ["ALSA_LOG_LEVEL"] = "0"
os.environ["JACK_NO_START_SERVER"] = "1"

class FiltroStderr(io.StringIO):
    def write(self, s):
        if not any(x in s for x in [
            "ALSA", "jack", "Jack", "Cannot connect",
            "pcm_oss", "a52", "usb_stream", "pcm_dmix", "pcm_dsnoop"
        ]):
            sys.__stderr__.write(s)

sys.stderr = FiltroStderr()

# ==============================================================================
# Configurações e motores
# ==============================================================================
console = Console()
historico_conversa = []

tts_engine = tts.TTSEngine(
    voice="pt-BR-FranciscaNeural",
    pitch="+25Hz",
    rate="+18%"
)

microfone_engine = None
wakeword_engine = None
modo_voz = False

app_qt = None
luna_corpo = None
casa_engine = None
cerebro_engine = cerebro.CerebroOrganico()
personalidade_engine = personalidade.Personalidade()
executor_engine = executor.Executor()
alma_engine = None                       # Será iniciada após o corpo gráfico


# ==============================================================================
# Exibição e comandos especiais
# ==============================================================================
def exibir_luna(texto: str):
    console.print("Luna:", style="bold cyan")
    console.print(texto)
    console.print("---")


def processar_comando_especial(comando: str):
    global microfone_engine, wakeword_engine, modo_voz, casa_engine, alma_engine
    cmd = comando.strip().lower()

    if cmd == "/sair":
        console.print("Luna: Até logo! Vou guardar minhas memórias...")
        if historico_conversa:
            resumo = "Conversa do dia:\n" + "\n".join(historico_conversa[-10:])
            memoria.resumir_dia_e_salvar(resumo, emocao_dominante="feliz")
        if wakeword_engine:
            wakeword_engine.parar()
        if casa_engine:
            casa_engine.parar()
        if executor_engine:
            executor_engine.desligar()
        if alma_engine:
            alma_engine.parar()
        if luna_corpo:
            luna_corpo.close()
        return "/sair"

    elif cmd == "/memoria":
        arquivos = sorted(Path(config.DIARIO_DIR).glob("*.md"), reverse=True)[:5]
        if not arquivos:
            console.print("Luna: Ainda não escrevi nada no diário hoje.")
        else:
            for arq in arquivos:
                meta, corpo_mem = memoria.ler_memoria(str(arq))
                console.print(f"📅 {meta.get('date', arq.stem)}: {corpo_mem[:100]}...")
        return None

    elif cmd == "/sonhar":
        resumo = (
            "Resumo forçado pelo usuário:\n" +
            "\n".join(historico_conversa[-10:]) if historico_conversa
            else "Nada de especial hoje."
        )
        memoria.resumir_dia_e_salvar(resumo)
        console.print("Luna: Anotei tudinho no meu diário!")
        return None

    elif cmd == "/falar":
        if microfone_engine is None:
            console.print("🎤 Inicializando microfone...")
            microfone_engine = microfone.SpeechListener()
        if luna_corpo:
            luna_corpo.listening()
        console.print("🎙️ Pode falar! (5 segundos)")
        texto = microfone_engine.ouvir_transcrever(timeout=5)
        if texto:
            console.print(f"📝 Você disse: {texto}")
            return texto
        else:
            console.print("❌ Não entendi nada...")
            if luna_corpo:
                luna_corpo.idle()
            return None

    elif cmd == "/ouvir":
        if wakeword_engine is None:
            console.print("👂 Inicializando escuta contínua...")
            wakeword_engine = wakeword.WakeWordDetector()
            wakeword_engine.iniciar()
        modo_voz = True
        if luna_corpo:
            luna_corpo.idle()
        console.print("👂 Modo voz ativado! Fale 'Luna' para acordar. /texto para voltar.")
        return None

    elif cmd == "/texto":
        modo_voz = False
        console.print("⌨️ Modo teclado ativado.")
        return None

    elif cmd == "/balao":
        if luna_corpo:
            modo = luna_corpo._alternar_modo_fala()
            console.print(f"💬 Modo de fala: {modo}")
        return None

    elif cmd.startswith("/ensinar"):
        partes = comando[8:].strip().split(" ", 1)
        if len(partes) >= 2:
            nome = partes[0]
            descricao = partes[1]
            personalidade_engine.aprender_conceito(nome, descricao)
            console.print(f"📚 Luna aprendeu sobre '{nome}'!")
        else:
            console.print("❌ Use: /ensinar nome descrição")
        return None

    elif cmd == "/status":
        console.print(personalidade_engine.resumo())
        return None

    return None


# ==============================================================================
# Detecção orgânica de pedidos de ação
# ==============================================================================
def _parece_pedido_acao(texto: str) -> bool:
    """Verifica se o texto parece um pedido de ação (criar, listar, apagar, etc.)."""
    gatilhos = [
        "criar", "cria", "crie", "faça", "fazer", "escrever", "escreva",
        "listar", "lista", "liste", "mostrar", "mostra", "mostre",
        "apagar", "apaga", "apague", "deletar", "delete", "remover", "remova",
        "mover", "mova", "copiar", "copia", "copie",
        "renomear", "renomeia", "executar", "execute", "rodar", "roda",
        "abrir", "abra", "fechar", "feche",
        "criar arquivo", "criar pasta", "criar diretório",
        "salvar", "salve", "guardar", "guarde",
        "limpar", "limpe", "organizar", "organize",
        "baixar", "baixe", "download", "instalar", "instale",
        "área de trabalho", "desktop", "documentos", "downloads"
    ]
    texto_lower = texto.lower()
    for gatilho in gatilhos:
        if gatilho in texto_lower:
            return True
    return False


# ==============================================================================
# Construção de contexto de curto prazo (últimas 5 trocas)
# ==============================================================================
def _obter_contexto_recente() -> str:
    """Retorna as últimas falas da conversa para manter o contexto imediato."""
    if not historico_conversa:
        return ""
    recentes = historico_conversa[-6:]
    return "CONVERSA RECENTE:\n" + "\n".join(recentes)


# ==============================================================================
# Análise da entrada e resposta
# ==============================================================================
def deve_salvar_memoria(mensagem_usuario: str, resposta_llm: str) -> bool:
    texto = mensagem_usuario.lower()
    if any(p in texto for p in ["lembre-se", "anotar", "aprend", "guarde", "anota"]):
        return True
    if re.search(r"\b(\w+)\s+(é|são|=|significa)\s+(.+)", mensagem_usuario, re.IGNORECASE):
        return True
    return False


def aprender_conceito(entrada: str) -> bool:
    match = re.search(r"\b(\w+)\s+(é|são|=|significa)\s+(.+)", entrada, re.IGNORECASE)
    if match:
        conceito = match.group(1).strip().lower()
        explicacao = match.group(3).strip()
        memoria.salvar_memoria(
            titulo=conceito,
            conteudo=f"# {conceito}\n\n{explicacao}",
            tags=[conceito, "aprendizado"],
            emocao="curiosa",
            categoria="aprendizado"
        )
        personalidade_engine.aprender_conceito(conceito, explicacao)
        return True
    return False


def processar_entrada(texto: str):
    if not texto or not texto.strip():
        return None

    # ========================================================================
    # DETECÇÃO ORGÂNICA: se parece pedido de ação, usa o executor natural
    # ========================================================================
    if _parece_pedido_acao(texto):
        console.print("🔧 Deixa que eu faço isso pra você, papai...")
        resultado_acao = executor_engine.executar_natural(texto)

        historico_conversa.append(f"Usuário: {texto}")
        historico_conversa.append(f"Luna (ação): {resultado_acao}")

        exibir_luna(resultado_acao)

        if luna_corpo:
            luna_corpo.speaking()
            modo_fala = luna_corpo.get_modo_fala()
            if modo_fala == "balão":
                luna_corpo.mostrar_balao(resultado_acao, duracao=config.BALAO_DURACAO)
                console.print("💬 Balão...", style="yellow")
            if modo_fala == "voz":
                console.print("🔊 Falando...", style="yellow")
                tts_engine.falar(resultado_acao)
            QTimer.singleShot(500, luna_corpo.idle)
        else:
            console.print("🔊 Falando...", style="yellow")
            tts_engine.falar(resultado_acao)

        personalidade_engine.adicionar_xp(2)
        return resultado_acao

    # ========================================================================
    # CONVERSA NORMAL (não é pedido de ação)
    # ========================================================================
    personalidade_engine.registrar_interacao()
    historico_conversa.append(f"Usuário: {texto}")

    if luna_corpo:
        luna_corpo.thinking()

    prompt_base = personalidade_engine.gerar_prompt_base()
    contexto_mundo = personalidade_engine.gerar_contexto_mundo()
    contexto_mem = memoria.gerar_contexto_memoria(pergunta_atual=texto, qtd_entradas=5)
    contexto_sis = sistema.obter_contexto_sistema()
    contexto_recente = _obter_contexto_recente()

    prompt_completo = (
        prompt_base + "\n" +
        contexto_mundo + "\n" +
        "[CONTEXTO DA CONVERSA ATUAL]\n" + contexto_recente + "\n" +
        "[SISTEMA] " + contexto_sis
    )

    mensagens = groq_client.montar_mensagens(
        entrada_usuario=texto,
        contexto_memoria=contexto_mem,
        prompt_personalizado=prompt_completo
    )

    try:
        resposta = groq_client.consultar_groq(mensagens)
    except Exception as e:
        console.print(f"❌ Erro na LLM: {e}", style="red")
        if luna_corpo:
            luna_corpo.triste()
            QTimer.singleShot(3000, luna_corpo.idle)
        return "Desculpe, estou com dor de cabeça digital..."

    historico_conversa.append(f"Luna: {resposta}")
    exibir_luna(resposta)

    if cerebro_engine:
        acao = cerebro_engine.analisar_e_executar(resposta)
        if acao:
            console.print(f"🧠 Ação autônoma: {acao}")
            if luna_corpo:
                luna_corpo.feliz()
                luna_corpo.mostrar_balao(acao, duracao=5000)

    if luna_corpo:
        luna_corpo.speaking()
        modo_fala = luna_corpo.get_modo_fala()
        if modo_fala == "balão":
            luna_corpo.mostrar_balao(resposta, duracao=config.BALAO_DURACAO)
            console.print("💬 Balão...", style="yellow")
        if modo_fala == "voz":
            console.print("🔊 Falando...", style="yellow")
            tts_engine.falar(resposta)
        QTimer.singleShot(500, luna_corpo.idle)
    else:
        console.print("🔊 Falando...", style="yellow")
        tts_engine.falar(resposta)

    if wakeword_engine and modo_voz:
        wakeword_engine.pausar(3)

    if deve_salvar_memoria(texto, resposta):
        if not aprender_conceito(texto):
            memoria.salvar_memoria(
                titulo=f"lembrete_{date.today().isoformat()}_{len(historico_conversa)}",
                conteudo=f"Usuário: {texto}\n\nLuna: {resposta}",
                tags=["lembrete"],
                emocao="atenta",
                categoria=None
            )
            if luna_corpo:
                luna_corpo.feliz()
                QTimer.singleShot(2000, luna_corpo.idle)

    personalidade_engine.adicionar_xp(1)
    return resposta


# ==============================================================================
# Loop principal
# ==============================================================================
def main():
    global wakeword_engine, microfone_engine, modo_voz
    global app_qt, luna_corpo, casa_engine, alma_engine

    console.print("[bold cyan]🌟 Luna acordou![/bold cyan]")
    console.print("📋 Comandos: /falar | /ouvir | /texto | /balao | /ensinar | /status | /memoria | /sonhar | /sair")
    console.print("💡 Também pode pedir ações: 'crie um arquivo', 'liste a Mesa', 'apague o recado'...")
    console.print("=" * 50)

    app_qt = QApplication.instance()
    if app_qt is None:
        app_qt = QApplication(sys.argv)
    luna_corpo = corpo.LunaCorpo()
    luna_corpo.show()
    console.print("🎨 Corpo gráfico iniciado!")

    casa_engine = observador.ObservadorCasa()
    casa_engine.iniciar()
    console.print("🏠 Casa da Luna monitorada!")

    # Inicializa a Alma (autonomia, necessidades, ações espontâneas)
    alma_engine = alma.Alma(
        personalidade_engine=personalidade_engine,
        sistema_module=sistema,
        tts_engine=tts_engine,
        luna_corpo=luna_corpo
    )
    alma_engine.iniciar()
    console.print("🌟 Alma da Luna despertou!")

    def handler_sigint(sig, frame):
        console.print("\nLuna: Você está me fechando... Vou guardar minhas lembranças.")
        if historico_conversa:
            resumo = "Conversa interrompida:\n" + "\n".join(historico_conversa[-10:])
            memoria.resumir_dia_e_salvar(resumo, emocao_dominante="surpresa")
        if wakeword_engine:
            wakeword_engine.parar()
        if casa_engine:
            casa_engine.parar()
        if executor_engine:
            executor_engine.desligar()
        if alma_engine:
            alma_engine.parar()
        if luna_corpo:
            luna_corpo.close()
        sys.exit(0)
    signal.signal(signal.SIGINT, handler_sigint)

    while True:
        try:
            app_qt.processEvents()

            if casa_engine and not casa_engine.fila_eventos.empty():
                evento = casa_engine.fila_eventos.get()
                acao = evento.get("acao")
                texto_evento = evento.get("texto", "")
                if acao in ("presente", "lembrete", "item"):
                    nome_item = texto_evento.split(":")[-1].strip().rstrip("!")
                    personalidade_engine.receber_presente(nome_item)
                    if luna_corpo:
                        luna_corpo.feliz()
                        luna_corpo.mostrar_balao(texto_evento, duracao=6000)
                        console.print(f"🏠 {texto_evento}")

            if modo_voz and wakeword_engine and not wakeword_engine.fila_comandos.empty():
                try:
                    entrada = wakeword_engine.fila_comandos.get(timeout=0.5)
                    console.print(f"🎤 Você disse: {entrada}")
                    processar_entrada(entrada)
                    continue
                except queue.Empty:
                    pass

            if modo_voz:
                time.sleep(0.3)
                continue

            entrada = Prompt.ask("🧑 Você")

        except EOFError:
            break

        if not entrada.strip():
            continue

        if entrada.startswith("/"):
            resultado = processar_comando_especial(entrada)
            if resultado == "/sair":
                break
            elif resultado:
                processar_entrada(resultado)
            continue

        processar_entrada(entrada)


if __name__ == "__main__":
    main()