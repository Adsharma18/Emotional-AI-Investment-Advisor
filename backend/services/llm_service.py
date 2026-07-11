import json
import random
import httpx
import google.generativeai as genai
from models import UserProfile, ChatMessage

PANIC_KEYWORDS = ["drop", "crash", "sell", "lose", "scared", "terrified", "panic", "fear", "dip", "bleeding", "plummet", "down", "ruined", "anxious", "worry", "worried", "recession", "uncertain", "red"]
GREED_KEYWORDS = ["moon", "crypto", "doge", "bitcoin", "fomo", "rich", "millionaire", "fast", "double", "10x", "hype", "greedy", "buy now", "miss out", "next big", "speculate", "gamble", "profit"]
LOGIC_KEYWORDS = ["long term", "diversify", "stable", "calm", "patient", "plan", "retirement", "budget", "strategy", "history", "hold", "index fund", "discipline", "research", "safety"]

PERSONA_PROMPTS = {
    "Empathetic": "You are a warm, highly empathetic financial advisor. You prioritize the user's emotional comfort, acknowledge their feelings first, and gently guide them to rational long-term investment strategies. Avoid harsh judgments. Speak in a supportive, comforting tone.",
    "Analytical": "You are an analytical, data-driven financial advisor. You focus heavily on historical statistics, risk ratios, and financial models. While you note the user's emotional state, you answer using logic, quantitative facts, and asset allocation theory. Speak in a clear, professional, and structured tone.",
    "Direct": "You are a direct, no-nonsense financial coach. You cut through emotional clutter and tell the user exactly what they need to hear, even if it is tough. You focus on discipline, avoiding biases, and taking action immediately. Speak in a candid, firm, and practical tone."
}

# Greeting variations for dynamic mock responses
GREETINGS = [
    "I understand your perspective.",
    "Thanks for sharing that.",
    "Let's look at this together.",
    "I hear what you're saying.",
    "That is an important question."
]

def generate_dynamic_fallback(profile: UserProfile, emotion: str, text: str, goals: list) -> str:
    persona = profile.advisor_persona or "Empathetic"
    name = profile.name or "Investor"
    text_lower = text.lower()
    
    # 1. Start with a greeting and name acknowledgment
    response = f"Hello {name}. " if random.random() > 0.5 else ""
    response += random.choice(GREETINGS) + " "
    
    # 2. Integrate a goal if one exists
    goal_mention = ""
    if goals and len(goals) > 0:
        target_goal = random.choice(goals)
        goal_mention = f"As you work towards your '{target_goal.name}' (target: ${target_goal.target_amount:,}), it is essential to align your decisions with that timeline. "
    
    # 3. Add context based on detected emotion and persona
    if emotion in ["Anxious", "Panic"]:
        if persona == "Empathetic":
            response += f"It's completely natural to feel stressed when markets drop. Volatility can feel uncomfortable. {goal_mention}However, cashing out during a dip locks in temporary losses. Historically, markets have always recovered. I recommend taking a breath and holding your current strategic asset mix."
        elif persona == "Analytical":
            response += f"Let's look at the data. Market drawdowns are statistically normal occurrences. Historically, the S&P 500 has recovered from every single correction. {goal_mention}Staying invested avoids the double-hazard of market timing: knowing when to exit and when to re-enter. The data shows long-term DCA beats panicking."
        else: # Direct
            response += f"Panic selling is the fastest way to destroy your wealth. Markets decline; that is the price we pay for equity growth. {goal_mention}If you can't handle a 10% drop, your portfolio was constructed too aggressively. Do not lock in losses out of fear. Stick to the plan."
            
        # Specific keyword extensions
        if "crypto" in text_lower or "bitcoin" in text_lower:
            response += " Especially with highly volatile digital assets, dramatic swings are part of the landscape. Don't let short-term swings dictate your core stability."
        elif "crash" in text_lower or "sell" in text_lower:
            response += " Historically, the best market days immediately follow the worst ones. Selling now means missing that recovery."
            
    elif emotion in ["Excited", "Greedy"]:
        if persona == "Empathetic":
            response += f"It is so exciting to watch returns jump up, and wanting to capitalize on hot trends is totally human! {goal_mention}But concentrating too much capital in speculative plays can backfire. Let's make sure your core savings are protected first before allocating capital to high-beta assets."
        elif persona == "Analytical":
            response += f"We must evaluate concentration risk. Standard portfolio theory advises keeping speculative assets below 5-10% of total holdings to maximize the Sharpe Ratio. {goal_mention}Chasing exponential charts usually leads to buying near the peak where standard deviation risk is highest."
        else: # Direct
            response += f"You are chasing hype, which is a classic FOMO trap. Investing is not a lottery. {goal_mention}Putting significant funds into speculative assets is gambling, not planning. Keep speculative assets under 5% or you will get burned."
            
        if "crypto" in text_lower or "bitcoin" in text_lower or "doge" in text_lower:
            response += " Cryptocurrencies can dump 80% as fast as they pump. Ensure you only invest what you are 100% prepared to write off as a total loss."
            
    elif emotion == "Calm":
        if persona == "Empathetic":
            response += f"I am glad to see you taking a calm, structured approach. {goal_mention}Staying focused on your long-term plan is the key. You are managing the emotional side of wealth creation beautifully."
        elif persona == "Analytical":
            response += f"Your logical outlook minimizes transaction slippage and portfolio tracking errors. {goal_mention}Maintaining target asset weightings under calm conditions maximizes compound efficiency."
        else: # Direct
            response += f"Good. Emotional discipline separates successful investors from losers. {goal_mention}Keep your automatic transfers running and let compounding do the heavy lifting."
            
    else: # Neutral
        if persona == "Empathetic":
            response += f"How can I help you navigate your wealth plan today? {goal_mention}I am here to discuss both your financial targets and how you're feeling about the markets."
        elif persona == "Analytical":
            response += f"I can assist you with portfolio optimization, goal horizon modeling, or risk assessments. {goal_mention}Please specify your criteria."
        else: # Direct
            response += f"Let's focus. What financial goals or portfolio queries are we adjusting today? {goal_mention}Give me the details."
            
    return response

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
    async def get_response(profile: UserProfile, conversation_history: list, new_message: str, goals: list = None) -> dict:
        api_type = profile.api_key_type
        api_key = profile.api_key_value
        persona = profile.advisor_persona or "Empathetic"
        
        # If API key is not configured, fall back to our advanced dynamic response builder
        if api_type == "mock" or not api_key:
            analysis = LLMService.analyze_heuristics(new_message)
            response_text = generate_dynamic_fallback(profile, analysis["emotion"], new_message, goals)
            
            return {
                "text": response_text,
                "emotion": analysis["emotion"],
                "fear_score": analysis["fear_score"],
                "greed_score": analysis["greed_score"],
                "logic_score": analysis["logic_score"]
            }

        # Format system prompt context
        goal_text = ""
        if goals and len(goals) > 0:
            goal_text = "The client has the following financial goals defined:\n"
            for g in goals:
                goal_text += f"- {g.name}: target ${g.target_amount:,}, current saved ${g.current_amount:,}, due by {g.target_date}, priority {g.priority}.\n"
            goal_text += "Please reference these goals when appropriate to offer highly personalized, context-aware coaching.\n"

        system_instruction = f"""
        {PERSONA_PROMPTS.get(persona, PERSONA_PROMPTS['Empathetic'])}
        
        {goal_text}
        
        Analyze the client's emotional state. Detect:
        - Primary emotion: 'Panic', 'Anxious', 'Calm', 'Greedy', 'Excited', or 'Neutral'.
        - Fear Score (0-100): Level of panic/scared/anxious feelings.
        - Greed Score (0-100): Level of FOMO/chasing returns/speculation/overconfidence.
        - Logic Score (0-100): Level of strategic, long-term, calm financial thinking.
        
        You MUST respond ONLY with a valid JSON object matching this structure:
        {{
          "response": "Your personalized coach advice here, reference their specific goals if relevant",
          "emotion": "Detected Emotion",
          "fear_score": 0.0,
          "greed_score": 0.0,
          "logic_score": 50.0
        }}
        """

        try:
            if api_type == "gemini":
                genai.configure(api_key=api_key)
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
                
            elif api_type == "groq" or api_type == "grok":
                if api_type == "groq":
                    endpoint = "https://api.groq.com/openai/v1/chat/completions"
                    model = "mixtral-8x7b-32768"
                else:
                    endpoint = "https://api.x.ai/v1/chat/completions"
                    model = "grok-beta"

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                messages = [{"role": "system", "content": system_instruction}]
                for msg in conversation_history[-6:]:
                    role = "user" if msg.sender == "user" else "assistant"
                    messages.append({"role": role, "content": msg.text})
                messages.append({"role": "user", "content": new_message})
                
                payload = {
                    "model": model,
                    "messages": messages,
                    "response_format": {"type": "json_object"},
                    "temperature": 0.5
                }
                
                async with httpx.AsyncClient() as client:
                    res = await client.post(endpoint, headers=headers, json=payload, timeout=15.0)
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
                        raise Exception(f"{api_type.upper()} API error: {res.text}")
                        
        except Exception as e:
            print(f"LLM API Call failed, falling back to heuristics: {str(e)}")
            fallback = LLMService.analyze_heuristics(new_message)
            response_text = generate_dynamic_fallback(profile, fallback["emotion"], new_message, goals)
            response_text = f"[API Fallback - {api_type.upper()} Error] {response_text}"
            return {
                "text": response_text,
                "emotion": fallback["emotion"],
                "fear_score": fallback["fear_score"],
                "greed_score": fallback["greed_score"],
                "logic_score": fallback["logic_score"]
            }
