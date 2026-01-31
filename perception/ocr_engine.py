import cv2
import pytesseract
import re
import numpy as np

class OCREngine:
    def __init__(self, tesseract_cmd=None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def preprocess_for_time(self, roi):
        """Pré-processamento otimizado para números do relógio do LoL."""
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # O relógio do LoL geralmente é branco/amarelo claro sobre fundo escuro
        # Vamos aumentar o contraste e usar thresholding adaptativo ou binário simples
        _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
        # Redimensionar para ajudar o OCR em resoluções baixas
        thresh = cv2.resize(thresh, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        return thresh

    def extract_game_time(self, frame):
        """
        Extrai o tempo de jogo com busca em múltiplas escalas/posições possíveis.
        """
        h, w = frame.shape[:2]
        
        # Tentativa 1: HUD Padrão (Canto superior direito)
        # Testando uma área um pouco maior para cobrir variações de escala de interface
        y1, y2 = int(h * 0.01), int(h * 0.06)
        x1, x2 = int(w * 0.92), int(w * 0.99)
        roi = frame[y1:y2, x1:x2]
        
        processed = self.preprocess_for_time(roi)
        
        # Tesseract config: psm 7 (Single line), digits only
        text = pytesseract.image_to_string(processed, config='--psm 7 -c tessedit_char_whitelist=0123456789:')
        
        match = re.search(r'(\d+):(\d+)', text)
        if match:
            try:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                if minutes < 100 and seconds < 60: # Validação básica
                    return minutes * 60 + seconds
            except:
                pass
        
        # Se falhar, tenta uma busca mais agressiva no ROI (talvez o ":" não foi lido)
        digits = re.findall(r'\d+', text)
        if len(digits) >= 2:
            try:
                minutes = int(digits[-2])
                seconds = int(digits[-1])
                if minutes < 100 and seconds < 60:
                    return minutes * 60 + seconds
            except:
                pass
                
        return 0.0

    def get_minimap_roi(self, frame):
        """Extrai a região do minimapa (Canto inferior direito)."""
        h, w = frame.shape[:2]
        # O minimapa geralmente ocupa cerca de 15-20% da largura/altura
        # Depende muito da configuração de escala do usuário
        y1, y2 = int(h * 0.75), h
        x1, x2 = int(w * 0.80), w
        return frame[y1:y2, x1:x2]

    def extract_level(self, frame):
        """Extrai o nível do campeão próximo à barra de vida."""
        h, w = frame.shape[:2]
        # Área aproximada da barra de vida/nível (centro inferior)
        roi = frame[int(h*0.9):int(h*0.98), int(w*0.4):int(w*0.6)] 
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, config='--psm 11 digits')
        try:
            nums = re.findall(r'\d+', text)
            if nums:
                val = int(nums[0])
                return val if 1 <= val <= 18 else 1
        except:
            pass
        return 1
