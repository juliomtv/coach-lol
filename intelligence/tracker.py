import time

class JunglerTracker:
    def __init__(self):
        self.alerts_fired = set()
        self.enemy_jungler = "Desconhecido"
        self.matchup_advice_given = False

    def get_matchup_advice(self, enemy_name):
        self.enemy_jungler = enemy_name
        advices = {
            "Lee Sin": "Lee Sin é forte no early game. Evite trocas 1v1 no nível 3. Proteja suas entradas da selva.",
            "Master Yi": "Yi escala muito bem. Tente invadir e punir o farm dele cedo. Guarde seu E (Jax) para o momento que ele usar o Q.",
            "Graves": "Graves limpa a selva rápido e é saudável. Cuidado com o counter-gank. Tente lutar quando ele não tiver stacks de E.",
            "Nidalee": "Nidalee vai tentar te invadir. Mantenha a vida alta e desvie das lanças. Se ela errar o Q, você ganha a troca.",
            "Shaco": "Compre sentinelas de controle. Shaco vai tentar roubar seu segundo buff. Não use seu E antes dele aparecer.",
            "Kayn": "Kayn é fraco antes da forma. Tente lutar com ele nos caranguejos. Não deixe ele farmar orbes de graça.",
            "Warwick": "Não lute com Warwick se você estiver com pouca vida. Ele tem muito sustain. Peça ajuda para matá-lo.",
            "Kha'Zix": "Evite ficar isolado. Lute perto de tropas ou monstros da selva para anular o dano passivo dele."
        }
        return advices.get(enemy_name, f"Você está contra {enemy_name}. Foque em farmar e procure janelas de gank seguras.")

    def get_time_alerts(self, game_time):
        alerts = []
        
        # Alertas de Nascimento (30 segundos de antecedência)
        milestones = [
            (100, "Os campos da selva nasceram. Comece sua rota."),
            (180, "O Aronguejo nasce em 30 segundos. Prepare-se para disputar o rio."),
            (210, "Aronguejo nasceu! Garanta a visão."),
            (270, "O Dragão nasce em 30 segundos. Garanta prioridade no bot."),
            (300, "O Dragão está vivo!"),
            (450, "O Arauto nasce em 30 segundos. Olho no topo."),
            (480, "O Arauto está vivo!"),
            (1170, "O Barão Nashor nasce em 30 segundos. Prepare a visão.")
        ]

        for t, msg in milestones:
            if t <= game_time <= t + 5 and msg not in self.alerts_fired:
                alerts.append(msg)
                self.alerts_fired.add(msg)

        # Lembretes de Buffs (Respawn a cada 5 min)
        # Assumindo morte por volta de 2:10 e 7:10
        if 400 <= game_time <= 405 and "buffs_2" not in self.alerts_fired:
            alerts.append("Seus buffs vão renascer em breve. Planeje sua rota de volta.")
            self.alerts_fired.add("buffs_2")

        return alerts

class JaxStrategy:
    @staticmethod
    def get_combat_tip(enemy_jungler):
        if "Master Yi" in enemy_jungler:
            return "Dica: Use seu Contra-Ataque apenas quando ele começar a te bater com o E ativo."
        if "Lee Sin" in enemy_jungler:
            return "Dica: Salte em uma sentinela ou tropa se ele acertar a primeira parte do Q."
        return "Mantenha o farm alto para garantir sua Força da Trindade."
