"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import GlassPanel from "@/components/ui/GlassPanel";
import StarScene from "@/components/3d/StarScene";
import { 
  Factory, 
  Droplets, 
  Car, 
  Shirt, 
  Tractor, 
  Truck, 
  Zap, 
  ChefHat, 
  ArrowRight, 
  ArrowLeft, 
  Sparkles,
  Plane,
  Trash2
} from "lucide-react";

const INDUSTRIES = [
  { id: "manufacturing", label: "Manufacturing", icon: <Factory size={24} /> },
  { id: "dairy", label: "Dairy & Beverage", icon: <Droplets size={24} /> },
  { id: "automobile", label: "Automobile", icon: <Car size={24} /> },
  { id: "textile", label: "Textile", icon: <Shirt size={24} /> },
  { id: "agriculture", label: "Agriculture", icon: <Tractor size={24} /> },
  { id: "logistics", label: "Logistics", icon: <Truck size={24} /> },
  { id: "energy", label: "Energy & Utilities", icon: <Zap size={24} /> },
  { id: "food", label: "Food Processing", icon: <ChefHat size={24} /> },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [industry, setIndustry] = useState("");
  const [userId, setUserId] = useState("1");
  const [userName, setUserName] = useState("Facility");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  // Form State
  const [formData, setFormData] = useState({
    electricity: "",
    fuel: "",
    waste: "",
    flights: "",
    transportation: "",
    diet: "Omnivore",
  });

  useEffect(() => {
    const savedUid = localStorage.getItem("user_id") || "1";
    const savedName = localStorage.getItem("user_name") || "Facility";
    setUserId(savedUid);
    setUserName(savedName);
  }, []);

  const handleNext = async () => {
    if (step === 1 && industry) {
      setLoading(true);
      setError("");
      
      try {
        // Save selected industry in PostgreSQL
        const res = await fetch(`http://localhost:8000/api/v1/users/${userId}/industry`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            industry_type: industry,
          }),
        });

        if (res.ok) {
          localStorage.setItem("industry_type", industry);
          setStep(2);
        } else {
          setError("Failed to register industry. Continuing locally...");
          setTimeout(() => setStep(2), 1000);
        }
      } catch (err) {
        // Fallback for offline usage
        localStorage.setItem("industry_type", industry);
        setStep(2);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const payload = {
      user_id: parseInt(userId),
      industry_type: industry,
      electricity_kwh: parseFloat(formData.electricity) || 0.0,
      fuel_liters: parseFloat(formData.fuel) || 0.0,
      waste_generated_kg: parseFloat(formData.waste) || 0.0,
      transportation_km: parseFloat(formData.transportation) || 0.0,
      flights_taken: parseInt(formData.flights) || 0,
      diet_type: formData.diet,
      month: new Date().getMonth() + 1,
      year: new Date().getFullYear(),
    };
    
    try {
      const res = await fetch("http://localhost:8000/api/v1/emissions/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        console.log("Onboarding completed via 8-Agent pipeline:", data);
        router.push("/dashboard");
      } else {
        const errText = await res.text();
        setError("API pipeline failure: " + errText.slice(0, 100));
        setTimeout(() => router.push("/dashboard"), 1500);
      }
    } catch (err) {
      setError("Backend down, proceeding to demo offline mode...");
      setTimeout(() => {
        router.push("/dashboard");
      }, 1500);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative w-full h-screen overflow-hidden flex flex-col justify-center items-center">
      <StarScene nebulaColor="#0d9488" />
      
      <div className="absolute inset-0 z-10 flex flex-col items-center justify-center p-6 pointer-events-none">
        <div className="w-full max-w-3xl pointer-events-auto">
          <GlassPanel className="p-8 md:p-10 relative overflow-hidden">
            
            {/* Step Indicators */}
            <div className="flex gap-2 mb-8 justify-center">
              <div className={`h-1.5 w-16 rounded-full transition-colors ${step >= 1 ? "bg-emerald-500" : "bg-white/20"}`} />
              <div className={`h-1.5 w-16 rounded-full transition-colors ${step >= 2 ? "bg-emerald-500" : "bg-white/20"}`} />
            </div>

            {error && (
              <div className="w-full p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs text-center mb-4">
                {error}
              </div>
            )}

            <AnimatePresence mode="wait">
              {step === 1 && (
                <motion.div
                  key="step1"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.3 }}
                >
                  <h2 className="text-3xl font-bold text-white mb-2 text-center tracking-tight">Data Collection Agent</h2>
                  <p className="text-white/50 text-center mb-8 text-sm">
                    Welcome <span className="text-emerald-400 font-semibold">{userName}</span>. Select your primary industry sector.
                  </p>
                  
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
                    {INDUSTRIES.map((ind) => (
                      <button
                        key={ind.id}
                        onClick={() => setIndustry(ind.id)}
                        className={`p-5 rounded-xl flex flex-col items-center gap-3 transition-all cursor-pointer ${
                          industry === ind.id 
                            ? "bg-emerald-500/20 border-2 border-emerald-500 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.3)]" 
                            : "bg-white/5 border-2 border-transparent text-white/70 hover:bg-white/10 hover:text-white"
                        }`}
                      >
                        {ind.icon}
                        <span className="font-semibold text-xs tracking-wide">{ind.label}</span>
                      </button>
                    ))}
                  </div>

                  <div className="flex justify-end">
                    <button 
                      onClick={handleNext}
                      disabled={!industry || loading}
                      className="px-6 py-3 bg-emerald-500 disabled:bg-white/10 disabled:text-white/30 hover:bg-emerald-400 text-white rounded-xl font-semibold flex items-center gap-2 transition-all cursor-pointer text-sm shadow-[0_0_15px_rgba(16,185,129,0.3)]"
                    >
                      {loading ? "Registering..." : "Continue"} <ArrowRight size={18} />
                    </button>
                  </div>
                </motion.div>
              )}

              {step === 2 && (
                <motion.div
                  key="step2"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.3 }}
                >
                  <h2 className="text-3xl font-bold text-white mb-2 text-center tracking-tight">Facility Metrics</h2>
                  <p className="text-white/50 text-center mb-6 text-sm">
                    Enter monthly carbon telemetry for <span className="text-emerald-400 font-semibold">{INDUSTRIES.find(i => i.id === industry)?.label}</span>.
                  </p>
                  
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <div className="flex justify-between items-center mb-1">
                          <label className="block text-[10px] uppercase tracking-wider text-white/60">Electricity Usage</label>
                          <span className="text-[10px] text-emerald-400 lowercase">kWh</span>
                        </div>
                        <div className="relative">
                          <Zap size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40" />
                          <input 
                            type="number" required min="0" step="any"
                            value={formData.electricity} onChange={e => setFormData({...formData, electricity: e.target.value})}
                            className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white focus:outline-none focus:border-emerald-500/50 text-sm"
                            placeholder="e.g. 5000"
                          />
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between items-center mb-1">
                          <label className="block text-[10px] uppercase tracking-wider text-white/60">Fuel Consumption</label>
                          <span className="text-[10px] text-emerald-400 lowercase">litres</span>
                        </div>
                        <div className="relative">
                          <Droplets size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40" />
                          <input 
                            type="number" required min="0" step="any"
                            value={formData.fuel} onChange={e => setFormData({...formData, fuel: e.target.value})}
                            className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white focus:outline-none focus:border-emerald-500/50 text-sm"
                            placeholder="e.g. 1200"
                          />
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between items-center mb-1">
                          <label className="block text-[10px] uppercase tracking-wider text-white/60">Fleet Transportation</label>
                          <span className="text-[10px] text-emerald-400 lowercase">km</span>
                        </div>
                        <div className="relative">
                          <Truck size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40" />
                          <input 
                            type="number" required min="0" step="any"
                            value={formData.transportation} onChange={e => setFormData({...formData, transportation: e.target.value})}
                            className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white focus:outline-none focus:border-emerald-500/50 text-sm"
                            placeholder="e.g. 2400"
                          />
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between items-center mb-1">
                          <label className="block text-[10px] uppercase tracking-wider text-white/60">Flights Taken</label>
                          <span className="text-[10px] text-emerald-400 lowercase">trips</span>
                        </div>
                        <div className="relative">
                          <Plane size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40" />
                          <input 
                            type="number" required min="0"
                            value={formData.flights} onChange={e => setFormData({...formData, flights: e.target.value})}
                            className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white focus:outline-none focus:border-emerald-500/50 text-sm"
                            placeholder="e.g. 3"
                          />
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between items-center mb-1">
                          <label className="block text-[10px] uppercase tracking-wider text-white/60">Waste Generated</label>
                          <span className="text-[10px] text-emerald-400 lowercase">kg</span>
                        </div>
                        <div className="relative">
                          <Trash2 size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40" />
                          <input 
                            type="number" required min="0" step="any"
                            value={formData.waste} onChange={e => setFormData({...formData, waste: e.target.value})}
                            className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white focus:outline-none focus:border-emerald-500/50 text-sm"
                            placeholder="e.g. 450"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-[10px] uppercase tracking-wider text-white/60 mb-1">Diet / Dining Policy</label>
                        <select 
                          value={formData.diet} onChange={e => setFormData({...formData, diet: e.target.value})}
                          className="w-full bg-white/5 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-emerald-500/50 text-sm cursor-pointer"
                        >
                          <option value="Omnivore" className="bg-[#050510]">Omnivore / Standard Canteen</option>
                          <option value="Vegetarian" className="bg-[#050510]">Vegetarian Canteen Options</option>
                          <option value="Vegan" className="bg-[#050510]">Strict Eco-Vegan Dining</option>
                        </select>
                      </div>
                    </div>

                    <div className="flex justify-between items-center mt-8 pt-4">
                      <button 
                        type="button"
                        onClick={() => setStep(1)}
                        className="px-5 py-2.5 bg-white/5 hover:bg-white/10 text-white rounded-xl font-medium flex items-center gap-2 transition-all cursor-pointer text-xs"
                      >
                        <ArrowLeft size={16} /> Back
                      </button>
                      
                      <button 
                        type="submit"
                        disabled={loading}
                        className="px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-white rounded-xl font-semibold flex items-center gap-2 transition-all shadow-[0_0_15px_rgba(16,185,129,0.4)] cursor-pointer text-xs"
                      >
                        {loading ? "Orchestrating 8 Agents..." : "Analyze & Generate Twin"}
                        <Sparkles size={16} className="ml-1 animate-pulse" />
                      </button>
                    </div>
                  </form>
                </motion.div>
              )}
            </AnimatePresence>
          </GlassPanel>
        </div>
      </div>
    </main>
  );
}
