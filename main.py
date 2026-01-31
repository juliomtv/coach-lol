import time
import json
import os
import sys
import psutil
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
        
        # Verificação básica do Tesseract
        if not os.path.exists(tess_path):
            print(f"\n[AVISO]: Tesseract não encontrado em: {tess_path}")
            print("[DICA]: Verifique o caminho no arquivo config/config.json")
            
        self.ocr = OCREngine(tesseract_cmd=tess_path)
        self.tracker = JunglerTracker()
        self.voice = VoiceCoach(
            rate=self.config['audio']['rate'], 
            volume=self.config['audio']['volume']
        )
        self.running = False
        self.in_game = False

    def is_lol_running(self):
        """Verifica se o processo do League of Legends (o jogo em si) está ativo."""
        for proc in psutil.process_iter(['name']):
            try:
                # O processo do jogo geralmente é "League of Legends.exe"
                if "League of Legends" in proc.info['name']:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def wait_for_game_start(self):
        """Fica em loop até detectar que o processo do LoL está ativo e o tempo começou."""
        print("\n[STAND-BY] Aguardando League of Legends ser detectado...")
        
        while self.running:
            # Passo 1: Verificar se o processo existe
            if not self.is_lol_running():
                time.sleep(5)
                continue
            
            print("[SISTEMA] Processo do League of Legends detectado! Aguardando início da partida...")
            
            # Passo 2: Tentar ler o tempo de jogo
            while self.is_lol_running():
                frame = self.capture.capture_frame()
                current_time = self.ocr.extract_game_time(frame)
                
                # Se o tempo for maior que 0, a partida começou
                if current_time > 0:
                    print(f"[SISTEMA] Partida detectada (Tempo: {int(current_time)}s)! Iniciando coach...")
                    self.voice.speak("Partida detectada. Boa sorte no Rift!")
                    self.in_game = True
                    return True
                
                # Se debug estiver ativo, salva o frame para o usuário ver o que o OCR está tentando ler
                if self.config['app'].get('debug', False):
                    self.capture.save_debug_frame(frame, "debug_wait_start.png")
                
                print("[SISTEMA] LoL aberto, mas tempo de jogo não detectado. Verifique se o jogo está em primeiro plano.")
                time.sleep(5)
            
            print("[SISTEMA] Processo do LoL fechado. Voltando para espera...")
            
        return False

    def run_session(self):
        """Executa a lógica durante uma partida ativa."""
        last_time_processed = -1
        consecutive_zero_time = 0
        
        try:
            while self.in_game and self.is_lol_running():
                frame = self.capture.capture_frame()
                current_time = self.ocr.extract_game_time(frame)
                
                # Lógica de detecção de fim de jogo (se o tempo parar de ser lido por muito tempo)
                if current_time == 0:
                    consecutive_zero_time += 1
                    if consecutive_zero_time > 15: # ~45 segundos sem ler tempo
                        print("[SISTEMA] Partida encerrada ou tempo não legível.")
                        self.in_game = False
                        break
                else:
                    consecutive_zero_time = 0

                if current_time != last_time_processed and current_time > 0:
                    self.state.update_time(current_time)
                    last_time_processed = current_time
                    
                    print(f"[LIVE] Tempo: {int(current_time // 60)}:{int(current_time % 60):02d}")

                    # Gatilhos de Inteligência
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
                    print("[SISTEMA] Partida finalizada. Voltando para o modo de espera...")
                    time.sleep(10)
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
