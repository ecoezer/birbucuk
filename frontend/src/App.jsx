import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, Cell
} from 'recharts';
import { LayoutDashboard, History, Zap, Trophy, TrendingUp, Info } from 'lucide-react';

const API_BASE = "http://localhost:8000/api";

const App = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [matches, setMatches] = useState([]);
  const [correlations, setCorrelations] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [matchesRes, corrRes] = await Promise.all([
        axios.get(`${API_BASE}/matches?limit=50`),
        axios.get(`${API_BASE}/stats/correlations`)
      ]);
      setMatches(matchesRes.data);
      setCorrelations(corrRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
    setLoading(false);
  };

  const CorrelationCard = ({ title, data }) => (
    <div className="glass p-6 rounded-2xl flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-200">{title}</h3>
        <Zap className="text-sky-400 w-5 h-5" />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col">
          <span className="text-slate-400 text-sm">Win Count</span>
          <span className="text-2xl font-bold text-white">{data.count}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-slate-400 text-sm">Avg Odd</span>
          <span className="text-2xl font-bold text-sky-400">{data.avg_winning_odd.toFixed(2)}</span>
        </div>
      </div>
      <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2">
        <div
          className="bg-sky-500 h-full rounded-full"
          style={{ width: `${Math.min((data.count / 100) * 100, 100)}%` }}
        ></div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen flex bg-slate-950 text-slate-50">
      {/* Sidebar */}
      <nav className="w-64 border-r border-slate-800 flex flex-col p-6 gap-8 bg-slate-900/50">
        <div className="flex items-center gap-3 px-2">
          <div className="w-10 h-10 bg-sky-500 rounded-xl flex items-center justify-center glow-shadow">
            <Zap className="text-white fill-white" />
          </div>
          <span className="text-xl font-bold bg-gradient-to-r from-white to-sky-400 bg-clip-text text-transparent">
            Birbucuk
          </span>
        </div>

        <div className="flex flex-col gap-2">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeTab === 'dashboard' ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
          >
            <LayoutDashboard size={20} />
            <span className="font-medium">Dashboard</span>
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeTab === 'history' ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
          >
            <History size={20} />
            <span className="font-medium">Match History</span>
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-y-auto">
        <header className="flex justify-between items-center mb-10">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              {activeTab === 'dashboard' ? 'Insight Dashboard' : 'Historical Analysis'}
            </h1>
            <p className="text-slate-400">Real-time betting correlations and historical data archive.</p>
          </div>
          <button
            onClick={fetchData}
            className="px-5 py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-xl font-medium transition-all flex items-center gap-2"
          >
            <TrendingUp size={18} />
            Refresh Data
          </button>
        </header>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-500"></div>
          </div>
        ) : (
          <>
            {activeTab === 'dashboard' && correlations && (
              <div className="flex flex-col gap-10">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <CorrelationCard title="MS - 1 (Home Win)" data={correlations['MS - 1']} />
                  <CorrelationCard title="MS - X (Draw)" data={correlations['MS - X']} />
                  <CorrelationCard title="KG - Var (Both Score)" data={correlations['KG - Var']} />
                  <CorrelationCard title="AÜ 2.5 - Üst (Over)" data={correlations['AÜ 2.5 - Üst']} />
                </div>

                {/* Charts Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <div className="glass p-8 rounded-3xl">
                    <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                      <Trophy className="text-yellow-400" />
                      Winning Counts by Type
                    </h3>
                    <div className="h-80 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={Object.entries(correlations).map(([k, v]) => ({ name: k, count: v.count }))}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                          <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                          <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                          <Tooltip
                            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px' }}
                            itemStyle={{ color: '#38bdf8' }}
                          />
                          <Bar dataKey="count" fill="#38bdf8" radius={[6, 6, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  <div className="glass p-8 rounded-3xl">
                    <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                      <TrendingUp className="text-green-400" />
                      Average Winning Odds
                    </h3>
                    <div className="h-80 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={Object.entries(correlations).map(([k, v]) => ({ name: k, odd: v.avg_winning_odd }))}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                          <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                          <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                          <Tooltip
                            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px' }}
                          />
                          <Line type="monotone" dataKey="odd" stroke="#818cf8" strokeWidth={3} dot={{ fill: '#818cf8', r: 4 }} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'history' && (
              <div className="glass rounded-3xl overflow-hidden">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-800/50">
                      <th className="p-4 text-slate-400 font-medium text-sm border-b border-slate-700">Date</th>
                      <th className="p-4 text-slate-400 font-medium text-sm border-b border-slate-700">Match</th>
                      <th className="p-4 text-slate-400 font-medium text-sm border-b border-slate-700">League</th>
                      <th className="p-4 text-slate-400 font-medium text-sm border-b border-slate-700">HT Score</th>
                      <th className="p-4 text-slate-400 font-medium text-sm border-b border-slate-700">FT Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {matches.map((m) => (
                      <tr key={m.id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="p-4 text-slate-300 text-sm border-b border-slate-800">
                          {new Date(m.date).toLocaleDateString()}
                        </td>
                        <td className="p-4 border-b border-slate-800">
                          <div className="flex flex-col">
                            <span className="font-semibold text-white">{m.home_team}</span>
                            <span className="text-slate-500 text-xs">vs</span>
                            <span className="font-semibold text-white">{m.away_team}</span>
                          </div>
                        </td>
                        <td className="p-4 text-slate-400 text-sm border-b border-slate-800">{m.league}</td>
                        <td className="p-4 text-sky-400 font-bold border-b border-slate-800">
                          {m.score_home_iy}-{m.score_away_iy}
                        </td>
                        <td className="p-4 text-green-400 font-bold border-b border-slate-800">
                          {m.score_home}-{m.score_away}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
};

export default App;
