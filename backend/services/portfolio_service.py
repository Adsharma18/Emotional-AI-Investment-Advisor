from schemas import PortfolioItem, PortfolioAllocationResponse

PORTFOLIO_BASELINES = {
    "Conservative": [
        {"asset_class": "Equities (Global Stocks)", "percentage": 20.0, "description": "High-quality, dividend-paying global stocks for long-term growth."},
        {"asset_class": "Fixed Income (Bonds)", "percentage": 60.0, "description": "Government and corporate bonds providing stability and steady yield."},
        {"asset_class": "Commodities (Gold)", "percentage": 10.0, "description": "Inflation hedge and defensive asset during market stress."},
        {"asset_class": "Cash Equivalents", "percentage": 10.0, "description": "Highly liquid, risk-free assets for immediate flexibility."}
    ],
    "Moderate": [
        {"asset_class": "Equities (Global Stocks)", "percentage": 60.0, "description": "Diversified index funds targeting capital appreciation."},
        {"asset_class": "Fixed Income (Bonds)", "percentage": 25.0, "description": "Intermediate-term bonds offering balanced risk/reward."},
        {"asset_class": "Commodities (Gold)", "percentage": 10.0, "description": "Inflation protection and portfolio diversification."},
        {"asset_class": "Cash Equivalents", "percentage": 5.0, "description": "Reserve cash for liquidity and adjustments."}
    ],
    "Aggressive": [
        {"asset_class": "Equities (Global Stocks)", "percentage": 80.0, "description": "Growth-oriented global equities for maximum long-term growth."},
        {"asset_class": "Fixed Income (Bonds)", "percentage": 10.0, "description": "Short-duration bonds for minor safety buffers."},
        {"asset_class": "Commodities (Gold)", "percentage": 5.0, "description": "Minimal hedge asset allocation."},
        {"asset_class": "Speculative (Crypto/Tech)", "percentage": 5.0, "description": "High-risk, high-reward digital assets or sector plays."}
    ]
}

class PortfolioService:
    @staticmethod
    def get_allocation(risk_profile: str, emotion: str, fear_score: float, greed_score: float) -> PortfolioAllocationResponse:
        baseline_profile = risk_profile if risk_profile in PORTFOLIO_BASELINES else "Moderate"
        base_items = PORTFOLIO_BASELINES[baseline_profile]
        
        # Deep copy base items
        allocated_items = [dict(item) for item in base_items]
        
        is_adjusted = False
        explanation = "Your portfolio is fully aligned with your strategic long-term risk profile."
        
        # Apply emotional logic adjustments
        if emotion in ["Anxious", "Panic"] or fear_score > 40.0:
            is_adjusted = True
            # Reduce Stocks, increase Cash/Bonds
            reduction_factor = min(15.0, (fear_score / 100.0) * 15.0)  # max 15% reduction
            
            # Find equities
            equity_index = -1
            cash_index = -1
            for i, item in enumerate(allocated_items):
                if "Equities" in item["asset_class"]:
                    equity_index = i
                if "Cash" in item["asset_class"]:
                    cash_index = i
            
            if equity_index != -1:
                # Deduct from equity
                old_equity = allocated_items[equity_index]["percentage"]
                new_equity = max(10.0, old_equity - reduction_factor)
                actual_deduction = old_equity - new_equity
                allocated_items[equity_index]["percentage"] = round(new_equity, 1)
                
                # Add to cash (or create cash if it doesn't exist)
                if cash_index != -1:
                    allocated_items[cash_index]["percentage"] = round(allocated_items[cash_index]["percentage"] + actual_deduction, 1)
                else:
                    allocated_items.append({
                        "asset_class": "Cash Equivalents",
                        "percentage": round(actual_deduction, 1),
                        "description": "Risk-free reserve cash added to cushion against high anxiety and prevent panic decisions."
                    })
                    
            explanation = f"Emotional Adjustment: We detected elevated fear/anxiety ({fear_score}% score). To mitigate panic-selling risks and protect your short-term peace of mind, we temporarily shifted {round(reduction_factor, 1)}% from Equities into Cash Equivalents. This shields your capital while you evaluate options rationally."
            
        elif emotion in ["Excited", "Greedy"] or greed_score > 40.0:
            is_adjusted = True
            # We want to lock in gains or curb FOMO
            # Check if there is speculative or high equities, and shift it to gold/bonds
            spec_index = -1
            equity_index = -1
            bond_index = -1
            gold_index = -1
            
            for i, item in enumerate(allocated_items):
                if "Speculative" in item["asset_class"]:
                    spec_index = i
                if "Equities" in item["asset_class"]:
                    equity_index = i
                if "Bonds" in item["asset_class"]:
                    bond_index = i
                if "Gold" in item["asset_class"]:
                    gold_index = i
                    
            shift_amount = 0.0
            
            # Cap speculative assets at 2% instead of 5% (or reduce by half)
            if spec_index != -1:
                old_spec = allocated_items[spec_index]["percentage"]
                new_spec = min(2.0, old_spec)
                shift_amount += (old_spec - new_spec)
                allocated_items[spec_index]["percentage"] = round(new_spec, 1)
                
            # Deduct from equities if FOMO is high
            reduction_factor = min(10.0, (greed_score / 100.0) * 10.0)
            if equity_index != -1:
                old_eq = allocated_items[equity_index]["percentage"]
                new_eq = max(20.0, old_eq - reduction_factor)
                shift_amount += (old_eq - new_eq)
                allocated_items[equity_index]["percentage"] = round(new_eq, 1)
                
            # Allocate shift_amount to gold or bonds
            if shift_amount > 0:
                if bond_index != -1:
                    allocated_items[bond_index]["percentage"] = round(allocated_items[bond_index]["percentage"] + shift_amount, 1)
                elif gold_index != -1:
                    allocated_items[gold_index]["percentage"] = round(allocated_items[gold_index]["percentage"] + shift_amount, 1)
                else:
                    allocated_items.append({
                        "asset_class": "Fixed Income (Bonds)",
                        "percentage": round(shift_amount, 1),
                        "description": "Stable bond reserves holding capital taken out of hot speculative plays."
                    })
                    
            explanation = f"Emotional Adjustment: We detected FOMO or high-yield seeking behavior ({greed_score}% score). To guard against buying at market peaks and concentration risk, we capped speculative exposures and redirected {round(shift_amount, 1)}% into defensive Fixed Income assets."
            
        elif emotion == "Calm":
            explanation = "Your emotional state is Calm. You are perfectly placed to hold your standard strategic allocation without panic or hype adjustments."

        # Map back to schemas
        result_allocation = []
        for item in allocated_items:
            result_allocation.append(PortfolioItem(
                asset_class=item["asset_class"],
                percentage=item["percentage"],
                description=item["description"]
            ))
            
        return PortfolioAllocationResponse(
            risk_profile=baseline_profile,
            detected_emotion=emotion,
            is_adjusted=is_adjusted,
            explanation=explanation,
            allocation=result_allocation
        )
