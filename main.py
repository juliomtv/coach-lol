import time
import json
import os
import sys
import psutil
import cv2
import pytesseract
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
        """Verifica se o processo do jogo está ativo."""
        for proc in psutil.process_iter(['name']):
            try:
                if "League of Legends" in proc.info['name']:
                    return True
            except:
                pass
        return False

    def speak_safe(self, text):
        """Envia para a fila de voz e printa no console."""
        current_time = time.time()
        # Filtro de repetição: não fala a mesma coisa em menos de 10 segundos
        # (Isso evita spam se o OCR ler o mesmo tempo várias vezes)
        print(f"[LIVE COACH] {text}")
        self.voice.speak(text)
        self.last_voice_time = current_time

    def detect_matchup(self, frame):
        """Tenta identificar o caçador inimigo."""
        try:
            # Pega uma região central onde os nomes costumam aparecer na loading screen
            h, w = frame.shape[:2]
            roi = frame[int(h*0.3):int(h*0.7), int(w*0.2):int(w*0.8)]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray)
            
            common_junglers = ["Lee Sin", "Master Yi", "Graves", "Nidalee", "Shaco", "Kayn", "Warwick", "Kha'Zix", "Jarvan", "Vi", "Amumu", "Elise", "Rengar"]
            for jg in common_junglers:
                if jg.lower() in text.lower():
                    return jg
        except:
            pass
        return None

    def wait_for_game_start(self):
        print("\n[SISTEMA] Aguardando partida (Monitorando Matchup e Tempo)...")
        while self.running:
            if not self.is_lol_running():
                time.sleep(5)
                continue
            
            frame = self.capture.capture_frame()
            
            # 1. Detectar Matchup
            if not self.matchup_detected:
                jg_inimigo = self.detect_matchup(frame)
                if jg_inimigo:
                    advice = self.tracker.get_matchup_advice(jg_inimigo)
                    self.speak_safe(f"Caçador inimigo: {jg_inimigo}. {advice}")
                    self.matchup_detected = True

            # 2. Detectar Início (Tempo > 0)
            current_time = self.ocr.extract_game_time(frame)
            if current_time > 0:
                self.speak_safe("Partida iniciada. Boa sorte no Rift!")
                self.in_game = True
                return True
            
            time.sleep(2)
        return False

    def run_session(self):
        last_time_processed = -1
        consecutive_zero_time = 0
        
        print("[SISTEMA] Sessão ativa. Monitorando objetivos e mapa.")
        
        try:
            while self.in_game and self.is_lol_running():
                frame = self.capture.capture_frame()
                current_time = self.ocr.extract_game_time(frame)
                
                if current_time == 0:
                    consecutive_zero_time += 1
                    if consecutive_zero_time > 30: # 30 segundos sem ler tempo encerra
                        self.in_game = False
                        break
                else:
                    consecutive_zero_time = 0

                # Só processa se o tempo mudou (evita processar o mesmo segundo várias vezes)
                if current_time != last_time_processed and current_time > 0:
                    last_time_processed = current_time
                    
                    # A. Alertas de Tempo (Objetivos/Selva)
                    alerts = self.tracker.get_time_alerts(current_time)
                    for alert in alerts:
                        self.speak_safe(alert)

                    # B. Análise de Minimapa
                    minimap_roi = self.ocr.get_minimap_roi(frame)
                    map_state = self.map_engine.analyze_map_state(minimap_roi)
                    
                    if map_state["enemy_count"] > 0:
                        for enemy in map_state["enemies"]:
                            loc = enemy["location"]
                            if "red" in loc.lower() or "blue" in loc.lower() or "dragon" in loc.lower():
                                self.speak_safe(f"Inimigo detectado perto do {loc}!")

                    # Log discreto
                    if int(current_time) % 30 == 0:
                        print(f"[LOG] Tempo: {int(current_time//60)}:{int(current_time%60):02d}")

                time.sleep(self.config['app']['capture_interval'])
                
        except Exception as e:
            print(f"Erro crítico na sessão: {e}")
            self.in_game = False

    def start(self):
        self.running = True
        print("--- Jax Jungle Coach v8 (Stable Voice) ---")
        try:
            while self.running:
                if self.wait_for_game_start():
                    self.run_session()
                    self.matchup_detected = False 
                    print("[SISTEMA] Partida finalizada. Reiniciando monitoramento...")
                    time.sleep(10)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        print("Encerrando...")
        sys.exit(0)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(base_dir, 'config', 'config.json')
    coach = JaxJungleCoach(config_file)
    coach.start()
