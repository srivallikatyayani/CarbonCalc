"use client";

import { ReactNode } from "react";
import { motion, HTMLMotionProps } from "framer-motion";

interface GlassPanelProps extends HTMLMotionProps<"div"> {
  children: ReactNode;
  className?: string;
  hoverEffect?: boolean;
}

export default function GlassPanel({ children, className = "", hoverEffect = false, ...props }: GlassPanelProps) {
  return (
    <motion.div
      className={`glass-panel rounded-2xl p-6 ${hoverEffect ? "glass-panel-hover transition-all duration-300" : ""} ${className}`}
      {...props}
    >
      {children}
    </motion.div>
  );
}
