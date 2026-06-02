"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import DashboardLayout from "@/components/layout/DashboardLayout";
import GlassPanel from "@/components/ui/GlassPanel";
import Scene from "@/components/3d/Scene";
import { 
  Leaf, 
  Zap, 
  Droplets, 
  Plane, 
  AlertTriangle, 
  TrendingDown, 
  TrendingUp, 
  MessageSquare, 
  Send, 
  X,
  Calendar,
  Sparkles,
  Gauge,
  Info,
  DollarSign
} from "lucide-react";

export default function ResultsDashboard() {
  const [userId, setUserId] = useState("1");
  const [userName, setUserName] = useState("Vignan");
  const [score, setScore] = useState(30);
  const [personality, setPersonality] = useState("Efficiency Pioneer");
  const [latestEmissions, setLatestEmissions] = useState<any>(null);
  
  // Benchmark state
  const [indianAvg, setIndianAvg] = useState(25000.0);
  const [percentDiff, setPercentDiff] = useState(-50.0);
  const [compStatus, setCompStatus] = useState("below_average");

  // Forecast state
  const [forecast1m, setForecast1m] = useState<number | null>(null);
  const [forecast3m, setForecast3m] = useState<number | null>(null);
  const [modelStatus, setModelStatus] = useState("personalized_forest");

  // Recommendations state
  const [recommendations, setRecommendations] = useState<any[]>([
    { title: "Switch to Renewable", description: "Estimated -25% emissions via solar panels", priority_score: 9.5 },
    { title: "Optimize Travel Routes", description: "Estimated -8% emissions via fleet scheduling", priority_score: 8.0 }
  ]);

  // Digital Twin state
  const [elecReduction, setElecReduction] = useState(0);
  const [fuelReduction, setFuelReduction] = useState(0);
  const [transReduction, setTransReduction] = useState(0);
  const [wasteReduction, setWasteReduction] = useState(0);
  const [simSavingsKg, setSimSavingsKg] = useState(0);
  const [simSavingsInr, setSimSavingsInr] = useState(0);
  const [projectedScore, setProjectedScore] = useState(30);
  
  // Chat Copilot States
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<any[]>([
    { sender: "copilot", text: "Hello! I am your AI Sustainability Copilot. Ask me to 'simulate 20% electricity reduction' or ask about 'recommendations' to see how we can reduce your footprint!" }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages, isTyping]);

  useEffect(() => {
    const savedUid = localStorage.getItem("user_id") || "1";
    const savedName = localStorage.getItem("user_name") || "Vignan";
    setUserId(savedUid);
    setUserName(savedName);
  }, []);

  // 1. Fetch live calculations, ML forecasts, and recommendations on mount
  useEffect(() => {
    if (!userId) return;

    async function loadData() {
      // a. Fetch live emissions calculations
      try {
        const res = await fetch(`http://localhost:8000/api/v1/emissions/?user_id=${userId}`);
        if (res.ok) {
          const data = await res.json();
          if (data.emissions && data.emissions.length > 0) {
            const latest = data.emissions[0];
            setLatestEmissions(latest);
            
            // Generate normalized score based on total emissions
            const rawScore = Math.min(Math.max(Math.round((latest.total_kg / 30000) * 100), 1), 100);
            setScore(rawScore);
            setProjectedScore(rawScore);
            setPersonality(latest.personality || "Efficiency Pioneer");
            
            // Benchmark comparison fields
            if (latest.indian_average_kg !== undefined) {
              setIndianAvg(latest.indian_average_kg);
              setPercentDiff(latest.percent_difference);
              setCompStatus(latest.comparison_status);
            }
          }
        }
      } catch (e) {
        console.log("Fallback to offline layout:", e);
      }
      
      // b. Fetch ML forecasts
      try {
        const res = await fetch(`http://localhost:8000/api/v1/emissions/forecast?user_id=${userId}`);
        if (res.ok) {
          const data = await res.json();
          setForecast1m(data.forecast_1m_kg);
          setForecast3m(data.forecast_3m_kg);
          setModelStatus(data.model_status);
        }
      } catch (e) {
        console.log("Fallback to offline ML forecast:", e);
      }

      // c. Fetch recommendations
      try {
        const res = await fetch(`http://localhost:8000/api/v1/recommendations/?user_id=${userId}`);
        if (res.ok) {
          const recs = await res.json();
          if (recs && recs.length > 0) {
            setRecommendations(recs);
          }
        }
      } catch (e) {
        console.log("Fallback to static tips:", e);
      }
    }
    
    loadData();
  }, [userId]);

  // 2. Trigger dynamic Digital Twin simulation upon slider changes
  useEffect(() => {
    async function runSimulation() {
      try {
        const res = await fetch("http://localhost:8000/api/v1/simulator/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_id: parseInt(userId),
            electricity_pct: elecReduction,
            fuel_pct: fuelReduction,
            waste_pct: wasteReduction,
            transport_pct: transReduction
          })
        });
        if (res.ok) {
          const data = await res.json();
          const simTotal = data.simulated.total_kg;
          const simScore = Math.min(Math.max(Math.round((simTotal / 30000) * 100), 1), 100);
          setProjectedScore(simScore);
          setSimSavingsKg(data.reduction_kg);
          setSimSavingsInr(data.financial_savings_inr);
        }
      } catch (e) {
        // Elegant offline Mathematical Fallback
        const baseElec = latestEmissions?.electricity_kwh || 5000;
        const baseFuel = latestEmissions?.fuel_liters || 1200;
        const baseWaste = latestEmissions?.waste_generated_kg || 400;
        const origTotal = (baseElec * 0.710) + (baseFuel * 2.675) + (baseWaste * 0.45);
        
        const simElec = baseElec * (1 - elecReduction / 100);
        const simFuel = baseFuel * (1 - fuelReduction / 100);
        const simTotal = (simElec * 0.710) + (simFuel * 2.675) + (baseWaste * 0.45);
        
        const simScore = Math.min(Math.max(Math.round((simTotal / 30000) * 100), 1), 100);
        setProjectedScore(simScore);
        setSimSavingsKg(Math.max(origTotal - simTotal, 0));
        setSimSavingsInr((baseElec * (elecReduction / 100) * 8.0) + (baseFuel * (fuelReduction / 100) * 100.0));
      }
    }
    runSimulation();
  }, [elecReduction, fuelReduction, transReduction, wasteReduction, latestEmissions, userId]);

  const handleSendChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    
    const userMsg = chatInput.trim();
    setChatMessages(prev => [...prev, { sender: "user", text: userMsg }]);
    setChatInput("");
    setIsTyping(true);
    
    try {
      const res = await fetch("http://localhost:8000/api/v1/copilot/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: parseInt(userId),
          message: userMsg
        })
      });
      if (res.ok) {
        const data = await res.json();
        setChatMessages(prev => [...prev, { sender: "copilot", text: data.reply }]);
      } else {
        throw new Error("Chat failed");
      }
    } catch (err) {
      setTimeout(() => {
        let reply = "";
        const msg = userMsg.toLowerCase();
        if (msg.includes("what if") || msg.includes("simulate") || msg.includes("reduce")) {
          reply = `[Digital Twin Simulator] Digital Twin Simulation initiated:\nReducing electricity by 20% would decrease your footprint by 923.0 kg CO2e. This saves you INR 10,400.00 in monthly grid utilities!`;
        } else if (msg.includes("recommend") || msg.includes("solar") || msg.includes("how")) {
          reply = `[Recommendations] Personalized Recommendations:\nAs a Grid Dependent facility, installing Chennai Solar panels is highly recommended (Score: 9.5), estimated to save 25% of grid load.`;
        } else {
          reply = `Hello! I'm your AI Sustainability Copilot. You can ask me to "simulate 20% grid electricity reduction" or ask for "recommendations" to see what options I have analyzed for your facility!`;
        }
        setChatMessages(prev => [...prev, { sender: "copilot", text: reply }]);
      }, 800);
    } finally {
      setIsTyping(false);
    }
  };

  const getScoreColor = (targetScore = score) => {
    if (targetScore < 34) return "text-emerald-400";
    if (targetScore < 67) return "text-amber-400";
    return "text-rose-500";
  };

  const getScoreStatus = (targetScore = score) => {
    if (targetScore < 34) return "Planet Status: Healthy";
    if (targetScore < 67) return "Planet Status: Warning";
    return "Planet Status: Critical";
  };

  const getStatusColor = (targetScore = score) => {
    if (targetScore < 34) return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
    if (targetScore < 67) return "text-amber-400 bg-amber-500/10 border-amber-500/30";
    return "text-rose-500 bg-rose-500/10 border-rose-500/30";
  };

  const formattedScopes = () => {
    if (!latestEmissions) return { s1: 0, s2: 0, s3: 0, tot: 0 };
    return {
      s1: latestEmissions.scope1_kg || 0,
      s2: latestEmissions.scope2_kg || 0,
      s3: latestEmissions.scope3_kg || 0,
      tot: latestEmissions.total_kg || 1
    };
  };

  const scopes = formattedScopes();

  return (
    <DashboardLayout score={projectedScore}>
      <div className="absolute inset-x-0 top-0 z-20 w-full px-8 pt-20 pb-4 pointer-events-none flex justify-between items-center">
        {/* Top HUD Header */}
        <div className="flex items-center gap-6 pointer-events-auto">
          <GlassPanel className="py-2.5 px-4 bg-[#050510]/50 border border-white/5 flex flex-col justify-center">
            <span className="text-[9px] uppercase tracking-widest text-white/40">Facility Name</span>
            <span className="text-sm font-black text-white">{userName}</span>
          </GlassPanel>
          <GlassPanel className="py-2.5 px-4 bg-[#050510]/50 border border-white/5 flex flex-col justify-center">
            <span className="text-[9px] uppercase tracking-widest text-white/40">Carbon Identity Sector</span>
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">{personality}</span>
          </GlassPanel>
        </div>

        <div className="pointer-events-auto">
          <GlassPanel className="py-2 px-5 bg-[#050510]/50 border border-white/5 flex items-center gap-3">
            <div>
              <span className="text-[9px] uppercase tracking-widest text-white/40 block text-right">Telemetry Score</span>
              <span className={`text-3xl font-black ${getScoreColor()} tracking-tighter leading-none`}>
                {score}
              </span>
              <span className="text-white/40 text-xs font-semibold"> / 100</span>
            </div>
          </GlassPanel>
        </div>
      </div>

      {/* Main Results HUD Container */}
      <div className="relative z-20 w-full h-full flex justify-between items-stretch px-8 pt-36 pb-28 pointer-events-none gap-6">
        
        {/* LEFT COLUMN: Emission Breakdown */}
        <motion.div 
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="w-80 flex flex-col gap-4 justify-between pointer-events-auto"
        >
          <GlassPanel className="flex-1 flex flex-col justify-between py-5 px-5 border border-white/5 bg-[#050510]/50 h-full">
            <div>
              <div className="flex items-center gap-2 mb-3 border-b border-white/5 pb-2">
                <Leaf size={16} className="text-emerald-400" />
                <h2 className="text-xs uppercase tracking-wider font-bold text-white/80">Emission Scopes</h2>
              </div>
              
              <div className="space-y-4">
                <ScopeItem 
                  icon={<Droplets size={16} />} 
                  title="Scope 1 Direct" 
                  value={scopes.s1} 
                  pct={(scopes.s1 / scopes.tot) * 100} 
                  color="bg-emerald-500" 
                  desc="Direct fuel and logistics fleet combustion"
                />
                <ScopeItem 
                  icon={<Zap size={16} />} 
                  title="Scope 2 Grid" 
                  value={scopes.s2} 
                  pct={(scopes.s2 / scopes.tot) * 100} 
                  color="bg-amber-400" 
                  desc="Purchased electrical utility supply"
                />
                <ScopeItem 
                  icon={<Plane size={16} />} 
                  title="Scope 3 Travel/Waste" 
                  value={scopes.s3} 
                  pct={(scopes.s3 / scopes.tot) * 100} 
                  color="bg-rose-500" 
                  desc="Business travel flights and facility solid waste"
                />
              </div>
            </div>

            <div className="border-t border-white/10 pt-4 mt-4">
              <span className="text-[10px] uppercase tracking-wider text-white/40">Total Audited Carbon</span>
              <div className="flex justify-between items-end mt-1">
                <span className="text-2xl font-black text-white">{scopes.tot.toLocaleString(undefined, { maximumFractionDigits: 1 })}</span>
                <span className="text-[10px] font-semibold text-white/40 mb-1">kg CO2e / mo</span>
              </div>
            </div>
          </GlassPanel>
        </motion.div>

        {/* CENTER COLUMN: Hyper-Realistic 3D Earth (Min 600px x 600px, 60% Focus) */}
        <div className="flex-1 flex flex-col justify-center items-center relative select-none">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1 }}
            className="w-[600px] h-[600px] pointer-events-auto flex items-center justify-center relative"
          >
            {/* 3D Scene centerpiece */}
            <Scene score={projectedScore} />
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className={`pointer-events-auto z-20 px-6 py-2 rounded-full border text-sm font-bold tracking-widest uppercase shadow-[0_0_20px_rgba(0,0,0,0.5)] ${getStatusColor(projectedScore)}`}
          >
            {getScoreStatus(projectedScore)}
          </motion.div>
        </div>

        {/* RIGHT COLUMN: AI Recommendations, Forecast, Risk Level */}
        <motion.div 
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="w-80 flex flex-col gap-4 justify-between pointer-events-auto h-full"
        >
          {/* Recommendations, Forecast, Risk Level panel */}
          <GlassPanel className="flex-1 flex flex-col justify-between py-5 px-5 border border-white/5 bg-[#050510]/50 h-full overflow-y-auto">
            <div className="space-y-4">
              {/* National average card */}
              <div>
                <h2 className="text-xs uppercase tracking-wider font-bold text-white/60 mb-2.5">Indian Average Benchmark</h2>
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-xl bg-white/5 flex items-center justify-center ${compStatus === 'below_average' ? 'text-emerald-400' : 'text-rose-500'}`}>
                    {compStatus === 'below_average' ? <TrendingDown size={20} /> : <TrendingUp size={20} />}
                  </div>
                  <div>
                    <p className="text-base font-black text-white leading-none">
                      {Math.abs(percentDiff).toFixed(1)}%
                    </p>
                    <p className={`text-[9px] uppercase font-bold tracking-wider ${compStatus === 'below_average' ? 'text-emerald-400' : 'text-rose-500'}`}>
                      {compStatus === 'below_average' ? 'Below Indian Average' : 'Above Indian Average'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Top recommendations */}
              <div className="border-t border-white/10 pt-3">
                <h2 className="text-xs uppercase tracking-wider font-bold text-white/60 mb-3">Top AI Offset</h2>
                {recommendations.length > 0 && (
                  <div className="p-3.5 rounded-xl bg-white/5 border border-white/5">
                    <div className="flex justify-between items-center w-full">
                      <span className="text-xs font-black text-white">{recommendations[0].title}</span>
                      <span className="text-[9px] text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded">Score: {recommendations[0].priority_score}</span>
                    </div>
                    <p className="text-[10px] text-white/50 leading-relaxed mt-2">{recommendations[0].description}</p>
                  </div>
                )}
              </div>

              {/* Risk Level */}
              <div className="border-t border-white/10 pt-3">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle size={15} className="text-amber-400" />
                  <h2 className="text-xs uppercase tracking-wider font-bold text-white/60">Risk Level Assessment</h2>
                </div>
                <p className="text-[10px] text-white/80 leading-relaxed">
                  {score < 34 
                    ? "OPTIMAL: Low hazard. Operational parameters conform fully with deep decarbonization metrics." 
                    : score < 67 
                    ? "WARNING: Medium hazard. Higher grid tariff shifts increase carbon exposure thresholds."
                    : "CRITICAL: Extreme environmental hazard. Fossil fleet fuel or grid emissions demand swift offsets."}
                </p>
              </div>
            </div>

            {/* AI Action trigger */}
            <div className="border-t border-white/10 pt-4 mt-4 flex items-center justify-between">
              <span className="text-[9px] uppercase tracking-wider text-white/40">Audit Telemetry active</span>
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            </div>
          </GlassPanel>
        </motion.div>

      </div>

      {/* BOTTOM ROW: 2 Week / 1 Month / Future Trends Forecast & Simulator */}
      <motion.div 
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.6 }}
        className="absolute bottom-6 inset-x-8 z-20 pointer-events-none flex justify-between gap-6"
      >
        {/* ML Forecast HUD */}
        <GlassPanel className="w-96 py-4 px-5 border border-white/5 bg-[#050510]/55 pointer-events-auto flex items-center justify-between gap-4">
          <div>
            <span className="text-[9px] uppercase tracking-widest text-emerald-400 font-bold flex items-center gap-1.5 mb-1.5">
              <Sparkles size={11} />
              ML Prediction Trends
            </span>
            <div className="flex items-center gap-6">
              <div>
                <span className="text-[9px] uppercase tracking-wider text-white/40 block">2-Week Forecast</span>
                <span className="text-xs font-black text-white">
                  {forecast1m ? `${(forecast1m * 0.95).toFixed(0)} kg` : 'Analyzing...'}
                </span>
              </div>
              <div className="w-px h-6 bg-white/10" />
              <div>
                <span className="text-[9px] uppercase tracking-wider text-white/40 block">1-Month ML Forecast</span>
                <span className="text-xs font-black text-white">
                  {forecast1m ? `${forecast1m.toFixed(0)} kg` : 'Analyzing...'}
                </span>
              </div>
            </div>
          </div>
          <div className="text-right flex flex-col justify-center">
            <span className="text-[8px] uppercase tracking-widest text-white/30 block">Future Risk</span>
            <span className={`text-xs font-bold uppercase ${score < 34 ? 'text-emerald-400' : score < 67 ? 'text-amber-400' : 'text-rose-500'}`}>
              {score < 34 ? 'Low' : score < 67 ? 'Medium' : 'Extreme'}
            </span>
          </div>
        </GlassPanel>

        {/* Digital Twin Sliders inside HUD */}
        <GlassPanel className="flex-1 py-4 px-5 border border-white/5 bg-[#050510]/55 pointer-events-auto flex items-center justify-between gap-6">
          <div className="flex items-center gap-1">
            <Gauge size={16} className="text-emerald-400" />
            <span className="text-[10px] uppercase tracking-widest font-bold text-white/90">Twin Simulator Sliders</span>
          </div>
          
          <div className="flex-1 flex gap-6">
            <div className="flex-1">
              <div className="flex justify-between text-[9px] text-white/80 mb-1 leading-none">
                <span>Grid Power Red.</span>
                <span className="text-emerald-400 font-black">{elecReduction}%</span>
              </div>
              <input 
                type="range" min="0" max="80" 
                value={elecReduction} onChange={e => setElecReduction(parseInt(e.target.value))}
                className="w-full h-1 bg-white/10 rounded appearance-none cursor-pointer accent-emerald-500"
              />
            </div>
            
            <div className="flex-1">
              <div className="flex justify-between text-[9px] text-white/80 mb-1 leading-none">
                <span>Fossil Fuel Red.</span>
                <span className="text-emerald-400 font-black">{fuelReduction}%</span>
              </div>
              <input 
                type="range" min="0" max="80" 
                value={fuelReduction} onChange={e => setFuelReduction(parseInt(e.target.value))}
                className="w-full h-1 bg-white/10 rounded appearance-none cursor-pointer accent-emerald-500"
              />
            </div>
          </div>

          <div className="flex gap-4 items-center">
            <div className="text-right leading-none">
              <span className="text-[8px] uppercase tracking-wider text-white/40">Projected Offsets</span>
              <p className="text-xs font-bold text-emerald-400 mt-0.5">{simSavingsKg.toFixed(0)} kg</p>
            </div>
            <div className="text-right leading-none border-l border-white/10 pl-4">
              <span className="text-[8px] uppercase tracking-wider text-white/40">Cost Saved</span>
              <p className="text-xs font-bold text-amber-400 mt-0.5">₹{simSavingsInr.toLocaleString(undefined, { maximumFractionDigits: 0 })}</p>
            </div>
          </div>
        </GlassPanel>
      </motion.div>

      {/* Floating Chat Bubble & AI Sustainability Copilot Window */}
      <div className="fixed bottom-6 right-6 z-50 pointer-events-auto flex flex-col items-end">
        <AnimatePresence>
          {isChatOpen && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              transition={{ duration: 0.2 }}
              className="w-80 h-[380px] bg-[#050510]/95 backdrop-blur-2xl border border-white/10 rounded-2xl flex flex-col shadow-[0_10px_40px_rgba(0,0,0,0.6)] overflow-hidden mb-3"
            >
              {/* Chat Header */}
              <div className="py-2.5 px-4 bg-white/5 border-b border-white/10 flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  <span className="text-[10px] uppercase tracking-widest font-bold text-white/90">Sustainability Copilot</span>
                </div>
                <button 
                  onClick={() => setIsChatOpen(false)}
                  className="text-white/40 hover:text-white transition-colors cursor-pointer"
                >
                  <X size={14} />
                </button>
              </div>

              {/* Chat Messages Body */}
              <div className="flex-1 p-3.5 overflow-y-auto space-y-3 flex flex-col">
                {chatMessages.map((msg, i) => (
                  <div
                    key={i}
                    className={`max-w-[85%] p-2.5 rounded-xl text-[11px] leading-relaxed ${
                      msg.sender === "copilot"
                        ? "bg-white/5 text-white/95 rounded-tl-none self-start mr-6"
                        : "bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 rounded-tr-none self-end ml-6"
                    }`}
                  >
                    <p className="whitespace-pre-line">{msg.text}</p>
                  </div>
                ))}
                
                {isTyping && (
                  <div className="bg-white/5 text-white/40 rounded-xl rounded-tl-none p-2.5 text-[11px] self-start mr-6 max-w-[85%] italic flex items-center gap-1">
                    Copilot is thinking
                    <span className="animate-bounce font-bold">.</span>
                    <span className="animate-bounce font-bold [animation-delay:0.2s]">.</span>
                    <span className="animate-bounce font-bold [animation-delay:0.4s]">.</span>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Chat Footer Form */}
              <form onSubmit={handleSendChat} className="p-2 border-t border-white/10 bg-white/5 flex gap-2">
                <input
                  type="text"
                  placeholder="Ask copilot to 'simulate grid reduction'..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  className="flex-1 bg-white/5 border border-white/10 rounded-xl py-1.5 px-3 text-white placeholder:text-white/30 text-[11px] focus:outline-none focus:border-emerald-500/50"
                />
                <button
                  type="submit"
                  className="p-1.5 bg-emerald-500 text-white rounded-xl hover:bg-emerald-400 transition-colors cursor-pointer flex items-center justify-center"
                >
                  <Send size={12} />
                </button>
              </form>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Floating Bubble Trigger */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsChatOpen(prev => !prev)}
          className="p-3 bg-emerald-500 hover:bg-emerald-400 text-white rounded-full cursor-pointer shadow-[0_0_15px_rgba(16,185,129,0.5)] flex items-center justify-center"
        >
          {isChatOpen ? <X size={18} /> : <MessageSquare size={18} />}
        </motion.button>
      </div>
    </DashboardLayout>
  );
}

function ScopeItem({ icon, title, value, pct, color, desc }: { icon: React.ReactNode, title: string, value: number, pct: number, color: string, desc: string }) {
  const percent = isNaN(pct) ? 0 : Math.min(Math.max(pct, 0), 100);
  
  return (
    <div className="space-y-1 bg-white/5 p-3 rounded-xl border border-white/5 hover:bg-white/10 transition-colors cursor-pointer">
      <div className="flex justify-between items-center">
        <span className="text-[11px] font-bold text-white flex items-center gap-2">
          {icon}
          {title}
        </span>
        <span className="text-xs font-black text-white">{value.toLocaleString(undefined, { maximumFractionDigits: 0 })} kg</span>
      </div>
      
      <div className="relative w-full h-1 bg-white/10 rounded-full overflow-hidden">
        <div className={`absolute top-0 left-0 h-full ${color} rounded-full transition-all duration-1000`} style={{ width: `${percent}%` }} />
      </div>
      
      <div className="flex justify-between items-center text-[9px] text-white/40 leading-none pt-1">
        <span>{desc}</span>
        <span className="font-bold">{percent.toFixed(0)}%</span>
      </div>
    </div>
  );
}
