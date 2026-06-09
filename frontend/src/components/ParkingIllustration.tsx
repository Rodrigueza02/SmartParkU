"use client";

import { motion } from "framer-motion";

export default function ParkingIllustration() {
  return (
    <div className="relative w-full h-72 flex items-center justify-center overflow-hidden">
      {/* Dynamic Background Mesh */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-20">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-mint-pastel rounded-full blur-[100px]" />
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-mint-solid rounded-full blur-[100px]" />
      </div>

      {/* Floating Leaves/Nature Particles */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1.5 }}
        className="absolute inset-0 flex justify-around items-end pb-12"
      >
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <motion.div
            key={i}
            animate={{ 
              y: [0, -15, 0],
              rotate: [0, 5, -5, 0],
              scale: [1, 1.1, 1]
            }}
            transition={{ 
              duration: 5 + i, 
              repeat: Infinity,
              ease: "easeInOut",
              delay: i * 0.5
            }}
            className="text-mint-solid/20"
          >
            <svg width="40" height="40" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17,8C8,10 5.9,16.17 3.82,21.34L5.71,22L6.66,19.7C7.14,19.87 7.64,20 8,20C19,20 22,3 22,3C21,5 14,5.25 9,6.25C4,7.25 2,11.5 2,13.5C2,15.5 3.75,17.25 3.75,17.25C7,8 17,8 17,8Z" />
            </svg>
          </motion.div>
        ))}
      </motion.div>

      {/* Modern Parking Spot with Glow */}
      <motion.div 
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 1, ease: "easeOut" }}
        className="absolute bottom-8 w-56 h-32 border-2 border-mint-solid/30 border-dashed rounded-2xl flex items-center justify-center bg-white/5 backdrop-blur-sm"
      >
        <div className="absolute inset-0 bg-mint-solid/5 rounded-2xl animate-pulse" />
        <span className="text-mint-solid/40 font-black text-3xl tracking-widest">UCC</span>
      </motion.div>

      {/* Sleek Modern Electric Car */}
      <motion.div
        initial={{ x: -400, opacity: 0, rotate: -5 }}
        animate={{ x: 0, opacity: 1, rotate: 0 }}
        transition={{ 
          type: "spring",
          stiffness: 50,
          damping: 15,
          delay: 0.2
        }}
        className="relative z-10 filter drop-shadow-[0_10px_15px_rgba(112,193,179,0.3)]"
      >
        <svg width="180" height="90" viewBox="0 0 180 90" fill="none" xmlns="http://www.w3.org/2000/svg">
          <ellipse cx="90" cy="82" rx="70" ry="6" fill="black" fillOpacity="0.1" />
          <path d="M10 55C10 55 15 45 35 40C55 35 120 35 145 40C170 45 175 55 175 65C175 75 165 80 155 80H25C15 80 10 75 10 65V55Z" fill="#70C1B3" />
          <path d="M40 42C40 42 55 15 90 15C125 15 145 38 150 42H40Z" fill="#70C1B3" />
          <path d="M50 40C50 40 62 20 90 20C118 20 135 38 140 40H50Z" fill="#E2E8F0" fillOpacity="0.4" />
          <path d="M92 20V40" stroke="#70C1B3" strokeWidth="1" strokeOpacity="0.3" />
          <circle cx="168" cy="58" r="4" fill="white">
            <animate attributeName="opacity" values="0.6;1;0.6" dur="2s" repeatCount="indefinite" />
          </circle>
          <path d="M168 58L180 55V61L168 58Z" fill="white" fillOpacity="0.2" />
          <path d="M10 60H15V70H10V60Z" fill="#EF4444" fillOpacity="0.8" />
          <g className="animate-spin-slow">
            <circle cx="45" cy="75" r="12" fill="#1F2937" />
            <circle cx="45" cy="75" r="8" stroke="#9CA3AF" strokeWidth="2" strokeDasharray="4 2" />
            <circle cx="45" cy="75" r="3" fill="#9CA3AF" />
          </g>
          <g className="animate-spin-slow">
            <circle cx="135" cy="75" r="12" fill="#1F2937" />
            <circle cx="135" cy="75" r="8" stroke="#9CA3AF" strokeWidth="2" strokeDasharray="4 2" />
            <circle cx="135" cy="75" r="3" fill="#9CA3AF" />
          </g>
          <motion.path 
            d="M30 65H150" 
            stroke="white" 
            strokeWidth="1.5" 
            strokeLinecap="round"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 0.4 }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          <path d="M158 72L162 72L160 76L164 76" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>

        {[1, 2, 3].map((p) => (
          <motion.div
            key={p}
            animate={{ 
              x: [0, 20, 0],
              y: [0, -10, 0],
              opacity: [0, 0.8, 0]
            }}
            transition={{ 
              duration: 2, 
              repeat: Infinity, 
              delay: p * 0.6 
            }}
            className="absolute top-1/2 left-1/2 w-1 h-1 bg-white rounded-full shadow-[0_0_8px_rgba(255,255,255,0.8)]"
          />
        ))}
      </motion.div>
    </div>
  );
}
