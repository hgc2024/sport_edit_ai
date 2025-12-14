import sys
import os
sys.path.append(os.getcwd())
from utils.data_loader import get_game_stats

game_id = "41800406"
stats = get_game_stats(game_id)
print(stats)
