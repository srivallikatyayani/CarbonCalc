"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { 
  ArrowRight, 
  Globe, 
  Zap, 
  BarChart3, 
  TrendingUp, 
  ShieldCheck, 
  SlidersHorizontal,
  FileCheck2,
  Sparkles
} from "lucide-react";
import StarScene from "@/components/3d/StarScene";
import GlassPanel from "@/components/ui/GlassPanel";

const FEATURES = [
  {
    icon: <BarChart3 className="text-emerald-400" size={24} />,
    title: "Carbon Accounting",
    desc: "Calculate Scope 1, 2, and 3 footprint dynamically using exact regional emission benchmarks."
  },
  {
    icon: <Sparkles className="text-amber-400" size={24} />,
    title: "AI Recommendations",
    desc: "Deploy Agentic intelligence to generate prioritized sustainability recommendations optimized for score impacts."
  },
  {
    icon: <SlidersHorizontal className="text-teal-400" size={24} />,
    title: "Digital Twin Simulator",
    desc: "Adjust grid load and fossil fuel consumption sliders to instantly model projected carbon and cost savings."
  },
  {
    icon: <TrendingUp className="text-blue-400" size={24} />,
    title: "ML Trend Forecasting",
    desc: "Train personalized Random Forest Regressors to predict future emission limits and identify environmental risks."
  },
  {
    icon: <FileCheck2 className="text-purple-400" size={24} />,
    title: "Sustainability Reports",
    desc: "Generate complete, audited PDF sustainability summaries illustrating scopes, comparisons, and AI guidelines."
  }
];

const STEPS = [
  { step: "01", title: "Select Sector", desc: "Choose your primary operational field." },
  { step: "02", title: "Activity Telemetry", desc: "Log monthly utility and transit metrics." },
  { step: "03", title: "Agentic Audit", desc: "Verify ranges via 8 distinct AI agents." },
  { step: "04", title: "Identify Personality", desc: "Dynamically classify Carbon Identity tags." },
  { step: "05", title: "Simulate savings", desc: "Test reductions inside your Digital Twin." },
  { step: "06", title: "Predict Trends", desc: "Forecast futures using custom-fit ML models." }
];

export default function IntroPage() {
  return (
    <main className="relative w-full min-h-screen overflow-y-auto overflow-x-hidden flex flex-col bg-[#050510]">
      {/* 3D Background Scene (Clean Emerald Glow) */}
      <StarScene nebulaColor="#10B981" />
      
      {/* Scrollable Container Content */}
      <div className="relative z-10 w-full flex flex-col items-center">
        
        {/* Header Navbar */}
        <header className="w-full max-w-6xl px-6 py-6 flex justify-between items-center border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-emerald-500 flex items-center justify-center font-bold text-base shadow-[0_0_15px_rgba(16,185,129,0.5)]">
              C
            </div>
            <h1 className="text-lg font-bold tracking-widest text-white/90">CARBON<span className="text-emerald-400">CALC</span></h1>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-sm font-medium text-white/60 hover:text-white transition-colors">
              Sign In
            </Link>
            <Link href="/signup">
              <button className="px-5 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-white rounded-full font-semibold text-xs tracking-wider transition-all shadow-[0_0_10px_rgba(16,185,129,0.4)] cursor-pointer">
                LAUNCH PLATFORM
              </button>
            </Link>
          </div>
        </header>

        {/* Hero Section */}
        <section className="w-full max-w-5xl px-6 pt-20 pb-16 flex flex-col items-center text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1 }}
            className="flex flex-col items-center"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-6">
              <Globe size={12} className="animate-spin" />
              NASA-Level Digital Twin Telemetry
            </div>

            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white mb-6 leading-tight max-w-4xl">
              AI-Powered Carbon <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-300 to-emerald-500">Intelligence Platform</span>
            </h1>

            <p className="text-lg md:text-xl text-white/70 mb-10 font-light leading-relaxed max-w-3xl">
              Measure, Predict, Simulate, and Reduce your Industrial Emissions. Harness an advanced multi-agent pipeline to audit scopes and forecast sustainability limits in real-time.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 mb-24">
              <Link href="/signup">
                <button className="px-8 py-4 bg-emerald-500 hover:bg-emerald-400 text-white rounded-xl font-bold tracking-wide flex items-center gap-3 transition-all shadow-[0_0_25px_rgba(16,185,129,0.5)] cursor-pointer text-sm">
                  Get Started
                  <ArrowRight size={18} />
                </button>
              </Link>
              <Link href="/login">
                <button className="px-8 py-4 bg-white/5 hover:bg-white/10 text-white border border-white/10 rounded-xl font-semibold tracking-wide flex items-center gap-2 transition-colors cursor-pointer text-sm">
                  Access Portal
                </button>
              </Link>
            </div>
          </motion.div>
        </section>

        {/* Features Grid Section */}
        <section className="w-full max-w-6xl px-6 py-20 border-t border-white/5 bg-[#050510]/60 backdrop-blur-md rounded-t-[40px]">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4 tracking-tight">Futuristic Platform Capabilities</h2>
            <p className="text-white/50 text-sm max-w-2xl mx-auto">
              Our 8-Agent architecture automates standard validation and feeds custom predictive algorithms.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {FEATURES.map((feat, i) => (
              <GlassPanel 
                key={i} 
                hoverEffect 
                className="p-8 flex flex-col gap-4 text-left border border-white/5 rounded-3xl"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <div className="p-3.5 w-fit rounded-xl bg-white/5">
                  {feat.icon}
                </div>
                <h3 className="text-lg font-bold text-white tracking-wide">{feat.title}</h3>
                <p className="text-white/50 text-xs leading-relaxed font-light">{feat.desc}</p>
              </GlassPanel>
            ))}
          </div>
        </section>

        {/* How It Works Section */}
        <section className="w-full max-w-6xl px-6 py-20 border-t border-white/5">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4 tracking-tight">How It Works</h2>
            <p className="text-white/50 text-sm max-w-2xl mx-auto">
              Follow our seamless pipeline flow to audit, predict, and offset your carbon footprint.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
            {STEPS.map((step, i) => (
              <GlassPanel 
                key={i} 
                className="p-5 flex flex-col justify-between h-48 border border-white/5 rounded-2xl relative overflow-hidden text-left"
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
              >
                <div className="text-2xl font-black text-emerald-500/20">{step.step}</div>
                <div>
                  <h4 className="text-xs font-bold text-white mb-1 tracking-wide">{step.title}</h4>
                  <p className="text-[10px] text-white/55 font-light leading-snug">{step.desc}</p>
                </div>
              </GlassPanel>
            ))}
          </div>
        </section>

        {/* Footer */}
        <footer className="w-full max-w-6xl px-6 py-12 border-t border-white/5 flex flex-col sm:flex-row justify-between items-center gap-6 text-white/40 text-xs">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 rounded-full bg-emerald-500 flex items-center justify-center font-bold text-xs text-white">
              C
            </div>
            <span className="font-semibold text-white/80 tracking-widest uppercase">CarbonCalc</span>
          </div>
          <div>
            © {new Date().getFullYear()} CarbonCalc Intelligence Platform. NASA-Inspired Environmental Modeling.
          </div>
        </footer>

      </div>
    </main>
  );
}
