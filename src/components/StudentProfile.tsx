'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { 
  User, 
  Mail, 
  Car, 
  Leaf, 
  Award, 
  QrCode, 
  ChevronLeft,
  Settings,
  ShieldCheck,
  CreditCard,
  Zap,
  TrendingUp,
  AlertCircle
} from 'lucide-react';

interface StudentProfileProps {
  user: {
    nombre: string;
    rol: string;
    correo?: string;
  };
  onBack?: () => void;
}

const StudentProfile = ({ user, onBack }: StudentProfileProps) => {
  // Mock data basada en requerimientos RF11 y RF01
  const ecoData = {
    co2Saved: 1240,
    ecoPoints: 450,
    level: 'Sostenible Pro',
    progress: 75,
    streak: 12
  };

  const vehicleData = {
    placa: 'UCC-2026',
    modelo: 'Mazda CX-30 / Eléctrico',
    tipo: 'Automóvil',
    color: 'Gris Polimetal',
    status: 'Validado LPR'
  };

  return (
    <div className="min-h-screen bg-[#FDFDFD] pb-32 font-sans text-slate-800">
      {/* --- Nordic Top Bar --- */}
      <nav className="px-8 pt-14 pb-6 flex justify-between items-center bg-white/70 backdrop-blur-xl sticky top-0 z-50 border-b border-slate-50">
        <motion.button 
          whileTap={{ scale: 0.9 }}
          onClick={onBack}
          className="p-2 rounded-2xl hover:bg-slate-50 transition-colors"
        >
          <ChevronLeft size={24} className="text-slate-400" />
        </motion.button>
        <span className="text-[11px] font-black uppercase tracking-[0.3em] text-slate-400">SmartParkU Profile</span>
        <motion.button 
          whileTap={{ scale: 0.9 }}
          className="p-2 rounded-2xl hover:bg-slate-50 transition-colors"
        >
          <Settings size={22} className="text-slate-400" />
        </motion.button>
      </nav>

      <main className="px-6 space-y-10 mt-8">
        
        {/* --- Identity Header (RF01) --- */}
        <section className="flex flex-col items-center">
          <div className="relative mb-6">
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="w-32 h-32 rounded-[3rem] bg-white p-1.5 shadow-[0_20px_40px_rgba(0,0,0,0.06)] border border-slate-100"
            >
              <div className="w-full h-full rounded-[2.6rem] bg-gradient-to-tr from-[#A3E4D7] to-[#70C1B3] flex items-center justify-center overflow-hidden">
                <User size={60} className="text-white/90 translate-y-2" />
              </div>
            </motion.div>
            <motion.div 
              initial={{ x: 20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="absolute -bottom-1 -right-1 bg-white p-2.5 rounded-2xl shadow-lg border border-slate-50"
            >
              <ShieldCheck size={20} className="text-[#70C1B3]" />
            </motion.div>
          </div>
          
          <div className="text-center space-y-2">
            <h1 className="text-2xl font-black tracking-tight text-slate-900">{user?.nombre || 'Jiliana Rodriguez'}</h1>
            <p className="text-sm font-medium text-slate-400 flex items-center justify-center gap-2">
              <Mail size={14} className="text-slate-300" />
              {user?.correo || 'jiliana.rodriguez@campusucc.edu.co'}
            </p>
            <div className="pt-2">
              <span className="px-5 py-2 rounded-2xl bg-[#A3E4D7]/15 text-[#5EB0A2] text-[10px] font-black uppercase tracking-[0.15em] border border-[#A3E4D7]/20">
                Rol: {user?.rol || 'Estudiante'}
              </span>
            </div>
          </div>
        </section>

        {/* --- Green Impact Premium Panel (RF11) --- */}
        <motion.section 
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-[3rem] p-8 shadow-[0_25px_50px_rgba(0,0,0,0.04)] border border-slate-50 relative overflow-hidden group"
        >
          {/* Subtle Background Icon */}
          <Leaf className="absolute -top-6 -right-6 text-[#A3E4D7]/10 w-40 h-40 -rotate-12 group-hover:rotate-0 transition-transform duration-700" />
          
          <div className="flex items-center justify-between mb-8 relative z-10">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-[#A3E4D7]/10 rounded-2xl">
                <TrendingUp size={22} className="text-[#70C1B3]" />
              </div>
              <div>
                <h3 className="text-lg font-black text-slate-800">Green Impact</h3>
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Estadísticas Ambientales</p>
              </div>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-orange-50 rounded-xl">
              <Zap size={14} className="text-orange-400 fill-orange-400" />
              <span className="text-[10px] font-black text-orange-600">{ecoData.streak} DÍAS</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6 relative z-10">
            <div className="space-y-1">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.1em]">CO₂ Ahorrados</p>
              <div className="flex items-baseline gap-1">
                <span className="text-3xl font-black text-slate-900">{ecoData.co2Saved}</span>
                <span className="text-xs font-bold text-slate-400">gr</span>
              </div>
            </div>
            <div className="space-y-1 border-l border-slate-100 pl-6">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.1em]">Eco-Puntos</p>
              <div className="flex items-baseline gap-1">
                <span className="text-3xl font-black text-[#70C1B3]">{ecoData.ecoPoints}</span>
                <span className="text-xs font-bold text-[#A3E4D7]">pts</span>
              </div>
            </div>
          </div>

          <div className="mt-8 space-y-3 relative z-10">
            <div className="flex justify-between items-end">
              <div className="flex items-center gap-2">
                <Award size={16} className="text-yellow-500" />
                <span className="text-xs font-black text-slate-600 uppercase tracking-wider">{ecoData.level}</span>
              </div>
              <span className="text-xs font-black text-[#70C1B3]">{ecoData.progress}%</span>
            </div>
            <div className="h-4 bg-slate-50 rounded-full p-1 border border-slate-100 overflow-hidden">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${ecoData.progress}%` }}
                transition={{ duration: 1.5, ease: "easeOut" }}
                className="h-full bg-gradient-to-r from-[#A3E4D7] to-[#70C1B3] rounded-full shadow-[0_0_15px_rgba(112,193,179,0.3)]"
              />
            </div>
            <p className="text-[10px] text-center text-slate-400 font-medium italic">¡Faltan 150g para el siguiente nivel!</p>
          </div>
        </motion.section>

        {/* --- Vehicle Linked (LPR System) --- */}
        <motion.section 
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-[#1A1C1E] rounded-[3rem] p-8 shadow-2xl shadow-slate-900/10 text-white relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 p-8 opacity-5">
            <Car size={120} />
          </div>

          <div className="flex justify-between items-center mb-8">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-white/5 rounded-2xl border border-white/10">
                <Car size={22} className="text-[#A3E4D7]" />
              </div>
              <div>
                <h3 className="text-lg font-bold">Vehículo Vinculado</h3>
                <p className="text-[10px] font-bold text-[#A3E4D7] uppercase tracking-widest">{vehicleData.status}</p>
              </div>
            </div>
          </div>

          <div className="bg-white/5 rounded-[2rem] p-6 border border-white/10 flex items-center justify-between">
            <div className="space-y-4">
              <div className="bg-white px-5 py-2.5 rounded-xl border-b-[4px] border-slate-200">
                <p className="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em] text-center mb-0.5">COLOMBIA</p>
                <p className="text-3xl font-black text-slate-900 tracking-tighter text-center">{vehicleData.placa}</p>
              </div>
              <div className="px-2">
                <p className="text-sm font-bold text-slate-100">{vehicleData.modelo}</p>
                <p className="text-[10px] font-medium text-slate-500 uppercase tracking-widest">{vehicleData.tipo} • {vehicleData.color}</p>
              </div>
            </div>
            <div className="h-20 w-[1px] bg-white/10 mx-4" />
            <div className="flex flex-col items-center gap-2">
              <div className="w-12 h-12 rounded-full bg-[#A3E4D7]/20 flex items-center justify-center border border-[#A3E4D7]/30">
                <ShieldCheck size={24} className="text-[#A3E4D7]" />
              </div>
              <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Activo</span>
            </div>
          </div>
        </motion.section>

        {/* --- Emergency QR / Manual Entry --- */}
        <motion.section 
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-[3rem] p-10 flex flex-col items-center space-y-8 shadow-[0_20px_40px_rgba(0,0,0,0.03)] border border-slate-50"
        >
          <div className="text-center space-y-2">
            <div className="flex items-center justify-center gap-2 text-slate-800 mb-1">
              <QrCode size={20} className="text-[#70C1B3]" />
              <h3 className="text-xl font-black tracking-tight">Acceso Manual</h3>
            </div>
            <p className="text-xs text-slate-400 font-medium max-w-[220px] mx-auto leading-relaxed">
              Escanea en el lector UCC si el sistema LPR presenta fallas.
            </p>
          </div>

          <div className="relative p-8 bg-slate-50/50 rounded-[2.5rem] border-2 border-dashed border-slate-200 group cursor-pointer hover:border-[#A3E4D7] transition-all duration-500">
            <QrCode size={180} className="text-slate-900 group-hover:text-[#70C1B3] transition-colors duration-500" />
            {/* Scanning Line Animation */}
            <motion.div 
              animate={{ top: ['2rem', '13.25rem', '2rem'] }}
              transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
              className="absolute left-8 right-8 h-1 bg-gradient-to-r from-transparent via-[#A3E4D7] to-transparent shadow-[0_0_15px_rgba(112,193,179,0.8)] z-10"
            />
            {/* Corner Accents */}
            <div className="absolute top-4 left-4 w-6 h-6 border-t-2 border-l-2 border-slate-300 rounded-tl-xl" />
            <div className="absolute top-4 right-4 w-6 h-6 border-t-2 border-r-2 border-slate-300 rounded-tr-xl" />
            <div className="absolute bottom-4 left-4 w-6 h-6 border-b-2 border-l-2 border-slate-300 rounded-bl-xl" />
            <div className="absolute bottom-4 right-4 w-6 h-6 border-b-2 border-r-2 border-slate-300 rounded-br-xl" />
          </div>

          <div className="flex items-center gap-3 px-6 py-3 bg-slate-50 rounded-2xl border border-slate-100">
            <CreditCard size={18} className="text-slate-400" />
            <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em]">ID: 809244 - UCC 2026</span>
          </div>
        </motion.section>

        {/* --- Panic Button Section (RF12) --- */}
        <section className="pt-4">
          <motion.button 
            whileTap={{ scale: 0.95 }}
            className="w-full py-6 bg-red-50 rounded-[2.5rem] border border-red-100 flex items-center justify-center gap-4 group hover:bg-red-100 transition-colors"
          >
            <div className="p-2.5 bg-white rounded-2xl shadow-sm text-red-500 group-hover:scale-110 transition-transform">
              <AlertCircle size={22} />
            </div>
            <div className="text-left">
              <p className="text-xs font-black text-red-600 uppercase tracking-widest">Reporte de Emergencia</p>
              <p className="text-[10px] font-bold text-red-400 uppercase tracking-tighter">Asistencia inmediata RF12</p>
            </div>
          </motion.button>
        </section>

      </main>

      {/* Spacing for Nav */}
      <div className="h-10" />
    </div>
  );
};

export default StudentProfile;
