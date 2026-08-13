'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  User, Mail, Car, Leaf, Award, ChevronLeft,
  Settings, ShieldCheck, Zap, TrendingUp, AlertCircle, QrCode, ChevronRight
} from 'lucide-react';

interface StudentProfileProps {
  user: { nombre: string; rol: string; correo?: string };
  onBack?: () => void;
  onGoToQR?: () => void;
}

const UCC = {
  green: '#6AB023',
  blue:  '#00AEEF',
  lime:  '#B5D334',
  navy:  '#1E3A5F',
  cyan:  '#00BCD4',
};

const StudentProfile = ({ user, onBack, onGoToQR }: StudentProfileProps) => {
  const ecoData = { co2Saved: 1240, ecoPoints: 450, level: 'Sostenible Pro', progress: 75, streak: 12 };
  const vehicleData = { placa: 'UCC-2026', modelo: 'Mazda CX-30 / Eléctrico', tipo: 'Automóvil', color: 'Gris Polimetal', status: 'Validado LPR' };

  return (
    <div className="min-h-screen pb-32 font-sans" style={{ background: '#F4FBFF', color: UCC.navy }}>

      {/* ── Navbar ── */}
      <nav
        className="px-6 pt-12 pb-5 flex justify-between items-center sticky top-0 z-50 border-b"
        style={{ background: 'rgba(244,251,255,0.92)', backdropFilter: 'blur(16px)', borderColor: '#e0f4ff' }}
      >
        <motion.button whileTap={{ scale: 0.9 }} onClick={onBack}
          className="p-2 rounded-2xl transition-colors hover:bg-white"
        >
          <ChevronLeft size={22} style={{ color: UCC.blue }} />
        </motion.button>
        <span className="text-[11px] font-black uppercase tracking-[0.25em]" style={{ color: UCC.navy, opacity: 0.5 }}>
          SmartParkU — Perfil
        </span>
        <motion.button whileTap={{ scale: 0.9 }} className="p-2 rounded-2xl hover:bg-white transition-colors">
          <Settings size={20} style={{ color: UCC.blue }} />
        </motion.button>
      </nav>

      <main className="px-5 space-y-6 mt-6">

        {/* ── Avatar + identidad ── */}
        <section className="flex flex-col items-center">
          <div className="relative mb-5">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="w-28 h-28 rounded-[2.5rem] p-1.5 shadow-xl"
              style={{ background: '#fff', border: `2px solid ${UCC.blue}30` }}
            >
              <div
                className="w-full h-full rounded-[2.2rem] flex items-center justify-center overflow-hidden"
                style={{ background: `linear-gradient(135deg, ${UCC.navy}, ${UCC.blue})` }}
              >
                <User size={52} className="text-white/90 translate-y-2" />
              </div>
            </motion.div>
            <motion.div
              initial={{ x: 16, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: 0.3 }}
              className="absolute -bottom-1 -right-1 p-2 rounded-2xl shadow-md"
              style={{ background: '#fff', border: `1.5px solid ${UCC.green}30` }}
            >
              <ShieldCheck size={18} style={{ color: UCC.green }} />
            </motion.div>
          </div>

          <h1 className="text-xl font-black tracking-tight" style={{ color: UCC.navy }}>
            {user?.nombre || 'Jiliana Rodriguez'}
          </h1>
          <p className="text-sm font-medium text-gray-400 flex items-center gap-1.5 mt-1">
            <Mail size={13} className="text-gray-300" />
            {user?.correo || 'jiliana.rodriguez@campusucc.edu.co'}
          </p>
          <div className="mt-3">
            <span
              className="px-4 py-1.5 rounded-2xl text-[10px] font-black uppercase tracking-widest"
              style={{ background: `${UCC.blue}15`, color: UCC.blue, border: `1px solid ${UCC.blue}25` }}
            >
              {user?.rol || 'Estudiante'}
            </span>
          </div>
        </section>

        {/* ── Green Impact ── */}
        <motion.section
          initial={{ y: 24, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.15 }}
          className="bg-white rounded-3xl p-6 shadow-md relative overflow-hidden"
          style={{ border: `1.5px solid ${UCC.green}20` }}
        >
          <Leaf className="absolute -top-4 -right-4 w-32 h-32 opacity-5" style={{ color: UCC.green }} />

          <div className="flex items-center justify-between mb-6 relative z-10">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-2xl" style={{ background: `${UCC.green}15` }}>
                <TrendingUp size={20} style={{ color: UCC.green }} />
              </div>
              <div>
                <h3 className="text-base font-black" style={{ color: UCC.navy }}>Green Impact</h3>
                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Estadísticas Ambientales</p>
              </div>
            </div>
            <div
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl"
              style={{ background: `${UCC.lime}20` }}
            >
              <Zap size={13} style={{ color: UCC.green }} />
              <span className="text-[10px] font-black" style={{ color: UCC.green }}>{ecoData.streak} DÍAS</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 relative z-10">
            <div>
              <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">CO₂ Ahorrados</p>
              <div className="flex items-baseline gap-1">
                <span className="text-3xl font-black" style={{ color: UCC.navy }}>{ecoData.co2Saved}</span>
                <span className="text-xs font-bold text-gray-400">gr</span>
              </div>
            </div>
            <div className="border-l pl-4" style={{ borderColor: '#e2e8f0' }}>
              <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">Eco-Puntos</p>
              <div className="flex items-baseline gap-1">
                <span className="text-3xl font-black" style={{ color: UCC.blue }}>{ecoData.ecoPoints}</span>
                <span className="text-xs font-bold" style={{ color: UCC.cyan }}>pts</span>
              </div>
            </div>
          </div>

          <div className="mt-5 relative z-10">
            <div className="flex justify-between items-center mb-2">
              <div className="flex items-center gap-2">
                <Award size={14} className="text-yellow-500" />
                <span className="text-xs font-black uppercase tracking-wide text-gray-600">{ecoData.level}</span>
              </div>
              <span className="text-xs font-black" style={{ color: UCC.green }}>{ecoData.progress}%</span>
            </div>
            <div className="h-3 bg-gray-100 rounded-full overflow-hidden border border-gray-100">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${ecoData.progress}%` }}
                transition={{ duration: 1.5, ease: 'easeOut' }}
                className="h-full rounded-full"
                style={{ background: `linear-gradient(90deg, ${UCC.lime}, ${UCC.green})` }}
              />
            </div>
            <p className="text-[10px] text-center text-gray-400 font-medium italic mt-2">
              ¡Faltan 150g para el siguiente nivel!
            </p>
          </div>
        </motion.section>

        {/* ── Vehículo vinculado ── */}
        <motion.section
          initial={{ y: 24, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.25 }}
          className="rounded-3xl p-6 shadow-xl relative overflow-hidden text-white"
          style={{ background: `linear-gradient(135deg, ${UCC.navy} 0%, #0a2544 100%)` }}
        >
          <div className="absolute top-0 right-0 p-6 opacity-5">
            <Car size={110} />
          </div>
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-2xl" style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.15)' }}>
                <Car size={20} style={{ color: UCC.cyan }} />
              </div>
              <div>
                <h3 className="text-base font-bold">Vehículo Vinculado</h3>
                <p className="text-[10px] font-bold uppercase tracking-widest" style={{ color: UCC.cyan }}>
                  {vehicleData.status}
                </p>
              </div>
            </div>
          </div>

          <div
            className="rounded-2xl p-5 flex items-center justify-between"
            style={{ background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.12)' }}
          >
            <div className="space-y-3">
              <div className="bg-white px-4 py-2 rounded-xl border-b-4 border-gray-200">
                <p className="text-[8px] font-black text-gray-400 uppercase tracking-widest text-center">COLOMBIA</p>
                <p className="text-2xl font-black text-gray-900 tracking-tighter text-center">{vehicleData.placa}</p>
              </div>
              <div>
                <p className="text-sm font-bold text-white">{vehicleData.modelo}</p>
                <p className="text-[10px] font-medium text-gray-400 uppercase tracking-widest">{vehicleData.tipo} • {vehicleData.color}</p>
              </div>
            </div>
            <div className="h-16 w-px mx-4" style={{ background: 'rgba(255,255,255,0.1)' }} />
            <div className="flex flex-col items-center gap-2">
              <div
                className="w-11 h-11 rounded-full flex items-center justify-center"
                style={{ background: `${UCC.green}30`, border: `1.5px solid ${UCC.green}50` }}
              >
                <ShieldCheck size={22} style={{ color: UCC.lime }} />
              </div>
              <span className="text-[9px] font-black text-gray-400 uppercase tracking-widest">Activo</span>
            </div>
          </div>
        </motion.section>

        {/* ── Acceso QR — redirige al tab QR real ── */}
        <motion.section
          initial={{ scale: 0.96, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ delay: 0.35 }}
          className="bg-white rounded-3xl p-6 shadow-md"
          style={{ border: `1.5px solid ${UCC.blue}15` }}
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2.5 rounded-2xl" style={{ background: `${UCC.blue}15` }}>
              <QrCode size={20} style={{ color: UCC.blue }} />
            </div>
            <div>
              <h3 className="text-base font-black" style={{ color: UCC.navy }}>Acceso al Parqueadero</h3>
              <p className="text-xs text-gray-400 font-medium">Genera tu QR de ingreso</p>
            </div>
          </div>
          <motion.button
            whileTap={{ scale: 0.97 }}
            onClick={onGoToQR}
            className="w-full py-4 text-white font-black rounded-2xl flex items-center justify-center gap-2"
            style={{
              background: `linear-gradient(135deg, ${UCC.green}, ${UCC.blue})`,
              boxShadow: '0 6px 20px rgba(0,174,239,0.25)',
            }}
          >
            <QrCode size={18} />
            Ir al Generador de QR
            <ChevronRight size={16} />
          </motion.button>
        </motion.section>

        {/* ── Emergencia ── */}
        <section className="pb-4">
          <motion.button
            whileTap={{ scale: 0.96 }}
            className="w-full py-5 rounded-3xl flex items-center justify-center gap-4 group transition-colors border border-red-100 bg-red-50 hover:bg-red-100"
          >
            <div className="p-2.5 bg-white rounded-2xl shadow-sm text-red-500 group-hover:scale-110 transition-transform">
              <AlertCircle size={20} />
            </div>
            <div className="text-left">
              <p className="text-xs font-black text-red-600 uppercase tracking-widest">Reporte de Emergencia</p>
              <p className="text-[10px] font-bold text-red-400 uppercase tracking-tight">Asistencia inmediata RF12</p>
            </div>
          </motion.button>
        </section>
      </main>
    </div>
  );
};

export default StudentProfile;
