# Jax Jungle Coach (Real-Time Assistant)

Este é um assistente de inteligência artificial para League of Legends, focado em auxiliar jogadores de **Jax Jungle**. O sistema utiliza processamento de imagem (OCR e Visão Computacional) para ler dados do jogo e fornecer conselhos estratégicos por voz.

## Funcionalidades
- **Captura Visual**: Lê o HUD e o minimapa sem interagir com a memória ou arquivos do jogo.
- **OCR Inteligente**: Extrai tempo de jogo, nível e itens.
- **Rastreamento de Jungler**: Predição probabilística da posição do jungler inimigo.
- **Conselhos de Jax**: Avisos de power spikes (nível 6, Trinity Force) e rotas ideais.
- **Output por Voz**: Feedback em tempo real para não distrair o jogador.

## Estrutura do Projeto
- `capture/`: Módulo de captura de tela e processamento de vídeo.
- `perception/`: Motores de OCR e reconhecimento de padrões.
- `intelligence/`: Lógica de decisão, tracking e análise de matchups.
- `core/`: Gerenciamento de estado global (`GameState`).
- `output/`: Interface de voz (TTS).
- `config/`: Configurações personalizáveis via JSON.

## Requisitos
- Python 3.10+
- Tesseract OCR instalado no sistema.
- Dependências Python: `opencv-python`, `pytesseract`, `mss`, `pyttsx3`, `numpy`, `pillow`.

## Como Usar
1. Certifique-se de que o League of Legends está em modo **Janela sem Bordas** ou **Janela**.
2. Ajuste as coordenadas de ROI no arquivo `perception/ocr_engine.py` conforme sua resolução (padrão 1920x1080).
3. Execute o script principal:
   ```bash
   python3 main.py
   ```

## Segurança
Este software é estritamente um assistente visual. Ele **não**:
- Lê a memória do jogo.
- Injeta código ou usa hooks.
- Automatiza movimentos ou cliques (No scripts/macros).
- Viola os termos de serviço ao atuar apenas como uma "segunda tela" inteligente.
