import pyttsx3
import threading
import queue
import time

class VoiceCoach:
    def __init__(self, rate=150, volume=1.0):
        self.rate = rate
        self.volume = volume
        self.msg_queue = queue.Queue()
        self.is_running = True
        # Inicia a thread de processamento
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()

    def _process_queue(self):
        """
        Processa a fila de mensagens. 
        Nota: pyttsx3.init() deve preferencialmente rodar na mesma thread que runAndWait().
        """
        # Inicializa a engine dentro da thread
        engine = pyttsx3.init()
        engine.setProperty('rate', self.rate)
        engine.setProperty('volume', self.volume)

        while self.is_running:
            try:
                # Espera por uma mensagem na fila
                msg = self.msg_queue.get(timeout=0.5)
                
                # Fala a mensagem
                engine.say(msg)
                engine.runAndWait()
                
                self.msg_queue.task_done()
                
                # Pequena pausa para não encavalar
                time.sleep(0.1)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[ERRO VOZ]: Reiniciando engine de voz devido a: {e}")
                try:
                    engine = pyttsx3.init()
                    engine.setProperty('rate', self.rate)
                    engine.setProperty('volume', self.volume)
                except:
                    pass

    def speak(self, text):
        """Adiciona uma mensagem à fila de fala."""
        if text:
            self.msg_queue.put(text)

    def stop(self):
        self.is_running = False
        if self.thread.is_alive():
            self.thread.join(timeout=2)
