import time

class JunglerTracker:
    def __init__(self):
        self.last_seen_pos = None
        self.last_seen_time = 0
        self.predicted_zone = "Unknown"
        self.camps_respawn = {
            "blue_buff": 300,
            "red_buff": 300,
            "scuttle": 150
        }

    def update_enemy_position(self, pos, game_time):
        self.last_seen_pos = pos
        self.last_seen_time = game_time

    def predict_enemy_location(self, current_game_time):
        """Lógica probabilística baseada no tempo desde a última visualização."""
        if self.last_seen_pos is None:
            return "Unknown (Probable Full Clear Start)"
        
        elapsed = current_game_time - self.last_seen_time
        
        if elapsed < 10:
            return f"Near {self.last_seen_pos}"
        elif elapsed < 30:
            return f"Transitioning from {self.last_seen_pos}"
        else:
            return "Missing - Check Objectives/Counter-gank"

class JaxStrategy:
    @staticmethod
    def get_power_spike_advice(level, items):
        if level == 6:
            return "Power spike nível 6 atingido. Procure trocas estendidas com a passiva da ult."
        if any("Trinity Force" in item for item in items):
            return "Trinity Force completa. Você é extremamente forte em 1v1 agora."
        return None

    @staticmethod
    def evaluate_risk(player_hp, enemy_pos_risk, game_time):
        if enemy_pos_risk == "High" or player_hp < 30:
            return "High"
        return "Low"
