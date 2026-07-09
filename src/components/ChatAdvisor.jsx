import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Trash2, 
  Brain, 
  Activity, 
  AlertTriangle, 
  TrendingUp, 
  Heart,
  CornerDownLeft
} from 'lucide-react';

export default function ChatAdvisor({ activeChats, onSendMessage, onClearHistory, isLoading }) {
  const [inputText, setInputText] = useState('');
  const chatBottomRef = useRef(null);
  
  // Local state for last analysis parameters
  const [lastAnalysis, setLastAnalysis] = useState({
    emotion: 'Neutral',
    fear: 0,
    greed: 0,
    logic: 50
  });

  useEffect(() => {
    // Scroll to bottom when chats update or loading state changes
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    
    // Extract latest user analysis
    if (activeChats && activeChats.length > 0) {
      const userMsgs = activeChats.filter(m => m.sender === 'user');
      if (userMsgs.length > 0) {
        const lastMsg = userMsgs[userMsgs.length - 1];
        setLastAnalysis({
          emotion: lastMsg.emotion || 'Neutral',
          fear: lastMsg.fear_score || 0,
          greed: lastMsg.greed_score || 0,
          logic: lastMsg.logic_score || 50
        });
      }
    } else {
      setLastAnalysis({
        emotion: 'Neutral',
        fear: 0,
        greed: 0,
        logic: 50
      });
    }
  }, [activeChats, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;
    onSendMessage(inputText);
    setInputText('');
  };

  const handleQuickPrompt = (promptText) => {
    if (isLoading) return;
    onSendMessage(promptText);
  };

  // Bias detection based on scores
  const getDetectedBiases = () => {
    const biases = [];
    if (lastAnalysis.fear > 50) {
      biases.push({
        name: 'Loss Aversion',
        desc: 'Pain of losses is felt twice as much as gains, driving early liquidation.'
      });
      biases.push({
        name: 'Recency Bias',
        desc: 'Over-indexing on recent market drops, assuming they will drop forever.'
      });
    }
    if (lastAnalysis.greed > 50) {
      biases.push({
        name: 'FOMO (Fear of Missing Out)',
        desc: 'Chasing skyrocketing assets near their peak due to social excitement.'
      });
      biases.push({
        name: 'Overconfidence Bias',
        desc: 'Underestimating market risks and overestimating personal timing ability.'
      });
    }
    if (lastAnalysis.fear <= 30 && lastAnalysis.greed <= 30 && lastAnalysis.logic > 60) {
      biases.push({
        name: 'Rational Asset Allocation',
        desc: 'Holding long term parameters and strategic rebalancing principles.'
      });
    }
    return biases;
  };

  const detectedBiases = getDetectedBiases();

  return (
    <div className="chat-advisor-view animate-fade-in" style={{ display: 'flex', gap: '30px', height: 'calc(100vh - 120px)' }}>
      
      {/* Left Area: Chat messages and input */}
      <div className="glass-card" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '20px', height: '100%', overflow: 'hidden' }}>
        
        {/* Chat Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '16px', borderBottom: '1px solid var(--border-glass)', marginBottom: '16px' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontFamily: 'var(--font-display)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Heart size={18} style={{ color: 'var(--primary)' }} />
              Emotional AI Financial Coach
            </h2>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Sentiment analysis is active. Feel free to talk about your market anxieties or exciting crypto plays.
            </span>
          </div>
          <button className="btn-secondary" style={{ padding: '6px 12px', fontSize: '0.85rem' }} onClick={onClearHistory} title="Clear Chat History">
            <Trash2 size={14} /> Clear
          </button>
        </div>

        {/* Messages list */}
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px', paddingRight: '8px', marginBottom: '20px' }}>
          {activeChats.length === 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', textAlign: 'center', gap: '15px' }}>
              <Brain size={48} style={{ strokeWidth: 1.5, opacity: 0.5 }} />
              <div>
                <h4 style={{ color: 'var(--text-main)', marginBottom: '4px' }}>Start your first conversational session</h4>
                <p style={{ fontSize: '0.85rem', maxWidth: '350px' }}>
                  Ask questions about budgeting, goals, or express your feelings on the current market environment.
                </p>
              </div>
              
              {/* Quick Prompt Cards */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', width: '100%', maxWidth: '350px', marginTop: '10px' }}>
                <button className="btn-secondary" style={{ fontSize: '0.8rem', textAlign: 'left', padding: '10px' }} onClick={() => handleQuickPrompt("I'm feeling really anxious about the market dropping recently. Should I sell my shares to be safe?")}>
                  "I'm anxious about the market dip. Should I sell?"
                </button>
                <button className="btn-secondary" style={{ fontSize: '0.8rem', textAlign: 'left', padding: '10px' }} onClick={() => handleQuickPrompt("Everyone is making 10x gains in crypto right now. I want to invest all my savings to not miss out!")}>
                  "I want to dump savings in hot crypto coins."
                </button>
                <button className="btn-secondary" style={{ fontSize: '0.8rem', textAlign: 'left', padding: '10px' }} onClick={() => handleQuickPrompt("I want to make a long term savings plan for my retirement in 25 years. How should I set it up?")}>
                  "Help me setup a long-term retirement plan."
                </button>
              </div>
            </div>
          ) : (
            activeChats.map((msg, index) => (
              <div key={msg.id || index} style={{ 
                alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '75%',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px'
              }}>
                <div style={{
                  background: msg.sender === 'user' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                  border: msg.sender === 'user' ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid var(--border-glass)',
                  padding: '14px 18px',
                  borderRadius: msg.sender === 'user' ? '16px 16px 2px 16px' : '16px 16px 16px 2px',
                  color: 'var(--text-main)',
                  fontSize: '0.92rem',
                  lineHeight: '1.5'
                }}>
                  {msg.text}
                </div>
                
                {/* Sentiment tag underneath advisor messages */}
                {msg.sender === 'advisor' && msg.emotion && msg.emotion !== 'Neutral' && (
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginTop: '2px', paddingLeft: '4px' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Detected Sentiment:</span>
                    <span className={`emotion-badge ${msg.emotion.toLowerCase()}`} style={{ fontSize: '0.6rem', padding: '1px 6px' }}>
                      {msg.emotion}
                    </span>
                  </div>
                )}
              </div>
            ))
          )}
          {isLoading && (
            <div style={{ alignSelf: 'flex-start', display: 'flex', gap: '8px', alignItems: 'center', padding: '12px 18px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-glass)', borderRadius: '16px' }}>
              <span className="dot-pulse" style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>AI Advisor is analyzing your sentiment...</span>
            </div>
          )}
          <div ref={chatBottomRef} />
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px', position: 'relative' }}>
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type your investment question or financial worries here..."
            disabled={isLoading}
            style={{ flex: 1, padding: '14px', borderRadius: '12px', paddingRight: '50px' }}
          />
          <button 
            type="submit" 
            className="btn-primary" 
            style={{ padding: '14px 20px', borderRadius: '12px' }} 
            disabled={isLoading || !inputText.trim()}
          >
            <Send size={16} />
          </button>
        </form>

      </div>

      {/* Right Area: Analysis dashboard */}
      <div className="glass-card" style={{ width: '280px', display: 'flex', flexDirection: 'column', gap: '20px', height: '100%', overflowY: 'auto' }}>
        
        <div>
          <h3 style={{ fontSize: '1rem', fontFamily: 'var(--font-display)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={16} style={{ color: 'var(--primary)' }} />
            Emotional Barometer
          </h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', background: 'rgba(255,255,255,0.02)', padding: '14px', borderRadius: '12px', border: '1px solid var(--border-glass)' }}>
            
            {/* Fear Indicator */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
                <span>Fear / Anxiety</span>
                <span style={{ color: 'var(--color-panic)', fontWeight: 'bold' }}>{lastAnalysis.fear.toFixed(0)}%</span>
              </div>
              <div style={{ height: '6px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${lastAnalysis.fear}%`, height: '100%', background: 'var(--color-panic)', borderRadius: '3' }} />
              </div>
            </div>

            {/* Greed Indicator */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
                <span>Greed / FOMO</span>
                <span style={{ color: 'var(--color-greedy)', fontWeight: 'bold' }}>{lastAnalysis.greed.toFixed(0)}%</span>
              </div>
              <div style={{ height: '6px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${lastAnalysis.greed}%`, height: '100%', background: 'var(--color-greedy)', borderRadius: '3' }} />
              </div>
            </div>

            {/* Logic Indicator */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
                <span>Logical Strategy</span>
                <span style={{ color: 'var(--color-calm)', fontWeight: 'bold' }}>{lastAnalysis.logic.toFixed(0)}%</span>
              </div>
              <div style={{ height: '6px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${lastAnalysis.logic}%`, height: '100%', background: 'var(--color-calm)', borderRadius: '3' }} />
              </div>
            </div>

          </div>
        </div>

        {/* Active Emotion Badge info */}
        <div>
          <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>Current Advisor Diagnosis</h4>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className={`emotion-badge ${lastAnalysis.emotion.toLowerCase()}`}>
              {lastAnalysis.emotion}
            </span>
          </div>
        </div>

        {/* Biases detected card */}
        <div style={{ flex: 1, borderTop: '1px solid var(--border-glass)', paddingTop: '15px' }}>
          <h3 style={{ fontSize: '0.9rem', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--color-anxious)' }}>
            <AlertTriangle size={14} />
            Detected Behavioral Biases
          </h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {detectedBiases.length === 0 ? (
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                No significant cognitive investment biases detected in the latest session. Keep it up!
              </p>
            ) : (
              detectedBiases.map((bias, idx) => (
                <div key={idx} style={{ padding: '10px', background: 'rgba(245, 158, 11, 0.05)', border: '1px solid rgba(245, 158, 11, 0.2)', borderRadius: '8px' }}>
                  <h5 style={{ fontSize: '0.8rem', color: 'var(--text-main)', marginBottom: '2px', fontWeight: 'bold' }}>{bias.name}</h5>
                  <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', lineHeight: '1.3' }}>{bias.desc}</p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Small disclaimer */}
        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', lineHeight: '1.4', background: 'rgba(255,255,255,0.01)', padding: '10px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.02)' }}>
          <strong>Note:</strong> Advice adjusts dynamically. Extreme fear adds cash buffers; excessive speculation caps assets. Review allocations on the Portfolio page.
        </div>

      </div>

    </div>
  );
}
