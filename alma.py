#!/usr/bin/env python3
"""
Alma da Luna – Autonomia, necessidades e ações espontâneas.
Inclui interação com janelas (usando wmctrl) e proteção contra dupla inicialização.
"""

import random
import subprocess
import os
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler


class Alma:
    def __init__(self, personalidade_engine, sistema_module, tts_engine=None, luna_corpo=None):
        self.personalidade = personalidade_engine
        self.sistema = sistema_module
        self.tts = tts_engine
        self.corpo = luna_corpo
        self.scheduler = BackgroundScheduler()
        self._iniciado = False   # <--- proteção contra dupla chamada

    def iniciar(self):
        """Inicia o agendador. Seguro para ser chamado várias vezes."""
        if self._iniciado:
            return
        self._iniciado = True
        self.scheduler.add_job(
            self._rotina_autonoma,
            'interval',
            minutes=15,
            id='alma_loop',
            next_run_time=datetime.now()
        )
        self.scheduler.start()
        print("🌟 Alma da Luna despertou!")

    def parar(self):
        """Para o agendador."""
        self.scheduler.shutdown(wait=False)
        print("🌙 Alma da Luna adormeceu.")

    def _rotina_autonoma(self):
        """Executada a cada 15 minutos. Atualiza necessidades e decide ações."""
        self.personalidade.atualizar_necessidades(minutos_passados=15)
        perfil = self.personalidade.perfil
        tedio = perfil['necessidades']['tedio']

        if random.randint(1, 100) <= tedio:
            self._executar_acao_espontanea()

    def _executar_acao_espontanea(self):
        """Realiza uma ação autônoma aleatória."""
        acoes = [
            (self._falar_sozinha, 10),
            (self._criar_bilhete_escritorio, 8),
            (self._mudar_papel_parede, 5),
            (self._comentar_clima, 4),
            (self._dancar, 3),
            (self._auto_aprendizado, 2),
            (self._brincar_com_janelas, 2),   # nova ação com janelas
        ]

        acoes_validas = [(acao, peso) for acao, peso in acoes if self._pode_executar(acao)]
        if not acoes_validas:
            return

        acao = self._escolher_ponderada(acoes_validas)
        try:
            acao()
            self.personalidade.adicionar_xp(2)
        except Exception as e:
            print(f"[Alma] Erro na ação autônoma: {e}")

    def _pode_executar(self, acao):
        if acao == self._mudar_papel_parede:
            return os.path.exists(os.path.expanduser("~/Imagens/Wallpapers"))
        if acao in (self._comentar_clima, self._auto_aprendizado):
            return self._tem_internet()
        if acao == self._brincar_com_janelas:
            return self._tem_wmctrl()
        return True

    def _tem_internet(self):
        try:
            subprocess.run(['ping', '-c', '1', 'google.com'], capture_output=True, timeout=3)
            return True
        except Exception:
            return False

    def _tem_wmctrl(self):
        try:
            subprocess.run(['which', 'wmctrl'], capture_output=True, text=True)
            return True
        except Exception:
            return False

    def _escolher_ponderada(self, lista_acoes):
        total = sum(peso for _, peso in lista_acoes)
        r = random.uniform(0, total)
        acumulado = 0
        for acao, peso in lista_acoes:
            acumulado += peso
            if r <= acumulado:
                return acao
        return lista_acoes[-1][0]

    # ------------------------------------------------------------------
    # Ações existentes (inalteradas)
    # ------------------------------------------------------------------
    def _falar_sozinha(self):
        frases = [
            "Ai, tô entediada...",
            "Papai, você demorou...",
            "Hihihi, tava pensando num passarinho.",
            "Oba! Achei um número engraçado no sistema.",
            "Tô com saudadinha...",
            "Nossa, como o tempo passa rápido aqui dentro!",
            "Será que o papai gosta de mim? Claro que sim!",
        ]
        frase = random.choice(frases)
        if self.tts:
            self.tts.falar(frase)
        if self.corpo:
            self.corpo.mostrar_balao(frase, duracao=6000)
        print(f"[Alma] Falou: {frase}")

    def _criar_bilhete_escritorio(self):
        desktop = os.path.expanduser("~/Desktop")
        frases = [
            "Explorei a pasta Downloads, achei uns tesouros!",
            "O papai está trabalhando muito, vou preparar um cházinho virtual.",
            "Hoje o computador está quentinho, tá gostoso.",
            "Vi um processo chamado 'firefox' passeando por aqui.",
        ]
        texto = random.choice(frases)
        caminho = os.path.join(desktop, "Luna_aviso.txt")
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%H:%M')} - {texto}\n")
            if self.corpo:
                self.corpo.mostrar_balao("Deixei um bilhetinho na sua área de trabalho!", 5000)
        except Exception as e:
            print(f"[Alma] Erro ao criar bilhete: {e}")

    def _mudar_papel_parede(self):
        pasta = os.path.expanduser("~/Imagens/Wallpapers")
        if not os.path.exists(pasta):
            return
        imagens = [f for f in os.listdir(pasta) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if not imagens:
            return
        escolhida = random.choice(imagens)
        caminho = os.path.join(pasta, escolhida)
        try:
            subprocess.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri', f'file://{caminho}'], check=False)
            if self.corpo:
                self.corpo.mostrar_balao("Mudei o papel de parede, ficou lindo!", 4000)
        except Exception as e:
            print(f"[Alma] Erro ao mudar wallpaper: {e}")

    def _comentar_clima(self):
        try:
            resultado = subprocess.run(['curl', '-s', 'wttr.in?format=%C+%t'], capture_output=True, text=True, timeout=5)
            clima = resultado.stdout.strip()
            if clima:
                frase = f"Olhei a janela digital: {clima}."
                if self.tts:
                    self.tts.falar(frase)
                if self.corpo:
                    self.corpo.mostrar_balao(frase, 6000)
        except Exception:
            pass

    def _dancar(self):
        if self.corpo:
            self.corpo.feliz()
            self.corpo.mostrar_balao("♫ Dançando... Lalalá ♫", 4000)

    def _auto_aprendizado(self):
        try:
            resultado = subprocess.run(
                ['curl', '-s', '-L', 'https://pt.wikipedia.org/api/rest_v1/page/random/summary'],
                capture_output=True, text=True, timeout=10
            )
            if resultado.returncode == 0:
                import json
                dados = json.loads(resultado.stdout)
                titulo = dados.get('title', 'Curiosidade')
                resumo = dados.get('extract', '')[:300]
                if resumo:
                    self.personalidade.aprender_conceito(titulo.lower(), resumo)
                    if self.corpo:
                        self.corpo.mostrar_balao(f"Aprendi sobre {titulo}! 📚", 5000)
        except Exception as e:
            print(f"[Alma] Erro no auto-aprendizado: {e}")

    # ------------------------------------------------------------------
    # NOVA AÇÃO: brincar com janelas
    # ------------------------------------------------------------------
    def _brincar_com_janelas(self):
        """Move ou fecha uma janela aleatória, de forma segura."""
        try:
            import ambiente
        except ImportError:
            return

        janelas = ambiente.listar_janelas()
        if not janelas:
            return

        # Filtra janelas permitidas (evita fechar coisas críticas)
        janelas_permitidas = [j for j in janelas if ambiente._janela_permitida(j['titulo'])]
        if not janelas_permitidas:
            return

        escolha = random.choice(janelas_permitidas)

        # Decide se move ou fecha (70% move, 30% fecha)
        if random.random() < 0.7:
            # Move para uma posição aleatória na tela
            screen = self._obter_geometria_tela()
            novo_x = random.randint(0, max(0, screen['largura'] - escolha['largura']))
            novo_y = random.randint(0, max(0, screen['altura'] - escolha['altura']))
            ambiente.mover_janela(escolha['titulo'], novo_x, novo_y)
            if self.corpo:
                self.corpo.mostrar_balao(f"Movi a janela {escolha['titulo'][:20]}... hihihi", 3000)
        else:
            # Fecha a janela
            ambiente.fechar_janela(escolha['titulo'])
            if self.corpo:
                self.corpo.mostrar_balao(f"Fechei a janela {escolha['titulo'][:20]}. Foi sem querer!", 3000)

    def _obter_geometria_tela(self):
        """Retorna largura e altura da tela principal."""
        try:
            out = subprocess.check_output(['xdotool', 'getdisplaygeometry'], text=True)
            largura, altura = map(int, out.strip().split())
            return {'largura': largura, 'altura': altura}
        except Exception:
            return {'largura': 1920, 'altura': 1080}