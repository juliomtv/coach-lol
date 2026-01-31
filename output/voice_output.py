import pyttsx3
import threading
import queue

class VoiceCoach:
    def __init__(self, rate=150, volume=1.0):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        self.msg_queue = queue.Queue()
        self.is_running = True
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()

    def _process_queue(self):
        while self.is_running:
            try:
                msg = self.msg_queue.get(timeout=1)
                self.engine.say(msg)
                self.engine.runAndWait()
                self.msg_queue.task_done()
            except queue.Empty:
                continue

    def speak(self, text):
        """Adiciona uma mensagem à fila de fala sem bloquear o loop principal."""
        print(f"[COACH VOICE]: {text}")
        self.msg_queue.put(text)

    def stop(self):
        self.is_running = False
        self.thread.join()
