"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Stars } from "@react-three/drei";
import Earth from "./Earth";

interface SceneProps {
  score: number;
}

export default function Scene({ score }: SceneProps) {
  return (
    <div className="relative w-full h-full aspect-square flex items-center justify-center">
      <Canvas camera={{ position: [0, 0, 6.2], fov: 45 }} className="w-full h-full">
        {/* Deep space ambient background lighting */}
        <ambientLight intensity={score < 34 ? 0.6 : score < 67 ? 0.45 : 0.3} />
        
        {/* Powerful HDR Sun key light */}
        <directionalLight 
          position={[10, 5, 8]} 
          intensity={score < 34 ? 2.5 : score < 67 ? 1.8 : 1.2} 
          color={score < 34 ? "#ffffff" : score < 67 ? "#fde047" : "#ef4444"} 
        />
        
        {/* Fill reflection light from space nebulae */}
        <pointLight position={[-10, -5, -8]} intensity={1.5} color={score < 34 ? "#38bdf8" : score < 67 ? "#f97316" : "#7f1d1d"} />
        
        {/* Intense score dynamic back glow */}
        <pointLight 
          position={[0, 0, -5]} 
          intensity={2.0} 
          color={score < 34 ? "#0284c7" : score < 67 ? "#ea580c" : "#b91c1c"} 
        />
        
        {/* Twinkling starfield backdrop */}
        <Stars radius={120} depth={50} count={2000} factor={6} saturation={0.5} fade speed={1.2} />

        {/* Hyper-Realistic Earth model */}
        <Earth score={score} />
        
        <OrbitControls 
          enableZoom={true} 
          enablePan={false}
          autoRotate={false}
          maxPolarAngle={Math.PI / 1.1}
          minPolarAngle={Math.PI / 8}
        />
      </Canvas>
    </div>
  );
}
