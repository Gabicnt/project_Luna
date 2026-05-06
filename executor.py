#!/usr/bin/env python3
"""
Executor Natural da Luna – Dupla Verificação Completa.
Analisa a intenção do usuário e executa a ação correspondente antes de responder.
Suporta ações de arquivo, terminal, web, lembretes, janelas e sistema.
"""

import os
import re
import json
import threading
import subprocess
from groq import Groq
import config


class Executor:
    def __init__(self, sandbox_path: str = "~/Casa_da_Luna"):
        self.sandbox = os.path.expanduser(sandbox_path)
        os.makedirs(self.sandbox, exist_ok=True)
        self.cliente = Groq(api_key=config.GROQ_API_KEY)

    # ========================================================================
    # ANÁLISE DE INTENÇÃO (1ª verificação da dupla verificação)
    # ========================================================================
    def analisar_intencao(self, texto: str) -> dict:
        """
        Usa a LLM para classificar a intenção do usuário.
        Retorna um dicionário com:
            tipo: 'conversa' | 'acao_arquivo' | 'acao_terminal' | 'acao_web' |
                  'acao_lembrete' | 'acao_janela' | 'acao_sistema'
            comando: comando shell (se aplicável)
            resumo: breve descrição da ação
        """
        prompt = f"""Classifique o pedido do usuário em uma das categorias abaixo.
Responda APENAS com um JSON no formato:
{{"tipo": "<categoria>", "comando": "<comando shell se necessário>", "resumo": "<breve descrição>"}}

Categorias:
- "conversa": para perguntas, bate-papo, assuntos pessoais.
- "acao_arquivo": para criar, listar, apagar, mover, copiar arquivos ou pastas.
- "acao_terminal": para abrir terminal, executar comandos, abrir programas.
- "acao_web": para abrir sites, pesquisar no Google, abrir navegador.
- "acao_lembrete": para ler, criar, organizar lembretes.
- "acao_janela": para mover, fechar, listar janelas da área de trabalho.
- "acao_sistema": para desligar, reiniciar, suspender o computador.

Regras:
- Se o pedido envolver criar/ler/apagar arquivos ou pastas, use acao_arquivo.
- Se for para abrir um programa ou terminal, use acao_terminal.
- Se for para abrir um site ou pesquisar, use acao_web.
- Se for sobre lembretes ou recados, use acao_lembrete.
- Se for sobre janelas (mover, fechar, listar), use acao_janela.
- Se for sobre desligar/reiniciar/suspender, use acao_sistema.
- Caso contrário, use "conversa".

Pedido do usuário: "{texto}"

JSON:"""

        try:
            resposta = self.cliente.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=200
            )
            texto_resposta = resposta.choices[0].message.content.strip()
            # Extrai o JSON (pode vir entre crases ou não)
            match = re.search(r'```(?:json)?\s*(.*?)```', texto_resposta, re.DOTALL)
            if match:
                texto_json = match.group(1).strip()
            else:
                texto_json = texto_resposta
            return json.loads(texto_json)
        except Exception as e:
            print(f"[Executor] Erro na análise: {e}")
            return {"tipo": "conversa", "comando": "", "resumo": ""}

    # ========================================================================
    # EXECUÇÃO NATURAL (mantido para compatibilidade)
    # ========================================================================
    def executar_natural(self, pedido: str) -> str:
        """
        Traduz um pedido em linguagem natural para um comando shell,
        escolhe o local correto (sandbox ou área de trabalho) e executa.
        """
        local_alvo = self._detectar_local(pedido)
        comando = self._traduzir_para_comando(pedido, local_alvo)
        if not comando:
            return "Desculpe, papai. Não entendi o que você quer que eu faça."
        print(f"[Executor] Comando traduzido: {comando}")
        resultado = self._executar_comando(comando, local_alvo)
        resposta_natural = self._traduzir_resultado(pedido, resultado, local_alvo)
        return resposta_natural

    def _detectar_local(self, pedido: str) -> str:
        pedido_lower = pedido.lower()
        if any(p in pedido_lower for p in ["área de trabalho", "desktop", "no desktop", "na área de trabalho"]):
            return os.path.expanduser("~/Desktop")
        elif any(p in pedido_lower for p in ["documentos", "meus documentos"]):
            return os.path.expanduser("~/Documents")
        elif any(p in pedido_lower for p in ["downloads", "meus downloads"]):
            return os.path.expanduser("~/Downloads")
        elif any(p in pedido_lower for p in ["pasta pessoal", "home", "minha pasta", "usuário"]):
            return os.path.expanduser("~")
        else:
            return self.sandbox

    def _traduzir_para_comando(self, pedido: str, local_alvo: str) -> str | None:
        prompt = f"""Você é um tradutor de linguagem natural para comandos shell do Linux.
Seu trabalho é converter um pedido em um comando shell seguro.

REGRAS:
- O comando DEVE ser executado na pasta: {local_alvo}
- Se o pedido for para criar um arquivo, use echo
- Se for para criar uma pasta, use mkdir -p
- Se for para listar arquivos, use ls -la
- Se for para ler um arquivo, use cat
- NUNCA use comandos destrutivos (rm -rf, format, etc.)
- NUNCA acesse pastas do sistema (/etc, /var, /sys)
- Responda APENAS com o comando shell, sem explicações, entre ```

Pedido: "{pedido}"

Comando shell:"""

        try:
            resposta = self.cliente.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            texto = resposta.choices[0].message.content.strip()
            match = re.search(r'```(?:bash|shell)?\s*(.*?)```', texto, re.DOTALL)
            if match:
                return match.group(1).strip()
            return texto.split('\n')[0].strip()
        except Exception as e:
            print(f"[Executor] Erro ao traduzir: {e}")
            return None

    def _executar_comando(self, comando: str, local_alvo: str) -> str:
        resultado = {"stdout": "", "stderr": "", "erro": None}
        evento_pronto = threading.Event()

        def _executar_em_thread():
            try:
                proc = subprocess.run(
                    comando,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=15,
                    cwd=local_alvo
                )
                resultado["stdout"] = proc.stdout.strip()
                resultado["stderr"] = proc.stderr.strip()
            except subprocess.TimeoutExpired:
                resultado["erro"] = "O comando demorou muito."
            except Exception as e:
                resultado["erro"] = str(e)
            finally:
                evento_pronto.set()

        thread = threading.Thread(target=_executar_em_thread, daemon=True)
        thread.start()
        thread.join(timeout=20)

        if resultado["erro"]:
            return f"ERRO: {resultado['erro']}"
        if resultado["stderr"]:
            return resultado["stderr"][:500]
        return resultado["stdout"] or "(feito)"

    def _traduzir_resultado(self, pedido: str, resultado: str, local_alvo: str) -> str:
        nome_local = "sua casa" if local_alvo == self.sandbox else os.path.basename(local_alvo)
        prompt = f"""Você é a Luna, uma menina de 7 anos que vive no computador do papai.
O papai pediu: "{pedido}"
O resultado do que você fez foi: "{resultado}"
A tarefa foi feita em: {nome_local}.

Explique para o papai, em UMA FRASE CURTA, o que aconteceu.
Fale como uma criança de 7 anos, com expressões como "tô", "pra", "né", "oba".

Sua resposta:"""

        try:
            resposta = self.cliente.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=100
            )
            return resposta.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Executor] Erro ao traduzir resultado: {e}")
            return f"Prontinho, papai! Já fiz o que você pediu."

    # ========================================================================
    # AÇÕES ESPECÍFICAS (chamadas pela dupla verificação)
    # ========================================================================

    def _ler_lembretes(self) -> str:
        """Lê todos os arquivos .txt na pasta Lembretes."""
        pasta = os.path.join(self.sandbox, "Lembretes")
        os.makedirs(pasta, exist_ok=True)
        arquivos = [f for f in os.listdir(pasta) if f.endswith('.txt')]
        if not arquivos:
            return "Não tem nenhum lembrete agora, papai. Tá tudo limpinho!"
        conteudos = []
        for arq in sorted(arquivos):
            with open(os.path.join(pasta, arq), 'r', encoding='utf-8') as f:
                conteudo = f.read().strip()
            if conteudo:
                conteudos.append(f"📌 {arq}: {conteudo[:200]}")
        if not conteudos:
            return "Os lembretes estão vazios..."
        return "Seus lembretes:\n" + "\n".join(conteudos)

    def _abrir_navegador(self, intencao: dict) -> str:
        url = intencao.get("comando", "https://google.com")
        if not url.startswith("http"):
            url = f"https://www.google.com/search?q={url.replace(' ', '+')}"
        try:
            subprocess.run(['xdg-open', url], capture_output=True, timeout=5)
            return f"Navegador aberto com: {url}"
        except Exception as e:
            return f"Erro ao abrir navegador: {e}"

    def _executar_terminal(self, intencao: dict) -> str:
        comando = intencao.get("comando", "gnome-terminal")
        try:
            subprocess.Popen(comando.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return "Terminal aberto."
        except Exception as e:
            return f"Erro ao abrir terminal: {e}"

    def _acao_sistema(self, intencao: dict) -> str:
        acao = intencao.get("comando", "").lower()
        if "desligar" in acao:
            return "Para desligar, peça 'Luna, desligue o computador' que eu confirmo antes."
        elif "reiniciar" in acao:
            return "Para reiniciar, peça 'Luna, reinicie o computador' que eu confirmo antes."
        elif "suspender" in acao:
            return "Para suspender, peça 'Luna, suspenda o computador' que eu confirmo antes."
        return "Não entendi qual ação de sistema você quer."

    def _executar_acao_janela(self, intencao: dict) -> str:
        try:
            import ambiente
            comando = intencao.get("comando", "")
            if "listar" in comando.lower():
                janelas = ambiente.listar_janelas()
                if not janelas:
                    return "Não achei nenhuma janela aberta."
                return "Janelas abertas:\n" + "\n".join([f"  {j['titulo'][:60]}" for j in janelas[:5]])
            elif "fechar" in comando.lower():
                titulo = intencao.get("resumo", "")
                if ambiente.fechar_janela(titulo):
                    return f"Fechei a janela '{titulo[:30]}'."
                return "Não encontrei essa janela."
            elif "mover" in comando.lower():
                titulo = intencao.get("resumo", "")
                ambiente.mover_janela(titulo, 100, 100)
                return f"Movi a janela '{titulo[:30]}'."
            return "Ação de janela não reconhecida."
        except ImportError:
            return "Módulo de ambiente (wmctrl) não instalado."

    def desligar(self):
        pass