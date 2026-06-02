"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import GlassPanel from "@/components/ui/GlassPanel";
import StarScene from "@/components/3d/StarScene";
import { Lock, Mail, ArrowRight } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await fetch("http://localhost:8000/api/v1/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        localStorage.setItem("user_id", data.id.toString());
        localStorage.setItem("user_name", data.name);
        
        // Save selected industry context
        if (data.industry_type) {
          localStorage.setItem("industry_type", data.industry_type);
          router.push("/dashboard");
        } else {
          router.push("/onboarding");
        }
      } else {
        const errText = await res.text();
        let errMsg = "Invalid email or password.";
        try {
          const errObj = JSON.parse(errText);
          errMsg = errObj.detail || errMsg;
        } catch {
          // ignore
        }
        setError(errMsg);
      }
    } catch (err) {
      setError("Cannot reach backend server. Using local simulation bypass...");
      setTimeout(() => {
        localStorage.setItem("user_id", "1");
        localStorage.setItem("user_name", "Demo Facility");
        localStorage.setItem("industry_type", "manufacturing");
        router.push("/dashboard");
      }, 1500);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative w-full h-screen overflow-hidden flex flex-col justify-center items-center">
      <StarScene nebulaColor="#6366f1" />
      
      <div className="absolute inset-0 z-10 flex flex-col items-center justify-center p-6 pointer-events-none">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md pointer-events-auto"
        >
          <GlassPanel className="p-10 flex flex-col items-center">
            <div className="w-12 h-12 rounded-full bg-emerald-500 flex items-center justify-center mb-6 shadow-[0_0_15px_rgba(16,185,129,0.5)]">
              <Lock size={24} className="text-white" />
            </div>
            
            <h2 className="text-3xl font-bold tracking-tight text-white mb-2">Sign In</h2>
            <p className="text-white/50 text-sm mb-6 text-center">
              Access your Carbon Identity and Digital Twin workspace.
            </p>

            {error && (
              <div className="w-full p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs text-center mb-4">
                {error}
              </div>
            )}
            
            <form onSubmit={handleLogin} className="w-full space-y-5">
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40" size={18} />
                <input 
                  type="email" 
                  required
                  placeholder="Company Email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white placeholder:text-white/30 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 transition-all text-sm"
                />
              </div>
              
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40" size={18} />
                <input 
                  type="password" 
                  required
                  placeholder="Password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white placeholder:text-white/30 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 transition-all text-sm"
                />
              </div>
              
              <button 
                type="submit"
                disabled={loading}
                className="w-full py-4 mt-4 bg-emerald-500 hover:bg-emerald-400 disabled:bg-emerald-500/50 text-white rounded-xl font-semibold tracking-wide flex items-center justify-center gap-2 transition-colors shadow-[0_0_15px_rgba(16,185,129,0.4)] cursor-pointer text-sm"
              >
                {loading ? "Authenticating..." : "Authenticate"}
                <ArrowRight size={18} />
              </button>
            </form>
            
            <div className="mt-8 text-sm text-white/40 text-center">
              Don&apos;t have a facility account? <Link href="/signup" className="text-emerald-400 hover:text-emerald-300">Register</Link>
            </div>
          </GlassPanel>
        </motion.div>
      </div>
    </main>
  );
}
