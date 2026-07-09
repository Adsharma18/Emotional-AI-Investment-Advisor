import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  ShieldAlert, 
  HelpCircle, 
  Info,
  Layers,
  ArrowRight,
  Activity,
  Smile,
  Compass
} from 'lucide-react';

export default function PortfolioVisualizer({ portfolioData, profile, onRefresh }) {
  const [useEmotionalAdjustment, setUseEmotionalAdjustment] = useState(true);

  // Asset class color mapping
  const assetColors = {
    "Equities (Global Stocks)": "#10b981",    // Emerald
    "Fixed Income (Bonds)": "#3b82f6",        // Blue
    "Commodities (Gold)": "#f59e0b",          // Gold
    "Cash Equivalents": "#6b7280",             // Gray
    "Speculative (Crypto/Tech)": "#8b5cf6",    // Purple
  };

  const getAssetColor = (assetClass) => {
    return assetColors[assetClass] || "#3b82f6";
  };

  const activeAllocation = useEmotionalAdjustment && portfolioData.is_adjusted
    ? portfolioData.allocation
    : getBaselineAllocation(portfolioData.risk_profile);

  // Calculate baseline static values
  function getBaselineAllocation(risk) {
    const baselines = {
      "Conservative": [
        {"asset_class": "Equities (Global Stocks)", "percentage": 20.0, "description": "High-quality, dividend-paying global stocks for long-term growth."},
        {"asset_class": "Fixed Income (Bonds)", "percentage": 60.0, "description": "Government and corporate bonds providing stability and steady yield."},
        {"asset_class": "Commodities (Gold)", "percentage": 10.0, "description": "Inflation hedge and defensive asset during market stress."},
        {"asset_class": "Cash Equivalents", "percentage": 10.0, "description": "Highly liquid, risk-free assets for immediate flexibility."}
      ],
      "Moderate": [
        {"asset_class": "Equities (Global Stocks)", "percentage": 60.0, "description": "Diversified index funds targeting capital appreciation."},
        {"asset_class": "Fixed Income (Bonds)", "percentage": 25.0, "description": "Intermediate-term bonds offering balanced risk/reward."},
        {"asset_class": "Commodities (Gold)", "percentage": 10.0, "description": "Inflation protection and portfolio diversification."},
        {"asset_class": "Cash Equivalents", "percentage": 5.0, "description": "Reserve cash for liquidity and adjustments."}
      ],
      "Aggressive": [
        {"asset_class": "Equities (Global Stocks)", "percentage": 80.0, "description": "Growth-oriented global equities for maximum long-term growth."},
        {"asset_class": "Fixed Income (Bonds)", "percentage": 10.0, "description": "Short-duration bonds for minor safety buffers."},
        {"asset_class": "Commodities (Gold)", "percentage": 5.0, "description": "Minimal hedge asset allocation."},
        {"asset_class": "Speculative (Crypto/Tech)", "percentage": 5.0, "description": "High-risk, high-reward digital assets or sector plays."}
      ]
    };
    return baselines[risk] || baselines["Moderate"];
  }

  // Donut chart math
  const radius = 70;
  const circumference = 2 * Math.PI * radius; // ~439.82
  let cumulativePercent = 0;

  return (
    <div className="portfolio-visualizer animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '2.2rem', marginBottom: '8px' }}>
            Portfolio Allocation
          </h1>
          <p style={{ color: 'var(--text-muted)' }}>
            Dynamic asset configurations tailored to your risk profile and adjusted in real-time to insulate you from emotional trading mistakes.
          </p>
        </div>
        <button className="btn-secondary" onClick={onRefresh}>
          Recalculate Allocation
        </button>
      </div>

      {/* Grid: 2 Columns (Chart + Explanation) */}
      <div className="grid-2">
        
        {/* Left Card: Chart and Allocation details */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '20px' }}>
          
          {/* Toggle buttons */}
          {portfolioData.is_adjusted && (
            <div style={{ display: 'flex', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-glass)', padding: '4px', borderRadius: '10px', width: '100%', maxWidth: '340px', margin: '0 auto 10px' }}>
              <button 
                onClick={() => setUseEmotionalAdjustment(false)}
                style={{
                  flex: 1,
                  background: !useEmotionalAdjustment ? 'rgba(255,255,255,0.08)' : 'transparent',
                  border: 'none',
                  color: !useEmotionalAdjustment ? 'var(--text-main)' : 'var(--text-muted)',
                  padding: '8px 12px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '0.85rem',
                  fontWeight: 'bold',
                  transition: 'all 0.2s'
                }}
              >
                Strategic Base
              </button>
              <button 
                onClick={() => setUseEmotionalAdjustment(true)}
                style={{
                  flex: 1,
                  background: useEmotionalAdjustment ? 'var(--primary)' : 'transparent',
                  border: 'none',
                  color: useEmotionalAdjustment ? 'white' : 'var(--text-muted)',
                  padding: '8px 12px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '0.85rem',
                  fontWeight: 'bold',
                  boxShadow: useEmotionalAdjustment ? '0 4px 10px rgba(16,185,129,0.2)' : 'none',
                  transition: 'all 0.2s'
                }}
              >
                Emotion Adjusted
              </button>
            </div>
          )}

          {/* SVG Donut Chart */}
          <div style={{ position: 'relative', width: '200px', height: '200px' }}>
            <svg width="200" height="200" viewBox="0 0 200 200">
              <circle cx="100" cy="100" r={radius} fill="none" stroke="rgba(255,255,255,0.02)" strokeWidth="18" />
              {activeAllocation.map((item, idx) => {
                const dashoffset = circumference - (item.percentage / 100) * circumference;
                const rotation = (cumulativePercent / 100) * 360 - 90;
                cumulativePercent += item.percentage;
                
                return (
                  <circle
                    key={idx}
                    cx="100"
                    cy="100"
                    r={radius}
                    fill="none"
                    stroke={getAssetColor(item.asset_class)}
                    strokeWidth="16"
                    strokeDasharray={circumference}
                    strokeDashoffset={dashoffset}
                    transform={`rotate(${rotation} 100 100)`}
                    strokeLinecap={item.percentage > 4 ? "round" : "butt"}
                    style={{ transition: 'stroke-dashoffset 0.6s ease, transform 0.6s ease' }}
                  />
                );
              })}
            </svg>
            <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block' }}>
                Profile
              </span>
              <span style={{ fontSize: '1.2rem', fontWeight: 'bold', fontFamily: 'var(--font-display)', color: 'var(--primary)' }}>
                {portfolioData.risk_profile}
              </span>
            </div>
          </div>

          {/* Legend and progress bars */}
          <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '10px' }}>
            {activeAllocation.map((item, idx) => (
              <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: getAssetColor(item.asset_class) }} />
                    <span style={{ fontWeight: 500 }}>{item.asset_class}</span>
                  </div>
                  <span style={{ fontWeight: 'bold' }}>{item.percentage}%</span>
                </div>
                <div style={{ height: '4px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '2px', overflow: 'hidden' }}>
                  <div style={{ width: `${item.percentage}%`, height: '100%', background: getAssetColor(item.asset_class) }} />
                </div>
              </div>
            ))}
          </div>

        </div>

        {/* Right Card: Diagnosis explanation & Behavioral Guide */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Active adjustments card */}
          <div className="glass-card" style={{ borderLeft: portfolioData.is_adjusted && useEmotionalAdjustment ? '4px solid var(--color-anxious)' : '1px solid var(--border-glass)' }}>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldAlert size={18} style={{ color: portfolioData.is_adjusted ? 'var(--color-anxious)' : 'var(--color-calm)' }} />
              Advisor Status: {portfolioData.is_adjusted && useEmotionalAdjustment ? 'Emotionally Adjusted' : 'Strategic Baseline'}
            </h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-main)', lineHeight: '1.5' }}>
              {useEmotionalAdjustment && portfolioData.is_adjusted 
                ? portfolioData.explanation 
                : "Your advisor is currently in standard strategic mode. The portfolio represents your long-term wealth roadmap."
              }
            </p>
            {portfolioData.is_adjusted && !useEmotionalAdjustment && (
              <div style={{ background: 'rgba(245, 158, 11, 0.05)', padding: '12px', border: '1px solid rgba(245, 158, 11, 0.15)', borderRadius: '8px', marginTop: '15px', fontSize: '0.8rem', color: 'var(--color-anxious)' }}>
                * We noticed emotional distress in your chat history. It is highly recommended to toggle on "Emotion Adjusted" mode above to add a safety buffer.
              </div>
            )}
          </div>

          {/* Allocation definitions */}
          <div className="glass-card">
            <h3 style={{ fontSize: '1.1rem', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Layers size={18} style={{ color: 'var(--primary)' }} />
              Asset Descriptions
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {activeAllocation.map((item, idx) => (
                <div key={idx} style={{ paddingLeft: '12px', borderLeft: `2px solid ${getAssetColor(item.asset_class)}` }}>
                  <h4 style={{ fontSize: '0.9rem', fontWeight: 'bold', marginBottom: '2px' }}>{item.asset_class}</h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.3' }}>{item.description}</p>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>

      {/* Behavioral insight card */}
      <div className="glass-card" style={{ display: 'flex', gap: '16px', alignItems: 'flex-start', background: 'rgba(16, 185, 129, 0.03)', borderColor: 'rgba(16, 185, 129, 0.15)' }}>
        <Info size={24} style={{ color: 'var(--primary)', flexShrink: 0, marginTop: '2px' }} />
        <div>
          <h4 style={{ fontSize: '0.95rem', marginBottom: '4px', color: 'var(--text-main)' }}>The Emotion-Aware Rebalancing Strategy</h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
            Traditional robo-advisors force clients into static models, but during crashes, clients override these and sell at the bottom. By introducing an **Emotional Buffer**, we temporarily shift the client to a safer cash/bond holding during high-anxiety sessions. Once the client's sentiment calms, we systematically shift back to the higher-yield baseline, preserving long-term performance.
          </p>
        </div>
      </div>

    </div>
  );
}
