import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import axios from "axios";
import { Activity, Bell, Bluetooth, HeartPulse, Home, RefreshCw, ShieldCheck, Thermometer, Wifi } from "lucide-react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import "./styles.css";

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api" });
type Measurement = { id: number; heart_rate: number; spo2: number; temperature: number; risk: string; source: string; recorded_at: string };
type Dashboard = { latest: Measurement | null; baseline: { heart_rate: number; spo2: number; temperature: number } | null; alerts: { id: number; severity: string; message: string; created_at: string }[]; device: { connected: boolean; simulation: boolean } };

function App() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [history, setHistory] = useState<Measurement[]>([]);
  const [error, setError] = useState("");
  const load = async () => {
    try { const [dashboard, measurements] = await Promise.all([api.get<Dashboard>("/dashboard"), api.get<Measurement[]>("/measurements")]); setData(dashboard.data); setHistory(measurements.data); setError(""); }
    catch { setError("Backend unavailable. Start the FastAPI server to view live data."); }
  };
  useEffect(() => { void load(); const timer = window.setInterval(() => void load(), 10000); return () => window.clearInterval(timer); }, []);
  const simulate = async () => { await api.post("/measurements/simulate"); await load(); };
  const latest = data?.latest;
  return <div className="shell">
    <aside><div className="brand"><HeartPulse size={28}/><span>Predi<span>Care</span></span></div><nav><a className="active"><Home size={18}/>Dashboard</a><a><Activity size={18}/>Live Monitoring</a><a><ShieldCheck size={18}/>Personal Baseline</a><a><Bell size={18}/>Alert History</a></nav><div className="side-note">Supporting insight, not a diagnosis.</div></aside>
    <main><header><div><p className="eyebrow">OVERVIEW</p><h1>Health dashboard</h1><p className="muted">Adaptive edge monitoring for your daily wellbeing.</p></div><button className="secondary" onClick={() => void load()}><RefreshCw size={16}/>Refresh</button><button onClick={() => void simulate()}><Wifi size={16}/>Generate reading</button></header>
      {error && <div className="error">{error}</div>}
      <section className="status-row"><div className="status"><span className="dot green"/><strong>{data?.device.connected ? "Device connected" : "Simulation mode"}</strong><small>{latest ? `Last update ${new Date(latest.recorded_at).toLocaleTimeString()}` : "No readings yet"}</small></div><div className={`risk ${latest?.risk?.toLowerCase() || "normal"}`}><ShieldCheck size={20}/><div><small>CURRENT RISK</small><strong>{latest?.risk || "NORMAL"}</strong></div></div></section>
      <section className="cards"><Vital icon={<HeartPulse/>} label="Heart rate" value={latest?.heart_rate} unit="BPM" accent="coral"/><Vital icon={<Activity/>} label="Blood oxygen" value={latest?.spo2} unit="%" accent="blue"/><Vital icon={<Thermometer/>} label="Temperature" value={latest?.temperature} unit="°C" accent="orange"/><div className="card device-card"><Bluetooth/><p>Sensor status</p><strong>MAX30102 <em>Ready</em></strong><strong>MLX90614 <em>Ready</em></strong></div></section>
      <section className="content-grid"><div className="panel chart-panel"><div className="panel-title"><div><h2>Recent measurements</h2><p className="muted">Live vital trends</p></div><span className="legend"><i/>Heart rate</span></div><ResponsiveContainer width="100%" height={260}><LineChart data={history}><XAxis dataKey="recorded_at" tickFormatter={(v) => new Date(v).toLocaleTimeString([], {hour:"2-digit", minute:"2-digit"})}/><YAxis domain={["auto","auto"]}/><Tooltip/><Line type="monotone" dataKey="heart_rate" stroke="#ef7666" strokeWidth={3} dot={false}/><Line type="monotone" dataKey="spo2" stroke="#3689d8" strokeWidth={2} dot={false}/></LineChart></ResponsiveContainer></div><div className="panel"><div className="panel-title"><div><h2>Latest alerts</h2><p className="muted">Review changes that need attention</p></div><Bell size={19}/></div>{data?.alerts.length ? data.alerts.map(a => <div className="alert" key={a.id}><span className={`alert-icon ${a.severity.toLowerCase()}`}><Bell size={15}/></span><div><strong>{a.severity.replace("_"," ")}</strong><p>{a.message}</p></div></div>) : <div className="empty">No alerts. Your recent readings look stable.</div>}</div></section>
      <section className="panel baseline"><div><p className="eyebrow">PERSONAL BASELINE</p><h2>Your reference profile</h2><p className="muted">Baseline makes changes meaningful to you.</p></div>{data?.baseline ? <div className="baseline-values"><b>{data.baseline.heart_rate.toFixed(0)} <small>BPM</small></b><b>{data.baseline.spo2.toFixed(1)} <small>SpO2</small></b><b>{data.baseline.temperature.toFixed(1)} <small>°C</small></b></div> : <button onClick={() => api.post("/baseline").then(load)}>Create from readings</button>}</section>
    </main>
  </div>;
}
function Vital({ icon, label, value, unit, accent }: { icon: React.ReactNode; label: string; value?: number; unit: string; accent: string }) { return <div className="card vital"><div className={`icon ${accent}`}>{icon}</div><p>{label}</p><strong>{value === undefined ? "--" : value.toFixed(1)} <small>{unit}</small></strong><span className="muted">Latest reading</span></div>; }
createRoot(document.getElementById("root")!).render(<StrictMode><App/></StrictMode>);
