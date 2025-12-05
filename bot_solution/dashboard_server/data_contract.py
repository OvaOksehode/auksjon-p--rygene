from typing import Dict, List, Any, TypedDict

class AuctionData(TypedDict):
    """Structure for auction information"""
    id: str
    die: int
    num: int
    bonus: int
    expected_value: float
    description: str

class PreviousAuctionData(TypedDict):
    """Structure for completed auction results"""
    id: str
    winning_agent: str
    winning_bid: int
    reward: int
    num_bids: int
    expected_value: float

class BankState(TypedDict):
    """Structure for bank/economy information"""
    gold_income: int
    interest_rate: float
    bank_limit: int

class Statistics(TypedDict):
    """Structure for aggregate statistics"""
    total_agents: int
    mean_gold: float
    std_gold: float
    mean_points: float
    std_points: float
    max_gold: int
    max_points: int

class PlayerState(TypedDict):
    """Structure for individual player state"""
    gold: int
    points: int

class GameStateData(TypedDict):
    """Complete game state sent from bot to dashboard"""
    timestamp: float
    round: int
    agent_id: str
    states: Dict[str, PlayerState]  # agent_id -> state
    statistics: Statistics
    current_auctions: List[AuctionData]
    previous_auctions: List[PreviousAuctionData]
    bank_state: BankState
    pool: int

