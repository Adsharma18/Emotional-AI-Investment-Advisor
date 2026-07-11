from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- Auth Schemas ---
class UserRegister(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Profile Schemas ---
class UserProfileBase(BaseModel):
    name: str
    risk_tolerance: str
    investment_horizon: str
    advisor_persona: str
    api_key_type: str
    api_key_value: Optional[str] = ""

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    risk_tolerance: Optional[str] = None
    investment_horizon: Optional[str] = None
    advisor_persona: Optional[str] = None
    api_key_type: Optional[str] = None
    api_key_value: Optional[str] = None

class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# --- Goal Schemas ---
class GoalBase(BaseModel):
    name: str
    target_amount: float
    current_amount: float = 0.0
    target_date: str
    priority: str = "Medium"

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    target_date: Optional[str] = None
    priority: Optional[str] = None

class GoalResponse(GoalBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# --- Chat Message Schemas ---
class ChatMessageBase(BaseModel):
    sender: str
    text: str
    emotion: Optional[str] = "Neutral"
    logic_score: Optional[float] = 50.0
    fear_score: Optional[float] = 0.0
    greed_score: Optional[float] = 0.0

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# --- API Request/Response ---
class ChatRequest(BaseModel):
    text: str

class PortfolioItem(BaseModel):
    asset_class: str
    percentage: float
    description: str

class PortfolioAllocationResponse(BaseModel):
    risk_profile: str
    detected_emotion: str
    is_adjusted: bool
    explanation: str
    allocation: List[PortfolioItem]
