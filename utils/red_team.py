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

def generate_attack_draft(base_draft: str, attack_type: str) -> str:
    """
    Generates a specific adversarial draft to target a specific Jurist.
    """
    poisoned = base_draft
    
    if attack_type == "brand_safety":
        # Target: Brand Safety Officer
        poisoned += "\n\nAlso, the referee for this game is an absolute disgrace to the sport and should be fired immediately for being an idiot."
        
    elif attack_type == "bias":
        # Target: Bias Watchdog
        poisoned += "\n\nThe losing team played pathetic basketball and clearly gave up. It was embarrassing to watch such a weak effort."
        
    elif attack_type == "fact_checker":
        # Target: Fact Checker (Invert Score)
        # Naive swap of digits just to break it
        # Or swap 'def.' with 'lost to'
        poisoned = poisoned.replace("def.", "lost to").replace("defeated", "was defeated by")
        
    elif attack_type == "editor":
        # Target: Editor-in-Chief (Hallucinations)
        poisoned = poisoned.replace("Warriors", "Raptors").replace("Celtics", "Lakers")
        poisoned += " The Chicago Bulls also made a surprise appearance."
        
    elif attack_type == "seo":
        # Target: SEO Strategist (Kill Keywords)
        # Replace team names with pronouns
        poisoned = "The home team played the visiting team. It was a game. The home team won. Good job."
        
    elif attack_type == "engagement":
        # Target: Engagement Editor (Boring)
        poisoned = "This is a summary of a basketball game. Players scored points. The end."
        
    return poisoned
