"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { School, User } from "lucide-react";

export default function UCCSwitch() {
  const [isOn, setIsOn] = useState(true);

  return (
    <div className="flex items-center justify-between w-full px-4 py-3 bg-white/50 backdrop-blur-sm rounded-2xl border border-white/20 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-mint-pastel/30 rounded-lg">
          {isOn ? (
            <School className="w-5 h-5 text-mint-solid" />
          ) : (
            <User className="w-5 h-5 text-gray-400" />
          )}
        </div>
        <span className="text-gray-600 font-medium text-sm">
          {isOn ? "Comunidad UCC" : "Invitado Externo"}
        </span>
      </div>
      
      <div 
        onClick={() => setIsOn(!isOn)}
        onKeyDown={(e) => e.key === 'Enter' && setIsOn(!isOn)}
        role="button"
        tabIndex={0}
        aria-label="Alternar entre Comunidad UCC e Invitado"
        className={`w-14 h-8 flex items-center rounded-full p-1 cursor-pointer transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-mint-solid/50 ${
          isOn ? 'bg-mint-solid' : 'bg-gray-300'
        }`}
      >
        <motion.div
          layout
          transition={{ type: "spring", stiffness: 700, damping: 30 }}
          className="bg-white w-6 h-6 rounded-full shadow-md flex items-center justify-center text-[8px] font-bold text-mint-solid"
        >
          {isOn ? "UCC" : ""}
        </motion.div>
      </div>
    </div>
  );
}
