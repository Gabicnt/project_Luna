#!/usr/bin/env python3
"""
Executor Natural da Luna (v2 - com contexto espacial).
Traduz pedidos em linguagem natural para comandos shell, agora entendendo
quando o papai quer algo fora da Casa (ex: "na minha área de trabalho").
"""

import os
import subprocess
import threading
import re
from groq import Groq
import config

class Executor:
    def __init__(self, sandbox_path: str = "~/Casa_da_Luna"):
        self.sandbox = os.path.expanduser(sandbox_path)
        os.makedirs(self.sandbox, exist_ok=True)
        self.cliente = Groq(api_key=config.GROQ_API_KEY)

    def executar_natural(self, pedido: str) -> str:
        """
        Traduz um pedido em linguagem natural para um comando shell,
        escolhe o local correto (sandbox ou área de trabalho) e executa.
        """
        # 1. Decide se é uma tarefa dentro ou fora da casa
        local_alvo = self._detectar_local(pedido)
        
        # 2. Traduz o pedido em comando shell
        comando = self._traduzir_para_comando(pedido, local_alvo)
        if not comando:
            return "Desculpe, papai. Não entendi o que você quer que eu faça."

        print(f"[Executor] Comando traduzido: {comando}")

        # 3. Executar o comando
        resultado = self._executar_comando(comando, local_alvo)

        # 4. Traduzir o resultado para linguagem natural
        resposta_natural = self._traduzir_resultado(pedido, resultado, local_alvo)
        return resposta_natural

    def _detectar_local(self, pedido: str) -> str:
        """Detecta se o pedido é para a área de trabalho, documentos, etc."""
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
            return self.sandbox  # Padrão: casa da Luna

    def _traduzir_para_comando(self, pedido: str, local_alvo: str) -> str | None:
        """Usa a LLM para converter linguagem natural em comando shell."""
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
        """Executa um comando shell no local correto."""
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
        """Usa a LLM para converter o resultado em uma frase natural."""
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

    def desligar(self):
        pass