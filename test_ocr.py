import cv2
import json
import os
import time
from capture.screen_capture import ScreenCapture
from perception.ocr_engine import OCREngine
from perception.map_engine import MapEngine

def test_diagnostics():
    print("--- Diagnóstico Completo: Relógio e Minimapa ---")
    config_path = os.path.join('config', 'config.json')
    
    with open(config_path, 'r') as f:
        config = json.load(f)

    tess_path = config['ocr']['tesseract_path']
    capture = ScreenCapture()
    ocr = OCREngine(tesseract_cmd=tess_path)
    map_eng = MapEngine()

    print("\nCapturando em 5 segundos... Abra o LoL na partida!")
    time.sleep(5)

    frame = capture.capture_frame()
    h, w = frame.shape[:2]
    print(f"Resolução Detectada: {w}x{h}")

    # Teste Relógio
    y1, y2 = int(h * 0.01), int(h * 0.06)
    x1, x2 = int(w * 0.92), int(w * 0.99)
    clock_roi = frame[y1:y2, x1:x2]
    processed_clock = ocr.preprocess_for_time(clock_roi)
    cv2.imwrite("diag_clock_raw.png", clock_roi)
    cv2.imwrite("diag_clock_processed.png", processed_clock)
    
    current_time = ocr.extract_game_time(frame)
    print(f"Tempo detectado: {current_time}s")

    # Teste Minimapa
    minimap_roi = ocr.get_minimap_roi(frame)
    cv2.imwrite("diag_minimap.png", minimap_roi)
    map_state = map_eng.analyze_map_state(minimap_roi)
    print(f"Inimigos no minimapa: {map_state['enemy_count']}")
    
    print("\nArquivos de diagnóstico gerados:")
    print("- diag_clock_raw.png (O que o script vê no relógio)")
    print("- diag_clock_processed.png (Como o OCR tenta ler o relógio)")
    print("- diag_minimap.png (O que o script vê no minimapa)")

if __name__ == "__main__":
    test_diagnostics()
