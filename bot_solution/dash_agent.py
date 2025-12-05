from datetime import datetime
import random
import os
from collections import defaultdict
from dnd_auction_game import AuctionGameClient

class EliteAuctionAgent:
    def __init__(self, log_dir: str = "bot_solution/logs"):
        self.bid_history = defaultdict(list)  # auction_id -> [winning_bids]
        self.opponent_aggression = defaultdict(lambda: 1.0)  # agent_id -> aggression multiplier
        self.rounds_played = 0
        self.consecutive_losses = 0
        self.my_wins = 0
        
        # Setup log file
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"elite_agent_{timestamp}.txt")
        with open(self.log_file, "w") as f:
            f.write("Round,Gold,Points,Strategy,TargetAuction,BidAmount,ExpectedValue\n")
    
    def _log_round(self, round_num, my_state, strategy, target_id, bid, expected_val):
        with open(self.log_file, "a") as f:
            f.write(f"{round_num},{my_state['gold']},{my_state['points']},{strategy},{target_id},{bid},{expected_val:.2f}\n")
    
    def _expected_value(self, auction):
        """Calculate expected points from auction"""
        return auction["num"] * (auction["die"] + 1) / 2 + auction["bonus"]
    
    def _estimate_winning_bid(self, auction_id, auction, prev_auctions, states, agent_id):
        """Estimate what it takes to win this auction"""
        expected_pts = self._expected_value(auction)
        
        # Base estimate from historical data
        base_estimate = 50
        if self.bid_history[auction_id]:
            base_estimate = sum(self.bid_history[auction_id]) / len(self.bid_history[auction_id])
        
        # Look at similar auctions from previous rounds
        similar_bids = []
        if prev_auctions:
            for prev_auction in prev_auctions.values():
                prev_expected = self._expected_value(prev_auction)
                if abs(prev_expected - expected_pts) < expected_pts * 0.2:
                    if prev_auction.get("bids"):
                        winning_bid = prev_auction["bids"][0].get("gold", 0)
                        similar_bids.append(winning_bid)
        
        if similar_bids:
            base_estimate = sum(similar_bids) / len(similar_bids)
        
        # Adjust for opponent aggression
        max_opponent_aggression = 1.0
        for opp_id in states:
            if opp_id != agent_id:
                max_opponent_aggression = max(max_opponent_aggression, self.opponent_aggression[opp_id])
        
        # Factor in market dynamics
        estimated_bid = base_estimate * max_opponent_aggression
        
        # If we've been losing, bid more aggressively
        if self.consecutive_losses > 2:
            estimated_bid *= 1.2 + (self.consecutive_losses - 2) * 0.1
        
        return estimated_bid
    
    def _calculate_roi(self, auction, bid_amount, bank_interest):
        """Calculate ROI considering points value and opportunity cost"""
        expected_pts = self._expected_value(auction)
        
        # Lost gold opportunity cost (50% loss + missed bank interest)
        opportunity_cost = bid_amount * 0.5 * (1 + bank_interest)
        
        # Net return: points gained vs gold lost
        # Assume 1 point = pool_gold / total_points ratio (dynamic pricing)
        # For now, use a heuristic: points are worth more early, less late
        point_value = 100 / (1 + self.rounds_played * 0.05)  # Diminishing point value
        
        expected_return = expected_pts * point_value
        net_roi = (expected_return - opportunity_cost) / bid_amount if bid_amount > 0 else 0
        
        return net_roi
    
    def _portfolio_bidding(self, auctions, prev_auctions, my_gold, states, agent_id, bank_interest):
        """Bid on multiple auctions to diversify risk"""
        auction_scores = []
        
        for a_id, auction in auctions.items():
            expected_pts = self._expected_value(auction)
            est_winning_bid = self._estimate_winning_bid(a_id, auction, prev_auctions, states, agent_id)
            
            # Cap bid at affordable amount
            est_winning_bid = min(est_winning_bid, my_gold * 0.4)  # Don't bet more than 40% on one auction
            
            roi = self._calculate_roi(auction, est_winning_bid, bank_interest)
            
            # Score combines ROI, expected value, and affordability
            score = roi * expected_pts * (1.0 if est_winning_bid <= my_gold else 0.1)
            
            auction_scores.append({
                'id': a_id,
                'score': score,
                'bid': est_winning_bid,
                'expected_pts': expected_pts,
                'roi': roi
            })
        
        # Sort by score
        auction_scores.sort(key=lambda x: x['score'], reverse=True)
        
        return auction_scores
    
    def elite_strategy(
        self,
        agent_id: str,
        round: int,
        states: dict,
        auctions: dict,
        prev_auctions: dict,
        pool: int,
        prev_pool_buys: dict,
        bank_state: dict
    ):
        self.rounds_played = round
        my_state = states[agent_id]
        my_gold = my_state["gold"]
        my_points = my_state["points"]
        
        # Bank parameters
        bank_interest = bank_state["bank_interest_per_round"][0] if bank_state["bank_interest_per_round"] else 0
        bank_limit = bank_state["bank_limit_per_round"][0] if bank_state["bank_limit_per_round"] else 10000
        
        # Update bid history and opponent tracking
        if prev_auctions:
            for prev_id, prev_auction in prev_auctions.items():
                if prev_auction.get("bids"):
                    winner = prev_auction["bids"][0]
                    winner_id = winner.get("a_id")
                    winning_bid = winner.get("gold", 0)
                    
                    self.bid_history[prev_id].append(winning_bid)
                    
                    # Track opponent aggression
                    if winner_id != agent_id:
                        expected_pts = self._expected_value(prev_auction)
                        # High bid per point = aggressive
                        bid_per_point = winning_bid / expected_pts if expected_pts > 0 else 1
                        self.opponent_aggression[winner_id] = 0.8 * self.opponent_aggression[winner_id] + 0.2 * (bid_per_point / 10)
                    
                    # Track my performance
                    if winner_id == agent_id:
                        self.consecutive_losses = 0
                        self.my_wins += 1
                    else:
                        # Check if I bid on this
                        my_bid = next((b.get("gold", 0) for b in prev_auction.get("bids", []) if b.get("a_id") == agent_id), 0)
                        if my_bid > 0:
                            self.consecutive_losses += 1
        
        bids = {}
        strategy = "aggressive"
        
        if not auctions:
            return {"bids": bids, "pool": 0}
        
        # Get portfolio of auctions ranked by attractiveness
        auction_scores = self._portfolio_bidding(auctions, prev_auctions, my_gold, states, agent_id, bank_interest)
        
        # Determine bidding strategy based on game state
        total_budget = my_gold * 0.85  # Reserve 15% for bank interest and emergencies
        
        if my_points < 10:
            # EARLY GAME: Focus on securing points efficiently
            strategy = "point_accumulation"
            # Bid aggressively on top 2-3 auctions
            num_targets = min(3, len(auction_scores))
            budget_per_auction = total_budget / num_targets
            
            for i in range(num_targets):
                auction = auction_scores[i]
                # Overbid estimate by 15% to ensure wins
                bid_amount = int(min(budget_per_auction, auction['bid'] * 1.15))
                if bid_amount >= 1:
                    bids[auction['id']] = bid_amount
                    
        elif my_gold < 1000:
            # LOW GOLD: Conservative, high-efficiency bids only
            strategy = "conservative"
            # Only bid on best ROI auction
            best = auction_scores[0]
            bid_amount = int(min(total_budget, best['bid'] * 1.1))
            if bid_amount >= 1:
                bids[best['id']] = bid_amount
                
        else:
            # MID/LATE GAME: Maximize points accumulation
            strategy = "maximize_points"
            # Spread bids across top auctions
            num_targets = min(4, len(auction_scores))
            allocated = 0
            
            for i in range(num_targets):
                auction = auction_scores[i]
                # Allocate proportional to expected value
                weight = auction['expected_pts'] / sum(a['expected_pts'] for a in auction_scores[:num_targets])
                budget = total_budget * weight
                
                # Bid slightly above estimate
                bid_amount = int(min(budget, auction['bid'] * 1.12))
                if bid_amount >= 1 and allocated + bid_amount <= total_budget:
                    bids[auction['id']] = bid_amount
                    allocated += bid_amount
        
        # Pool strategy: Buy gold when it's efficient
        pool_spend = 0
        if pool > 0 and my_points > 20:
            # Calculate pool efficiency: gold per point
            estimated_buyers = max(1, len([p for p in prev_pool_buys.values() if p > 0]))
            gold_per_point = pool / (my_points + sum(prev_pool_buys.values()) + 1)
            
            # If efficiency is good (> 50 gold per point) and we have spare points
            if gold_per_point > 50 and my_points > 30:
                pool_spend = min(5, my_points - 25)  # Keep 25 points buffer
        
        # Emergency gold acquisition
        if my_gold < 300 and my_points > 15:
            pool_spend = min(3, my_points - 10)
        
        # Log the round
        target_id = list(bids.keys())[0] if bids else "none"
        bid_val = bids.get(target_id, 0)
        expected_val = auction_scores[0]['expected_pts'] if auction_scores else 0
        self._log_round(round, my_state, strategy, target_id, bid_val, expected_val)
        
        return {"bids": bids, "pool": pool_spend}


if __name__ == "__main__":
    host = "localhost"
    port = 8000
    agent_name = f"elite_destroyer_{random.randint(1000,9999)}"
    player_id = "elite_player_id"
    
    game = AuctionGameClient(
        host=host,
        agent_name=agent_name,
        player_id=player_id,
        port=port
    )
    
    agent = EliteAuctionAgent()
    
    try:
        game.run(agent.elite_strategy)
    except KeyboardInterrupt:
        print("<interrupt - shutting down>")
    
    print("<game is done>")