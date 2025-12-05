import threading

class GameStateManager:
    def __init__(self):
        self.state = {
            "round": 0,
            "statistics": {},
            "states": {},
            "current_auctions": [],
            "previous_auctions": [],
            "bank_state": {},
            "pool": 0,
            "timestamp": 0
        }
        self.lock = threading.Lock()
    
    def update(self, data: dict):
        """Update game state with new data from bot."""
        with self.lock:
            self.state.update(data)
    
    def get_round(self) -> int:
        with self.lock:
            return self.state.get("round", 0)
    
    def get_statistics(self) -> dict:
        with self.lock:
            return self.state.get("statistics", {})
    
    def get_player_states(self) -> dict:
        with self.lock:
            return self.state.get("states", {})
    
    def get_player_count(self) -> int:
        return len(self.get_player_states())
    
    def get_mean_gold(self) -> float:
        return self.get_statistics().get('mean_gold', 0)
    
    def get_mean_points(self) -> float:
        return self.get_statistics().get('mean_points', 0)
    
    def get_current_auctions(self) -> list:
        with self.lock:
            return self.state.get("current_auctions", [])
    
    def get_previous_auctions(self) -> list:
        with self.lock:
            return self.state.get("previous_auctions", [])
    
    def get_pool(self) -> int:
        with self.lock:
            return self.state.get("pool", 0)

# Global instance
game_state_manager = GameStateManager()