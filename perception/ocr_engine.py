import cv2
import pytesseract
import re

class OCREngine:
    def __init__(self, tesseract_cmd=None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_game_time(self, frame):
        """
        Extrai o tempo de jogo do canto superior direito (HUD padrão).
        Nota: Coordenadas dependem da resolução. Exemplo para 1920x1080.
        """
        # Região aproximada do tempo no HUD (1920x1080)
        # x, y, w, h = 1750, 10, 100, 30 (Exemplo hipotético)
        # Por agora, vamos definir uma lógica genérica que o usuário pode ajustar
        # Ajustado: Mais para a direita (1750->1800) e um pouco para baixo (10->20)
        # Valores para 1920x1080. Se sua resolução for diferente, o cálculo proporcional ajuda.
        h, w = frame.shape[:2]
        y1, y2 = int(h * 0.018), int(h * 0.045) # Ex: 20 a 48
        x1, x2 = int(w * 0.935), int(w * 0.985) # Ex: 1795 a 1891
        roi = frame[y1:y2, x1:x2]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        text = pytesseract.image_to_string(thresh, config='--psm 7')
        match = re.search(r'(\d+):(\d+)', text)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            return minutes * 60 + seconds
        return 0.0

    def extract_level(self, frame):
        """Extrai o nível do campeão próximo à barra de vida."""
        # ROI simplificada para exemplo
        roi = frame[1000:1050, 800:850] 
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, config='--psm 10 digits')
        try:
            return int(re.sub(r'\D', '', text))
        except:
            return 1
