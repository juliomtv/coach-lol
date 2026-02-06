import time
import sys
import os

# Adiciona o diretório atual ao path para importar o VoiceCoach
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from output.voice_output import VoiceCoach
    print("--- Teste de Áudio v2 (Subprocesso Isolado) ---")
    print("Este teste usa um método novo para evitar travamentos no Windows.")
    
    # Inicializa o coach de voz
    coach = VoiceCoach(rate=180, volume=1.0)
    
    print("\n[1/2] Testando primeira fala...")
    coach.speak("Iniciando teste do sistema de voz isolado.")
    
    # Espera um pouco para a fila processar
    time.sleep(4)
    
    print("\n[2/2] Testando segunda fala...")
    coach.speak("Se você ouviu as duas frases, o problema de áudio foi resolvido.")
    
    print("\nAguardando finalização...")
    time.sleep(5)
    
    print("\n--- FIM DO TESTE ---")
    print("Se o áudio ainda não saiu, tente o seguinte:")
    print("1. Verifique se o volume do Windows para o 'Python' não está no mudo no Mixer de Volume.")
    print("2. Tente executar o VS Code como Administrador.")

except Exception as e:
    print(f"\n[ERRO]: {e}")
    import traceback
    traceback.print_exc()
