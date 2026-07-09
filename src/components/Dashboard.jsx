import React, { useEffect, useState } from 'react';
import { 
  PiggyBank, 
  Brain, 
  TrendingUp, 
  ShieldAlert, 
  Activity, 
  ArrowRight,
  Sparkles,
  Compass,
  AlertTriangle
} from 'lucide-react';

export default function Dashboard({ profile, goals, activeChats, setView }) {
  const [marketMood, setMarketMood] = useState(50); // 0 (Fear) to 100 (Greed)
  const [latestEmotion, setLatestEmotion] = useState('Neutral');
  const [fearScore, setFearScore] = useState(0);
  const [greedScore, setGreedScore] = useState(0);
  const [logicScore, setLogicScore] = useState(50);
  
  useEffect(() => {
    // Generate an arbitrary fluctuating market mood for interactive interest
    const randomMood = Math.floor(45 + Math.random() * 20); // 45-65 range
    setMarketMood(randomMood);
    
    // Find latest user chat emotion
    if (activeChats && activeChats.length > 0) {
      const userMsgs = activeChats.filter(m => m.sender === 'user');
      if (userMsgs.length > 0) {
        const lastMsg = userMsgs[userMsgs.length - 1];
        setLatestEmotion(lastMsg.emotion || 'Neutral');
        setFearScore(lastMsg.fear_score || 0);
        setGreedScore(lastMsg.greed_score || 0);
        setLogicScore(lastMsg.logic_score || 50);
      }
    }
  }, [activeChats]);

  // Goal math
  const totalGoals = goals.length;
  const totalTarget = goals.reduce((sum, g) => sum + g.target_amount, 0);
  const totalSaved = goals.reduce((sum, g) => sum + g.current_amount, 0);
  const overallProgress = totalTarget > 0 ? (totalSaved / totalTarget) * 100 : 0;

  const getEmotionDetails = (emotion) => {
    switch (emotion) {
      case 'Panic':
        return {
          title: 'Extreme Panic Detected',
          desc: 'High market anxiety detected in your chat responses. Avoid making rushed decisions to sell out of assets.',
          color: 'var(--color-panic)',
          bias: 'Loss Aversion Bias: You feel losses twice as painfully as gains, prompting irrational asset liquidation.'
        };
      case 'Anxious':
        return {
          title: 'Anxiety Level Elevating',
          desc: 'You seem worried about market dips. Check your diversification rather than watching day-to-day fluctuations.',
          color: 'var(--color-anxious)',
          bias: 'Herd Mentality / Recency Bias: Worrying that recent negative trends will persist indefinitely.'
        };
      case 'Greedy':
        return {
          title: 'High Speculative Drive',
          desc: 'FOMO detected! Be cautious of allocating large amounts to hyper-growth or hype assets right now.',
          color: 'var(--color-greedy)',
          bias: 'Overconfidence / FOMO: Chasing high returns without accounting for tail-risk standard deviation.'
        };
      case 'Excited':
        return {
          title: 'Optimistic State',
          desc: 'You are feeling enthusiastic. Harness this energy for disciplined monthly automatic allocations rather than lump sum hype.',
          color: 'var(--color-excited)',
          bias: 'Hindsight Bias: Overestimating personal ability to predict market upsides.'
        };
      case 'Calm':
        return {
          title: 'Logical & Balanced',
          desc: 'Excellent discipline. You are holding a rational perspective, looking past short-term volatility.',
          color: 'var(--color-calm)',
          bias: 'No major behavioral bias detected. Keep sticking to your long-term plan.'
        };
      default:
        return {
          title: 'Balanced & Steady',
          desc: 'Ask your advisor about optimizing your portfolio or tracking a specific target goal today.',
          color: 'var(--color-neutral)',
          bias: 'Neutral state. Your advisor is ready to map out new goal allocations.'
        };
    }
  };

  const emotionMeta = getEmotionDetails(latestEmotion);

  return (
    <div className="dashboard-view animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '2.2rem', marginBottom: '8px' }}>
            Welcome back, {profile.name || 'Investor'}
          </h1>
          <p style={{ color: 'var(--text-muted)' }}>
            Empowering your wealth creation by aligning your financial plans with emotional discipline.
          </p>
        </div>
        <button className="btn-primary" onClick={() => setView('chat')}>
          Talk to Advisor <ArrowRight size={16} />
        </button>
      </div>

      {/* Row 1: KPI Stats */}
      <div className="grid-3">
        
        {/* Goals Progress Card */}
        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '16px', borderRadius: '12px', color: 'var(--primary)' }}>
            <PiggyBank size={28} />
          </div>
          <div style={{ flex: 1 }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Goal Progress
            </span>
            <h3 style={{ fontSize: '1.8rem', margin: '4px 0', fontFamily: 'var(--font-display)' }}>
              {overallProgress.toFixed(0)}%
            </h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              ${totalSaved.toLocaleString()} of ${totalTarget.toLocaleString()} saved
            </span>
            <div className="progress-container">
              <div className="progress-bar" style={{ width: `${overallProgress}%` }}></div>
            </div>
          </div>
        </div>

        {/* Emotion Score Barometer */}
        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ background: 'rgba(139, 92, 246, 0.1)', padding: '16px', borderRadius: '12px', color: 'var(--color-excited)' }}>
            <Brain size={28} />
          </div>
          <div style={{ flex: 1 }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Emotional Tone
            </span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: '4px 0' }}>
              <h3 style={{ fontSize: '1.6rem', fontFamily: 'var(--font-display)', color: emotionMeta.color }}>
                {latestEmotion}
              </h3>
              <span className={`emotion-badge ${latestEmotion.toLowerCase()}`} style={{ fontSize: '0.65rem', padding: '2px 8px' }}>
                Active
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '8px' }}>
              <span>Fear: {fearScore.toFixed(0)}%</span>
              <span>Greed: {greedScore.toFixed(0)}%</span>
              <span>Logic: {logicScore.toFixed(0)}%</span>
            </div>
          </div>
        </div>

        {/* Advisor Personality */}
        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ background: 'rgba(59, 130, 246, 0.1)', padding: '16px', borderRadius: '12px', color: 'var(--color-neutral)' }}>
            <Compass size={28} />
          </div>
          <div>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Advisor Persona
            </span>
            <h3 style={{ fontSize: '1.8rem', margin: '4px 0', fontFamily: 'var(--font-display)' }}>
              {profile.advisor_persona}
            </h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Style: {profile.risk_tolerance} Risk
            </span>
          </div>
        </div>

      </div>

      {/* Row 2: Charts and Emotional Alert */}
      <div className="grid-2">
        
        {/* Market Mood and Emotional Meter */}
        <div className="glass-card" style={{ position: 'relative', overflow: 'hidden' }}>
          <h2 style={{ fontSize: '1.2rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={18} style={{ color: 'var(--primary)' }} />
            Market Mood vs. Advisor Sentiment
          </h2>
          
          {/* Custom SVG gauge */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: '20px' }}>
            <svg width="220" height="120" viewBox="0 0 200 110">
              <defs>
                <linearGradient id="gauge-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="var(--color-panic)" />
                  <stop offset="50%" stopColor="var(--color-neutral)" />
                  <stop offset="100%" stopColor="var(--color-greedy)" />
                </linearGradient>
              </defs>
              {/* Arc path */}
              <path 
                d="M20,100 A80,80 0 0,1 180,100" 
                fill="none" 
                stroke="url(#gauge-grad)" 
                strokeWidth="15" 
                strokeLinecap="round"
              />
              {/* Needle for Market Mood */}
              <g transform={`translate(100,100) rotate(${180 * (marketMood/100) - 90})`}>
                <line x1="0" y1="0" x2="0" y2="-75" stroke="#f8fafc" strokeWidth="3" strokeLinecap="round" />
                <circle cx="0" cy="0" r="8" fill="#f8fafc" />
              </g>
            </svg>
            <div style={{ display: 'flex', justifyContent: 'space-between', width: '200px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              <span>Panic/Fear</span>
              <span>Greed/FOMO</span>
            </div>
            <div style={{ textAlign: 'center', marginTop: '10px' }}>
              <span style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>Market Index: {marketMood}</span>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem', display: 'block' }}>
                (Self-correcting Index: Stable ranges)
              </span>
            </div>
          </div>

          <div style={{ borderTop: '1px solid var(--border-glass)', marginTop: '20px', paddingTop: '15px' }}>
            <h4 style={{ fontSize: '0.9rem', marginBottom: '4px' }}>Latest User Sentiment Index</h4>
            <div style={{ height: '8px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '4px', overflow: 'hidden', position: 'relative' }}>
              {/* Fear marker */}
              <div style={{ 
                position: 'absolute', 
                left: '0', 
                width: `${fearScore}%`, 
                height: '100%', 
                background: 'var(--color-panic)', 
                opacity: 0.8 
              }} />
              {/* Greed marker */}
              <div style={{ 
                position: 'absolute', 
                right: '0', 
                width: `${greedScore}%`, 
                height: '100%', 
                background: 'var(--color-greedy)', 
                opacity: 0.8 
              }} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              <span>Anxiety: {fearScore.toFixed(0)}%</span>
              <span>Greed/FOMO: {greedScore.toFixed(0)}%</span>
            </div>
          </div>
        </div>

        {/* Dynamic Behavioral Biases Guard */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <h2 style={{ fontSize: '1.2rem', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px', color: emotionMeta.color }}>
              <ShieldAlert size={20} />
              {emotionMeta.title}
            </h2>
            <p style={{ fontSize: '0.95rem', lineHeight: '1.5', color: 'var(--text-main)', marginBottom: '16px' }}>
              {emotionMeta.desc}
            </p>
            
            <div style={{ background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-glass)', borderRadius: '12px', padding: '16px' }}>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--color-anxious)', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px', textTransform: 'uppercase', fontWeight: 700 }}>
                <AlertTriangle size={14} />
                Cognitive Bias Warning
              </h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                {emotionMeta.bias}
              </p>
            </div>
          </div>

          <div style={{ marginTop: '20px', display: 'flex', gap: '12px' }}>
            <button className="btn-secondary" style={{ flex: 1, padding: '10px' }} onClick={() => setView('portfolio')}>
              View Portfolio Adjustments
            </button>
            <button className="btn-primary" style={{ flex: 1, padding: '10px' }} onClick={() => setView('chat')}>
              Talk Out Volatility
            </button>
          </div>
        </div>

      </div>

      {/* Row 3: Educational Insights & Tips */}
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
          <Sparkles size={18} style={{ color: 'var(--color-excited)' }} />
          <h2 style={{ fontSize: '1.2rem' }}>Disciplined Investing Principle</h2>
        </div>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-start', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '280px' }}>
            <h3 style={{ fontSize: '1rem', color: 'var(--primary)', marginBottom: '6px' }}>The Core-Satellite Philosophy</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
              We recommend keeping 90% of your wealth in well-diversified index funds, bonds, and high-quality blue chips. Limit speculative asset plays to 10% or less. This ensures that even in periods of extreme greed or panic, your financial foundation remains unshaken.
            </p>
          </div>
          <div style={{ borderLeft: '1px solid var(--border-glass)', height: '80px', display: 'block' }} className="hide-on-mobile"></div>
          <div style={{ flex: 1, minWidth: '280px' }}>
            <h3 style={{ fontSize: '1rem', color: 'var(--color-neutral)', marginBottom: '6px' }}>Market Recency Bias</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
              Human nature overweights recent events. When stocks are down, we believe they will drop forever. When assets surge, we assume they will rise to infinity. Counteract this by setting up automatic transfers, allowing you to buy more shares when assets are cheap, and fewer when expensive.
            </p>
          </div>
        </div>
      </div>

    </div>
  );
}
