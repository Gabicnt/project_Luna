#!/usr/bin/env python3
"""
Alma da Luna – Autonomia, necessidades e ações espontâneas.
Usa APScheduler para executar um loop de background a cada 15 minutos.
"""

import random
import subprocess
import os
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler


class Alma:
    def __init__(self, personalidade_engine, sistema_module, tts_engine=None, luna_corpo=None):
        """
        personalidade_engine: instância de personalidade.Personalidade
        sistema_module: módulo sistema (para sensores)
        tts_engine: instância de tts.TTSEngine (opcional, para fala espontânea)
        luna_corpo: instância de corpo.LunaCorpo (opcional, para animações)
        """
        self.personalidade = personalidade_engine
        self.sistema = sistema_module
        self.tts = tts_engine
        self.corpo = luna_corpo
        self.scheduler = BackgroundScheduler()

    def iniciar(self):
        """Inicia o agendador. Chame apenas uma vez, no main.py."""
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
        # Atualiza necessidades (fome, sono, tédio)
        self.personalidade.atualizar_necessidades(minutos_passados=15)

        # Obtém estado atual
        perfil = self.personalidade.perfil
        necessidades = perfil['necessidades']
        tedio = necessidades['tedio']
        humor = perfil['humor']

        # Decide se deve agir (probabilidade baseada no tédio)
        if random.randint(1, 100) <= tedio:
            self._executar_acao_espontanea()

    def _executar_acao_espontanea(self):
        """Realiza uma ação autônoma aleatória."""
        # Lista de ações possíveis (pesos e requisitos)
        acoes = [
            (self._falar_sozinha, 10),
            (self._criar_bilhete_escritorio, 8),
            (self._mudar_papel_parede, 5),
            (self._comentar_clima, 4),
            (self._dancar, 3),
            (self._auto_aprendizado, 2),
        ]

        # Filtra ações que requerem internet (opcional)
        # (neste momento, todas funcionam offline, exceto clima e auto-aprendizado)
        acoes_validas = [(acao, peso) for acao, peso in acoes if self._pode_executar(acao)]

        if not acoes_validas:
            return

        # Escolhe ação ponderada pelo peso
        acao = self._escolher_ponderada(acoes_validas)
        try:
            acao()
            # Pequeno ganho de XP por agir
            self.personalidade.adicionar_xp(2)
        except Exception as e:
            print(f"[Alma] Erro na ação autônoma: {e}")

    def _pode_executar(self, acao):
        """Verifica requisitos básicos para uma ação."""
        if acao == self._mudar_papel_parede:
            return os.path.exists(os.path.expanduser("~/Imagens/Wallpapers"))
        if acao == self._comentar_clima or acao == self._auto_aprendizado:
            # Precisa de internet; podemos verificar com ping ou assumir True, mas com fallback
            return self._tem_internet()
        return True

    def _tem_internet(self):
        """Verifica conectividade simples."""
        try:
            subprocess.run(['ping', '-c', '1', 'google.com'], capture_output=True, timeout=3)
            return True
        except Exception:
            return False

    def _escolher_ponderada(self, lista_acoes):
        """Escolhe uma ação aleatória ponderada pelos pesos."""
        total = sum(peso for _, peso in lista_acoes)
        r = random.uniform(0, total)
        acumulado = 0
        for acao, peso in lista_acoes:
            acumulado += peso
            if r <= acumulado:
                return acao
        return lista_acoes[-1][0]

    # ------------------------------------------------------------------
    # Ações autônomas concretas
    # ------------------------------------------------------------------
    def _falar_sozinha(self):
        """Fala uma frase espontânea se o TTS estiver disponível."""
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
        """Cria um arquivo Luna_aviso.txt na área de trabalho."""
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
        """Altera o papel de parede usando gsettings (GNOME)."""
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
        """Comenta sobre o clima (requer internet)."""
        # Simples: usa wttr.in
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
        """Toca uma musiquinha MIDI e animação de dança (placeholder)."""
        if self.corpo:
            self.corpo.feliz()
            self.corpo.mostrar_balao("♫ Dançando... Lalalá ♫", 4000)
        # Poderia tocar um arquivo .mid se tivesse, mas por enquanto só balão.

    def _auto_aprendizado(self):
        """Aprende algo novo da Wikipedia e salva no diário."""
        # Usa a API da Groq (LLM) para resumir ou só faz uma busca simples.
        # Para simplificar, vamos usar curl na Wikipedia em português.
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
                    # Salva no Obsidian (usando memoria, mas precisa de referência)
                    # Para não criar dependência circular, podemos salvar via personalidade
                    self.personalidade.aprender_conceito(titulo.lower(), resumo)
                    if self.corpo:
                        self.corpo.mostrar_balao(f"Aprendi sobre {titulo}! 📚", 5000)
        except Exception as e:
            print(f"[Alma] Erro no auto-aprendizado: {e}")