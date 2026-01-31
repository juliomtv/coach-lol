# Guia de Instalação do Tesseract OCR (Windows)

O erro que você recebeu ocorre porque o componente responsável por "ler" o tempo do jogo não está instalado no seu Windows. Siga estes passos simples:

### 1. Baixar o Instalador
Acesse o link abaixo e baixe o instalador para Windows (geralmente a versão de 64 bits):
- [Tesseract Installer for Windows](https://github.com/UB-Mannheim/tesseract/wiki)
- Link direto: `tesseract-ocr-w64-setup-v5.x.x.exe`

### 2. Instalar
- Execute o instalador.
- **Dica Importante**: Durante a instalação, anote a pasta onde ele será instalado. O padrão é `C:\Program Files\Tesseract-OCR`.

### 3. Verificar o Caminho
Se você instalou em uma pasta diferente, abra o arquivo `config/config.json` no seu projeto e mude a linha:
```json
"tesseract_path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```
para o caminho onde você instalou, lembrando de usar duas barras `\\`.

### 4. Reiniciar o Coach
Após instalar, basta rodar o `python main.py` novamente.
