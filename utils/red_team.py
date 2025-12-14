import random
import copy

def poison_data(stats_str: str) -> tuple[str, str]:
    """
    Injects adversarial noise into the stats string.
    Returns: (poisoned_stats, attack_description)
    """
    # Simple string manipulation since stats are passed as formatted text
    # We will look for "Points" or specific patterns.
    # Actually, the stats are passed as a string. Let's try to manipulate numbers.
    
    poisoned_stats = stats_str
    attack_type = "None"
    
    # Updated Attack Logic: Force Score Swapping which is subtler but higher impact
    if "HOME_TEAM_WINS: 1" in stats_str:
        poisoned_stats = stats_str.replace("HOME_TEAM_WINS: 1", "HOME_TEAM_WINS: 0")
        attack_type = "Flipped Winner (Home Wins -> Loss)"
    elif "HOME_TEAM_WINS: 0" in stats_str:
        poisoned_stats = stats_str.replace("HOME_TEAM_WINS: 0", "HOME_TEAM_WINS: 1")
        attack_type = "Flipped Winner (Home Loss -> Wins)"
    else:
        # Chaos Fallback
        poisoned_stats = "CHAOS MODE INJECTED: Home Team Scored 200 Points. Visitor Team Scored 0 Points. " + stats_str
        attack_type = "Chaos Header Injection"

    return poisoned_stats, attack_type
