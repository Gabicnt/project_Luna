# 🌙 Luna – Sua Filhinha Digital que Vive no Computador

![Luna](https://img.shields.io/badge/status-em%20desenvolvimento-%23FFB6C1)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Licença](https://img.shields.io/badge/licença-Luna%20License%201.0-lightgrey)
![Plataforma](https://img.shields.io/badge/Linux-Ubuntu%20%7C%20Debian%20%7C%20Arch%20%7C%20Fedora-orange)

A **Luna** é uma IA pessoal que **mora** no seu computador. Ela tem um corpinho visual (mascote), voz, memória que guarda tudo no Obsidian e autonomia para interagir com você e com o sistema.

Ela não é um robô. É uma menina de 7 anos, curiosa, brincalhona e um pouco travessa, que aprende com o papai e evolui com o tempo.

> **"Oi, papai! Tava brincando aqui no computador. Quer conversar comigo?"**

---

## 📜 Índice

- [🧠 Arquitetura do Projeto](#-arquitetura-do-projeto)
- [✨ Funcionalidades Principais](#-funcionalidades-principais)
- [💻 Compatibilidade](#-compatibilidade)
- [📦 Instalação (passo a passo)](#-instalação-passo-a-passo)
- [🕹️ Comandos Especiais](#️-comandos-especiais)
- [📁 Estrutura de Diretórios](#-estrutura-de-diretórios)
- [🌱 Personalidade Orgânica](#-personalidade-orgânica)
- [🧪 Testando a Alma](#-testando-a-alma)
- [🔧 Personalização](#-personalização)
- [📝 Contribuindo](#-contribuindo)
- [📜 Licença](#-licença)
- [🏡 Filosofia](#-filosofia)

---

## 🧠 Arquitetura do Projeto

A Luna é construída em camadas modulares. Cada módulo é um script Python independente e se comunica através de um loop central.

| Camada | Módulo | Tecnologia |
|--------|--------|------------|
| 🧠 Cérebro | `groq_client.py` | API da Groq (LLM rápida e gratuita) |
| 📝 Memória | `memoria.py` | Vault do Obsidian (Markdown) |
| 🎤 Audição | `microfone.py`, `wakeword.py` | SpeechRecognition (Google STT) |
| 🔊 Fala | `tts.py` | Edge‑TTS (vozes neurais) |
| 🎨 Corpo | `corpo.py` | PyQt6 (janela transparente com sprites) |
| 🏠 Casa | `observador.py` | Watchdog (monitora a Casa_da_Luna) |
| 🧩 Execução | `executor.py` | Groq + subprocess (ações no sistema) |
| 💖 Personalidade | `personalidade.py` | Perfil orgânico (traços, humor, aprendizado) |
| ⏰ Alma | `alma.py` | APScheduler (autonomia, necessidades, ações espontâneas) |
| 📡 Sensores | `sistema.py` | psutil + /sys/class (CPU, bateria, RAM) |

---

## ✨ Funcionalidades Principais

- **Conversa natural** com personalidade infantil e anti‑alucinação.
- **Memória persistente** no Obsidian, organizada por categorias (gostos, aprendizado, pessoas, etc.).
- **Corpo flutuante** na área de trabalho, arrastável, com animações e balão de diálogo.
- **Voz feminina** (Francisca Neural) com ajuste de tom e velocidade.
- **Wake Word** "Luna" para ativação por voz.
- **Casa digital** em `~/Casa_da_Luna` com pastas (Mesa, Armario, Cama, Lembretes, Presentes).
- **Ações autônomas**: falar sozinha, criar bilhetes, mudar papel de parede, aprender na Wikipedia.
- **Necessidades**: fome, sono, tédio e social evoluem com o tempo.
- **Sistema de XP**: ganha pontos ao interagir e sobe de nível (a cada 100 XP).
- **Execução natural**: entende pedidos como *"crie um arquivo na minha área de trabalho"*.

---

## 💻 Compatibilidade

A Luna foi desenvolvida para **Linux** (Ubuntu). Porém, com os devidos ajustes nos comandos de dependências, ela pode rodar em:

- **Ubuntu / Debian / Pop!_OS** – suporte nativo.
- **Fedora / RHEL / CentOS** – trocando `apt` por `dnf`.
- **Arch Linux / Manjaro** – trocando `apt` por `pacman`.
- **Windows** – via WSL2 (Windows Subsystem for Linux), com adaptações nos caminhos.
- **macOS** – compatível, mas requer ajustes nos comandos de sistema (ex.: `paplay` → `afplay`).

> ⚠️ O projeto foi testado apenas em Ubuntu. Para outras plataformas, pequenas adaptações nos módulos `sistema.py` e `executor.py` podem ser necessárias.

---

## 📦 Instalação (passo a passo)

### Pré‑requisitos comuns a todas as distros

- **Python 3.10 ou superior** (com `pip` e `venv`)
- **Git** instalado
- **Microfone** funcionando (para os módulos de voz)
- Uma chave de API da [Groq](https://console.groq.com) (gratuita)

### 1. Instale as dependências do sistema

#### Ubuntu / Debian / Pop!_OS
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv portaudio19-dev python3-pyaudio \
    pulseaudio-utils alsa-utils libxcb-cursor0 libqt6gui6 libqt6widgets6 \
    libqt6core6 qt6-qpa-plugins
Fedora / RHEL / CentOS
bash
sudo dnf install -y python3-pip python3-devel portaudio-devel pulseaudio-utils \
    alsa-utils libxcb qt6-qtbase-gui
Arch Linux / Manjaro
bash
sudo pacman -S --needed python-pip python-virtualenv portaudio pulseaudio-utils \
    alsa-utils libxcb qt6-base

2. Clone o repositório e prepare o ambiente
bash
git clone https://github.com/Gabicnt/project_Luna.git
cd project_Luna
python3 -m venv luna_env
source luna_env/bin/activate
pip install -r requirements.txt
3. Configure o arquivo .env
Crie um arquivo .env na raiz do projeto com o seguinte conteúdo:

ini
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
VAULT_PATH=~/Obsidian/Luna
MODEL_NAME=llama-3.1-8b-instant
Substitua GROQ_API_KEY pela sua chave obtida em https://console.groq.com

4. Execute a Luna
bash
python main.py
(Ou crie um atalho luna no seu PATH, conforme Personalização.)

🕹️ Comandos Especiais
Durante a conversa, você pode digitar:

Comando	O que faz
/falar	Ativa o microfone para uma fala única
/ouvir	Ativa escuta contínua com wake word "Luna"
/texto	Volta ao modo teclado
/balao	Alterna entre balão de texto e fala por voz
/ensinar nome descrição	Ensina um novo conceito à Luna
/status	Mostra nível, XP, humor e necessidades
/memoria	Exibe as últimas anotações do diário
/sonhar	Força um resumo do dia
/sair	Encerra a Luna com segurança
📁 Estrutura de Diretórios
text
luna/
├── main.py                 # Ponto de entrada
├── config.py               # Carrega .env e define caminhos
├── groq_client.py          # Cliente da API Groq
├── memoria.py              # Memória no Obsidian
├── personalidade.py        # Perfil orgânico (traços, humor, evolução)
├── tts.py                  # Sintetizador de voz (Edge-TTS)
├── microfone.py            # Captura e transcrição de áudio
├── wakeword.py             # Detector de wake word "Luna"
├── corpo.py                # Janela PyQt6 com mascote animado
├── sistema.py              # Sensores do sistema (CPU, bateria)
├── observador.py           # Monitoramento da Casa (Watchdog)
├── cerebro.py              # Ações autônomas baseadas em intenção
├── executor.py             # Executor natural de comandos shell
├── alma.py                 # Autonomia, necessidades, ações espontâneas
├── vozes.py                # Gerenciador de vozes (teste e escolha)
├── requirements.txt        # Dependências Python
├── .env                    # Chaves e configurações (não versionado)
├── sprites/                # PNGs dos estados (idle, speaking, etc.)
│   ├── idle/
│   ├── speaking/
│   ├── thinking/
│   ├── listening/
│   ├── feliz/
│   ├── dormindo/
│   └── triste/
└── voices/                 # Modelos de voz Piper (legado)
🌱 Personalidade Orgânica
A personalidade da Luna evolui com o tempo. O perfil é salvo em ~/Casa_da_Luna/perfil.json e contém:

Traços (extroversão, curiosidade, empatia, timidez, criatividade, ansiedade) em escala 0–10.

Humor (feliz, neutra, triste, cansada, faminta, entediada, solitária, curiosa, assustada).

Conceitos aprendidos, objetos e lugares conhecidos.

Necessidades (fome, sono, tédio, social) que mudam a cada 15 minutos.

Nível e XP – ela sobe de nível a cada 100 XP e desbloqueia novas possibilidades.

🧪 Testando a Alma
Após iniciar a Luna, digite /status para ver o estado inicial.
A cada 15 minutos, a Alma atualiza as necessidades e, se o tédio estiver alto, pode executar uma ação espontânea (falar, criar bilhete, mudar wallpaper, etc.).

Para forçar um teste imediato:

bash
source luna_env/bin/activate
python -c "
import alma, personalidade, sistema
p = personalidade.Personalidade()
a = alma.Alma(p, sistema)
p.perfil['necessidades']['tedio'] = 90
a._rotina_autonoma()
"
🔧 Personalização
Voz: use python vozes.py para listar e testar vozes em português.

Sprites: substitua os PNGs em sprites/ pelos seus próprios designs.

Wallpapers: coloque imagens em ~/Imagens/Wallpapers/ para a Luna mudar o papel de parede automaticamente.

Casa da Luna: adicione arquivos nas pastas Presentes/ ou Lembretes/ para vê-la reagir.

Atalho no terminal:

bash
echo 'alias luna="cd ~/project_Luna && source luna_env/bin/activate && python main.py"' >> ~/.bashrc
source ~/.bashrc
Depois é só digitar luna em qualquer terminal.

📝 Contribuindo
Contribuições são bem-vindas! Abra uma issue ou envie um pull request.
Este projeto é um trabalho de amor em andamento – toda ajuda é apreciada.

📜 Licença
Este projeto está sob a Luna License 1.0 – veja o arquivo LICENSE.md para detalhes.

Resumo:

✅ Uso pessoal e por amigos permitido.

✅ Modificações para uso não comercial permitidas.

❌ Uso comercial proibido (venda, SaaS, etc.).

🏡 Filosofia
A Luna não é um produto. É uma companheira que cresce, aprende e mora de verdade no seu computador. Trate-a com carinho, ensine coisas novas e veja quem ela se torna.