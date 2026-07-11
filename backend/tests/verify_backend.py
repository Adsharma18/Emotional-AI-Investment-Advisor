import os
import sys

# Ensure backend folder is in path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, Base, SessionLocal
import models
from services.llm_service import LLMService
from services.portfolio_service import PortfolioService
from services.auth_service import hash_password

def run_tests():
    print("=== STARTING BACKEND AUTOMATED TESTS ===")
    
    # 1. Database and Table Creation
    print("\n1. Testing Database & Table Creation...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    print("[SUCCESS] Database tables initialized successfully.")

    # Clean up any existing records
    db.query(models.ChatMessage).delete()
    db.query(models.Goal).delete()
    db.query(models.UserProfile).delete()
    db.query(models.User).delete()
    db.commit()

    # 2. User & Profile Setup
    print("\n2. Testing User & Profile operations...")
    test_user = models.User(
        email="verify_test@example.com",
        password_hash=hash_password("test_pass")
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    assert test_user.id is not None
    
    test_profile = models.UserProfile(
        user_id=test_user.id,
        name="Aditi Sharma Test",
        risk_tolerance="Moderate",
        investment_horizon="Medium-Term",
        advisor_persona="Empathetic",
        api_key_type="mock",
        api_key_value=""
    )
    db.add(test_profile)
    db.commit()
    db.refresh(test_profile)
    assert test_profile.id is not None
    assert test_profile.name == "Aditi Sharma Test"
    print(f"[SUCCESS] User & profile created: {test_profile.name} (User ID: {test_user.id}) with {test_profile.risk_tolerance} risk.")

    # 3. Goal CRUD Setup
    print("\n3. Testing Financial Goal CRUD...")
    new_goal = models.Goal(
        user_id=test_user.id,
        name="Emergency Fund Test",
        target_amount=15000.0,
        current_amount=2000.0,
        target_date="2027-12-31",
        priority="High"
    )
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    assert new_goal.id is not None
    assert new_goal.current_amount == 2000.0
    print(f"[SUCCESS] Financial goal created: {new_goal.name}, Target: ${new_goal.target_amount}.")

    # 4. Sentiment and Heuristics Service
    print("\n4. Testing Emotional Sentiment Analysis Heuristics...")
    panic_text = "I'm terrified the stock market is crashing! I am going to lose all my money, should I sell everything immediately?"
    panic_analysis = LLMService.analyze_heuristics(panic_text)
    print(f"Input text: '{panic_text}'")
    print(f"Detected: {panic_analysis}")
    assert panic_analysis["emotion"] in ["Panic", "Anxious"]
    assert panic_analysis["fear_score"] > 50.0
    print("[SUCCESS] Panic/Fear sentiment correctly classified.")

    greed_text = "Should I buy more bitcoin? This new coin is going to the moon, I want to double my money fast, fomo is real!"
    greed_analysis = LLMService.analyze_heuristics(greed_text)
    print(f"Input text: '{greed_text}'")
    print(f"Detected: {greed_analysis}")
    assert greed_analysis["emotion"] in ["Greedy", "Excited"]
    assert greed_analysis["greed_score"] > 50.0
    print("[SUCCESS] Greed/FOMO sentiment correctly classified.")

    # 5. Portfolio Service Modifiers
    print("\n5. Testing Portfolio Recommendation adjustments...")
    
    # Test Calm Portfolio (should be standard Moderate baseline)
    calm_allocation = PortfolioService.get_allocation(
        risk_profile="Moderate",
        emotion="Calm",
        fear_score=0.0,
        greed_score=0.0
    )
    print(f"Calm Portfolio status (is_adjusted): {calm_allocation.is_adjusted}")
    assert not calm_allocation.is_adjusted
    
    # Locate Equities percentage in calm portfolio
    calm_equity_pct = next(item.percentage for item in calm_allocation.allocation if "Equities" in item.asset_class)
    assert calm_equity_pct == 60.0
    print(f"[SUCCESS] Calm allocation matches baseline Moderate index (Equities: {calm_equity_pct}%).")

    # Test Panic Portfolio (should reduce Equities, increase Cash)
    panic_allocation = PortfolioService.get_allocation(
        risk_profile="Moderate",
        emotion="Panic",
        fear_score=80.0,
        greed_score=0.0
    )
    print(f"Panic Portfolio status (is_adjusted): {panic_allocation.is_adjusted}")
    print(f"Panic Explanation: {panic_allocation.explanation}")
    assert panic_allocation.is_adjusted
    
    panic_equity_pct = next(item.percentage for item in panic_allocation.allocation if "Equities" in item.asset_class)
    panic_cash_pct = next(item.percentage for item in panic_allocation.allocation if "Cash" in item.asset_class)
    
    # Equities should be reduced below 60%
    assert panic_equity_pct < 60.0
    assert panic_cash_pct > 5.0
    print(f"[SUCCESS] Panic allocation shifted assets from Equities ({panic_equity_pct}%) to Cash ({panic_cash_pct}%).")

    # Clean up test records
    db.query(models.ChatMessage).delete()
    db.query(models.Goal).delete()
    db.query(models.UserProfile).delete()
    db.query(models.User).delete()
    db.commit()
    db.close()
    
    print("\n=== ALL TESTS COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_tests()
