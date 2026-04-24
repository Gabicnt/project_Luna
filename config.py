#!/usr/bin/env python3
"""
Configuração centralizada da Luna.
Carrega variáveis do arquivo .env e disponibiliza caminhos e constantes
para todos os módulos do projeto.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# ----------------------------------------------------------------------
# 1. Carregar o arquivo .env
# ----------------------------------------------------------------------
load_dotenv()

# ----------------------------------------------------------------------
# 2. API da Groq
# ----------------------------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError(
        "❌ GROQ_API_KEY não definida no arquivo .env.\n"
        "   Crie um arquivo .env com: GROQ_API_KEY=sua_chave_aqui"
    )

MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")

# ----------------------------------------------------------------------
# 3. Caminhos do Obsidian (memória de longo prazo)
# ----------------------------------------------------------------------
VAULT_PATH = os.path.expanduser(
    os.getenv("VAULT_PATH", "~/Obsidian/Luna")
)

# Subpastas do vault
DIARIO_DIR      = os.path.join(VAULT_PATH, "Diario")
APRENDIZADO_DIR = os.path.join(VAULT_PATH, "Aprendizado")
MEMORIAS_DIR    = os.path.join(VAULT_PATH, "Memorias")
PESSOAS_DIR     = os.path.join(VAULT_PATH, "Pessoas")
GOSTOS_DIR      = os.path.join(VAULT_PATH, "Gostos")
SISTEMA_DIR     = os.path.join(VAULT_PATH, "Sistema")

# ----------------------------------------------------------------------
# 4. Caminho da Casa da Luna (necessidades, perfil, ações)
# ----------------------------------------------------------------------
CASA_PATH = os.path.expanduser(
    os.getenv("CASA_PATH", "~/Casa_da_Luna")
)

# Subpastas da casa
CASA_ARMARIO    = os.path.join(CASA_PATH, "Armario")
CASA_CAMA       = os.path.join(CASA_PATH, "Cama")
CASA_MOCHILA    = os.path.join(CASA_PATH, "Mochila")
CASA_MESA       = os.path.join(CASA_PATH, "Mesa")
CASA_LEMBRETES  = os.path.join(CASA_PATH, "Lembretes")
CASA_PRESENTES  = os.path.join(CASA_PATH, "Presentes")

# Arquivos importantes
PERFIL_FILE     = os.path.join(CASA_PATH, "perfil.json")
STATUS_FILE     = os.path.join(CASA_PATH, "status.json")
CAMA_STATUS     = os.path.join(CASA_CAMA, "cama.status")

# ----------------------------------------------------------------------
# 5. Arquivos do projeto
# ----------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.absolute()
SPRITES_DIR  = os.path.join(PROJECT_ROOT, "sprites")
VOICES_DIR   = os.path.join(PROJECT_ROOT, "voices")

# ----------------------------------------------------------------------
# 6. Criação automática de diretórios essenciais
# ----------------------------------------------------------------------
def _criar_diretorios():
    """Garante que todos os diretórios necessários existam."""
    diretorios = [
        # Obsidian
        VAULT_PATH, DIARIO_DIR, APRENDIZADO_DIR, MEMORIAS_DIR,
        PESSOAS_DIR, GOSTOS_DIR, SISTEMA_DIR,
        # Casa
        CASA_PATH, CASA_ARMARIO, CASA_CAMA, CASA_MOCHILA,
        CASA_MESA, CASA_LEMBRETES, CASA_PRESENTES,
        # Sprites
        SPRITES_DIR,
    ]
    for d in diretorios:
        os.makedirs(d, exist_ok=True)

_criar_diretorios()

# ----------------------------------------------------------------------
# 7. Constantes de comportamento
# ----------------------------------------------------------------------
# Temperatura da LLM (criatividade vs. precisão)
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.5"))

# Máximo de tokens por resposta
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1024"))

# Tempo (em segundos) que o balão de diálogo permanece visível
BALAO_DURACAO = int(os.getenv("BALAO_DURACAO", "8000"))

# Modo de fala padrão ("voz" ou "balao")
FALA_PADRAO = os.getenv("FALA_PADRAO", "balao")

# Tempo de escuta do microfone (segundos)
MIC_TIMEOUT = int(os.getenv("MIC_TIMEOUT", "5"))

# ----------------------------------------------------------------------
# 8. Exibição amigável ao iniciar
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print("🧩 Configuração da Luna carregada com sucesso!")
    print(f"   🔑 API Key: {'✅' if GROQ_API_KEY else '❌'}")
    print(f"   🧠 Modelo: {MODEL_NAME}")
    print(f"   📁 Vault Obsidian: {VAULT_PATH}")
    print(f"   🏠 Casa da Luna: {CASA_PATH}")
    print(f"   🎨 Sprites: {SPRITES_DIR}")
    print(f"   🔊 Vozes: {VOICES_DIR}")
    print(f"   🌡️ Temperatura LLM: {LLM_TEMPERATURE}")
    print(f"   💬 Modo de fala padrão: {FALA_PADRAO}")