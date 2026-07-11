import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, 
  MessageSquare, 
  Target, 
  PieChart, 
  Settings as SettingsIcon,
  Brain,
  RefreshCw,
  LogOut
} from 'lucide-react';

import Dashboard from './components/Dashboard';
import ChatAdvisor from './components/ChatAdvisor';
import GoalsTracker from './components/GoalsTracker';
import PortfolioVisualizer from './components/PortfolioVisualizer';
import Settings from './components/Settings';
import Auth from './components/Auth';

const BACKEND_URL = 'http://localhost:8000';

function App() {
  const [token, setToken] = useState(localStorage.getItem('aura_token') || '');
  const [view, setView] = useState('dashboard');
  const [profile, setProfile] = useState({
    name: 'Investor',
    risk_tolerance: 'Moderate',
    investment_horizon: 'Medium-Term',
    advisor_persona: 'Empathetic',
    api_key_type: 'mock',
    api_key_value: ''
  });
  const [goals, setGoals] = useState([]);
  const [activeChats, setActiveChats] = useState([]);
  const [portfolioData, setPortfolioData] = useState({
    risk_profile: 'Moderate',
    detected_emotion: 'Neutral',
    is_adjusted: false,
    explanation: '',
    allocation: []
  });
  const [isLoadingChat, setIsLoadingChat] = useState(false);
  const [loadingApp, setLoadingApp] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Initialize data when token changes
  useEffect(() => {
    if (token) {
      fetchInitialData(token);
    }
  }, [token]);

  const fetchInitialData = async (activeToken) => {
    try {
      setLoadingApp(true);
      setErrorMsg(null);

      const headers = {
        'Authorization': `Bearer ${activeToken}`,
        'Content-Type': 'application/json'
      };

      // Fetch user profile
      const profileRes = await fetch(`${BACKEND_URL}/api/profile`, { headers });
      if (profileRes.status === 401) {
        handleLogout();
        return;
      }
      if (!profileRes.ok) throw new Error("Could not load profile from backend.");
      const profileData = await profileRes.json();
      setProfile(profileData);

      // Fetch goals
      const goalsRes = await fetch(`${BACKEND_URL}/api/goals`, { headers });
      const goalsData = await goalsRes.json();
      setGoals(goalsData);

      // Fetch chats
      const chatsRes = await fetch(`${BACKEND_URL}/api/chat`, { headers });
      const chatsData = await chatsRes.json();
      setActiveChats(chatsData);

      // Fetch portfolio recommendation
      const portRes = await fetch(`${BACKEND_URL}/api/portfolio`, { headers });
      const portData = await portRes.json();
      setPortfolioData(portData);

      setLoadingApp(false);
    } catch (err) {
      console.error(err);
      setErrorMsg("Failed to connect to the backend API. Please make sure the FastAPI server is running on port 8000.");
      setLoadingApp(false);
    }
  };

  const handleAuthSuccess = (newToken) => {
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('aura_token');
    setToken('');
    setView('dashboard');
    setProfile({
      name: 'Investor',
      risk_tolerance: 'Moderate',
      investment_horizon: 'Medium-Term',
      advisor_persona: 'Empathetic',
      api_key_type: 'mock',
      api_key_value: ''
    });
    setGoals([]);
    setActiveChats([]);
    setPortfolioData({
      risk_profile: 'Moderate',
      detected_emotion: 'Neutral',
      is_adjusted: false,
      explanation: '',
      allocation: []
    });
  };

  // Chat logic
  const handleSendMessage = async (text) => {
    setIsLoadingChat(true);
    try {
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      // Optimistically append user message to chat UI
      const tempUserMsg = {
        id: Date.now(),
        sender: 'user',
        text: text,
        timestamp: new Date().toISOString(),
        emotion: 'Neutral'
      };
      setActiveChats(prev => [...prev, tempUserMsg]);

      const res = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ text })
      });
      
      if (res.status === 401) {
        handleLogout();
        return;
      }
      
      const data = await res.json();
      
      // Update with database messages (contains analysis details)
      const chatsRes = await fetch(`${BACKEND_URL}/api/chat`, { headers });
      const chatsData = await chatsRes.json();
      setActiveChats(chatsData);

      // Re-fetch portfolio to apply any new emotional modifiers
      const portRes = await fetch(`${BACKEND_URL}/api/portfolio`, { headers });
      const portData = await portRes.json();
      setPortfolioData(portData);

    } catch (err) {
      console.error("Chat error:", err);
    } finally {
      setIsLoadingChat(false);
    }
  };

  const handleClearHistory = async () => {
    try {
      const headers = { 'Authorization': `Bearer ${token}` };
      await fetch(`${BACKEND_URL}/api/chat`, { method: 'DELETE', headers });
      setActiveChats([]);
      
      // Reset portfolio
      const portRes = await fetch(`${BACKEND_URL}/api/portfolio`, { headers });
      const portData = await portRes.json();
      setPortfolioData(portData);
    } catch (err) {
      console.error("Error clearing chat:", err);
    }
  };

  // Goals logic
  const handleAddGoal = async (newGoal) => {
    try {
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };
      const res = await fetch(`${BACKEND_URL}/api/goals`, {
        method: 'POST',
        headers,
        body: JSON.stringify(newGoal)
      });
      if (res.ok) {
        const goalsRes = await fetch(`${BACKEND_URL}/api/goals`, { headers });
        const goalsData = await goalsRes.json();
        setGoals(goalsData);
      }
    } catch (err) {
      console.error("Error adding goal:", err);
    }
  };

  const handleDeleteGoal = async (goalId) => {
    try {
      const headers = { 'Authorization': `Bearer ${token}` };
      const res = await fetch(`${BACKEND_URL}/api/goals/${goalId}`, {
        method: 'DELETE',
        headers
      });
      if (res.ok) {
        setGoals(prev => prev.filter(g => g.id !== goalId));
      }
    } catch (err) {
      console.error("Error deleting goal:", err);
    }
  };

  // Settings logic
  const handleSaveSettings = async (updatedSettings) => {
    try {
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };
      const res = await fetch(`${BACKEND_URL}/api/profile`, {
        method: 'POST',
        headers,
        body: JSON.stringify(updatedSettings)
      });
      if (res.ok) {
        const data = await res.json();
        setProfile(data);

        // Recalculate portfolio under new settings
        const portRes = await fetch(`${BACKEND_URL}/api/portfolio`, { headers });
        const portData = await portRes.json();
        setPortfolioData(portData);
      }
    } catch (err) {
      console.error("Error saving settings:", err);
    }
  };

  // Refresh data helper
  const handleRefreshPortfolio = async () => {
    try {
      const headers = { 'Authorization': `Bearer ${token}` };
      const portRes = await fetch(`${BACKEND_URL}/api/portfolio`, { headers });
      const portData = await portRes.json();
      setPortfolioData(portData);
    } catch (err) {
      console.error("Error refreshing portfolio:", err);
    }
  };

  // Get Initials for Avatar
  const getInitials = (fullName) => {
    if (!fullName) return 'U';
    return fullName.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
  };

  // 1. If not authenticated, render auth view
  if (!token) {
    return <Auth onAuthSuccess={handleAuthSuccess} />;
  }

  // 2. If loading app configs
  if (loadingApp) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', background: 'var(--bg-primary)', gap: '15px' }}>
        <Brain size={48} style={{ color: 'var(--primary)', animation: 'pulse-glow 1.5s infinite' }} />
        <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>Initialising Emotional AI Advisor...</span>
      </div>
    );
  }

  // 3. Connection Error
  if (errorMsg) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', background: 'var(--bg-primary)', padding: '24px', textAlign: 'center', gap: '20px' }}>
        <Brain size={48} style={{ color: 'var(--color-panic)' }} />
        <h2 style={{ fontFamily: 'var(--font-display)', color: 'var(--text-main)' }}>Connection Error</h2>
        <p style={{ color: 'var(--text-muted)', maxWidth: '450px', fontSize: '0.95rem', lineHeight: '1.5' }}>
          {errorMsg}
        </p>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn-primary" onClick={() => fetchInitialData(token)} style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
            <RefreshCw size={16} /> Retry Connection
          </button>
          <button className="btn-secondary" onClick={handleLogout} style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
            <LogOut size={16} /> Log Out
          </button>
        </div>
      </div>
    );
  }

  const renderView = () => {
    switch (view) {
      case 'dashboard':
        return <Dashboard profile={profile} goals={goals} activeChats={activeChats} setView={setView} />;
      case 'chat':
        return <ChatAdvisor activeChats={activeChats} onSendMessage={handleSendMessage} onClearHistory={handleClearHistory} isLoading={isLoadingChat} />;
      case 'goals':
        return <GoalsTracker goals={goals} onAddGoal={handleAddGoal} onDeleteGoal={handleDeleteGoal} />;
      case 'portfolio':
        return <PortfolioVisualizer portfolioData={portfolioData} profile={profile} onRefresh={handleRefreshPortfolio} />;
      case 'settings':
        return <Settings profile={profile} onSaveSettings={handleSaveSettings} />;
      default:
        return <Dashboard profile={profile} goals={goals} activeChats={activeChats} setView={setView} />;
    }
  };

  return (
    <div className="app-container">
      
      {/* Sidebar Navigation */}
      <nav className="sidebar">
        <div className="logo-container">
          <Brain size={24} style={{ color: 'var(--primary)' }} />
          <span className="logo-text">AURA ADVISOR</span>
        </div>
        
        <ul className="nav-links">
          <li>
            <div className={`nav-item ${view === 'dashboard' ? 'active' : ''}`} onClick={() => setView('dashboard')}>
              <LayoutDashboard size={18} /> Dashboard
            </div>
          </li>
          <li>
            <div className={`nav-item ${view === 'chat' ? 'active' : ''}`} onClick={() => setView('chat')}>
              <MessageSquare size={18} /> AI Coach Chat
            </div>
          </li>
          <li>
            <div className={`nav-item ${view === 'goals' ? 'active' : ''}`} onClick={() => setView('goals')}>
              <Target size={18} /> Goals Tracker
            </div>
          </li>
          <li>
            <div className={`nav-item ${view === 'portfolio' ? 'active' : ''}`} onClick={() => setView('portfolio')}>
              <PieChart size={18} /> Portfolio Recommendation
            </div>
          </li>
          <li>
            <div className={`nav-item ${view === 'settings' ? 'active' : ''}`} onClick={() => setView('settings')}>
              <SettingsIcon size={18} /> Settings
            </div>
          </li>
        </ul>

        <div className="sidebar-footer" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className="user-badge">
            <div className="user-avatar">
              {getInitials(profile.name)}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '0.9rem', fontWeight: 'bold', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '120px' }}>
                {profile.name}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {profile.risk_tolerance} Risk
              </div>
            </div>
          </div>
          
          <button 
            className="btn-secondary" 
            onClick={handleLogout} 
            style={{ width: '100%', padding: '8px 12px', justifyContent: 'center', fontSize: '0.82rem', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}
          >
            <LogOut size={14} /> Log Out
          </button>
        </div>
      </nav>

      {/* Main Panel Content */}
      <main className="main-content">
        {renderView()}
      </main>

    </div>
  );
}

export default App;
