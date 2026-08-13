"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { School, User } from "lucide-react";

export default function UCCSwitch() {
  const [isOn, setIsOn] = useState(true);

  return (
    <div
      className="flex items-center justify-between px-4 py-3 rounded-2xl border"
      style={{ background: 'rgba(255,255,255,0.7)', backdropFilter: 'blur(8px)', borderColor: '#e2e8f0' }}
    >
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg" style={{ background: isOn ? '#00AEEF15' : '#f1f5f9' }}>
          {isOn
            ? <School className="w-4 h-4" style={{ color: '#00AEEF' }} />
            : <User   className="w-4 h-4 text-gray-400" />
          }
        </div>
        <span className="text-sm font-semibold" style={{ color: isOn ? '#1E3A5F' : '#94a3b8' }}>
          {isOn ? "Comunidad UCC" : "Invitado Externo"}
        </span>
      </div>

      <div
        onClick={() => setIsOn(!isOn)}
        onKeyDown={(e) => e.key === 'Enter' && setIsOn(!isOn)}
        role="button"
        tabIndex={0}
        aria-label="Alternar entre Comunidad UCC e Invitado"
        className="w-14 h-8 flex items-center rounded-full p-1 cursor-pointer transition-all duration-300 focus:outline-none focus:ring-2"
        style={{
          background: isOn ? 'linear-gradient(90deg, #6AB023, #00AEEF)' : '#d1d5db',
          boxShadow: isOn ? '0 2px 10px rgba(0,174,239,0.35)' : 'none',
        }}
      >
        <motion.div
          layout
          transition={{ type: "spring", stiffness: 700, damping: 30 }}
          className="bg-white w-6 h-6 rounded-full shadow-md flex items-center justify-center text-[7px] font-black"
          style={{ color: isOn ? '#00AEEF' : '#9ca3af' }}
        >
          {isOn ? "UCC" : ""}
        </motion.div>
      </div>
    </div>
  );
}
