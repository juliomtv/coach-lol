import cv2
import json
import os
import time
import numpy as np
from capture.screen_capture import ScreenCapture
from perception.ocr_engine import OCREngine
from perception.map_engine import MapEngine

def test_map_logic():
    print("--- Teste de Filtragem de Minimapa (Campeões vs Tropas) ---")
    capture = ScreenCapture()
    ocr = OCREngine()
    map_eng = MapEngine()

    print("\nCapturando em 5 segundos... Certifique-se de que há tropas e talvez um bot no mapa.")
    time.sleep(5)

    frame = capture.capture_frame()
    minimap_roi = ocr.get_minimap_roi(frame)
    
    if minimap_roi is None:
        print("Erro: Minimapa não localizado.")
        return

    # Salva o minimapa original
    cv2.imwrite("test_map_original.png", minimap_roi)
    
    # Executa detecção
    enemies = map_eng.detect_enemy_icons(minimap_roi)
    
    # Desenha os resultados para debug
    debug_img = minimap_roi.copy()
    for (x, y) in enemies:
        cv2.circle(debug_img, (x, y), 10, (0, 255, 0), 2) # Verde para campeões detectados
        
    cv2.imwrite("test_map_detection.png", debug_img)
    
    print(f"\nResultado: {len(enemies)} campeões detectados.")
    print("Verifique 'test_map_detection.png'. Círculos verdes devem estar apenas em campeões.")
    print("Se as tropas estiverem circuladas, o filtro de área no 'map_engine.py' precisa ser aumentado.")

if __name__ == "__main__":
    test_map_logic()
