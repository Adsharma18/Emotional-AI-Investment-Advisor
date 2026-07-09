import json
import re
import httpx
import google.generativeai as genai
from models import UserProfile, ChatMessage

# Heuristic Fallback Analysis & Advisor Responses
PANIC_KEYWORDS = ["drop", "crash", "sell", "lose", "scared", "terrified", "panic", "fear", "dip", "bleeding", "plummet", "down", "ruined", "anxious", "worry", "worried", "recession", "uncertain"]
GREED_KEYWORDS = ["moon", "crypto", "doge", "bitcoin", "fomo", "rich", "millionaire", "fast", "double", "10x", "hype", "greedy", "buy now", "miss out", "next big", "speculate", "gamble"]
LOGIC_KEYWORDS = ["long term", "diversify", "stable", "calm", "patient", "plan", "retirement", "budget", "strategy", "history", "hold", "index fund", "discipline", "research"]

PERSONA_PROMPTS = {
    "Empathetic": "You are a warm, highly empathetic financial advisor. You prioritize the user's emotional comfort, acknowledge their feelings first, and gently guide them to rational long-term investment strategies. Avoid harsh judgments. Speak in a supportive, comforting tone.",
    "Analytical": "You are an analytical, data-driven financial advisor. You focus heavily on historical statistics, risk ratios, and financial models. While you note the user's emotional state, you answer using logic, quantitative facts, and asset allocation theory. Speak in a clear, professional, and structured tone.",
    "Direct": "You are a direct, no-nonsense financial coach. You cut through emotional clutter and tell the user exactly what they need to hear, even if it is tough. You focus on discipline, avoiding biases, and taking action immediately. Speak in a candid, firm, and practical tone."
}

MOCK_ANSWERS = {
    "Panic": {
        "Empathetic": "I hear how stressful this market downturn is for you, and it's completely natural to feel anxious when seeing your portfolio value decline. However, selling during a dip locks in those losses. Historically, markets have always recovered. Let's look at your goals and consider if your current assets are diversified enough to help you sleep at night.",
        "Analytical": "Market volatility is a normal statistical occurrence. Equities historically fluctuate, but selling during a downturn compromises the compounding effect. Historically, the S&P 500 recovers within 12-18 months of a correction. Statistically, staying invested yields a 35% higher return over a 10-year horizon than trying to time the market.",
        "Direct": "Stop. Panic selling is the fastest way to lose money. Markets go up and down; that is the price you pay for equity returns. If you sell now, you lock in losses and miss the eventual recovery. Check your risk tolerance: if this drop makes you want to cash out, your portfolio was too aggressive to begin with."
    },
    "Greedy": {
        "Empathetic": "It's so exciting to see these massive returns, and it's completely understandable to want to jump on a hot trend! However, allocating too much to speculative assets like crypto or single stocks can expose you to high risk. Let's make sure we protect your core savings first, and maybe set aside a small, controlled 'fun fund' for these opportunities.",
        "Analytical": "Concentration risk is one of the leading causes of portfolio failure. While high-beta assets show short-term explosive growth, they also display high standard deviation and downside risk. Portfolio theory recommends keeping speculative assets below 5-10% of total assets to optimize the Sharpe Ratio.",
        "Direct": "You are chasing hype, and that is a classic FOMO trap. Investing is not a get-rich-quick scheme. If you dump your life savings into a volatile asset just because it went up 50% last week, you are gambling, not investing. Rebalance back into diversified assets immediately."
    },
    "Calm": {
        "Empathetic": "I am so glad to see you taking a calm and structured approach to your finances. Staying focused on your long-term plan is the key to investment success. What specific goal or project should we focus on optimizing today?",
        "Analytical": "Your structured approach aligns with optimal portfolio management. Maintaining asset allocation targets under calm market parameters minimizes transaction costs and tracking error. Let's review your goal metrics and cash-flow efficiency.",
        "Direct": "Good. Discipline is what separates successful investors from the rest. You have a plan, now stick to it. Let's check if your automatic contributions are set up correctly so you don't even have to think about it."
    },
    "Neutral": {
        "Empathetic": "Hello! I'm here to help you navigate both your financial goals and the emotional side of investing. Whether you want to plan for a specific goal or just talk through market feelings, I'm here to listen.",
        "Analytical": "Welcome. I can assist you with portfolio optimization, risk profiling, and goal tracking. Let's begin by defining your investment horizon and target assets.",
        "Direct": "Let's get to work. What are we planning for today? Tell me your financial goals, and we'll map out a strategy to get you there."
    }
}

class LLMService:
    @staticmethod
    def analyze_heuristics(text: str) -> dict:
        text_lower = text.lower()
        
        # Count keywords
        panic_count = sum(1 for w in PANIC_KEYWORDS if w in text_lower)
        greed_count = sum(1 for w in GREED_KEYWORDS if w in text_lower)
        logic_count = sum(1 for w in LOGIC_KEYWORDS if w in text_lower)
        
        total_counts = panic_count + greed_count + logic_count
        
        # Default scores
        fear_score = 0.0
        greed_score = 0.0
        logic_score = 50.0
        emotion = "Neutral"
        
        if total_counts > 0:
            fear_pct = (panic_count / total_counts) * 100
            greed_pct = (greed_count / total_counts) * 100
            logic_pct = (logic_count / total_counts) * 100
            
            fear_score = min(100.0, fear_pct * 1.5)
            greed_score = min(100.0, greed_pct * 1.5)
            logic_score = max(0.0, min(100.0, 50.0 + (logic_pct - (fear_pct + greed_pct)/2)))
            
            if fear_score > 40.0:
                emotion = "Panic" if fear_score > 70.0 else "Anxious"
            elif greed_score > 40.0:
                emotion = "Greedy" if greed_score > 70.0 else "Excited"
            elif logic_score > 60.0:
                emotion = "Calm"
        else:
            # Default state based on simple sentence cues
            if any(w in text_lower for w in ["hi", "hello", "how are you", "help"]):
                emotion = "Neutral"
            else:
                emotion = "Calm"
                logic_score = 60.0
                
        return {
            "emotion": emotion,
            "fear_score": round(fear_score, 1),
            "greed_score": round(greed_score, 1),
            "logic_score": round(logic_score, 1)
        }

    @staticmethod
    async def get_response(profile: UserProfile, conversation_history: list, new_message: str) -> dict:
        api_type = profile.api_key_type
        api_key = profile.api_key_value
        persona = profile.advisor_persona or "Empathetic"
        
        # If API key is not configured, fall back to mock
        if api_type == "mock" or not api_key:
            analysis = LLMService.analyze_heuristics(new_message)
            emotion = analysis["emotion"]
            
            # Select response template
            key_emotion = emotion
            if emotion in ["Anxious", "Panic"]:
                key_emotion = "Panic"
            elif emotion in ["Excited", "Greedy"]:
                key_emotion = "Greedy"
            elif emotion == "Calm":
                key_emotion = "Calm"
            else:
                key_emotion = "Neutral"
                
            response_text = MOCK_ANSWERS[key_emotion][persona]
            
            # Add context-specific details if available
            if "crypto" in new_message.lower() and key_emotion == "Greedy":
                response_text += " Cryptocurrencies can be highly volatile, with drops of 80% or more common. Do not invest money you cannot afford to lose entirely."
            elif "crash" in new_message.lower() and key_emotion == "Panic":
                response_text += " Remember, market corrections are temporary. The average recovery time is a fraction of the time spent in bull markets."

            return {
                "text": response_text,
                "emotion": emotion,
                "fear_score": analysis["fear_score"],
                "greed_score": analysis["greed_score"],
                "logic_score": analysis["logic_score"]
            }

        # Real API Calls
        system_instruction = f"""
        {PERSONA_PROMPTS.get(persona, PERSONA_PROMPTS['Empathetic'])}
        
        Analyze the client's emotional state. Detect:
        - Primary emotion: 'Panic', 'Anxious', 'Calm', 'Greedy', 'Excited', or 'Neutral'.
        - Fear Score (0-100): Level of panic/scared/anxious feelings.
        - Greed Score (0-100): Level of FOMO/chasing returns/speculation/overconfidence.
        - Logic Score (0-100): Level of strategic, long-term, calm financial thinking.
        
        You MUST respond ONLY with a valid JSON object matching this structure:
        {{
          "response": "Your advisor advice text here",
          "emotion": "Detected Emotion",
          "fear_score": 0.0,
          "greed_score": 0.0,
          "logic_score": 50.0
        }}
        """

        try:
            if api_type == "gemini":
                genai.configure(api_key=api_key)
                # Use Gemini 1.5 Flash for speed
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config={"response_mime_type": "application/json"}
                )
                
                # Format history for Gemini
                contents = []
                for msg in conversation_history[-6:]:  # limit context
                    role = "user" if msg.sender == "user" else "model"
                    contents.append({"role": role, "parts": [msg.text]})
                
                # Add system instruction as prefix or model setup
                # Since we are using standard Gemini SDK, we can pass system_instruction in GenerativeModel constructor
                model_with_system = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=system_instruction,
                    generation_config={"response_mime_type": "application/json"}
                )
                
                response = model_with_system.generate_content(new_message)
                data = json.loads(response.text.strip())
                return {
                    "text": data.get("response", ""),
                    "emotion": data.get("emotion", "Neutral"),
                    "fear_score": float(data.get("fear_score", 0.0)),
                    "greed_score": float(data.get("greed_score", 0.0)),
                    "logic_score": float(data.get("logic_score", 50.0))
                }
                
            elif api_type == "groq":
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                # Compile chat history
                messages = [{"role": "system", "content": system_instruction}]
                for msg in conversation_history[-6:]:
                    role = "user" if msg.sender == "user" else "assistant"
                    messages.append({"role": role, "content": msg.text})
                messages.append({"role": "user", "content": new_message})
                
                payload = {
                    "model": "mixtral-8x7b-32768", # or llama3-8b-8192
                    "messages": messages,
                    "response_format": {"type": "json_object"},
                    "temperature": 0.5
                }
                
                async with httpx.AsyncClient() as client:
                    res = await client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=15.0)
                    if res.status_code == 200:
                        res_data = res.json()
                        content = res_data["choices"][0]["message"]["content"]
                        data = json.loads(content.strip())
                        return {
                            "text": data.get("response", ""),
                            "emotion": data.get("emotion", "Neutral"),
                            "fear_score": float(data.get("fear_score", 0.0)),
                            "greed_score": float(data.get("greed_score", 0.0)),
                            "logic_score": float(data.get("logic_score", 50.0))
                        }
                    else:
                        raise Exception(f"Groq API error: {res.text}")
                        
        except Exception as e:
            # If API fails, fall back to mock heuristics with warning
            print(f"LLM API Call failed, falling back to heuristics: {str(e)}")
            fallback = LLMService.analyze_heuristics(new_message)
            emotion = fallback["emotion"]
            key_emotion = "Panic" if emotion in ["Anxious", "Panic"] else ("Greedy" if emotion in ["Excited", "Greedy"] else ("Calm" if emotion == "Calm" else "Neutral"))
            response_text = f"[API Fallback Mode] {MOCK_ANSWERS[key_emotion][persona]}"
            return {
                "text": response_text,
                "emotion": emotion,
                "fear_score": fallback["fear_score"],
                "greed_score": fallback["greed_score"],
                "logic_score": fallback["logic_score"]
            }
