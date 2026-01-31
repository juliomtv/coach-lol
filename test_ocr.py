import cv2
import json
import os
import sys
from capture.screen_capture import ScreenCapture
from perception.ocr_engine import OCREngine

def test_ocr():
    print("--- Teste de Diagnóstico de OCR ---")
    config_path = os.path.join('config', 'config.json')
    
    if not os.path.exists(config_path):
        print("Erro: Arquivo config/config.json não encontrado.")
        return

    with open(config_path, 'r') as f:
        config = json.load(f)

    tess_path = config['ocr']['tesseract_path']
    print(f"Caminho do Tesseract: {tess_path}")
    
    if not os.path.exists(tess_path):
        print("[ERRO] Tesseract não encontrado no caminho especificado!")
        return

    capture = ScreenCapture()
    ocr = OCREngine(tesseract_cmd=tess_path)

    print("\nCapturando tela em 3 segundos... Mude para a janela do LoL!")
    import time
    time.sleep(3)

    frame = capture.capture_frame()
    
    # Tenta extrair o tempo
    h, w = frame.shape[:2]
    y1, y2 = int(h * 0.018), int(h * 0.045)
    x1, x2 = int(w * 0.935), int(w * 0.985)
    roi = frame[y1:y2, x1:x2]
    
    # Salva para o usuário ver
    cv2.imwrite("debug_ocr_roi.png", roi)
    cv2.imwrite("debug_full_frame.png", frame)
    
    current_time = ocr.extract_game_time(frame)
    
    print(f"\nResultado da leitura: {current_time}")
    if current_time > 0:
        print("SUCESSO: O tempo foi detectado corretamente!")
    else:
        print("FALHA: O tempo não foi detectado.")
        print("DICA: Verifique o arquivo 'debug_ocr_roi.png' para ver se a região capturada contém o relógio do jogo.")
        print(f"Sua resolução detectada: {w}x{h}")

if __name__ == "__main__":
    test_ocr()
