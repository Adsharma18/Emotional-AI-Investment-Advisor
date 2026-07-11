from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
import datetime

from database import engine, Base, get_db
import models
import schemas
from services.llm_service import LLMService
from services.portfolio_service import PortfolioService
from services.auth_service import hash_password, verify_password, create_access_token, verify_token

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Emotional AI Investment Advisor API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development simplicity, allow all.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication token scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

# Dependency: Get active authenticated user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token missing. Please log in.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# --- Auth Endpoints ---

@app.post("/api/auth/register", response_model=schemas.Token)
def register_user(user_reg: schemas.UserRegister, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == user_reg.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered.")
    
    # Create user
    new_user = models.User(
        email=user_reg.email,
        password_hash=hash_password(user_reg.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create default user profile
    default_profile = models.UserProfile(
        user_id=new_user.id,
        name=user_reg.name,
        risk_tolerance="Moderate",
        investment_horizon="Medium-Term",
        advisor_persona="Empathetic",
        api_key_type="mock",
        api_key_value=""
    )
    db.add(default_profile)
    db.commit()
    
    # Generate token
    token = create_access_token(data={"sub": new_user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/api/auth/login", response_model=schemas.Token)
def login_user(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user or not verify_password(user.password_hash, login_data.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    
    # Generate token
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

# --- Profile Endpoints (Scoped) ---

@app.get("/api/profile", response_model=schemas.UserProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()
    if not profile:
        # Fallback profile setup
        profile = models.UserProfile(
            user_id=current_user.id,
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

@app.post("/api/profile", response_model=schemas.UserProfileResponse)
def update_profile(
    profile_update: schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    for var, value in vars(profile_update).items():
        if value is not None:
            setattr(profile, var, value)
    db.commit()
    db.refresh(profile)
    return profile

# --- Goal Endpoints (Scoped) ---

@app.get("/api/goals", response_model=List[schemas.GoalResponse])
def get_goals(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Goal).filter(models.Goal.user_id == current_user.id).all()

@app.post("/api/goals", response_model=schemas.GoalResponse)
def create_goal(
    goal: schemas.GoalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_goal = models.Goal(
        user_id=current_user.id,
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
def update_goal(
    goal_id: int,
    goal_update: schemas.GoalUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id, 
        models.Goal.user_id == current_user.id
    ).first()
    
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    for var, value in vars(goal_update).items():
        if value is not None:
            setattr(db_goal, var, value)
            
    db.commit()
    db.refresh(db_goal)
    return db_goal

@app.delete("/api/goals/{goal_id}")
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id, 
        models.Goal.user_id == current_user.id
    ).first()
    
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(db_goal)
    db.commit()
    return {"message": "Goal deleted successfully"}

# --- Chat Endpoints (Scoped) ---

@app.get("/api/chat", response_model=List[schemas.ChatMessageResponse])
def get_chat_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.ChatMessage).filter(
        models.ChatMessage.user_id == current_user.id
    ).order_by(models.ChatMessage.timestamp.asc()).all()

@app.post("/api/chat", response_model=schemas.ChatMessageResponse)
async def send_chat_message(
    chat_req: schemas.ChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # 1. Fetch recent history for LLM context
    history = db.query(models.ChatMessage).filter(
        models.ChatMessage.user_id == current_user.id
    ).order_by(models.ChatMessage.timestamp.desc()).limit(10).all()
    history.reverse() # chronologically ascending
    
    # 2. Get LLM analysis and response
    goals = db.query(models.Goal).filter(models.Goal.user_id == current_user.id).all()
    result = await LLMService.get_response(profile, history, chat_req.text, goals)
    
    # 3. Save User Message
    user_msg = models.ChatMessage(
        user_id=current_user.id,
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
        user_id=current_user.id,
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
def clear_chat_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db.query(models.ChatMessage).filter(models.ChatMessage.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Chat history cleared"}

# --- Portfolio Recommendation Endpoint (Scoped & Dynamic) ---

@app.get("/api/portfolio", response_model=schemas.PortfolioAllocationResponse)
def get_portfolio_recommendation(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Retrieve the latest chat message to extract the latest emotional state
    latest_msg = db.query(models.ChatMessage).filter(
        models.ChatMessage.user_id == current_user.id,
        models.ChatMessage.sender == "user"
    ).order_by(models.ChatMessage.timestamp.desc()).first()
    
    emotion = "Neutral"
    fear_score = 0.0
    greed_score = 0.0
    
    if latest_msg:
        emotion = latest_msg.emotion
        fear_score = latest_msg.fear_score
        greed_score = latest_msg.greed_score
        
    goals = db.query(models.Goal).filter(models.Goal.user_id == current_user.id).all()
    return PortfolioService.get_allocation(profile.risk_tolerance, emotion, fear_score, greed_score, goals)

# --- Educational Insights Endpoint (Scoped) ---

@app.get("/api/market-insights")
def get_market_insights(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    latest_msg = db.query(models.ChatMessage).filter(
        models.ChatMessage.user_id == current_user.id,
        models.ChatMessage.sender == "user"
    ).order_by(models.ChatMessage.timestamp.desc()).first()
    
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
