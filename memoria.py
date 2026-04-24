import os
import re
from datetime import date
from pathlib import Path
from typing import List, Tuple, Optional
import config

# Mapeamento de categorias e palavras-chave
CATEGORIAS = {
    "gostos": {
        "pasta": "Gostos",
        "palavras": ["gosto", "gosta", "comida", "bebida", "favorito", "prefere", "adoro", "odeio", "amo", "batata", "pizza", "doce", "salgado"]
    },
    "aprendizado": {
        "pasta": "Aprendizado",
        "palavras": ["aprend", "ensinar", "significa", "é", "são", "sabe", "conhece", "explica"]
    },
    "pessoas": {
        "pasta": "Pessoas",
        "palavras": ["quem", "pessoa", "amigo", "família", "conhece", "nome"]
    },
    "memorias": {
        "pasta": "Memorias",
        "palavras": ["lembra", "memória", "aconteceu", "evento", "dia", "quando", "história"]
    },
    "sistema": {
        "pasta": "Sistema",
        "palavras": ["humor", "status", "cansada", "feliz", "triste"]
    }
}

def _extrair_frontmatter_e_conteudo(texto: str) -> Tuple[dict, str]:
    meta = {}
    conteudo = texto
    if texto.startswith("---"):
        partes = texto.split("---", 2)
        if len(partes) >= 3:
            cabecalho = partes[1]
            conteudo = partes[2].strip()
            for linha in cabecalho.strip().split("\n"):
                if ":" in linha:
                    chave, valor = linha.split(":", 1)
                    meta[chave.strip()] = valor.strip()
    return meta, conteudo

def _criar_frontmatter(meta: dict) -> str:
    linhas = ["---"]
    for chave, valor in meta.items():
        linhas.append(f"{chave}: {valor}")
    linhas.append("---")
    return "\n".join(linhas)

def _criar_pasta_categoria(categoria: str) -> str:
    """Retorna o caminho da pasta da categoria, cria se não existir."""
    pasta = os.path.join(config.VAULT_PATH, categoria)
    os.makedirs(pasta, exist_ok=True)
    return pasta

def _normalizar_categoria(categoria: str) -> str:
    if not categoria:
        return "aprendizado"
    categoria = categoria.lower().strip()
    if categoria not in CATEGORIAS:
        return "aprendizado"
    return categoria

def _detectar_categoria(texto: str) -> str:
    texto_lower = texto.lower()
    for cat, info in CATEGORIAS.items():
        for palavra in info["palavras"]:
            if palavra in texto_lower:
                return cat
    return "aprendizado"

def _criar_links_entre_notas(titulo: str, categoria: str, conteudo: str):
    try:
        categoria = _normalizar_categoria(categoria)
        pasta_info = CATEGORIAS[categoria]
        pasta_nome = pasta_info["pasta"]
        
        inicio_path = os.path.join(config.VAULT_PATH, "🏠 Início.md")
        link_nota = f"[[{pasta_nome}/{titulo}|{titulo}]]"
        
        if not os.path.exists(inicio_path):
            with open(inicio_path, "w", encoding="utf-8") as f:
                f.write("# 🏠 Casa da Luna\n\nBem-vindo ao meu diário digital!\n\n")
                f.write("## 📂 Categorias\n\n")
                for cat, info in CATEGORIAS.items():
                    f.write(f"- [[{info['pasta']}|{info['pasta']}]]\n")
        
        pasta_path = _criar_pasta_categoria(pasta_nome)
        
        categoria_readme = os.path.join(pasta_path, "README.md")
        if not os.path.exists(categoria_readme):
            with open(categoria_readme, "w", encoding="utf-8") as f:
                f.write(f"# {pasta_nome}\n\n")
        
        with open(categoria_readme, "a", encoding="utf-8") as f:
            f.write(f"- {link_nota}\n")
    except Exception as e:
        print(f"[Memória] Aviso ao criar links: {e}")

def salvar_memoria(titulo: str, conteudo: str, tags: Optional[List[str]] = None,
                   emocao: Optional[str] = None, categoria: Optional[str] = None) -> str:
    if categoria is None:
        categoria = _detectar_categoria(conteudo)
    
    categoria = _normalizar_categoria(categoria)
    
    pasta_categoria = CATEGORIAS[categoria]["pasta"]
    diretorio = _criar_pasta_categoria(pasta_categoria)
    
    nome_arquivo = f"{titulo.lower().replace(' ', '_')}.md"
    caminho_completo = os.path.join(diretorio, nome_arquivo)
    
    meta = {
        "date": date.today().isoformat(),
        "tags": ", ".join(tags) if tags else categoria,
        "emocao": emocao or "neutra",
        "categoria": categoria
    }
    frontmatter = _criar_frontmatter(meta)
    
    links = ""
    if categoria == "gostos":
        links = "\nRelacionado: [[Pessoas/Papai|Papai]]"
    elif categoria == "aprendizado":
        links = "\nRelacionado: [[🏠 Início|Início]]"
    
    texto_completo = f"{frontmatter}\n\n# {titulo}\n\n{conteudo}{links}\n"
    
    with open(caminho_completo, "w", encoding="utf-8") as f:
        f.write(texto_completo)
    
    _criar_links_entre_notas(titulo, categoria, conteudo)
    
    return caminho_completo

def ler_memoria(caminho_arquivo: str) -> Tuple[dict, str]:
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        texto = f.read()
    return _extrair_frontmatter_e_conteudo(texto)

def buscar_na_categoria(termo: str, categoria: str = None, limite: int = 3) -> List[Tuple[str, str, dict]]:
    if categoria is None:
        categoria = _detectar_categoria(termo)
    
    categoria = _normalizar_categoria(categoria)
    
    pasta_categoria = CATEGORIAS[categoria]["pasta"]
    diretorio = os.path.join(config.VAULT_PATH, pasta_categoria)
    
    if not os.path.exists(diretorio):
        return []
    
    resultados = []
    termo_lower = termo.lower()
    
    for arquivo in Path(diretorio).rglob("*.md"):
        if arquivo.name == "README.md":
            continue
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                conteudo = f.read()
            meta, corpo = _extrair_frontmatter_e_conteudo(conteudo)
            if termo_lower in arquivo.stem.lower() or termo_lower in corpo.lower():
                trecho = corpo[:300].replace("\n", " ")
                resultados.append((str(arquivo), trecho, meta))
                if len(resultados) >= limite:
                    break
        except Exception:
            continue
    return resultados

def gerar_contexto_memoria(pergunta_atual: str = "", qtd_entradas: int = 5) -> str:
    trechos = []
    
    if pergunta_atual:
        categoria = _detectar_categoria(pergunta_atual)
        categoria = _normalizar_categoria(categoria)
        resultados = buscar_na_categoria(pergunta_atual, categoria, limite=2)
        for arq, trecho, meta in resultados:
            trechos.append(f"[{categoria}] {trecho}")
    
    diario_path = Path(config.DIARIO_DIR)
    if diario_path.exists():
        for arq in sorted(diario_path.glob("*.md"), reverse=True)[:2]:
            try:
                meta, corpo = ler_memoria(str(arq))
                data = meta.get("date", arq.stem)
                trechos.append(f"[Diário {data}] {corpo[:150]}")
            except Exception:
                continue
    
    if trechos:
        return "Memórias relevantes:\n" + "\n".join(trechos)
    return ""

def resumir_dia_e_salvar(conversa_do_dia: str, emocao_dominante: str = "neutra"):
    hoje = date.today().isoformat()
    meta = {
        "date": hoje,
        "tags": "diario, resumo",
        "emocao": emocao_dominante
    }
    frontmatter = _criar_frontmatter(meta)
    
    links = ""
    for cat, info in CATEGORIAS.items():
        for palavra in info["palavras"]:
            if palavra in conversa_do_dia.lower():
                links += f"\n- [[{info['pasta']}|{info['pasta']}]]"
                break
    
    conteudo = f"# Resumo do dia {hoje}\n\n{conversa_do_dia}\n\n## Categorias mencionadas{links}\n"
    caminho = os.path.join(config.DIARIO_DIR, f"{hoje}.md")
    
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(f"{frontmatter}\n\n{conteudo}\n")