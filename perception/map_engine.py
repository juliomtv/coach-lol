import cv2
import numpy as np

class MapEngine:
    def __init__(self):
        # Coordenadas relativas de objetivos comuns no minimapa (0.0 a 1.0)
        # Considerando o minimapa como um quadrado perfeito
        self.objectives = {
            "baron_nashor": (0.35, 0.35),
            "dragon": (0.65, 0.65),
            "blue_buff_top": (0.25, 0.45),
            "red_buff_top": (0.45, 0.25),
            "blue_buff_bot": (0.75, 0.55),
            "red_buff_bot": (0.55, 0.75)
        }

    def detect_enemy_icons(self, minimap_roi):
        """
        Detecta ícones de inimigos (geralmente círculos vermelhos ou ícones específicos).
        Esta é uma implementação simplificada usando detecção de cores.
        """
        # Converte para HSV para melhor detecção de cores
        hsv = cv2.cvtColor(minimap_roi, cv2.COLOR_BGR2HSV)
        
        # Range para vermelho (inimigos)
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.add(mask1, mask2)
        
        # Encontra contornos que podem ser ícones
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        enemies = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 20 < area < 500: # Filtro por tamanho de ícone no minimapa
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    enemies.append((cX, cY))
        
        return enemies

    def get_relative_position(self, pos, minimap_size):
        """Converte pixels do minimapa em posição relativa (0-1)."""
        x, y = pos
        w, h = minimap_size
        return (x / w, y / h)

    def analyze_map_state(self, minimap_roi):
        """Retorna um resumo do que está acontecendo no mapa."""
        h, w = minimap_roi.shape[:2]
        enemies = self.detect_enemy_icons(minimap_roi)
        
        state = {
            "enemy_count": len(enemies),
            "enemy_positions": [self.get_relative_position(e, (w, h)) for e in enemies],
            "hot_zones": []
        }
        
        # Identifica se há inimigos perto de objetivos
        for e_pos in state["enemy_positions"]:
            for obj_name, obj_pos in self.objectives.items():
                dist = np.sqrt((e_pos[0]-obj_pos[0])**2 + (e_pos[1]-obj_pos[1])**2)
                if dist < 0.1: # 10% de distância do mapa
                    state["hot_zones"].append(obj_name)
                    
        return state
