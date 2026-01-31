import cv2
import numpy as np

class MapEngine:
    def __init__(self):
        # Coordenadas relativas de objetivos (0.0 a 1.0)
        self.objectives = {
            "baron_nashor": (0.35, 0.35),
            "dragon": (0.65, 0.65),
            "herald": (0.35, 0.35) # Mesma área do Barão antes dos 20min
        }

    def detect_enemy_icons(self, minimap_roi):
        """
        Detecta ícones de inimigos ignorando tropas.
        Tropas são pequenas e numerosas; campeões têm ícones circulares maiores e bordas distintas.
        """
        if minimap_roi is None or minimap_roi.size == 0:
            return []

        hsv = cv2.cvtColor(minimap_roi, cv2.COLOR_BGR2HSV)
        
        # Inimigos no LoL têm borda vermelha/contorno específico
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.add(mask1, mask2)
        
        # Limpeza morfológica para remover ruído (tropas pequenas)
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        enemies = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # No minimapa, ícones de campeões são significativamente maiores que tropas
            # Tropas costumam ter área < 15-20 pixels. Campeões > 40.
            if 40 < area < 600: 
                # Verificar circularidade (campeões são círculos, tropas são pontos/quadrados)
                perimeter = cv2.arcLength(cnt, True)
                if perimeter == 0: continue
                circularity = 4 * np.pi * (area / (perimeter * perimeter))
                
                if circularity > 0.6: # Filtro de forma circular
                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                        enemies.append((cX, cY))
        
        return enemies

    def get_relative_position(self, pos, minimap_size):
        x, y = pos
        w, h = minimap_size
        return (x / w, y / h)

    def analyze_map_state(self, minimap_roi):
        h, w = minimap_roi.shape[:2]
        enemies = self.detect_enemy_icons(minimap_roi)
        
        state = {
            "enemy_count": len(enemies),
            "enemy_positions": [self.get_relative_position(e, (w, h)) for e in enemies],
            "hot_zones": []
        }
        
        for e_pos in state["enemy_positions"]:
            for obj_name, obj_pos in self.objectives.items():
                dist = np.sqrt((e_pos[0]-obj_pos[0])**2 + (e_pos[1]-obj_pos[1])**2)
                if dist < 0.12: 
                    state["hot_zones"].append(obj_name)
                    
        return state
