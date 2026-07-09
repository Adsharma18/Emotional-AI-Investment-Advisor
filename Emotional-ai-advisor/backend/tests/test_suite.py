import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def make_request(url, method="GET", data=None):
    req_data = json.dumps(data).encode('utf-8') if data else None
    headers = {'Content-Type': 'application/json'} if data else {}
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode('utf-8'))

def run_integration_tests():
    print("====================================================")
    print("   RUNNING EMOTIONAL AI ADVISOR FULL TEST SUITE     ")
    print("====================================================\n")
    
    # --- 1. PROFILE TESTS ---
    print("1. Profile Endpoint Verification...")
    try:
        # Fetch current profile
        prof = make_request(f"{BASE_URL}/api/profile")
        print(f"  [PASS] Fetch default profile: Name={prof['name']}, Risk={prof['risk_tolerance']}")

        # Update profile
        updated_prof = make_request(f"{BASE_URL}/api/profile", "POST", {
            "name": "Aditi Sharma",
            "risk_tolerance": "Aggressive",
            "advisor_persona": "Direct"
        })
        assert updated_prof["name"] == "Aditi Sharma"
        assert updated_prof["risk_tolerance"] == "Aggressive"
        assert updated_prof["advisor_persona"] == "Direct"
        print(f"  [PASS] Update profile: Name={updated_prof['name']}, Risk={updated_prof['risk_tolerance']}, Persona={updated_prof['advisor_persona']}")
    except Exception as e:
        print(f"  [FAIL] Profile test failure: {e}")
        sys.exit(1)

    # --- 2. GOAL CRUD TESTS ---
    print("\n2. Goals CRUD Endpoint Verification...")
    try:
        # Clear existing goals if any (we can do it manually or test by adding new ones)
        initial_goals = make_request(f"{BASE_URL}/api/goals")
        initial_count = len(initial_goals)
        print(f"  [INFO] Initial goal count: {initial_count}")

        # Create goal
        new_goal = make_request(f"{BASE_URL}/api/goals", "POST", {
            "name": "Retirement Fund",
            "target_amount": 500000.0,
            "current_amount": 10000.0,
            "target_date": "2046-12-31",
            "priority": "High"
        })
        assert new_goal["id"] is not None
        assert new_goal["name"] == "Retirement Fund"
        print(f"  [PASS] Create goal: ID={new_goal['id']}, Target=${new_goal['target_amount']}")

        # Update goal progress
        goal_id = new_goal["id"]
        updated_goal = make_request(f"{BASE_URL}/api/goals/{goal_id}", "PUT", {
            "current_amount": 15000.0
        })
        assert updated_goal["current_amount"] == 15000.0
        print(f"  [PASS] Update goal: ID={goal_id}, Current Saved=${updated_goal['current_amount']}")

        # Verify goal list increases
        current_goals = make_request(f"{BASE_URL}/api/goals")
        assert len(current_goals) == initial_count + 1
        print(f"  [PASS] Goals list correctly incremented to {len(current_goals)} items")

        # Delete goal
        del_res = make_request(f"{BASE_URL}/api/goals/{goal_id}", "DELETE")
        assert "success" in del_res["message"].lower()
        print(f"  [PASS] Delete goal: ID={goal_id}")

        # Verify goals list decrements back
        final_goals = make_request(f"{BASE_URL}/api/goals")
        assert len(final_goals) == initial_count
        print(f"  [PASS] Goals list correctly decremented back to {len(final_goals)} items")
    except Exception as e:
        print(f"  [FAIL] Goals test failure: {e}")
        sys.exit(1)

    # --- 3. CHAT EMOTION & SENTIMENT TESTS ---
    print("\n3. Chat Analysis & Sentiment Verification...")
    try:
        # Clear chat history for clean test
        make_request(f"{BASE_URL}/api/chat", "DELETE")
        print("  [INFO] Chat history cleared.")

        # Test Panic Sentiment
        panic_chat = make_request(f"{BASE_URL}/api/chat", "POST", {
            "text": "I can't take this anymore. The market dip is bleeding my portfolio. I feel terrified. Should I sell?"
        })
        assert panic_chat["sender"] == "advisor"
        assert panic_chat["emotion"] in ["Panic", "Anxious"]
        assert panic_chat["fear_score"] > 50.0
        print(f"  [PASS] Panic Chat: Emotion={panic_chat['emotion']}, Fear Score={panic_chat['fear_score']}%")

        # Test Greed Sentiment
        greed_chat = make_request(f"{BASE_URL}/api/chat", "POST", {
            "text": "Crypto is pumping! Everyone is getting rich. I want to FOMO buy this high-risk coin immediately to double my cash!"
        })
        assert greed_chat["emotion"] in ["Greedy", "Excited"]
        assert greed_chat["greed_score"] > 50.0
        print(f"  [PASS] Greed Chat: Emotion={greed_chat['emotion']}, Greed Score={greed_chat['greed_score']}%")

        # Test Calm Sentiment
        calm_chat = make_request(f"{BASE_URL}/api/chat", "POST", {
            "text": "I want to rebalance my portfolio logically, diversify across index funds, and stay focused on my 10-year retirement plan."
        })
        assert calm_chat["emotion"] == "Calm"
        assert calm_chat["logic_score"] > 60.0
        print(f"  [PASS] Calm Chat: Emotion={calm_chat['emotion']}, Logic Score={calm_chat['logic_score']}%")
    except Exception as e:
        print(f"  [FAIL] Chat sentiment test failure: {e}")
        sys.exit(1)

    # --- 4. DYNAMIC PORTFOLIO REBALANCING TESTS ---
    print("\n4. Portfolio Rebalancing Engine Verification...")
    try:
        # Trigger another Panic text to evaluate portfolio adaptation
        make_request(f"{BASE_URL}/api/chat", "POST", {
            "text": "I'm terrified the stock market is crashing! I want to sell everything to protect my money."
        })
        
        # Request dynamic portfolio
        portfolio = make_request(f"{BASE_URL}/api/portfolio")
        assert portfolio["is_adjusted"] == True
        assert portfolio["detected_emotion"] in ["Panic", "Anxious"]
        
        # Verify equities are scaled down for defensive buffering
        equities_item = next(item for item in portfolio["allocation"] if "Equities" in item["asset_class"])
        cash_item = next(item for item in portfolio["allocation"] if "Cash" in item["asset_class"])
        
        # Strategic Aggressive baseline is 80% equities. Under Panic it should be reduced
        assert equities_item["percentage"] < 80.0
        assert cash_item["percentage"] > 0.0
        print(f"  [PASS] Portfolio adjusted from Aggressive base (80% Equities) due to Panic:")
        print(f"         - Equities reduced to {equities_item['percentage']}%")
        print(f"         - Cash buffer increased to {cash_item['percentage']}%")
        print(f"         - Explanation: {portfolio['explanation'][:80]}...")
    except Exception as e:
        print(f"  [FAIL] Portfolio rebalancing test failure: {e}")
        sys.exit(1)

    # --- 5. DYNAMIC MARKET INSIGHTS TESTS ---
    print("\n5. Market Insights Engine Verification...")
    try:
        insights = make_request(f"{BASE_URL}/api/market-insights")
        
        # Since latest chat text is panic, verify we receive loss aversion bias warnings
        has_bias_warning = any("Loss Aversion" in item["title"] for item in insights)
        has_action_plan = any("48-Hour Rule" in item["title"] for item in insights)
        
        assert has_bias_warning
        assert has_action_plan
        print(f"  [PASS] Insights dynamically load 'Loss Aversion Bias' and 'The 48-Hour Rule' during Panic state.")
    except Exception as e:
        print(f"  [FAIL] Market insights test failure: {e}")
        sys.exit(1)

    # --- RESET PROFILE AND CLEAN UP ---
    try:
        # Restore normal Moderate default
        make_request(f"{BASE_URL}/api/profile", "POST", {
            "name": "Investor",
            "risk_tolerance": "Moderate",
            "advisor_persona": "Empathetic"
        })
        make_request(f"{BASE_URL}/api/chat", "DELETE")
        print("\n  [INFO] Test data re-seeded and cleaned.")
    except Exception:
        pass

    print("\n====================================================")
    print("   ALL API INTEGRATION TESTS PASSED SUCCESSFULLY!   ")
    print("====================================================")

if __name__ == "__main__":
    run_integration_tests()
