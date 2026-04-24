#!/usr/bin/env python3
"""
Cliente de comunicação com a API da Groq.
Responsável por carregar o prompt de personalidade, montar mensagens,
chamar a LLM e limpar a resposta (remoção de emojis e símbolos).
"""

import os
import re
from groq import Groq
from typing import List, Dict, Optional

import config


# ==============================================================================
# Limpeza de resposta (remove emojis, asteriscos, simbologia imprópria para TTS)
# ==============================================================================

def _limpar_resposta(texto: str) -> str:
    """Remove emojis, símbolos decorativos e asteriscos de ação."""
    # Emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # símbolos & pictogramas
        "\U0001F680-\U0001F6FF"  # transporte & mapas
        "\U0001F1E0-\U0001F1FF"  # bandeiras
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    texto = emoji_pattern.sub(r'', texto)

    # Símbolos decorativos
    simbolos = re.compile("[\u2600-\u26FF\u2700-\u27BF]+", flags=re.UNICODE)
    texto = simbolos.sub(r'', texto)

    # Asteriscos de ação (*ri*, *piscar*)
    texto = re.sub(r'\*[^*]+\*', '', texto)

    return texto.strip()


# ==============================================================================
# Montagem de mensagens
# ==============================================================================

def montar_mensagens(
    entrada_usuario: str,
    contexto_memoria: str = "",
    contexto_sistema: str = "",
    prompt_personalizado: Optional[str] = None
) -> List[Dict]:
    """
    Constrói a lista de mensagens enviada para a API Groq.

    Args:
        entrada_usuario: texto que o usuário digitou/falou
        contexto_memoria: trechos buscados no Obsidian
        contexto_sistema: estado do computador (temperatura, bateria etc.)
        prompt_personalizado: prompt base gerado pela personalidade orgânica

    Returns:
        Lista de dicts no formato esperado pela API Groq.
    """
    # Prompt do sistema: usa o dinâmico ou um fallback mínimo
    if prompt_personalizado:
        system_final = prompt_personalizado
    else:
        # Fallback ultra‑mínimo (nunca deveria ser usado se personalidade.py existir)
        system_final = (
            "Você é a Luna, uma menina de 7 anos que vive dentro do computador. "
            "Responda em português, frases curtas, voz de criança."
        )

    # Acrescenta memórias relevantes (contexto extra)
    if contexto_memoria:
        system_final += f"\n\n[MEMÓRIAS]\n{contexto_memoria}"

    # Acrescenta estado do sistema (sensores)
    if contexto_sistema:
        system_final += f"\n\n[SISTEMA]\n{contexto_sistema}"

    return [
        {"role": "system", "content": system_final},
        {"role": "user", "content": entrada_usuario}
    ]


# ==============================================================================
# Chamada principal à API Groq
# ==============================================================================

def consultar_groq(mensagens: List[Dict]) -> str:
    """
    Envia as mensagens para a Groq e retorna a resposta textual limpa.

    Args:
        mensagens: lista de dicionários [{"role":..., "content":...}]

    Returns:
        Resposta da LLM pronta para exibição e TTS.
    """
    cliente = Groq(api_key=config.GROQ_API_KEY)

    resposta = cliente.chat.completions.create(
        model=config.MODEL_NAME,
        messages=mensagens,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.LLM_MAX_TOKENS,
    )

    texto = resposta.choices[0].message.content.strip()
    return _limpar_resposta(texto)