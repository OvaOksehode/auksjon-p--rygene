import random
import os
import time
import sys
from typing import Dict, Any
import numpy as np

# Add the parent directory to the path so we can import dnd_auction_game
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dnd_auction_game import AuctionGameClient


class StreamingDashboardAgent:
    def __init__(self, dashboard_host="localhost", dashboard_port=8001):
        self.dashboard_host = dashboard_host
        self.dashboard_port = dashboard_port
        self.game_data_history = []
        
    def test_dashboard_connection(self):
        """Test if dashboard is reachable"""
        try:
            import requests
            response = requests.get(f"http://{self.dashboard_host}:{self.dashboard_port}/", timeout=5)
            if response.status_code == 200:
                print(f"✅ Dashboard is reachable at {self.dashboard_host}:{self.dashboard_port}")
                return True
            else:
                print(f"❌ Dashboard returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot reach dashboard: {e}")
            return False
    
    def send_to_dashboard_sync(self, data: Dict[str, Any]):
        """Send data to dashboard via HTTP POST"""
        try:
            import requests
            response = requests.post(
                f"http://{self.dashboard_host}:{self.dashboard_port}/api/game-data",
                json={"data": data},
                timeout=5
            )
            if response.status_code == 200:
                print(f"✅ Sent game data to dashboard (Round {data.get('round', 'N/A')})")
            else:
                print(f"❌ Failed to send data: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to send data to dashboard: {e}")
    
    def calculate_auction_expected_value(self, auction: Dict[str, Any]) -> float:
        """Calculate expected value for an auction"""
        average_roll_for_die = {
            2: 1.5, 3: 2.0, 4: 2.5, 6: 3.5, 8: 4.5, 
            10: 5.5, 12: 6.5, 20: 10.5
        }
        return (average_roll_for_die[auction["die"]] * auction["num"]) + auction["bonus"]
    
    def process_game_data(self, agent_id: str, current_round: int, states: Dict, 
                         auctions: Dict, prev_auctions: Dict, bank_state: Dict) -> Dict:
        """Process and stream game data to dashboard"""
        
        # Calculate statistics
        all_gold = [state["gold"] for state in states.values()]
        all_points = [state["points"] for state in states.values()]
        
        # Process current auctions
        current_auctions_data = []
        for auction_id, auction in auctions.items():
            expected_value = self.calculate_auction_expected_value(auction)
            current_auctions_data.append({
                "id": auction_id,
                "die": auction["die"],
                "num": auction["num"],
                "bonus": auction["bonus"],
                "expected_value": expected_value,
                "description": f"{auction['num']}d{auction['die']}+{auction['bonus']}"
            })
        
        # Process previous auctions with results
        prev_auctions_data = []
        for auction_id, auction in prev_auctions.items():
            bids = auction.get("bids", [])
            if bids:
                winning_bid = bids[0]
                prev_auctions_data.append({
                    "id": auction_id,
                    "winning_agent": winning_bid["a_id"],
                    "winning_bid": winning_bid["gold"],
                    "reward": auction["reward"],
                    "num_bids": len(bids),
                    "expected_value": self.calculate_auction_expected_value(auction)
                })
        
        # Create comprehensive game state
        game_state = {
            "timestamp": time.time(),
            "round": current_round,
            "agent_id": agent_id,
            "states": {
                agent_id: states[agent_id] for agent_id in states.keys()
            },
            "statistics": {
                "total_agents": len(states),
                "mean_gold": float(np.mean(all_gold)),
                "std_gold": float(np.std(all_gold)),
                "mean_points": float(np.mean(all_points)),
                "std_points": float(np.std(all_points)),
                "max_gold": max(all_gold),
                "max_points": max(all_points)
            },
            "current_auctions": current_auctions_data,
            "previous_auctions": prev_auctions_data,
            "bank_state": {
                "gold_income": bank_state["gold_income_per_round"][0] if bank_state["gold_income_per_round"] else 0,
                "interest_rate": bank_state["bank_interest_per_round"][0] if bank_state["bank_interest_per_round"] else 0,
                "bank_limit": bank_state["bank_limit_per_round"][0] if bank_state["bank_limit_per_round"] else 0
            }
        }
        
        # Store in history
        self.game_data_history.append(game_state)
        
        # Send to dashboard
        self.send_to_dashboard_sync(game_state)
        
        # Return empty bids (this agent just observes)
        return {}


# Global streaming agent instance
streaming_agent = StreamingDashboardAgent()

def streaming_agent_callback(agent_id: str, current_round: int, states: Dict, 
                           auctions: Dict, prev_auctions: Dict, bank_state: Dict):
    """Main callback function for the streaming agent"""
    return streaming_agent.process_game_data(agent_id, current_round, states, 
                                           auctions, prev_auctions, bank_state)


if __name__ == "__main__":
    # Initialize streaming agent
    streaming_agent = StreamingDashboardAgent()
    
    # Test dashboard connection
    if not streaming_agent.test_dashboard_connection():
        print("❌ Dashboard not reachable. Please start the dashboard server first.")
        print("Run: python dashboard_server.py")
        sys.exit(1)
    
    # Game client setup
    host = "localhost"
    agent_name = f"streaming_dashboard_{random.randint(1, 1000)}"
    player_id = "dashboard_observer"
    port = 8000
    
    print(f"🎮 Connecting to auction server at {host}:{port}")
    game = AuctionGameClient(host=host,
                            agent_name=agent_name,
                            player_id=player_id,
                            port=port)
    
    try:
        # Run the game with streaming
        print("🚀 Starting streaming agent...")
        game.run(streaming_agent_callback)
    except KeyboardInterrupt:
        print("<interrupt - shutting down>")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("<streaming agent done>")
