"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  QrCode, 
  Map as MapIcon, 
  Users, 
  ShieldCheck, 
  AlertTriangle, 
  Settings, 
  Database, 
  Camera, 
  Ban,
  ChevronRight,
  UserCircle
} from "lucide-react";

// --- Sub-componente: Pantalla Visitante ---
const VisitorScreen = () => (
  <div className="flex flex-col h-full bg-[#F9FBFA] text-gray-800 font-sans p-6 rounded-[3rem] border-[8px] border-gray-900 shadow-2xl overflow-hidden relative">
    <div className="flex justify-between items-center mb-8 px-2">
      <span className="text-xs font-bold">9:41</span>
      <div className="flex gap-1">
        <div className="w-4 h-4 rounded-full bg-gray-200" />
        <div className="w-4 h-4 rounded-full bg-gray-200" />
      </div>
    </div>

    <header className="mb-8">
      <motion.h1 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-2xl font-light tracking-tight"
      >
        ¡Bienvenido!
      </motion.h1>
      <motion.p 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="text-sm text-gray-500"
      >
        Inicie Sesión UCC
      </motion.p>
    </header>

    <div className="flex-1 flex flex-col gap-6">
      <div className="relative h-48 bg-gray-100 rounded-3xl overflow-hidden border border-gray-200">
        <div className="absolute inset-0 flex items-center justify-center">
          <MapIcon className="w-12 h-12 text-gray-300" />
        </div>
        <motion.div 
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="absolute top-10 left-10 right-10 bottom-10 bg-mint-pastel/40 border-2 border-mint-solid rounded-xl flex items-center justify-center"
        >
          <span className="text-mint-solid font-bold text-xs uppercase tracking-widest">
            Cortesía / Evento
          </span>
        </motion.div>
      </div>

      <motion.button 
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="w-full py-5 bg-mint-solid text-white rounded-2xl shadow-lg shadow-mint-solid/20 flex items-center justify-center gap-3 font-semibold"
      >
        <QrCode className="w-5 h-5" />
        Validar Acceso (QR/LPR)
      </motion.button>
    </div>

    <footer className="mt-auto pt-6 text-center">
      <button className="text-mint-solid text-sm font-medium hover:underline transition-all">
        Registrarse como Estudiante UCC
      </button>
    </footer>
  </div>
);

// --- Sub-componente: Pantalla Súper Admin ---
const AdminScreen = () => {
  const [activeWidget, setActiveWidget] = useState<string | null>(null);

  const widgets = [
    { id: 'users', icon: Users, label: 'Gestión Usuarios UCC', color: 'bg-blue-50 text-blue-600' },
    { id: 'roles', icon: ShieldCheck, label: 'Roles y Permisos', color: 'bg-purple-50 text-purple-600' },
    { id: 'reports', icon: AlertTriangle, label: 'Incidentes y Auditoría', color: 'bg-orange-50 text-orange-600' },
    { id: 'hardware', icon: Settings, label: 'Mantenimiento IoT', color: 'bg-gray-100 text-gray-600' },
  ];

  return (
    <div className="flex flex-col h-full bg-white text-gray-900 font-sans p-6 rounded-[3rem] border-[8px] border-gray-900 shadow-2xl overflow-hidden relative">
      <div className="flex justify-between items-center mb-6 px-2">
        <span className="text-xs font-bold">9:41</span>
        <div className="flex gap-1 italic text-[10px] text-mint-solid font-bold">SUPER ADMIN</div>
      </div>

      <header className="mb-6 flex items-center gap-3">
        <div className="w-12 h-12 bg-mint-pastel rounded-full flex items-center justify-center">
          <UserCircle className="w-8 h-8 text-mint-solid" />
        </div>
        <div>
          <h1 className="text-lg font-bold leading-tight">Hola, Súper Admin</h1>
          <p className="text-xs text-gray-500">Panel de Control Global</p>
        </div>
      </header>

      <div className="grid grid-cols-2 gap-3 mb-6">
        {widgets.map((w) => (
          <motion.button
            key={w.id}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setActiveWidget(w.id === activeWidget ? null : w.id)}
            className={`p-4 rounded-2xl flex flex-col items-start gap-2 transition-all ${w.color} border border-transparent hover:border-current/20 shadow-sm`}
          >
            <w.icon className="w-6 h-6" />
            <span className="text-[10px] font-bold text-left leading-tight uppercase tracking-tighter">
              {w.label}
            </span>
          </motion.button>
        ))}
      </div>

      <div className="flex-1 relative bg-slate-900 rounded-3xl overflow-hidden mb-4 border-2 border-mint-solid/30">
        <div className="absolute top-4 left-4 right-4 flex justify-between">
          <div className="flex gap-2">
            <div className="px-2 py-1 bg-mint-solid/90 text-white text-[8px] rounded-md flex items-center gap-1">
              <Database className="w-2 h-2" /> Sensores OK
            </div>
            <div className="px-2 py-1 bg-blue-500/90 text-white text-[8px] rounded-md flex items-center gap-1">
              <Camera className="w-2 h-2" /> LPR 4K
            </div>
          </div>
        </div>

        {[1, 2, 3, 4, 5].map((i) => (
          <motion.div
            key={i}
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 2, repeat: Infinity, delay: i * 0.3 }}
            className="absolute w-3 h-3 bg-mint-solid rounded-full shadow-[0_0_10px_rgba(112,193,179,0.8)]"
            style={{ 
              top: `${20 + i * 15}%`, 
              left: `${30 + (i % 2) * 40}%` 
            }}
          />
        ))}

        <div className="absolute bottom-4 left-4 text-[8px] text-mint-pastel font-mono">
          RF02: LPR/CAM ACTIVE_STREAM
        </div>
      </div>

      <motion.button 
        whileHover={{ scale: 1.02, backgroundColor: '#EF4444', color: '#fff' }}
        whileTap={{ scale: 0.98 }}
        className="w-full py-4 border-2 border-red-500 text-red-500 rounded-2xl flex items-center justify-center gap-2 font-bold text-sm transition-colors"
      >
        <Ban className="w-4 h-4" />
        Sanciones / Bloqueos (RF15)
      </motion.button>
      
      <AnimatePresence>
        {activeWidget && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="absolute inset-6 bg-white rounded-[2rem] z-10 p-6 flex flex-col shadow-2xl border border-mint-pastel"
          >
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-bold text-mint-solid uppercase text-xs">Detalle de Gestión</h2>
              <button onClick={() => setActiveWidget(null)} className="text-gray-400 text-xs">Cerrar</button>
            </div>
            <div className="flex-1 flex flex-col items-center justify-center text-center gap-4">
              <div className="p-4 bg-mint-pastel/20 rounded-full">
                {React.createElement(widgets.find(w => w.id === activeWidget)?.icon || Settings, { className: "w-8 h-8 text-mint-solid" })}
              </div>
              <p className="text-sm font-medium">Cargando módulos de {widgets.find(w => w.id === activeWidget)?.label}...</p>
              <div className="w-full bg-gray-100 h-1 rounded-full overflow-hidden">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: '100%' }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  className="h-full bg-mint-solid"
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default function ComparisonPage() {
  return (
    <main className="min-h-screen bg-lightGray p-12 flex flex-col items-center">
      <div className="mb-12 text-center">
        <h1 className="text-3xl font-black text-gray-900 mb-2">Comparativa de Roles SmartParkU</h1>
        <p className="text-gray-500 max-w-2xl">
          Visualización de la experiencia de usuario contrastada entre un Visitante (RF03) y un Súper Administrador, 
          manteniendo la coherencia visual con la paleta Verde Menta.
        </p>
      </div>

      <div className="flex flex-wrap justify-center gap-16 items-start">
        <div className="flex flex-col items-center gap-6">
          <div className="w-[380px] h-[780px]">
            <VisitorScreen />
          </div>
          <div className="bg-white px-6 py-3 rounded-full shadow-sm border border-gray-100 flex items-center gap-2">
            <span className="w-3 h-3 bg-mint-solid rounded-full" />
            <span className="text-sm font-bold text-gray-700">Rol: Visitante (Minimalista)</span>
          </div>
        </div>

        <div className="flex flex-col items-center gap-6">
          <div className="w-[380px] h-[780px]">
            <AdminScreen />
          </div>
          <div className="bg-white px-6 py-3 rounded-full shadow-sm border border-gray-100 flex items-center gap-2">
            <span className="w-3 h-3 bg-blue-500 rounded-full animate-pulse" />
            <span className="text-sm font-bold text-gray-700">Rol: Súper Admin (Avanzado)</span>
          </div>
        </div>
      </div>

      <section className="mt-20 max-w-4xl w-full grid grid-cols-1 md:grid-cols-2 gap-8 bg-white p-8 rounded-3xl shadow-xl border border-mint-pastel/30">
        <div>
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            <div className="w-2 h-6 bg-mint-solid rounded-full" />
            UX Visitante (RF03)
          </h3>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-center gap-2"><ChevronRight className="w-4 h-4 text-mint-solid" /> Estética Nórdica: Espacios limpios y tipografía ligera.</li>
            <li className="flex items-center gap-2"><ChevronRight className="w-4 h-4 text-mint-solid" /> Foco en Conversión: Iniciar sesión o registrarse.</li>
            <li className="flex items-center gap-2"><ChevronRight className="w-4 h-4 text-mint-solid" /> Mapa Abstraído: Solo información relevante de cortesía.</li>
          </ul>
        </div>
        <div>
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            <div className="w-2 h-6 bg-blue-500 rounded-full" />
            UX Súper Admin (RF02/RF12/RF15)
          </h3>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-center gap-2"><ChevronRight className="w-4 h-4 text-blue-500" /> Control Total: Dashboard modular con widgets interactivos.</li>
            <li className="flex items-center gap-2"><ChevronRight className="w-4 h-4 text-blue-500" /> Telemetría IoT: Visualización en tiempo real de sensores.</li>
            <li className="flex items-center gap-2"><ChevronRight className="w-4 h-4 text-blue-500" /> Gestión de Seguridad: Acceso rápido a sanciones y bloqueos.</li>
          </ul>
        </div>
      </section>
    </main>
  );
}
