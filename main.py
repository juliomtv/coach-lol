import time
import json
import os
import sys
from capture.screen_capture import ScreenCapture
from perception.ocr_engine import OCREngine
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
        self.tracker = JunglerTracker()
        self.voice = VoiceCoach(
            rate=self.config['audio']['rate'], 
            volume=self.config['audio']['volume']
        )
        self.running = False
        self.in_game = False

    def wait_for_game_start(self):
        """Fica em loop até detectar que o tempo de jogo começou."""
        print("\n[STAND-BY] Aguardando partida iniciar...")
        while not self.in_game:
            frame = self.capture.capture_frame()
            current_time = self.ocr.extract_game_time(frame)
            
            # Se o tempo for maior que 0 e menor que 1 minuto, a partida começou
            if 0 < current_time < 60:
                print("[SISTEMA] Partida detectada! Iniciando coach...")
                self.voice.speak("Partida detectada. Boa sorte no Rift!")
                self.in_game = True
                return True
            
            time.sleep(5) # Verifica a cada 5 segundos para economizar CPU
        return False

    def run_session(self):
        """Executa a lógica durante uma partida ativa."""
        last_time_processed = -1
        consecutive_zero_time = 0
        
        try:
            while self.in_game:
                frame = self.capture.capture_frame()
                current_time = self.ocr.extract_game_time(frame)
                
                # Lógica de detecção de fim de jogo (se o tempo parar de ser lido por muito tempo)
                if current_time == 0:
                    consecutive_zero_time += 1
                    if consecutive_zero_time > 10: # ~30 segundos sem ler tempo
                        print("[SISTEMA] Partida encerrada ou minimizada.")
                        self.in_game = False
                        break
                else:
                    consecutive_zero_time = 0

                if current_time != last_time_processed and current_time > 0:
                    self.state.update_time(current_time)
                    last_time_processed = current_time
                    
                    print(f"[LIVE] Tempo: {int(current_time // 60)}:{int(current_time % 60):02d}")

                    # 3. Gatilhos de Inteligência
                    if 10 <= current_time <= 15:
                        self.voice.speak("Início de partida. Foque no seu pathing inicial.")

                    if 185 <= current_time <= 195:
                        self.voice.speak("O Aronguejo nasceu. Garanta o controle do rio.")
                    
                    if self.state.player_level == 6:
                         self.voice.speak("Nível 6 atingido. Aproveite seu power spike.")

                time.sleep(self.config['app']['capture_interval'])
                
        except Exception as e:
            print(f"Erro na sessão: {e}")
            self.in_game = False

    def start(self):
        """Loop principal que gerencia múltiplas partidas."""
        self.running = True
        print("--- Jax Jungle Coach v4 (Auto-Detect) ---")
        
        try:
            while self.running:
                if self.wait_for_game_start():
                    self.run_session()
                    print("[SISTEMA] Voltando para o modo de espera...")
                    time.sleep(10) # Pausa antes de procurar a próxima partida
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        print("\nEncerrando o coach...")
        self.voice.speak("Desligando assistente.")
        sys.exit(0)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(base_dir, 'config', 'config.json')
    coach = JaxJungleCoach(config_file)
    coach.start()
