#!/usr/bin/env python3
"""
Corpo Gráfico da Luna – Janela transparente com mascote animado (sprites PNG)
e balão de diálogo. Suporte a arrasto, gravidade e menu de contexto.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QMenu
from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, pyqtSignal
)
from PyQt6.QtGui import QPixmap, QPainter, QColor, QAction, QFont
from enum import Enum


class Estado(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    FELIZ = "feliz"
    DORMINDO = "dormindo"
    TRISTE = "triste"


class LunaCorpo(QWidget):
    """Janela flutuante que representa o corpo da Luna na área de trabalho."""

    # Sinais emitidos para o main.py
    clique_simples = pyqtSignal()
    clique_duplo = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.estado_atual = Estado.IDLE
        self.frame_idx = 0
        self.arrastando = False
        self.drag_pos = QPoint()
        self.sprites = {}
        self.usar_sprites = False
        self.modo_balão = True          # True = balão, False = fala por voz

        # ---- configurações da janela ----
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(250, 280)

        # ---- label do sprite (personagem) ----
        self.label = QLabel(self)
        self.label.setGeometry(25, 80, 200, 200)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ---- label do balão de fala ----
        self.balao = QLabel(self)
        self.balao.setGeometry(10, 5, 230, 70)
        self.balao.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.balao.setWordWrap(True)
        self.balao.setFont(QFont("Sans", 10))
        self.balao.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px solid #FFB6C1;
                border-radius: 15px;
                padding: 8px;
                font-size: 11px;
                color: #333;
            }
        """)
        self.balao.setVisible(False)

        # ---- timer da animação ----
        self.timer = QTimer()
        self.timer.timeout.connect(self._proximo_frame)
        self.timer.start(400)

        # ---- menu de contexto (botão direito) ----
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._menu_contexto)

        # ---- carrega sprites PNG, se existirem ----
        self._carregar_sprites()
        self._posicionar_canto()
        self._desenhar_estado()
        self.show()

    # ========================================================================
    #  SPRITES
    # ========================================================================

    def _carregar_sprites(self):
        base = os.path.join(os.path.dirname(__file__), "sprites")
        if not os.path.exists(base):
            print("🎨 Pasta sprites/ não encontrada. Usando desenhos padrão.")
            return

        for estado in Estado:
            pasta = os.path.join(base, estado.value)
            if os.path.exists(pasta):
                frames = []
                for i in range(4):
                    caminho = os.path.join(pasta, f"frame_{i}.png")
                    if os.path.exists(caminho):
                        pixmap = QPixmap(caminho)
                        if not pixmap.isNull():
                            frames.append(pixmap)
                if len(frames) >= 2:
                    self.sprites[estado] = frames
                    print(f"🎨 {estado.value}: {len(frames)} frames carregados")
        if self.sprites:
            self.usar_sprites = True
            print(f"✅ {len(self.sprites)} estados com sprites PNG!")
        else:
            print("🎨 Nenhum sprite PNG. Usando desenhos padrão.")

    # ========================================================================
    #  POSICIONAMENTO E REDERIZAÇÃO
    # ========================================================================

    def _posicionar_canto(self):
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - 270
        y = screen.height() - 310
        self.move(x, y)

    def _proximo_frame(self):
        self.frame_idx = (self.frame_idx + 1) % 4
        self._desenhar_estado()

    def _desenhar_estado(self):
        if self.usar_sprites and self.estado_atual in self.sprites:
            frames = self.sprites[self.estado_atual]
            frame = frames[self.frame_idx % len(frames)]
            self.label.setPixmap(
                frame.scaled(
                    200, 200,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
        else:
            pixmap = QPixmap(200, 200)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self._desenhar_fallback(painter)
            painter.end()
            self.label.setPixmap(pixmap)

    # ========================================================================
    #  FALLBACK – DESENHOS PADRÃO
    # ========================================================================

    def _desenhar_fallback(self, p):
        estados = {
            Estado.IDLE: self._desenhar_idle,
            Estado.LISTENING: self._desenhar_listening,
            Estado.THINKING: self._desenhar_thinking,
            Estado.SPEAKING: self._desenhar_speaking,
            Estado.FELIZ: self._desenhar_feliz,
            Estado.DORMINDO: self._desenhar_dormindo,
            Estado.TRISTE: self._desenhar_triste,
        }
        desenho = estados.get(self.estado_atual, self._desenhar_idle)
        desenho(p)

    def _base_corpo(self, p, cor_corpo=(255, 182, 193)):
        p.setBrush(QColor(*cor_corpo))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(30, 30, 140, 140)
        p.setBrush(QColor(255, 255, 255))
        p.drawEllipse(65, 75, 25, 25)
        p.drawEllipse(110, 75, 25, 25)
        p.setBrush(QColor(0, 0, 0))
        if self.frame_idx % 2 == 0:
            p.drawEllipse(72, 82, 10, 10)
            p.drawEllipse(117, 82, 10, 10)

    def _desenhar_idle(self, p):
        self._base_corpo(p)
        p.setPen(QColor(0, 0, 0))
        p.drawArc(75, 110, 50, 20, 0, -180 * 16)

    def _desenhar_listening(self, p):
        self._base_corpo(p)
        p.setBrush(QColor(255, 255, 255))
        p.drawEllipse(60, 70, 30, 30)
        p.drawEllipse(110, 70, 30, 30)
        p.setBrush(QColor(0, 0, 0))
        p.drawEllipse(70, 80, 12, 12)
        p.drawEllipse(118, 80, 12, 12)

    def _desenhar_thinking(self, p):
        self._base_corpo(p)
        p.setBrush(QColor(255, 255, 255))
        p.drawEllipse(65, 65, 25, 25)
        p.drawEllipse(110, 65, 25, 25)
        p.setBrush(QColor(0, 0, 0))
        p.drawEllipse(72, 70, 8, 8)
        p.drawEllipse(117, 70, 8, 8)

    def _desenhar_speaking(self, p):
        self._base_corpo(p)
        p.setBrush(QColor(0, 0, 0))
        if self.frame_idx % 2 == 0:
            p.drawEllipse(85, 115, 30, 20)
        else:
            p.drawEllipse(90, 118, 20, 15)

    def _desenhar_feliz(self, p):
        self._base_corpo(p)
        p.setBrush(QColor(255, 0, 0))
        if self.frame_idx == 0:
            p.drawText(160, 30, "♥")
        elif self.frame_idx == 2:
            p.drawText(20, 40, "♥")

    def _desenhar_dormindo(self, p):
        p.setBrush(QColor(200, 200, 200))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(30, 30, 140, 140)
        p.setPen(QColor(0, 0, 0))
        p.drawLine(60, 85, 90, 85)
        p.drawLine(110, 85, 140, 85)
        p.drawText(150, 50, "Z")
        if self.frame_idx >= 1:
            p.drawText(165, 35, "z")
        if self.frame_idx >= 2:
            p.drawText(180, 20, "z")

    def _desenhar_triste(self, p):
        self._base_corpo(p, (180, 200, 255))
        p.setPen(QColor(0, 0, 0))
        p.drawArc(75, 130, 50, 20, 180 * 16, 180 * 16)

    # ========================================================================
    #  MUDANÇA DE ESTADOS (API pública)
    # ========================================================================

    def set_estado(self, estado):
        if isinstance(estado, str):
            try:
                estado = Estado(estado)
            except ValueError:
                return
        self.estado_atual = estado
        self._desenhar_estado()

    def idle(self):         self.set_estado(Estado.IDLE)
    def listening(self):    self.set_estado(Estado.LISTENING)
    def thinking(self):     self.set_estado(Estado.THINKING)
    def speaking(self):     self.set_estado(Estado.SPEAKING)
    def feliz(self):        self.set_estado(Estado.FELIZ)
    def dormir(self):       self.set_estado(Estado.DORMINDO)
    def triste(self):       self.set_estado(Estado.TRISTE)

    # ========================================================================
    #  BALÃO DE DIÁLOGO
    # ========================================================================

    def mostrar_balao(self, texto: str, duracao: int = 5000):
        texto_curto = texto[:150] + "..." if len(texto) > 150 else texto
        self.balao.setText(texto_curto)
        self.balao.setVisible(True)
        QTimer.singleShot(duracao, self._esconder_balao)

    def _esconder_balao(self):
        self.balao.setVisible(False)

    def get_modo_fala(self) -> str:
        return "balão" if self.modo_balão else "voz"

    def _alternar_modo_fala(self):
        self.modo_balão = not self.modo_balão
        modo = self.get_modo_fala()
        self.mostrar_balao(f"Modo: {modo} 💬", 2000)
        return modo

    # ========================================================================
    #  MENU DE CONTEXTO (botão direito)
    # ========================================================================

    def _menu_contexto(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("color: white; background-color: #333;")

        texto_modo = "🔊 Usar Voz" if self.modo_balão else "💬 Usar Balão"
        acao_modo = QAction(texto_modo, self)
        acao_modo.triggered.connect(self._alternar_modo_fala)
        menu.addAction(acao_modo)

        menu.addSeparator()

        acao_dormir = QAction("😴 Dormir", self)
        acao_dormir.triggered.connect(self.dormir)
        menu.addAction(acao_dormir)

        acao_feliz = QAction("😊 Ficar feliz", self)
        acao_feliz.triggered.connect(self.feliz)
        menu.addAction(acao_feliz)

        acao_triste = QAction("😢 Ficar triste", self)
        acao_triste.triggered.connect(self.triste)
        menu.addAction(acao_triste)

        menu.addSeparator()

        acao_fechar = QAction("❌ Fechar Luna", self)
        acao_fechar.triggered.connect(self.close)
        menu.addAction(acao_fechar)

        menu.exec(self.mapToGlobal(pos))

    # ========================================================================
    #  EVENTOS DE MOUSE (ARRASTO + GRAVIDADE)
    # ========================================================================

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.arrastando = True
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.clique_simples.emit()

    def mouseMoveEvent(self, event):
        if self.arrastando:
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        if self.arrastando:
            self.arrastando = False
            # Queda suave até o chão
            screen = QApplication.primaryScreen().geometry()
            final_y = screen.height() - self.height() - 10
            anim = QPropertyAnimation(self, b"pos")
            anim.setDuration(500)
            anim.setStartValue(self.pos())
            anim.setEndValue(QPoint(self.x(), final_y))
            anim.setEasingCurve(QEasingCurve.Type.OutBounce)
            anim.start()

    def mouseDoubleClickEvent(self, event):
        self.clique_duplo.emit()
        self.feliz()
        self.mostrar_balao("Oi, papai! 😊", 3000)


# ==============================================================================
# Teste rápido
# ==============================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    luna = LunaCorpo()
    luna.mostrar_balao("Oi, papai! Testando o balão!", 4000)
    QTimer.singleShot(2000, luna.listening)
    QTimer.singleShot(4000, luna.thinking)
    QTimer.singleShot(6000, luna.speaking)
    QTimer.singleShot(8000, luna.feliz)
    sys.exit(app.exec())