import datetime
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
    def get_allocation(risk_profile: str, emotion: str, fear_score: float, greed_score: float, goals: list = None) -> PortfolioAllocationResponse:
        baseline_profile = risk_profile if risk_profile in PORTFOLIO_BASELINES else "Moderate"
        base_items = PORTFOLIO_BASELINES[baseline_profile]
        
        # Deep copy base items
        allocated_items = [dict(item) for item in base_items]
        
        is_adjusted = False
        adjustments = []
        
        # --- 1. Goal Horizon-Based Adjustments ---
        goal_adjusted = False
        if goals and len(goals) > 0:
            short_term_targets = 0.0
            total_targets = 0.0
            today = datetime.date.today()
            
            for goal in goals:
                total_targets += goal.target_amount
                try:
                    # Parse target date
                    g_date = datetime.datetime.strptime(goal.target_date, "%Y-%m-%d").date()
                    days_left = (g_date - today).days
                    years_left = days_left / 365.25
                    # If goal is short-term (< 3 years away)
                    if years_left < 3.0:
                        short_term_targets += goal.target_amount
                except Exception:
                    pass
            
            if total_targets > 0 and short_term_targets > 0:
                short_term_ratio = short_term_targets / total_targets
                # If short-term goals comprise > 15% of total goal targets
                if short_term_ratio > 0.15:
                    shift_pct = min(15.0, short_term_ratio * 15.0)  # shift up to 15%
                    
                    # Deduct from Equities, add to Bonds
                    eq_idx = -1
                    bond_idx = -1
                    for i, item in enumerate(allocated_items):
                        if "Equities" in item["asset_class"]:
                            eq_idx = i
                        if "Bonds" in item["asset_class"]:
                            bond_idx = i
                            
                    if eq_idx != -1 and bond_idx != -1:
                        old_eq = allocated_items[eq_idx]["percentage"]
                        new_eq = max(10.0, old_eq - shift_pct)
                        actual_shift = old_eq - new_eq
                        allocated_items[eq_idx]["percentage"] = round(new_eq, 1)
                        allocated_items[bond_idx]["percentage"] = round(allocated_items[bond_idx]["percentage"] + actual_shift, 1)
                        
                        goal_adjusted = True
                        is_adjusted = True
                        adjustments.append(f"Goal Horizon Adjustment: We detected that {round(short_term_ratio * 100)}% of your financial goal targets are short-term (due in < 3 years). To insulate this capital from equity corrections, we shifted {round(actual_shift, 1)}% from Equities into Fixed Income (Bonds) for safety.")

        # --- 2. Emotional State-Based Adjustments ---
        emotion_adjusted = False
        if emotion in ["Anxious", "Panic"] or fear_score > 40.0:
            emotion_adjusted = True
            is_adjusted = True
            # Reduce Equities, increase Cash buffer
            reduction_factor = min(15.0, (fear_score / 100.0) * 15.0)
            
            # Find Equities index
            eq_idx = -1
            cash_idx = -1
            for i, item in enumerate(allocated_items):
                if "Equities" in item["asset_class"]:
                    eq_idx = i
                if "Cash" in item["asset_class"]:
                    cash_idx = i
            
            if eq_idx != -1:
                old_eq = allocated_items[eq_idx]["percentage"]
                new_eq = max(10.0, old_eq - reduction_factor)
                actual_deduction = old_eq - new_eq
                allocated_items[eq_idx]["percentage"] = round(new_eq, 1)
                
                # Add to Cash reserves
                if cash_idx != -1:
                    allocated_items[cash_idx]["percentage"] = round(allocated_items[cash_idx]["percentage"] + actual_deduction, 1)
                else:
                    allocated_items.append({
                        "asset_class": "Cash Equivalents",
                        "percentage": round(actual_deduction, 1),
                        "description": "Risk-free reserve cash added to cushion against high anxiety and prevent panic decisions."
                    })
                    
            adjustments.append(f"Emotional Buffer: High market fear/anxiety ({round(fear_score)}% score) was detected. To help you maintain discipline and avoid sell-offs, we temporarily shifted {round(reduction_factor, 1)}% from Equities to Cash reserves.")
            
        elif emotion in ["Excited", "Greedy"] or greed_score > 40.0:
            emotion_adjusted = True
            is_adjusted = True
            
            spec_idx = -1
            eq_idx = -1
            bond_idx = -1
            gold_idx = -1
            for i, item in enumerate(allocated_items):
                if "Speculative" in item["asset_class"]:
                    spec_idx = i
                if "Equities" in item["asset_class"]:
                    eq_idx = i
                if "Bonds" in item["asset_class"]:
                    bond_idx = i
                if "Gold" in item["asset_class"]:
                    gold_idx = i
                    
            shift_amount = 0.0
            
            # Cap speculative assets at 2%
            if spec_idx != -1:
                old_spec = allocated_items[spec_idx]["percentage"]
                new_spec = min(2.0, old_spec)
                shift_amount += (old_spec - new_spec)
                allocated_items[spec_idx]["percentage"] = round(new_spec, 1)
                
            # Deduct from general equities under FOMO
            reduction_factor = min(10.0, (greed_score / 100.0) * 10.0)
            if eq_idx != -1:
                old_eq = allocated_items[eq_idx]["percentage"]
                new_eq = max(20.0, old_eq - reduction_factor)
                shift_amount += (old_eq - new_eq)
                allocated_items[eq_idx]["percentage"] = round(new_eq, 1)
                
            # Shift assets to Gold/Bonds
            if shift_amount > 0:
                if bond_idx != -1:
                    allocated_items[bond_idx]["percentage"] = round(allocated_items[bond_idx]["percentage"] + shift_amount, 1)
                elif gold_idx != -1:
                    allocated_items[gold_idx]["percentage"] = round(allocated_items[gold_idx]["percentage"] + shift_amount, 1)
                else:
                    allocated_items.append({
                        "asset_class": "Fixed Income (Bonds)",
                        "percentage": round(shift_amount, 1),
                        "description": "Stable bond reserves holding capital taken out of hot speculative plays."
                    })
                    
            adjustments.append(f"FOMO Control: Elevated speculative signals ({round(greed_score)}% score) were detected. To protect your compounding roadmap from buying at local peaks, we capped speculative exposures and redirected {round(shift_amount, 1)}% into defensive assets.")

        # --- 3. Compile Final Explanation ---
        if is_adjusted:
            explanation = " ".join(adjustments)
        else:
            explanation = "Your portfolio is fully aligned with your strategic long-term risk profile. What a great state of balance!"

        # Map back to Pydantic schemas
        result_allocation = []
        for item in allocated_items:
            # Ensure percentages are positive and non-zero before adding
            if item["percentage"] > 0:
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
