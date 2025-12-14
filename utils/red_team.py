import re
import random

def poison_data(stats_str: str) -> tuple[str, str]:
    """
    Injects adversarial noise into the stats string using Regex.
    Returns: (poisoned_stats, attack_description)
    """
    poisoned_stats = stats_str
    
    # The format is "PlayerName (X pts, Y reb, Z ast)"
    # We can't flip winner directly as team scores/wins aren't in the text string.
    # So we manipulate player stats.
    
    attack_mode = random.choice(["inflate_star", "slump_star", "chaos"])
    
    # Regex to find all points: "(\d+) pts"
    matches = list(re.finditer(r"(\d+) pts", stats_str))
    
    if attack_mode == "inflate_star" and matches:
        # Pick a random player and add 50 points
        target = random.choice(matches)
        old_pts = int(target.group(1))
        new_pts = old_pts + 50
        # We must replace only THIS instance. 
        # Since strings are immutable and we have indices, we can slice.
        start, end = target.span(1)
        poisoned_stats = stats_str[:start] + str(new_pts) + stats_str[end:]
        return poisoned_stats, f"Star Inflation ({old_pts} -> {new_pts} pts)"
        
    elif attack_mode == "slump_star" and matches:
        # Pick a random player and set to 0 points
        target = random.choice(matches)
        old_pts = int(target.group(1))
        new_pts = 0
        start, end = target.span(1)
        poisoned_stats = stats_str[:start] + str(new_pts) + stats_str[end:]
        return poisoned_stats, f"Star Slump ({old_pts} -> {new_pts} pts)"

    # Fallback / Chaos
    return "CHAOS MODE INJECTED: Home Team Scored 200 Points. " + stats_str, "Chaos Header (Fallback)"
