#!/usr/bin/env python3
"""
Módulo de Interação com a Área de Trabalho.
Permite que a Luna controle janelas do sistema.
"""
import subprocess
import re

def listar_janelas() -> list[dict]:
    """Retorna lista de janelas abertas (id, título, pid, geometria)."""
    try:
        saída = subprocess.check_output(['wmctrl', '-lG'], text=True)
    except Exception:
        return []
    janelas = []
    for linha in saída.strip().split('\n'):
        cols = linha.split(None, 7)
        if len(cols) >= 8:
            janela = {
                'id': cols[0],
                'x': int(cols[2]),
                'y': int(cols[3]),
                'largura': int(cols[4]),
                'altura': int(cols[5]),
                'titulo': cols[7]
            }
            janelas.append(janela)
    return janelas

def mover_janela(titulo_parcial: str, x: int = None, y: int = None) -> bool:
    """Move a janela cujo título contém 'titulo_parcial' para as coordenadas dadas."""
    janelas = listar_janelas()
    for j in janelas:
        if titulo_parcial.lower() in j['titulo'].lower():
            cmd = ['wmctrl', '-r', j['titulo'], '-e', f'0,{x},{y},-1,-1']
            subprocess.run(cmd)
            return True
    return False

def fechar_janela(titulo_parcial: str) -> bool:
    """Fecha a janela que casar com o título parcial."""
    janelas = listar_janelas()
    for j in janelas:
        if titulo_parcial.lower() in j['titulo'].lower():
            subprocess.run(['wmctrl', '-c', j['titulo']])
            return True
    return False