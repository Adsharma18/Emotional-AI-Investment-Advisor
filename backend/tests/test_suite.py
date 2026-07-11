import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

# Token holder
TOKEN = ""

def make_request(url, method="GET", data=None):
    global TOKEN
    req_data = json.dumps(data).encode('utf-8') if data else None
    headers = {'Content-Type': 'application/json'}
    if TOKEN:
        headers['Authorization'] = f"Bearer {TOKEN}"
    
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            err_detail = json.loads(body)
            raise Exception(f"HTTP {e.code}: {err_detail.get('detail', body)}")
        except Exception:
            raise Exception(f"HTTP {e.code}: {body}")

def run_integration_tests():
    global TOKEN
    print("====================================================")
    print("  RUNNING SECURE EMOTIONAL AI ADVISOR TEST SUITE    ")
    print("====================================================\n")
    
    # --- 1. REGISTRATION & LOGIN TESTS ---
    print("1. Authentication System Verification...")
    test_user_data = {
        "email": "test_investor_aditi@example.com",
        "password": "SecurePassword123!",
        "name": "Aditi Sharma"
    }
    
    try:
        # Register User
        reg_res = make_request(f"{BASE_URL}/api/auth/register", "POST", test_user_data)
        assert "access_token" in reg_res
        TOKEN = reg_res["access_token"]
        print(f"  [PASS] Register new user successfully. Token acquired.")

        # Try registering same user again (should fail with 400)
        try:
            make_request(f"{BASE_URL}/api/auth/register", "POST", test_user_data)
            print("  [FAIL] Registering duplicate email succeeded but should have failed.")
            sys.exit(1)
        except Exception as e:
            assert "already registered" in str(e).lower()
            print("  [PASS] Duplicate registration rejected correctly.")

        # Login User
        login_res = make_request(f"{BASE_URL}/api/auth/login", "POST", {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        assert "access_token" in login_res
        TOKEN = login_res["access_token"]  # Use fresh login token
        print("  [PASS] Login user successfully. Access token verified.")
    except Exception as e:
        print(f"  [FAIL] Authentication tests failed: {e}")
        sys.exit(1)

    # --- 2. PROFILE TESTS ---
    print("\n2. Profile Endpoint Verification...")
    try:
        # Fetch current profile
        prof = make_request(f"{BASE_URL}/api/profile")
        assert prof["name"] == "Aditi Sharma"
        print(f"  [PASS] Fetch default profile: Name={prof['name']}, Risk={prof['risk_tolerance']}")

        # Update profile
        updated_prof = make_request(f"{BASE_URL}/api/profile", "POST", {
            "risk_tolerance": "Aggressive",
            "advisor_persona": "Direct",
            "api_key_type": "grok",
            "api_key_value": "xai_test_key_12345"
        })
        assert updated_prof["risk_tolerance"] == "Aggressive"
        assert updated_prof["advisor_persona"] == "Direct"
        assert updated_prof["api_key_type"] == "grok"
        print(f"  [PASS] Update profile: Risk={updated_prof['risk_tolerance']}, Persona={updated_prof['advisor_persona']}, LLM={updated_prof['api_key_type']}")
    except Exception as e:
        print(f"  [FAIL] Profile test failure: {e}")
        sys.exit(1)

    # --- 3. GOAL CRUD TESTS ---
    print("\n3. Goals CRUD Endpoint Verification...")
    try:
        initial_goals = make_request(f"{BASE_URL}/api/goals")
        assert len(initial_goals) == 0
        print("  [PASS] Goals list is empty initially for new user.")

        # Create goal
        new_goal = make_request(f"{BASE_URL}/api/goals", "POST", {
            "name": "Trip to Japan",
            "target_amount": 5000.0,
            "current_amount": 500.0,
            "target_date": "2027-12-31",
            "priority": "Medium"
        })
        assert new_goal["id"] is not None
        assert new_goal["name"] == "Trip to Japan"
        print(f"  [PASS] Create goal: ID={new_goal['id']}, Target=${new_goal['target_amount']}")

        # Update goal progress
        goal_id = new_goal["id"]
        updated_goal = make_request(f"{BASE_URL}/api/goals/{goal_id}", "PUT", {
            "current_amount": 1000.0
        })
        assert updated_goal["current_amount"] == 1000.0
        print(f"  [PASS] Update goal: ID={goal_id}, Current Saved=${updated_goal['current_amount']}")

        # Delete goal
        del_res = make_request(f"{BASE_URL}/api/goals/{goal_id}", "DELETE")
        assert "success" in del_res["message"].lower()
        print(f"  [PASS] Delete goal: ID={goal_id}")
    except Exception as e:
        print(f"  [FAIL] Goals test failure: {e}")
        sys.exit(1)

    # --- 4. CHAT EMOTION & SENTIMENT TESTS ---
    print("\n4. Chat Analysis & Sentiment Verification...")
    try:
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
    except Exception as e:
        print(f"  [FAIL] Chat sentiment test failure: {e}")
        sys.exit(1)

    # --- 5. DYNAMIC PORTFOLIO REBALANCING TESTS ---
    print("\n5. Portfolio Rebalancing Engine Verification...")
    try:
        # Trigger panic text to evaluate portfolio adaptation
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
    except Exception as e:
        print(f"  [FAIL] Portfolio rebalancing test failure: {e}")
        sys.exit(1)

    print("\n====================================================")
    print("  ALL SECURE API INTEGRATION TESTS PASSED SUCCESSFULLY! ")
    print("====================================================")

if __name__ == "__main__":
    run_integration_tests()
