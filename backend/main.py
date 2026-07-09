from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import datetime

from database import engine, Base, get_db
import models
import schemas
from services.llm_service import LLMService
from services.portfolio_service import PortfolioService

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Emotional AI Investment Advisor API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development simplicity, allow all. In production limit to http://localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper: Get or create default user profile
def get_user_profile(db: Session = Depends(get_db)) -> models.UserProfile:
    profile = db.query(models.UserProfile).first()
    if not profile:
        profile = models.UserProfile(
            name="Investor",
            risk_tolerance="Moderate",
            investment_horizon="Medium-Term",
            advisor_persona="Empathetic",
            api_key_type="mock",
            api_key_value=""
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

# --- Profile Endpoints ---

@app.get("/api/profile", response_model=schemas.UserProfileResponse)
def get_profile(profile: models.UserProfile = Depends(get_user_profile)):
    return profile

@app.post("/api/profile", response_model=schemas.UserProfileResponse)
def update_profile(
    profile_update: schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
    profile: models.UserProfile = Depends(get_user_profile)
):
    for var, value in vars(profile_update).items():
        if value is not None:
            setattr(profile, var, value)
    db.commit()
    db.refresh(profile)
    return profile

# --- Goal Endpoints ---

@app.get("/api/goals", response_model=List[schemas.GoalResponse])
def get_goals(db: Session = Depends(get_db)):
    return db.query(models.Goal).all()

@app.post("/api/goals", response_model=schemas.GoalResponse)
def create_goal(goal: schemas.GoalCreate, db: Session = Depends(get_db)):
    db_goal = models.Goal(
        name=goal.name,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        target_date=goal.target_date,
        priority=goal.priority
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

@app.put("/api/goals/{goal_id}", response_model=schemas.GoalResponse)
def update_goal(goal_id: int, goal_update: schemas.GoalUpdate, db: Session = Depends(get_db)):
    db_goal = db.query(models.Goal).filter(models.Goal.id == goal_id).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    for var, value in vars(goal_update).items():
        if value is not None:
            setattr(db_goal, var, value)
            
    db.commit()
    db.refresh(db_goal)
    return db_goal

@app.delete("/api/goals/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    db_goal = db.query(models.Goal).filter(models.Goal.id == goal_id).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(db_goal)
    db.commit()
    return {"message": "Goal deleted successfully"}

# --- Chat Endpoints ---

@app.get("/api/chat", response_model=List[schemas.ChatMessageResponse])
def get_chat_history(db: Session = Depends(get_db)):
    return db.query(models.ChatMessage).order_by(models.ChatMessage.timestamp.asc()).all()

@app.post("/api/chat", response_model=schemas.ChatMessageResponse)
async def send_chat_message(
    chat_req: schemas.ChatRequest,
    db: Session = Depends(get_db),
    profile: models.UserProfile = Depends(get_user_profile)
):
    # 1. Fetch recent history for LLM context
    history = db.query(models.ChatMessage).order_by(models.ChatMessage.timestamp.desc()).limit(10).all()
    history.reverse() # chronologically ascending
    
    # 2. Get LLM analysis and response
    result = await LLMService.get_response(profile, history, chat_req.text)
    
    # 3. Save User Message
    user_msg = models.ChatMessage(
        sender="user",
        text=chat_req.text,
        emotion=result["emotion"],
        fear_score=result["fear_score"],
        greed_score=result["greed_score"],
        logic_score=result["logic_score"]
    )
    db.add(user_msg)
    
    # 4. Save Advisor Message
    advisor_msg = models.ChatMessage(
        sender="advisor",
        text=result["text"],
        emotion=result["emotion"],
        fear_score=result["fear_score"],
        greed_score=result["greed_score"],
        logic_score=result["logic_score"]
    )
    db.add(advisor_msg)
    
    db.commit()
    db.refresh(advisor_msg)
    return advisor_msg

@app.delete("/api/chat")
def clear_chat_history(db: Session = Depends(get_db)):
    db.query(models.ChatMessage).delete()
    db.commit()
    return {"message": "Chat history cleared"}

# --- Portfolio Recommendation Endpoint ---

@app.get("/api/portfolio", response_model=schemas.PortfolioAllocationResponse)
def get_portfolio_recommendation(
    db: Session = Depends(get_db),
    profile: models.UserProfile = Depends(get_user_profile)
):
    # Retrieve the latest chat message to extract the latest emotional state
    latest_msg = db.query(models.ChatMessage).filter(models.ChatMessage.sender == "user").order_by(models.ChatMessage.timestamp.desc()).first()
    
    emotion = "Neutral"
    fear_score = 0.0
    greed_score = 0.0
    
    if latest_msg:
        emotion = latest_msg.emotion
        fear_score = latest_msg.fear_score
        greed_score = latest_msg.greed_score
        
    return PortfolioService.get_allocation(profile.risk_tolerance, emotion, fear_score, greed_score)

# --- Educational Insights Endpoint ---

@app.get("/api/market-insights")
def get_market_insights(db: Session = Depends(get_db)):
    latest_msg = db.query(models.ChatMessage).filter(models.ChatMessage.sender == "user").order_by(models.ChatMessage.timestamp.desc()).first()
    
    emotion = "Neutral"
    if latest_msg:
        emotion = latest_msg.emotion
        
    insights = []
    
    # Static general insights
    insights.append({
        "type": "general",
        "title": "Dangers of Market Timing",
        "content": "Trying to predict market peaks and valleys usually leads to buying high and selling low. Long-term dollar-cost averaging (DCA) is statistically superior.",
        "icon": "TrendingUp"
    })
    
    # Emotion-specific insights
    if emotion in ["Anxious", "Panic"]:
        insights.append({
            "type": "bias-alert",
            "title": "Loss Aversion Bias",
            "content": "Behavioral finance shows we feel the pain of a loss twice as intensely as the pleasure of an equal gain. This can trigger an irrational urge to sell sound investments during market dips.",
            "icon": "ShieldAlert"
        })
        insights.append({
            "type": "actionable",
            "title": "Action Plan: The 48-Hour Rule",
            "content": "Before executing any panic sale, wait 48 hours. Review whether the underlying business fundamentals of your holdings have actually changed, or if it is just price volatility.",
            "icon": "Hourglass"
        })
    elif emotion in ["Excited", "Greedy"]:
        insights.append({
            "type": "bias-alert",
            "title": "FOMO & Herd Behavior",
            "content": "When assets rise quickly, we feel left out and buy near the top. This is known as herd mentality. It often ends in buying overvalued, highly speculative assets.",
            "icon": "Zap"
        })
        insights.append({
            "type": "actionable",
            "title": "Action Plan: The Core-Satellite Rule",
            "content": "Keep at least 90% of your capital in diversified core assets (index funds/bonds). Limit speculative bets (crypto/hype stocks) to a maximum of 5-10% of total wealth.",
            "icon": "Layers"
        })
    else:
        insights.append({
            "type": "info",
            "title": "Behavioral Discipline",
            "content": "Emotional stability is the superpower of successful investors. Keeping a regular journal of your financial feelings can help you recognize emotional triggers.",
            "icon": "BookOpen"
        })
        
    return insights
