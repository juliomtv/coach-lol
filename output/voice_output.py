import pyttsx3
import threading
import queue
import time
import sys

class VoiceCoach:
    def __init__(self, rate=150, volume=1.0):
        self.rate = rate
        self.volume = volume
        self.msg_queue = queue.Queue()
        self.is_running = True
        
        # Tentativa de inicialização imediata para checar drivers
        try:
            temp_engine = pyttsx3.init()
            del temp_engine
        except Exception as e:
            print(f"[AVISO]: Erro ao testar driver de voz: {e}")

        # Inicia a thread de processamento
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()

    def _process_queue(self):
        """
        Thread dedicada para processar a fala. 
        Usar uma única instância da engine e tratar erros de runtime.
        """
        engine = None
        
        def init_engine():
            nonlocal engine
            try:
                if engine:
                    del engine
                engine = pyttsx3.init()
                engine.setProperty('rate', self.rate)
                engine.setProperty('volume', self.volume)
                return True
            except Exception as e:
                print(f"[ERRO]: Falha ao inicializar engine de voz: {e}")
                return False

        if not init_engine():
            print("[CRÍTICO]: O sistema de voz não pôde ser iniciado.")

        while self.is_running:
            try:
                # Pega a mensagem da fila
                try:
                    msg = self.msg_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                print(f"[AUDIO-LOG] Falando: {msg}")
                
                # Garante que a engine existe
                if engine is None:
                    init_engine()
                
                if engine:
                    engine.say(msg)
                    engine.runAndWait()
                    # Pequeno delay após falar para estabilizar o driver
                    time.sleep(0.2)
                
                self.msg_queue.task_done()

            except Exception as e:
                print(f"[ERRO NA FALA]: {e}")
                # Se der erro, tenta resetar a engine para a próxima mensagem
                time.sleep(1)
                init_engine()

    def speak(self, text):
        """Adiciona uma mensagem à fila de fala e garante que seja string."""
        if text and self.is_running:
            # Limpa o texto de caracteres estranhos que podem travar o OCR/Voz
            clean_text = str(text).strip()
            if clean_text:
                self.msg_queue.put(clean_text)

    def stop(self):
        self.is_running = False
        print("[SISTEMA] Parando serviço de voz...")
        # Não damos join para não travar o encerramento se a engine estiver ocupada
