import time
import json
import os
import sys
import psutil
import cv2
import pytesseract
import re
from capture.screen_capture import ScreenCapture
from perception.ocr_engine import OCREngine
from perception.map_engine import MapEngine
from core.state import GameState
from intelligence.tracker import JunglerTracker, JaxStrategy
from output.voice_output import VoiceCoach

class JaxJungleCoach:
    def __init__(self, config_path):
        if not os.path.exists(config_path):
            print(f"Erro: Arquivo de configuração não encontrado em {config_path}")
            sys.exit(1)
            
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.state = GameState()
        self.capture = ScreenCapture()
        tess_path = self.config['ocr']['tesseract_path']
        self.ocr = OCREngine(tesseract_cmd=tess_path)
        self.map_engine = MapEngine()
        self.tracker = JunglerTracker()
        self.voice = VoiceCoach(
            rate=self.config['audio']['rate'], 
            volume=self.config['audio']['volume']
        )
        self.running = False
        self.in_game = False
        self.matchup_detected = False
        self.last_voice_time = 0

    def is_lol_running(self):
        for proc in psutil.process_iter(['name']):
            try:
                if "League of Legends" in proc.info['name']:
                    return True
            except:
                pass
        return False

    def speak_safe(self, text):
        current_time = time.time()
        if current_time - self.last_voice_time > 4: # Intervalo de 4s
            print(f"[COACH] {text}")
            self.voice.speak(text)
            self.last_voice_time = current_time

    def detect_matchup(self, frame):
        """Tenta ler os nomes dos campeões na tela de carregamento ou TAB."""
        # Na tela de carregamento, os nomes ficam em áreas específicas. 
        # Como simplificação, vamos ler o centro da tela por palavras-chave de campeões.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
        
        common_junglers = ["Lee Sin", "Master Yi", "Graves", "Nidalee", "Shaco", "Kayn", "Warwick", "Kha'Zix", "Jarvan", "Vi"]
        for jg in common_junglers:
            if jg.lower() in text.lower():
                return jg
        return None

    def wait_for_game_start(self):
        print("\n[STAND-BY] Monitorando tela de carregamento e início...")
        while self.running:
            if not self.is_lol_running():
                time.sleep(5)
                continue
            
            frame = self.capture.capture_frame()
            
            # 1. Tentar detectar matchup se ainda não detectou
            if not self.matchup_detected:
                jg_inimigo = self.detect_matchup(frame)
                if jg_inimigo:
                    advice = self.tracker.get_matchup_advice(jg_inimigo)
                    self.speak_safe(f"Inimigo detectado: {jg_inimigo}. {advice}")
                    self.matchup_detected = True

            # 2. Verificar se o tempo de jogo começou
            current_time = self.ocr.extract_game_time(frame)
            if current_time > 0:
                self.speak_safe("Partida iniciada! Foque no seu primeiro buff.")
                self.in_game = True
                return True
            
            time.sleep(3)
        return False

    def run_session(self):
        last_time_processed = -1
        consecutive_zero_time = 0
        
        try:
            while self.in_game and self.is_lol_running():
                frame = self.capture.capture_frame()
                current_time = self.ocr.extract_game_time(frame)
                
                if current_time == 0:
                    consecutive_zero_time += 1
                    if consecutive_zero_time > 20:
                        self.in_game = False
                        break
                else:
                    consecutive_zero_time = 0

                if current_time != last_time_processed and current_time > 0:
                    self.state.update_time(current_time)
                    last_time_processed = current_time
                    
                    # Alertas de Tempo
                    for alert in self.tracker.get_time_alerts(current_time):
                        self.speak_safe(alert)

                    # Análise de Minimapa
                    minimap_roi = self.ocr.get_minimap_roi(frame)
                    map_state = self.map_engine.analyze_map_state(minimap_roi)
                    
                    if map_state["enemy_count"] > 0:
                        for enemy in map_state["enemies"]:
                            loc = enemy["location"]
                            if "red" in loc.lower() or "blue" in loc.lower():
                                self.speak_safe(f"Inimigo detectado na área do {loc}!")
                            elif "dragon" in loc.lower():
                                self.speak_safe("Inimigo no Dragão! Considere contestar.")

                    print(f"[LIVE] Tempo: {int(current_time // 60)}:{int(current_time % 60):02d} | Inimigos: {map_state['enemy_count']}")

                time.sleep(self.config['app']['capture_interval'])
                
        except Exception as e:
            print(f"Erro na sessão: {e}")
            self.in_game = False

    def start(self):
        self.running = True
        print("--- Jax Jungle Coach v7 (Matchup Aware) ---")
        try:
            while self.running:
                if self.wait_for_game_start():
                    self.run_session()
                    self.matchup_detected = False # Reset para a próxima
                    print("[SISTEMA] Partida finalizada.")
                    time.sleep(10)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        sys.exit(0)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(base_dir, 'config', 'config.json')
    coach = JaxJungleCoach(config_file)
    coach.start()
