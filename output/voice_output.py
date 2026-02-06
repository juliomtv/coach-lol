import os
import subprocess
import threading
import queue
import time
import sys

class VoiceCoach:
    def __init__(self, rate=180, volume=1.0):
        self.rate = rate
        self.volume = volume
        self.msg_queue = queue.Queue()
        self.is_running = True
        
        # Cria um script auxiliar temporário para falar via subprocesso
        # Isso isola o driver de áudio do processo principal do jogo
        self.voice_script = os.path.join(os.path.dirname(__file__), "speaker_node.py")
        self._create_speaker_node()

        # Inicia a thread de monitoramento da fila
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()

    def _create_speaker_node(self):
        """Cria um script Python independente apenas para lidar com a voz."""
        content = f"""
import pyttsx3
import sys

def speak(text, rate, volume):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', {self.rate})
        engine.setProperty('volume', {self.volume})
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"Erro no speaker node: {{e}}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text_to_speak = " ".join(sys.argv[1:])
        speak(text_to_speak, {self.rate}, {self.volume})
"""
        with open(self.voice_script, "w", encoding="utf-8") as f:
            f.write(content)

    def _process_queue(self):
        """Processa a fila chamando o subprocesso de voz."""
        while self.is_running:
            try:
                msg = self.msg_queue.get(timeout=0.5)
                
                # Chama o script de voz como um processo independente
                # Isso força o Windows a gerenciar o áudio de forma isolada
                try:
                    subprocess.run(
                        [sys.executable, self.voice_script, msg],
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                        timeout=15
                    )
                except Exception as e:
                    print(f"[ERRO SUBPROCESSO VOZ]: {e}")
                
                self.msg_queue.task_done()
                time.sleep(0.1)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[ERRO FILA VOZ]: {e}")

    def speak(self, text):
        """Adiciona uma mensagem à fila de fala."""
        if text and self.is_running:
            clean_text = str(text).strip()
            if clean_text:
                # Mostra no console imediatamente
                print(f"[AUDIO-QUEUE] {clean_text}")
                self.msg_queue.put(clean_text)

    def stop(self):
        self.is_running = False
        # Limpa o script temporário
        try:
            if os.path.exists(self.voice_script):
                os.remove(self.voice_script)
        except:
            pass
