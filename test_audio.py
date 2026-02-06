import time
import sys
import os

# Adiciona o diretório atual ao path para importar o VoiceCoach
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from output.voice_output import VoiceCoach
    print("--- Teste de Áudio do Coach-LoL ---")
    
    # Inicializa o coach de voz
    coach = VoiceCoach(rate=180, volume=1.0)
    
    print("\n1. Enviando primeira mensagem...")
    coach.speak("Teste de áudio iniciado. Se você está ouvindo isso, o driver está funcionando.")
    
    time.sleep(3)
    
    print("2. Enviando segunda mensagem...")
    coach.speak("O sistema de voz está pronto para a partida. Boa sorte no Rift!")
    
    print("\nAguardando 5 segundos para finalizar as falas...")
    time.sleep(5)
    
    print("\nTeste concluído. Se você NÃO ouviu nada, mas viu os prints acima, verifique se o volume do Windows está alto e se o dispositivo de saída correto está selecionado.")

except Exception as e:
    print(f"\n[ERRO CRÍTICO NO TESTE]: {e}")
    import traceback
    traceback.print_exc()
