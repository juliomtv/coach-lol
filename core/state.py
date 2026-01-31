from dataclasses import dataclass, field
from typing import List, Dict, Optional
import time

@dataclass
class ChampionState:
    name: str
    level: int = 1
    items: List[str] = field(default_factory=list)
    position: Optional[tuple] = None
    last_seen: float = 0.0

@dataclass
class GameState:
    game_time: float = 0.0
    player_level: int = 1
    player_items: List[str] = field(default_factory=list)
    smite_status: bool = True
    smite_damage: int = 600
    enemy_jungler: Optional[ChampionState] = None
    allies: Dict[str, ChampionState] = field(default_factory=dict)
    enemies: Dict[str, ChampionState] = field(default_factory=dict)
    objectives: Dict[str, bool] = field(default_factory=dict)
    risk_level: str = "Low"

    def update_time(self, new_time: float):
        self.game_time = new_time

    def set_risk(self, level: str):
        if level in ["Low", "Medium", "High"]:
            self.risk_level = level
