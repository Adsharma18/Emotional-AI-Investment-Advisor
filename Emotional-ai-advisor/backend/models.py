from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
import datetime
from database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="User")
    risk_tolerance = Column(String, default="Moderate")  # Conservative, Moderate, Aggressive
    investment_horizon = Column(String, default="Medium-Term")  # Short-Term, Medium-Term, Long-Term
    advisor_persona = Column(String, default="Empathetic")  # Empathetic, Direct, Analytical
    api_key_type = Column(String, default="mock")  # gemini, groq, mock
    api_key_value = Column(String, default="")

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    target_date = Column(String, nullable=False)  # ISO string or date
    priority = Column(String, default="Medium")  # Low, Medium, High

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, nullable=False)  # "user" or "advisor"
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    emotion = Column(String, default="Neutral")  # Anxious, Panic, Calm, Greedy, Excited, Neutral
    logic_score = Column(Float, default=50.0)
    fear_score = Column(Float, default=0.0)
    greed_score = Column(Float, default=0.0)
