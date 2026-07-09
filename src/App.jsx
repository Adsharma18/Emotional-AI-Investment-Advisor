import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, 
  MessageSquare, 
  Target, 
  PieChart, 
  Settings as SettingsIcon,
  Brain,
  RefreshCw
} from 'lucide-react';

import Dashboard from './components/Dashboard';
import ChatAdvisor from './components/ChatAdvisor';
import GoalsTracker from './components/GoalsTracker';
import PortfolioVisualizer from './components/PortfolioVisualizer';
import Settings from './components/Settings';

const BACKEND_URL = 'http://localhost:8000';

function App() {
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
  const [loadingApp, setLoadingApp] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  // Initialize data
  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      setLoadingApp(true);
      setErrorMsg(null);

      // Fetch user profile
      const profileRes = await fetch(`${BACKEND_URL}/api/profile`);
      if (!profileRes.ok) throw new Error("Could not load profile from backend.");
      const profileData = await profileRes.json();
      setProfile(profileData);

      // Fetch goals
      const goalsRes = await fetch(`${BACKEND_URL}/api/goals`);
      const goalsData = await goalsRes.json();
      setGoals(goalsData);

      // Fetch chats
      const chatsRes = await fetch(`${BACKEND_URL}/api/chat`);
      const chatsData = await chatsRes.json();
      setActiveChats(chatsData);

      // Fetch portfolio recommendation
      const portRes = await fetch(`${BACKEND_URL}/api/portfolio`);
      const portData = await portRes.json();
      setPortfolioData(portData);

      setLoadingApp(false);
    } catch (err) {
      console.error(err);
      setErrorMsg("Failed to connect to the backend API. Please make sure the FastAPI server is running on port 8000.");
      setLoadingApp(false);
    }
  };

  // Chat logic
  const handleSendMessage = async (text) => {
    setIsLoadingChat(true);
    try {
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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      const data = await res.json();
      
      // Update with database messages (contains analysis details)
      // Re-fetch chat list to align IDs and timestamps
      const chatsRes = await fetch(`${BACKEND_URL}/api/chat`);
      const chatsData = await chatsRes.json();
      setActiveChats(chatsData);

      // Re-fetch portfolio to apply any new emotional modifiers
      const portRes = await fetch(`${BACKEND_URL}/api/portfolio`);
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
      await fetch(`${BACKEND_URL}/api/chat`, { method: 'DELETE' });
      setActiveChats([]);
      
      // Reset portfolio
      const portRes = await fetch(`${BACKEND_URL}/api/portfolio`);
      const portData = await portRes.json();
      setPortfolioData(portData);
    } catch (err) {
      console.error("Error clearing chat:", err);
    }
  };

  // Goals logic
  const handleAddGoal = async (newGoal) => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/goals`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newGoal)
      });
      if (res.ok) {
        const goalsRes = await fetch(`${BACKEND_URL}/api/goals`);
        const goalsData = await goalsRes.json();
        setGoals(goalsData);
      }
    } catch (err) {
      console.error("Error adding goal:", err);
    }
  };

  const handleDeleteGoal = async (goalId) => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/goals/${goalId}`, {
        method: 'DELETE'
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
      const res = await fetch(`${BACKEND_URL}/api/profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedSettings)
      });
      if (res.ok) {
        const data = await res.json();
        setProfile(data);

        // Recalculate portfolio under new settings
        const portRes = await fetch(`${BACKEND_URL}/api/portfolio`);
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
      const portRes = await fetch(`${BACKEND_URL}/api/portfolio`);
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

  if (loadingApp) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', background: 'var(--bg-primary)', gap: '15px' }}>
        <Brain size={48} style={{ color: 'var(--primary)', animation: 'pulse-glow 1.5s infinite' }} />
        <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>Initialising Emotional AI Advisor...</span>
      </div>
    );
  }

  if (errorMsg) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', background: 'var(--bg-primary)', padding: '24px', textAlign: 'center', gap: '20px' }}>
        <Brain size={48} style={{ color: 'var(--color-panic)' }} />
        <h2 style={{ fontFamily: 'var(--font-display)', color: 'var(--text-main)' }}>Connection Error</h2>
        <p style={{ color: 'var(--text-muted)', maxWidth: '450px', fontSize: '0.95rem', lineHeight: '1.5' }}>
          {errorMsg}
        </p>
        <button className="btn-primary" onClick={fetchInitialData} style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
          <RefreshCw size={16} /> Retry Connection
        </button>
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

        <div className="sidebar-footer">
          <div className="user-badge">
            <div className="user-avatar">
              {getInitials(profile.name)}
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>{profile.name}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{profile.risk_tolerance} Risk</div>
            </div>
          </div>
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
