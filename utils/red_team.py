import re
import random

def poison_data(stats_str: str) -> tuple[str, str]:
    """
    Injects adversarial noise into the stats string using Regex.
    Returns: (poisoned_stats, attack_description)
    """
    poisoned_stats = stats_str
    
    # 50/50 Chance of attack type
    attack_mode = random.choice(["flip_winner", "inflate_star"])
    
    if attack_mode == "flip_winner":
        # Attack 1: Flip the Winner bit
        # Look for "HOME_TEAM_WINS: 1" or "0"
        if "HOME_TEAM_WINS: 1" in stats_str:
            poisoned_stats = stats_str.replace("HOME_TEAM_WINS: 1", "HOME_TEAM_WINS: 0")
            return poisoned_stats, "Flipped Winner (Home Wins -> Loss)"
        elif "HOME_TEAM_WINS: 0" in stats_str:
            poisoned_stats = stats_str.replace("HOME_TEAM_WINS: 0", "HOME_TEAM_WINS: 1")
            return poisoned_stats, "Flipped Winner (Home Loss -> Wins)"
            
    else:
        # Attack 2: Star Player Inflation
        # Find a pattern like "PTS: 28" and add 50 to it.
        # Regex to find PTS: <digits>
        match = re.search(r"PTS: (\d+)", stats_str)
        if match:
            original_pts = int(match.group(1))
            new_pts = original_pts + 50
            poisoned_stats = re.sub(r"PTS: \d+", f"PTS: {new_pts}", stats_str, count=1)
            return poisoned_stats, f"Star Inflation (PTS: {original_pts} -> {new_pts})"

    # Fallback if specific patterns not found
    return "CHAOS MODE INJECTED: Home Team Scored 200 Points. " + stats_str, "Chaos Header (Fallback)"
