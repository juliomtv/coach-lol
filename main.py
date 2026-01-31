import time
import json
import os
import sys
import psutil
import cv2
from capture.screen_capture import ScreenCapture
from perception.ocr_engine import OCREngine
from perception.map_engine import MapEngine
from core.state import GameState, ChampionState
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
        
        if not os.path.exists(tess_path):
            print(f"\n[AVISO]: Tesseract não encontrado em: {tess_path}")
            
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

    def is_lol_running(self):
        for proc in psutil.process_iter(['name']):
            try:
                if "League of Legends" in proc.info['name']:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def wait_for_game_start(self):
        print("\n[STAND-BY] Aguardando League of Legends...")
        while self.running:
            if not self.is_lol_running():
                time.sleep(5)
                continue
            
            print("[SISTEMA] LoL detectado! Tentando ler o relógio...")
            frame = self.capture.capture_frame()
            current_time = self.ocr.extract_game_time(frame)
            
            if current_time > 0:
                print(f"[SISTEMA] Partida detectada! Iniciando...")
                self.voice.speak("Partida iniciada. Boa sorte!")
                self.in_game = True
                return True
            
            # Debug para ajudar o usuário a ver o que o script está vendo
            debug_roi = self.ocr.preprocess_for_time(frame[int(frame.shape[0]*0.01):int(frame.shape[0]*0.06), int(frame.shape[1]*0.92):int(frame.shape[1]*0.99)])
            cv2.imwrite("debug_clock_view.png", debug_roi)
            
            print("[SISTEMA] Relógio não detectado. Verifique 'debug_clock_view.png'.")
            time.sleep(5)
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
                    
                    # 1. Analisar Minimapa
                    minimap_roi = self.ocr.get_minimap_roi(frame)
                    map_state = self.map_engine.analyze_map_state(minimap_roi)
                    
                    # 2. Lógica de Alertas de Mapa
                    if time.time() - self.last_map_alert > 15: # Evita spam de voz
                        if map_state["enemy_count"] > 0:
                            if any(zone in map_state["hot_zones"] for zone in ["dragon", "baron_nashor"]):
                                self.voice.speak("Inimigos detectados perto de objetivo importante!")
                                self.last_map_alert = time.time()
                            elif map_state["enemy_count"] >= 3:
                                self.voice.speak(f"Cuidado, {map_state['enemy_count']} inimigos visíveis no mapa.")
                                self.last_map_alert = time.time()

                    # 3. Gatilhos de Tempo
                    if 10 <= current_time <= 15:
                        self.voice.speak("Inicie sua rota de selva.")
                    elif 185 <= current_time <= 195:
                        self.voice.speak("Aronguejo disponível.")

                    print(f"[LIVE] Tempo: {int(current_time // 60)}:{int(current_time % 60):02d} | Inimigos: {map_state['enemy_count']}")

                time.sleep(self.config['app']['capture_interval'])
                
        except Exception as e:
            print(f"Erro na sessão: {e}")
            self.in_game = False

    def start(self):
        self.running = True
        print("--- Jax Jungle Coach v5 (Map Aware) ---")
        try:
            while self.running:
                if self.wait_for_game_start():
                    self.run_session()
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
