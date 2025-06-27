# dfs_optimizer/__init__.py
# Módulo de optimización DFS para MLB Betting Bot

from .optimize_lineup import optimize_lineup
from .player_stats_fetcher import get_mock_player_stats

__all__ = [
    'optimize_lineup',
    'get_mock_player_stats'
] 