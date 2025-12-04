class GameStateManager:
    def __init__(self):
        self.state = {"round": 0, "statistics": {}, "states": {}}
    
    def update(self, data: dict):
        """Update game state with new data."""
        self.state.update(data)
    
    def get_round(self) -> int:
        return self.state.get("round", 0)
    
    def get_statistics(self) -> dict:
        return self.state.get("statistics", {})
    
    def get_player_states(self) -> dict:
        return self.state.get("states", {})
    
    def get_player_count(self) -> int:
        return len(self.get_player_states())
    
    def get_mean_gold(self) -> float:
        return self.get_statistics().get('mean_gold', 0)
    
    def get_mean_points(self) -> float:
        return self.get_statistics().get('mean_points', 0)

# Global instance
game_state_manager = GameStateManager()

