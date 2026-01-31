import time
import json
import os
import sys
import psutil
import cv2
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
        self.last_map_alert = 0
        self.last_voice_time = 0

    def is_lol_running(self):
        for proc in psutil.process_iter(['name']):
            try:
                if "League of Legends" in proc.info['name']:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def speak_safe(self, text):
        """Evita sobreposição de falas e garante um intervalo mínimo."""
        current_time = time.time()
        if current_time - self.last_voice_time > 3: # 3 segundos entre falas
            print(f"[COACH] {text}")
            self.voice.speak(text)
            self.last_voice_time = current_time

    def wait_for_game_start(self):
        print("\n[STAND-BY] Aguardando partida iniciar...")
        while self.running:
            if not self.is_lol_running():
                time.sleep(5)
                continue
            
            frame = self.capture.capture_frame()
            current_time = self.ocr.extract_game_time(frame)
            
            if current_time > 0:
                self.speak_safe("Partida detectada. Boa sorte no Rift!")
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
                    
                    # 1. Alertas Baseados em Tempo (Objetivos e Selva)
                    time_alerts = self.tracker.get_time_alerts(current_time)
                    for alert in time_alerts:
                        self.speak_safe(alert)

                    # 2. Análise de Minimapa (Inimigos Reais)
                    minimap_roi = self.ocr.get_minimap_roi(frame)
                    map_state = self.map_engine.analyze_map_state(minimap_roi)
                    
                    # 3. Lógica de Alertas de Mapa e Objetivos
                    enemy_count = map_state["enemy_count"]
                    
                    if enemy_count > 0:
                        # Prioridade: Inimigos perto de objetivos
                        if any(zone in map_state["hot_zones"] for zone in ["dragon", "baron_nashor"]):
                            self.speak_safe("Atenção! Inimigo detectado próximo ao objetivo!")
                        
                        # Estratégia baseada em posição
                        advice = JaxStrategy.evaluate_objective_priority(current_time, 0, 0) # Simplificado
                        if advice:
                            self.speak_safe(advice)

                    # Log de status no console
                    print(f"[LIVE] Tempo: {int(current_time // 60)}:{int(current_time % 60):02d} | Inimigos Reais: {enemy_count}")

                time.sleep(self.config['app']['capture_interval'])
                
        except Exception as e:
            print(f"Erro na sessão: {e}")
            self.in_game = False

    def start(self):
        self.running = True
        print("--- Jax Jungle Coach v6 (Final Polish) ---")
        try:
            while self.running:
                if self.wait_for_game_start():
                    self.run_session()
                    print("[SISTEMA] Partida finalizada. Voltando para espera...")
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
