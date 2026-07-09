import React, { useState } from 'react';
import { 
  Settings as SettingsIcon, 
  Key, 
  User, 
  Sliders, 
  ShieldCheck, 
  Save 
} from 'lucide-react';

export default function Settings({ profile, onSaveSettings }) {
  const [name, setName] = useState(profile.name || '');
  const [riskTolerance, setRiskTolerance] = useState(profile.risk_tolerance || 'Moderate');
  const [investmentHorizon, setInvestmentHorizon] = useState(profile.investment_horizon || 'Medium-Term');
  const [advisorPersona, setAdvisorPersona] = useState(profile.advisor_persona || 'Empathetic');
  const [apiKeyType, setApiKeyType] = useState(profile.api_key_type || 'mock');
  const [apiKeyValue, setApiKeyValue] = useState(profile.api_key_value || '');
  const [showSavedAlert, setShowSavedAlert] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSaveSettings({
      name,
      risk_tolerance: riskTolerance,
      investment_horizon: investmentHorizon,
      advisor_persona: advisorPersona,
      api_key_type: apiKeyType,
      api_key_value: apiKeyValue
    });
    
    setShowSavedAlert(true);
    setTimeout(() => {
      setShowSavedAlert(false);
    }, 3000);
  };

  return (
    <div className="settings-view animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '30px', maxWidth: '800px' }}>
      
      {/* Header */}
      <div>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '2.2rem', marginBottom: '8px' }}>
          Advisor Configurations
        </h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Configure advisor personalities, financial metrics, and LLM connections.
        </p>
      </div>

      {showSavedAlert && (
        <div style={{ background: 'rgba(16, 185, 129, 0.15)', border: '1px solid var(--primary)', borderRadius: '12px', padding: '16px', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 'bold' }} className="animate-fade-in">
          <ShieldCheck size={20} /> Settings saved successfully!
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        
        {/* Profile Details */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', fontFamily: 'var(--font-display)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <User size={18} style={{ color: 'var(--primary)' }} />
            Personal Profile
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div>
              <label>Your Name</label>
              <input 
                type="text" 
                value={name} 
                onChange={(e) => setName(e.target.value)} 
                placeholder="e.g. Aditi Sharma"
                style={{ width: '100%' }}
                required
              />
            </div>
          </div>
        </div>

        {/* Investment Parameters */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', fontFamily: 'var(--font-display)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sliders size={18} style={{ color: 'var(--primary)' }} />
            Financial Risk Parameters
          </h3>
          
          <div className="grid-2" style={{ gap: '16px' }}>
            <div>
              <label>Risk Tolerance Profile</label>
              <select value={riskTolerance} onChange={(e) => setRiskTolerance(e.target.value)} style={{ width: '100%' }}>
                <option value="Conservative">Conservative (20% Stocks / 60% Bonds / 20% Defs)</option>
                <option value="Moderate">Moderate (60% Stocks / 25% Bonds / 15% Defs)</option>
                <option value="Aggressive">Aggressive (80% Stocks / 10% Bonds / 10% Defs)</option>
              </select>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginTop: '4px' }}>
                Governs your core baseline portfolio asset allocation mix.
              </span>
            </div>
            
            <div>
              <label>Investment Horizon</label>
              <select value={investmentHorizon} onChange={(e) => setInvestmentHorizon(e.target.value)} style={{ width: '100%' }}>
                <option value="Short-Term">Short-Term (Under 2 years)</option>
                <option value="Medium-Term">Medium-Term (2 - 7 years)</option>
                <option value="Long-Term">Long-Term (Over 7 years)</option>
              </select>
            </div>
          </div>

          <div style={{ marginTop: '20px' }}>
            <label>Advisor Persona Style</label>
            <select value={advisorPersona} onChange={(e) => setAdvisorPersona(e.target.value)} style={{ width: '100%' }}>
              <option value="Empathetic">Empathetic (Acknowledges emotions first, comforting tone)</option>
              <option value="Analytical">Analytical (Focuses on quantitative facts, data-driven response)</option>
              <option value="Direct">Direct (No-nonsense, firm, focuses on investor discipline)</option>
            </select>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginTop: '4px' }}>
              Determines how the conversational chatbot responds to panic or excitement.
            </span>
          </div>
        </div>

        {/* AI Key Configuration */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', fontFamily: 'var(--font-display)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Key size={18} style={{ color: 'var(--primary)' }} />
            AI & LLM Services Configuration
          </h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label>LLM Engine Provider</label>
              <select value={apiKeyType} onChange={(e) => setApiKeyType(e.target.value)} style={{ width: '100%' }}>
                <option value="mock">Built-in Advisor Heuristics (Default - Free & Offline)</option>
                <option value="gemini">Google Gemini AI API (Real LLM)</option>
                <option value="groq">Groq LLM API (Real LLM)</option>
              </select>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginTop: '4px' }}>
                Offline heuristics analyze keywords for emotion. Connecting an API enables full LLM conversations.
              </span>
            </div>

            {apiKeyType !== 'mock' && (
              <div className="animate-fade-in">
                <label>{apiKeyType === 'gemini' ? 'Gemini API Key' : 'Groq API Key'}</label>
                <input 
                  type="password" 
                  value={apiKeyValue} 
                  onChange={(e) => setApiKeyValue(e.target.value)} 
                  placeholder={apiKeyType === 'gemini' ? 'AIzaSy...' : 'gsk_...'}
                  style={{ width: '100%' }}
                  required
                />
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginTop: '4px' }}>
                  Your key is saved locally in SQLite db and never sent to external servers other than directly to the LLM API provider.
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Save button */}
        <button type="submit" className="btn-primary" style={{ padding: '14px', width: '100%', justifyContent: 'center' }}>
          <Save size={16} /> Save Configurations
        </button>

      </form>

    </div>
  );
}
