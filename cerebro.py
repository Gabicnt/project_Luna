#!/usr/bin/env python3
"""
Cérebro Orgânico da Luna – Módulo de Ações Autônomas (Skills/Tools).
Analisa as respostas da Luna e executa ações no sistema (ex.: criar arquivos,
mover itens na Casa, etc.) de forma automática, sem comandos explícitos.
"""

import os
import re
from datetime import datetime
from pathlib import Path


class CerebroOrganico:
    """
    Detecta intenções nas falas da Luna e as transforma em ações reais
    no sistema de arquivos da Casa_da_Luna.

    Funcionamento:
    1. A resposta da LLM é analisada em busca de palavras-chave que indiquem
       vontade de "guardar", "anotar", "escrever", "salvar".
    2. Se a intenção é detectada, o conteúdo relevante é extraído e salvo
       como um arquivo Markdown na pasta adequada da Casa.
    3. Outras intenções podem ser adicionadas futuramente (ex.: mover, apagar,
       criar lembretes, etc.).
    """

    def __init__(self, caminho_casa: str = "~/Casa_da_Luna"):
        self.caminho_casa = os.path.expanduser(caminho_casa)
        # Garante que as subpastas principais existam
        for sub in ["Mesa", "Armario", "Mochila", "Lembretes", "Presentes"]:
            os.makedirs(os.path.join(self.caminho_casa, sub), exist_ok=True)

    # ------------------------------------------------------------------
    # Análise principal
    # ------------------------------------------------------------------

    def analisar_e_executar(self, texto_resposta: str) -> str | None:
        """
        Examina o texto da resposta da Luna.
        Se detectar intenção de guardar/anotar/criar, executa a ação
        e retorna uma mensagem de confirmação. Caso contrário, retorna None.
        """
        if not texto_resposta:
            return None

        texto = texto_resposta.strip()
        texto_lower = texto.lower()

        # Intenção: guardar / anotar / escrever / criar / salvar
        if self._tem_intencao_guardar(texto_lower):
            conteudo = self._extrair_conteudo_util(texto)
            destino = self._detectar_local(texto_lower)
            nome_arquivo = self._gerar_nome_arquivo()
            self._criar_arquivo(nome_arquivo, conteudo, destino)
            return f"📄 Prontinho, papai! Guardei isso no/a {destino}."

        # Intenção: "vou lembrar disso" → cria lembrete
        if self._tem_intencao_lembrete(texto_lower):
            conteudo = self._extrair_conteudo_util(texto)
            nome_arquivo = f"lembrete_{self._timestamp()}.txt"
            self._criar_arquivo(nome_arquivo, conteudo, "Lembretes")
            return "📌 Tá lembrado, papai! Deixei nos seus Lembretes."

        # Nenhuma ação detectada
        return None

    # ------------------------------------------------------------------
    # Detectores de intenção
    # ------------------------------------------------------------------

    def _tem_intencao_guardar(self, texto: str) -> bool:
        """Verifica se o texto indica vontade de guardar algo."""
        gatilhos = [
            "guardar", "vou guardar", "guardei", "anotar", "vou anotar",
            "escrever", "vou escrever", "escrevi", "criar", "vou criar",
            "salvar", "vou salvar", "salvei", "registrar", "vou registrar"
        ]
        return any(g in texto for g in gatilhos)

    def _tem_intencao_lembrete(self, texto: str) -> bool:
        """Verifica se o texto indica vontade de criar um lembrete."""
        gatilhos = [
            "vou lembrar", "vou me lembrar", "lembrete", "não vou esquecer",
            "vou anotar pra lembrar", "marcar"
        ]
        return any(g in texto for g in gatilhos)

    # ------------------------------------------------------------------
    # Extração de conteúdo e destino
    # ------------------------------------------------------------------

    def _extrair_conteudo_util(self, texto: str) -> str:
        """
        Tenta extrair a parte principal do texto, removendo frases
        puramente introdutórias.
        """
        # Remove frases curtas de confirmação no início
        padroes_inicio = [
            r"^(tá|ok|prontinho|claro|sim|claro que sim|oba)[,!\s]+",
            r"^(vou guardar|vou anotar|vou escrever|vou salvar|vou criar)[,:\s]*",
        ]
        for padrao in padroes_inicio:
            texto = re.sub(padrao, "", texto, flags=re.IGNORECASE).strip()

        return texto if texto else "Nova anotação da Luna."

    def _detectar_local(self, texto: str) -> str:
        """Identifica onde a Luna quer guardar o arquivo."""
        if any(p in texto for p in ["mesa", "mesinha"]):
            return "Mesa"
        if any(p in texto for p in ["armário", "armario", "guardar"]):
            return "Armario"
        if any(p in texto for p in ["mochila", "mochilinha"]):
            return "Mochila"
        if any(p in texto for p in ["lembrete", "lembretes"]):
            return "Lembretes"
        return "Mesa"  # padrão

    # ------------------------------------------------------------------
    # Criação do arquivo
    # ------------------------------------------------------------------

    def _criar_arquivo(self, nome: str, conteudo: str, pasta: str):
        """Cria um arquivo Markdown na subpasta especificada."""
        caminho_pasta = os.path.join(self.caminho_casa, pasta)
        os.makedirs(caminho_pasta, exist_ok=True)

        caminho_arquivo = os.path.join(caminho_pasta, nome)

        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write(f"# {nome.replace('.md', '').replace('_', ' ').title()}\n\n")
            f.write(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
            f.write(conteudo)

        print(f"[Cérebro] Arquivo criado: {caminho_arquivo}")

    # ------------------------------------------------------------------
    # Utilitários
    # ------------------------------------------------------------------

    def _gerar_nome_arquivo(self) -> str:
        """Gera um nome único para o arquivo."""
        return f"anotacao_{self._timestamp()}.md"

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# ==============================================================================
# Teste rápido (executar diretamente)
# ==============================================================================
if __name__ == "__main__":
    cerebro = CerebroOrganico()
    
    print("🧠 Teste do Cérebro Orgânico\n")
    
    # Teste 1: intenção de guardar
    resposta1 = "Claro, papai! Vou guardar essa história pra você. Era uma vez um coelhinho..."
    resultado1 = cerebro.analisar_e_executar(resposta1)
    print(f"Resposta: {resposta1}")
    print(f"Ação: {resultado1}\n")
    
    # Teste 2: intenção de lembrete
    resposta2 = "Pode deixar! Vou lembrar disso. Comprar pão amanhã cedo."
    resultado2 = cerebro.analisar_e_executar(resposta2)
    print(f"Resposta: {resposta2}")
    print(f"Ação: {resultado2}\n")
    
    # Teste 3: sem intenção
    resposta3 = "Oi, papai! Tô feliz hoje!"
    resultado3 = cerebro.analisar_e_executar(resposta3)
    print(f"Resposta: {resposta3}")
    print(f"Ação: {resultado3}")