import urllib.request
import json

def test_api():
    print("Testing running API endpoints...")
    base_url = "http://127.0.0.1:8000"
    
    # 1. Test GET /api/profile
    try:
        with urllib.request.urlopen(f"{base_url}/api/profile") as response:
            profile = json.loads(response.read().decode('utf-8'))
            print(f"[SUCCESS] Profile API active. User name: {profile.get('name')}, Persona: {profile.get('advisor_persona')}")
    except Exception as e:
        print(f"[ERROR] Profile API failed to respond: {e}")
        return

    # 2. Test POST /api/chat (Panic Test)
    try:
        data = json.dumps({"text": "I am so anxious and scared the markets are crashing, should I cash out?"}).encode('utf-8')
        req = urllib.request.Request(
            f"{base_url}/api/chat", 
            data=data, 
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            chat_res = json.loads(response.read().decode('utf-8'))
            print(f"[SUCCESS] Chat API responded.")
            print(f"  Advisor: {chat_res.get('text')}")
            print(f"  Emotion: {chat_res.get('emotion')}, Fear Score: {chat_res.get('fear_score')}")
    except Exception as e:
        print(f"[ERROR] Chat API failed: {e}")
        return

    # 3. Test GET /api/portfolio
    try:
        with urllib.request.urlopen(f"{base_url}/api/portfolio") as response:
            portfolio = json.loads(response.read().decode('utf-8'))
            print(f"[SUCCESS] Portfolio API responded. Emotion status: {portfolio.get('detected_emotion')}, Adjusted: {portfolio.get('is_adjusted')}")
            print(f"  Explanation: {portfolio.get('explanation')}")
            print("  Allocation Details:")
            for item in portfolio.get('allocation', []):
                print(f"    - {item.get('asset_class')}: {item.get('percentage')}%")
    except Exception as e:
        print(f"[ERROR] Portfolio API failed: {e}")
        return

if __name__ == "__main__":
    test_api()
