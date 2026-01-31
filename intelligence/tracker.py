import time

class JunglerTracker:
    def __init__(self):
        # Tempos de nascimento (em segundos de jogo)
        self.spawn_times = {
            "blue_buff": 100,  # 1:40
            "red_buff": 100,   # 1:40
            "scuttle": 210,    # 3:30
            "dragon_first": 300, # 5:00
            "herald": 480,     # 8:00
            "baron": 1200      # 20:00
        }
        
        # Intervalos de respawn (em segundos)
        self.respawn_intervals = {
            "small_camps": 135, # 2:15
            "buffs": 300,       # 5:00
            "dragon": 300,      # 5:00
            "baron": 360        # 6:00
        }
        
        self.alerts_fired = set()

    def get_time_alerts(self, game_time):
        """Retorna alertas baseados puramente no tempo de jogo."""
        alerts = []
        
        # 1. Alertas de Nascimento Inicial
        if 200 <= game_time <= 205 and "scuttle_spawn" not in self.alerts_fired:
            alerts.append("O Aronguejo vai nascer em 10 segundos. Garanta a visão do rio.")
            self.alerts_fired.add("scuttle_spawn")
            
        if 270 <= game_time <= 275 and "dragon_spawn_soon" not in self.alerts_fired:
            alerts.append("O primeiro Dragão nasce em 30 segundos. Prepare a rota inferior.")
            self.alerts_fired.add("dragon_spawn_soon")
            
        if 450 <= game_time <= 455 and "herald_spawn_soon" not in self.alerts_fired:
            alerts.append("O Arauto vai nascer em breve. Olho no topo.")
            self.alerts_fired.add("herald_spawn_soon")

        # 2. Alertas de Buffs (Ciclo inicial aproximado se não houver visão)
        # Buffs nascem 1:40 -> Morrem ~2:00 -> Nascem ~7:00
        if 400 <= game_time <= 405 and "buffs_second_spawn" not in self.alerts_fired:
            alerts.append("Seus buffs devem estar renascendo. Verifique sua selva.")
            self.alerts_fired.add("buffs_second_spawn")

        # 3. Alertas Recorrentes (Lembretes de farm)
        if game_time > 0 and game_time % 180 == 0: # A cada 3 minutos
            alerts.append("Não esqueça de limpar seus campos da selva para manter o XP.")

        return alerts

class JaxStrategy:
    @staticmethod
    def get_pathing_advice(game_time, side="blue"):
        """Sugere rotas baseadas no tempo de jogo."""
        if 0 < game_time < 90:
            return "Comece no seu Buff mais forte e planeje sua rota para o lado oposto."
        if 180 < game_time < 240:
            return "Procure gankar uma rota ou garantir o Aronguejo agora."
        return None

    @staticmethod
    def evaluate_objective_priority(game_time, enemy_count_bot, enemy_count_top):
        """Sugere qual objetivo focar."""
        if 300 <= game_time < 1200:
            if enemy_count_bot >= 3:
                return "Muitos inimigos no bot. Considere fazer o Arauto ou invadir a selva superior."
            if enemy_count_top >= 2:
                return "Inimigos no topo. O Dragão está livre, aproveite!"
        return None
