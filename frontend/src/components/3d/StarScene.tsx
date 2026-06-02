"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { Stars } from "@react-three/drei";
import { useRef } from "react";
import * as THREE from "three";

function TwinklingStars() {
  const starsRef = useRef<THREE.Group>(null);

  useFrame((state, delta) => {
    if (starsRef.current) {
      // Slow background cosmic drift
      starsRef.current.rotation.y += delta * 0.015;
      starsRef.current.rotation.x += delta * 0.005;
    }
  });

  return (
    <group ref={starsRef}>
      <Stars 
        radius={150} 
        depth={60} 
        count={2500} 
        factor={6} 
        saturation={0.8} 
        fade 
        speed={1.2} 
      />
    </group>
  );
}

interface StarSceneProps {
  nebulaColor?: string;
}

export default function StarScene({ nebulaColor = "#10B981" }: StarSceneProps) {
  return (
    <div className="absolute inset-0 w-full h-full -z-10 pointer-events-none overflow-hidden bg-[#03030c]">
      <Canvas camera={{ position: [0, 0, 10], fov: 60 }} className="w-full h-full">
        {/* Subtle space ambient lighting */}
        <ambientLight intensity={0.4} />
        
        {/* Beautiful colored nebula point light at the center */}
        <pointLight position={[0, 0, 0]} intensity={3.5} color={nebulaColor} distance={30} decay={2} />
        
        {/* Secondary soft blue galactic reflection backlight */}
        <pointLight position={[-10, 10, -10]} intensity={1.5} color="#0055ff" distance={40} />
        <pointLight position={[10, -10, 10]} intensity={1.5} color="#6366f1" distance={40} />

        <TwinklingStars />
      </Canvas>
      
      {/* Soft overlay gradient to ensure high readability of text content */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#03030c]/30 to-[#03030c] pointer-events-none" />
    </div>
  );
}
