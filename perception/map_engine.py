import cv2
import numpy as np

class MapEngine:
    def __init__(self):
        # Coordenadas relativas precisas baseadas no mapa explicado (x, y) de 0.0 a 1.0
        # O minimapa no LoL é espelhado/rotacionado dependendo do lado, 
        # mas aqui usamos uma referência padrão de 1920x1080 (canto inferior direito)
        self.locations = {
            "nexus_blue": (0.05, 0.95),
            "nexus_red": (0.95, 0.05),
            # Selva Azul (Inferior)
            "blue_buff_blue": (0.28, 0.76),
            "grompe_blue": (0.20, 0.72),
            "lobos_blue": (0.35, 0.68),
            "red_buff_blue": (0.52, 0.82),
            "acuaminas_blue": (0.45, 0.78),
            "krugues_blue": (0.62, 0.88),
            # Selva Vermelha (Superior)
            "blue_buff_red": (0.72, 0.24),
            "grompe_red": (0.80, 0.28),
            "lobos_red": (0.65, 0.32),
            "red_buff_red": (0.48, 0.18),
            "acuaminas_red": (0.55, 0.22),
            "krugues_red": (0.38, 0.12),
            # Objetivos de Rio
            "dragon_pit": (0.75, 0.75),
            "baron_pit": (0.25, 0.25),
            "scuttle_bot": (0.65, 0.65),
            "scuttle_top": (0.35, 0.35)
        }

    def detect_enemy_icons(self, minimap_roi):
        if minimap_roi is None or minimap_roi.size == 0:
            return []

        hsv = cv2.cvtColor(minimap_roi, cv2.COLOR_BGR2HSV)
        
        # Inimigos (Vermelho)
        lower_red1 = np.array([0, 150, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 150, 100])
        upper_red2 = np.array([180, 255, 255])
        
        mask = cv2.add(cv2.inRange(hsv, lower_red1, upper_red1), 
                       cv2.inRange(hsv, lower_red2, upper_red2))
        
        # Filtro morfológico para remover tropas
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        enemies = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Aumentando o limite para garantir que tropas não entrem (campeões > 60)
            if 60 < area < 800:
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    enemies.append((cX, cY))
        
        return enemies

    def get_location_name(self, rel_x, rel_y):
        """Retorna o nome da localização mais próxima."""
        min_dist = 1.0
        closest = "Rio/Desconhecido"
        for name, pos in self.locations.items():
            dist = np.sqrt((rel_x - pos[0])**2 + (rel_y - pos[1])**2)
            if dist < 0.1: # Raio de 10% do mapa
                min_dist = dist
                closest = name
        return closest

    def analyze_map_state(self, minimap_roi):
        h, w = minimap_roi.shape[:2]
        enemies = self.detect_enemy_icons(minimap_roi)
        
        enemy_data = []
        for e in enemies:
            rel_x, rel_y = e[0]/w, e[1]/h
            loc = self.get_location_name(rel_x, rel_y)
            enemy_data.append({"pos": (rel_x, rel_y), "location": loc})
            
        return {
            "enemy_count": len(enemies),
            "enemies": enemy_data
        }
