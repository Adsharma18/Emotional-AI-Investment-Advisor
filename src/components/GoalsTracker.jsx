import React, { useState } from 'react';
import { 
  PiggyBank, 
  Plus, 
  Trash2, 
  Calendar, 
  TrendingUp, 
  Info,
  ChevronRight,
  AlertCircle
} from 'lucide-react';

export default function GoalsTracker({ goals, onAddGoal, onDeleteGoal }) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [name, setName] = useState('');
  const [targetAmount, setTargetAmount] = useState('');
  const [currentAmount, setCurrentAmount] = useState('');
  const [targetDate, setTargetDate] = useState('');
  const [priority, setPriority] = useState('Medium');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name || !targetAmount || !targetDate) return;

    onAddGoal({
      name,
      target_amount: parseFloat(targetAmount),
      current_amount: parseFloat(currentAmount || 0),
      target_date: targetDate,
      priority
    });

    // Reset fields
    setName('');
    setTargetAmount('');
    setCurrentAmount('');
    setTargetDate('');
    setPriority('Medium');
    setShowAddForm(false);
  };

  // Helper to calculate monthly savings required
  const calculateMonthlySavings = (target, current, dateStr) => {
    const remaining = target - current;
    if (remaining <= 0) return 0;

    const targetDateObj = new Date(dateStr);
    const today = new Date();
    
    // Calculate difference in months
    let months = (targetDateObj.getFullYear() - today.getFullYear()) * 12;
    months -= today.getMonth();
    months += targetDateObj.getMonth();

    if (months <= 0) return remaining; // Due immediately
    return remaining / months;
  };

  return (
    <div className="goals-tracker-view animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '2.2rem', marginBottom: '8px' }}>
            Goal-Based Planning
          </h1>
          <p style={{ color: 'var(--text-muted)' }}>
            Break down your financial aspirations into trackable milestones. Your advisor will recommend asset allocations supporting these specific dates.
          </p>
        </div>
        <button className="btn-primary" onClick={() => setShowAddForm(!showAddForm)}>
          {showAddForm ? 'Cancel' : 'Add Financial Goal'} <Plus size={16} />
        </button>
      </div>

      {/* Add Goal Form Panel */}
      {showAddForm && (
        <div className="glass-card animate-fade-in" style={{ borderColor: 'var(--primary-glow)' }}>
          <h3 style={{ marginBottom: '16px', fontFamily: 'var(--font-display)' }}>Create New Investment Goal</h3>
          <form onSubmit={handleSubmit} className="grid-3" style={{ gap: '16px', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
            <div>
              <label>Goal Name</label>
              <input 
                type="text" 
                placeholder="e.g. Retirement Fund, Home Downpayment" 
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                style={{ width: '100%' }}
              />
            </div>
            <div>
              <label>Target Amount ($)</label>
              <input 
                type="number" 
                placeholder="e.g. 50000" 
                value={targetAmount}
                onChange={(e) => setTargetAmount(e.target.value)}
                required
                min="1"
                style={{ width: '100%' }}
              />
            </div>
            <div>
              <label>Initial Saved Amount ($)</label>
              <input 
                type="number" 
                placeholder="e.g. 5000 (optional)" 
                value={currentAmount}
                onChange={(e) => setCurrentAmount(e.target.value)}
                min="0"
                style={{ width: '100%' }}
              />
            </div>
            <div>
              <label>Target Date</label>
              <input 
                type="date" 
                value={targetDate}
                onChange={(e) => setTargetDate(e.target.value)}
                required
                style={{ width: '100%' }}
              />
            </div>
            <div>
              <label>Goal Priority</label>
              <select value={priority} onChange={(e) => setPriority(e.target.value)} style={{ width: '100%' }}>
                <option value="Low">Low Priority</option>
                <option value="Medium">Medium Priority</option>
                <option value="High">High Priority</option>
              </select>
            </div>
            <div style={{ display: 'flex', alignItems: 'flex-end' }}>
              <button type="submit" className="btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
                Save Goal
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Goals List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {goals.length === 0 ? (
          <div className="glass-card" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            <PiggyBank size={48} style={{ opacity: 0.3, marginBottom: '16px', display: 'inline-block' }} />
            <h3>No Active Financial Goals</h3>
            <p style={{ fontSize: '0.9rem', maxWidth: '400px', margin: '8px auto 20px' }}>
              Define what you are saving for, and the advisor will formulate custom monthly budgets and investment portfolios to help you achieve them.
            </p>
            <button className="btn-primary" onClick={() => setShowAddForm(true)}>
              Define A Goal Now
            </button>
          </div>
        ) : (
          goals.map((goal) => {
            const progress = Math.min(100, (goal.current_amount / goal.target_amount) * 100);
            const remaining = Math.max(0, goal.target_amount - goal.current_amount);
            const monthlySaving = calculateMonthlySavings(goal.target_amount, goal.current_amount, goal.target_date);
            const priorityColors = {
              High: 'var(--color-panic)',
              Medium: 'var(--color-anxious)',
              Low: 'var(--color-neutral)'
            };

            return (
              <div key={goal.id} className="glass-card" style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', alignItems: 'center' }}>
                
                {/* Info block */}
                <div style={{ flex: 2, minWidth: '250px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                    <h3 style={{ fontSize: '1.25rem', fontFamily: 'var(--font-display)' }}>{goal.name}</h3>
                    <span style={{ 
                      fontSize: '0.65rem', 
                      padding: '2px 8px', 
                      borderRadius: '10px', 
                      background: 'rgba(255,255,255,0.04)', 
                      border: `1px solid ${priorityColors[goal.priority] || 'var(--border-glass)'}`,
                      color: priorityColors[goal.priority],
                      fontWeight: 'bold',
                      textTransform: 'uppercase'
                    }}>
                      {goal.priority}
                    </span>
                  </div>
                  
                  {/* Progress bar */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    <span>Progress: {progress.toFixed(0)}%</span>
                    <span>${goal.current_amount.toLocaleString()} of ${goal.target_amount.toLocaleString()}</span>
                  </div>
                  <div className="progress-container" style={{ height: '10px' }}>
                    <div className="progress-bar" style={{ width: `${progress}%` }}></div>
                  </div>
                </div>

                {/* Monthly estimate calculator block */}
                <div style={{ flex: 1.5, minWidth: '220px', background: 'rgba(255,255,255,0.02)', padding: '12px 18px', borderRadius: '12px', border: '1px solid var(--border-glass)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    <Calendar size={14} />
                    Target Date: {new Date(goal.target_date).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
                  </div>
                  {remaining > 0 ? (
                    <>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        Monthly Savings Required:
                      </div>
                      <div style={{ fontSize: '1.4rem', fontWeight: 'bold', color: 'var(--primary)', fontFamily: 'var(--font-display)' }}>
                        ${monthlySaving.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </div>
                    </>
                  ) : (
                    <div style={{ fontSize: '0.9rem', fontWeight: 'bold', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <TrendingUp size={16} /> Goal Completed!
                    </div>
                  )}
                </div>

                {/* Operations column */}
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <button className="btn-secondary" style={{ padding: '10px', color: 'var(--color-panic)', borderColor: 'rgba(239, 68, 68, 0.2)' }} onClick={() => onDeleteGoal(goal.id)} title="Delete Goal">
                    <Trash2 size={16} />
                  </button>
                </div>

              </div>
            );
          })
        )}
      </div>

      {/* Goal advice box */}
      <div className="glass-card" style={{ display: 'flex', gap: '16px', alignItems: 'flex-start', background: 'rgba(59, 130, 246, 0.03)', borderColor: 'rgba(59, 130, 246, 0.15)' }}>
        <Info size={24} style={{ color: 'var(--color-neutral)', flexShrink: 0, marginTop: '2px' }} />
        <div>
          <h4 style={{ fontSize: '0.95rem', marginBottom: '4px', color: 'var(--text-main)' }}>Understanding Goal Horizons</h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
            Short-term goals (under 2 years) should be held in highly secure assets like Cash or Bonds. Long-term goals (over 7 years) can comfortably accommodate a higher proportion of Equities, allowing compounding interest to counter inflation, even during intermediate market drops.
          </p>
        </div>
      </div>

    </div>
  );
}
