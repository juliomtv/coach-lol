import cv2
import numpy as np
import mss
from PIL import Image

def calibrar():
    sct = mss.mss()
    monitor = sct.monitors[1]
    
    print("--- Ferramenta de Calibração de Tela ---")
    print("Capturando tela em 3 segundos... Abra o League of Legends no tempo de jogo.")
    import time
    time.sleep(3)
    
    screenshot = sct.grab(monitor)
    img = np.array(Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX"))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    # Salva a imagem inteira para o usuário ver
    cv2.imwrite("captura_total.png", img)
    print("Imagem 'captura_total.png' salva. Verifique se o jogo aparece nela.")
    
    # Exemplo de ROI para o Tempo (Ajuste esses valores se necessário)
    # No 1920x1080, o tempo fica aprox em [10:40, 1750:1850]
    h, w, _ = img.shape
    print(f"Sua resolução detectada: {w}x{h}")
    
    # Tenta desenhar um retângulo onde o OCR está lendo (Nova V5)
    y1, y2 = int(h * 0.018), int(h * 0.045)
    x1, x2 = int(w * 0.935), int(w * 0.985)
    roi_tempo = img[y1:y2, x1:x2]
    cv2.imwrite("debug_tempo_roi.png", roi_tempo)
    print(f"ROI do Tempo salva em 'debug_tempo_roi.png'. Se estiver vazia ou errada, precisamos ajustar as coordenadas no ocr_engine.py.")

if __name__ == "__main__":
    calibrar()
