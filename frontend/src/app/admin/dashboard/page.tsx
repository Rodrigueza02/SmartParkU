"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Bell, 
  Map as MapIcon, 
  LayoutDashboard, 
  AlertTriangle, 
  PieChart, 
  User, 
  Clock,
  ShieldAlert,
  ChevronRight,
  MoreVertical,
  ArrowUpRight,
  Car,
  Bike,
  Zap,
  LogOut
} from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { useRouter } from "next/navigation";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// --- Tipos ---
type SlotStatus = "Occupied" | "Fixed" | "Yielded" | "Available";

interface ParkingSlot {
  id: string;
  type: "Admin" | "Standard" | "VIP";
  status: SlotStatus;
}

// --- Mock Data ---
const INITIAL_SLOTS: ParkingSlot[] = [
  { id: "A-01", type: "Admin",    status: "Fixed" },
  { id: "A-02", type: "Admin",    status: "Fixed" },
  { id: "A-03", type: "Admin",    status: "Occupied" },
  { id: "B-12", type: "Standard", status: "Occupied" },
  { id: "B-13", type: "Standard", status: "Available" },
  { id: "V-05", type: "VIP",      status: "Occupied" },
];

const ALERTS = [
  { id: 1, type: "Security", message: "Intento de acceso no autorizado en Puerta Norte", time: "Hace 5 min", level: "Critical" },
  { id: 2, type: "Time",     message: "Vehículo ABC-123 ha excedido el tiempo límite",   time: "Hace 12 min", level: "Warning" },
];

const USAGE_DATA = [
  { label: "Autos",    value: 65, color: "#6AB023", icon: Car },
  { label: "Motos",    value: 25, color: "#00AEEF", icon: Bike },
  { label: "Scooters", value: 10, color: "#B5D334", icon: Zap },
];

// --- Componentes ---

const AdminHeader = () => {
  const logout = useAuthStore((state) => state.logout);
  const router = useRouter();
  const handleLogout = () => { logout(); router.push("/"); };

  return (
    <header
      className="p-6 flex items-center justify-between sticky top-0 z-30 border-b"
      style={{ background: 'rgba(244,251,255,0.92)', backdropFilter: 'blur(16px)', borderColor: '#e0f4ff' }}
    >
      <div className="flex items-center gap-4">
        <div
          className="w-14 h-14 rounded-2xl flex items-center justify-center shadow"
          style={{ background: 'linear-gradient(135deg, #1E3A5F, #00AEEF)' }}
        >
          <User className="text-white w-7 h-7" />
        </div>
        <div>
          <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Panel de Gestión</p>
          <h1 className="text-xl font-black" style={{ color: '#1E3A5F' }}>
            Hola, <span style={{ color: '#00AEEF' }}>Admin Jiliana</span>
          </h1>
          <span className="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-0.5 rounded-md">
            Mantenimiento / Gestión
          </span>
        </div>
      </div>
      <div className="flex gap-2">
        <button
          className="p-3 rounded-2xl relative transition-colors hover:opacity-80"
          style={{ background: '#f1f5f9', color: '#64748b' }}
        >
          <Bell className="w-5 h-5" />
          <span className="absolute top-3 right-3 w-2 h-2 bg-red-500 border-2 border-white rounded-full" />
        </button>
        <button
          onClick={handleLogout}
          className="p-3 rounded-2xl transition-colors hover:opacity-80"
          style={{ background: '#fee2e2', color: '#ef4444' }}
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
};

const UsageAnalysisWidget = () => {
  let cumulativePercent = 0;

  return (
    <motion.section 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white rounded-[2.5rem] p-6 border border-lightGray shadow-sm"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="font-black text-gray-700 flex items-center gap-2">
          <PieChart className="w-5 h-5 text-mint-solid" />
          Análisis de Uso
        </h2>
        <button className="text-[10px] font-bold text-mint-solid flex items-center gap-1 bg-mint-pastel/20 px-3 py-1.5 rounded-full">
          DETALLES <ArrowUpRight className="w-3 h-3" />
        </button>
      </div>

      <div className="flex flex-col md:flex-row items-center gap-8">
        <div className="relative w-40 h-40">
          <svg viewBox="0 0 32 32" className="w-full h-full -rotate-90">
            {USAGE_DATA.map((item, i) => {
              const startPercent = cumulativePercent;
              cumulativePercent += item.value;
              const dashArray = `${item.value} ${100 - item.value}`;
              const dashOffset = -startPercent;
              
              return (
                <circle
                  key={i}
                  cx="16" cy="16" r="12"
                  fill="transparent"
                  stroke={item.color}
                  strokeWidth="6"
                  strokeDasharray={dashArray}
                  strokeDashoffset={dashOffset}
                  className="transition-all duration-1000"
                />
              );
            })}
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-black text-gray-800">84%</span>
            <span className="text-[8px] font-bold text-gray-400 uppercase">Ocupación</span>
          </div>
        </div>

        <div className="flex-1 grid grid-cols-1 gap-3 w-full">
          {USAGE_DATA.map((item, i) => (
            <div key={i} className="flex items-center justify-between p-3 rounded-2xl bg-softWhite border border-lightGray/50">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl" style={{ backgroundColor: `${item.color}20` }}>
                  <item.icon className="w-4 h-4" style={{ color: item.color }} />
                </div>
                <span className="text-sm font-bold text-gray-600">{item.label}</span>
              </div>
              <span className="font-black text-gray-800">{item.value}%</span>
            </div>
          ))}
        </div>
      </div>
    </motion.section>
  );
};

const AlertsWidget = () => (
  <section className="flex flex-col gap-4">
    <div className="flex items-center justify-between">
      <h2 className="font-black text-gray-700 flex items-center gap-2">
        <ShieldAlert className="w-5 h-5 text-red-400" />
        Alertas del Sistema
      </h2>
      <span className="text-[10px] font-bold px-2 py-1 bg-red-50 text-red-500 rounded-lg animate-pulse">2 ACTIVAS</span>
    </div>
    
    <div className="flex flex-col gap-3">
      {ALERTS.map((alert) => (
        <motion.div 
          key={alert.id}
          whileHover={{ x: 5 }}
          className={cn(
            "p-4 rounded-[1.5rem] border flex items-start gap-4 transition-all",
            alert.level === 'Critical' ? "bg-red-50 border-red-100" : "bg-orange-50 border-orange-100"
          )}
        >
          <div className={cn(
            "p-2.5 rounded-xl mt-1",
            alert.level === 'Critical' ? "bg-red-500 text-white" : "bg-orange-400 text-white"
          )}>
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div className="flex-1">
            <div className="flex justify-between items-center mb-1">
              <span className={cn(
                "text-[10px] font-black uppercase",
                alert.level === 'Critical' ? "text-red-500" : "text-orange-500"
              )}>{alert.type}</span>
              <span className="text-[10px] font-medium text-gray-400 flex items-center gap-1">
                <Clock className="w-3 h-3" /> {alert.time}
              </span>
            </div>
            <p className="text-sm font-bold text-gray-800 leading-tight">{alert.message}</p>
          </div>
          <MoreVertical className="w-4 h-4 text-gray-400" />
        </motion.div>
      ))}
    </div>
  </section>
);

const AdminMapWidget = () => {
  const [slots, setSlots] = useState<ParkingSlot[]>(INITIAL_SLOTS);
  const [selectedSlot, setSelectedSlot] = useState<ParkingSlot | null>(null);

  const handleCederCupo = (id: string) => {
    setSlots(prev => prev.map(slot => 
      slot.id === id ? { ...slot, status: "Yielded" as SlotStatus } : slot
    ));
    setSelectedSlot(null);
  };

  return (
    <section className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="font-black text-gray-700 flex items-center gap-2">
          <MapIcon className="w-5 h-5 text-mint-solid" />
          Mapa de Gestión de Cupos
        </h2>
        <div className="flex gap-2">
          <div className="flex items-center gap-1 text-[10px] font-bold text-gray-400">
            <div className="w-2 h-2 rounded-full bg-blue-500" /> Fijo
          </div>
          <div className="flex items-center gap-1 text-[10px] font-bold text-gray-400">
            <div className="w-2 h-2 rounded-full bg-mint-solid animate-pulse" /> Libre
          </div>
        </div>
      </div>

      <div className="bg-white rounded-[2.5rem] p-8 shadow-sm border border-lightGray grid grid-cols-2 sm:grid-cols-3 gap-6">
        {slots.map((slot) => (
          <motion.button
            key={slot.id}
            whileTap={{ scale: 0.95 }}
            onClick={() => setSelectedSlot(slot)}
            className={cn(
              "h-24 rounded-2xl flex flex-col items-center justify-center gap-2 border-2 transition-all relative overflow-hidden",
              slot.status === 'Occupied' && "bg-red-50 border-red-100 text-red-400",
              slot.status === 'Fixed' && "bg-blue-50 border-blue-200 text-blue-500",
              slot.status === 'Yielded' && "bg-mint-pastel/30 border-mint-solid text-mint-solid",
              slot.status === 'Available' && "bg-softWhite border-lightGray text-gray-400"
            )}
          >
            {slot.status === 'Yielded' && (
              <motion.div 
                animate={{ opacity: [0.3, 0.6, 0.3] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="absolute inset-0 bg-mint-solid/10"
              />
            )}
            <span className="text-[10px] font-black tracking-wider uppercase opacity-60">#{slot.id}</span>
            <div className={cn(
              "w-10 h-5 rounded-md",
              slot.status === 'Occupied' && "bg-red-200",
              slot.status === 'Fixed' && "bg-blue-400",
              slot.status === 'Yielded' && "bg-mint-solid shadow-[0_0_10px_rgba(112,193,179,0.5)]",
              slot.status === 'Available' && "bg-gray-200"
            )} />
            <span className="text-[10px] font-black uppercase tracking-widest">{slot.type}</span>
          </motion.button>
        ))}
      </div>

      <AnimatePresence>
        {selectedSlot && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="bg-white p-6 rounded-[2rem] border-2 border-mint-pastel shadow-xl"
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-black text-gray-800">Cajón {selectedSlot.id}</h3>
                <p className="text-xs text-gray-500">Estado actual: <span className="font-bold uppercase">{selectedSlot.status}</span></p>
              </div>
              <button onClick={() => setSelectedSlot(null)} className="text-gray-400 hover:text-gray-600 font-bold">✕</button>
            </div>

            {selectedSlot.type === "Admin" && selectedSlot.status === "Fixed" && (
              <button 
                onClick={() => handleCederCupo(selectedSlot.id)}
                className="w-full bg-mint-solid text-white font-black py-4 rounded-2xl shadow-lg shadow-mint-solid/30 hover:brightness-105 active:scale-95 transition-all flex items-center justify-center gap-2"
              >
                <Zap className="w-5 h-5" />
                CEDER CUPO (+2 días)
              </button>
            )}
            
            {selectedSlot.status === "Occupied" && (
              <div className="bg-red-50 text-red-500 p-4 rounded-xl flex items-center gap-3">
                <ShieldAlert className="w-5 h-5" />
                <p className="text-xs font-bold">Vehículo detectado. Gestión restringida.</p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
};

export default function AdminDashboard() {
  const { token, user } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!token || !user) { router.push("/"); return; }
    if (user.rol !== "SuperAdmin" && user.rol !== "Administrativo") { router.push("/"); }
  }, [token, user, router]);

  if (!token || !user) return null;

  return (
    <div className="min-h-screen pb-24 font-sans" style={{ background: '#F4FBFF', color: '#1E3A5F' }}>
      <AdminHeader />

      <main className="px-6 py-8 flex flex-col gap-10 max-w-4xl mx-auto">
        <UsageAnalysisWidget />
        <AlertsWidget />
        <AdminMapWidget />
      </main>

      {/* ── Bottom Nav ── */}
      <nav
        className="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-xl border-t px-8 py-4 flex justify-between items-center z-40"
        style={{ borderColor: '#e0f4ff' }}
      >
        <button className="flex flex-col items-center gap-1.5" style={{ color: '#00AEEF' }}>
          <div className="p-2 rounded-xl" style={{ background: '#00AEEF15' }}>
            <LayoutDashboard className="w-5 h-5" />
          </div>
          <span className="text-[10px] font-black uppercase tracking-tighter">Dashboard</span>
        </button>
        <button className="flex flex-col items-center gap-1.5 text-gray-400 hover:text-[#00AEEF] transition-colors">
          <MapIcon className="w-5 h-5" />
          <span className="text-[10px] font-bold uppercase tracking-tighter">Mapa Total</span>
        </button>
        <button className="relative flex flex-col items-center gap-1.5 group">
          <div
            className="text-white p-4 rounded-2xl -mt-10 group-active:scale-90 transition-transform"
            style={{ background: 'linear-gradient(135deg, #1E3A5F, #00AEEF)', boxShadow: '0 8px 24px rgba(0,174,239,0.35)' }}
          >
            <MoreVertical className="w-5 h-5" />
          </div>
          <span className="text-[10px] font-black text-gray-600 uppercase tracking-tighter mt-1">Panel Admin</span>
        </button>
        <button className="flex flex-col items-center gap-1.5 text-gray-400 hover:text-[#6AB023] transition-colors">
          <PieChart className="w-5 h-5" />
          <span className="text-[10px] font-bold uppercase tracking-tighter">Reportes</span>
        </button>
        <button className="flex flex-col items-center gap-1.5 text-gray-400 hover:text-[#6AB023] transition-colors">
          <User className="w-5 h-5" />
          <span className="text-[10px] font-bold uppercase tracking-tighter">Usuarios</span>
        </button>
      </nav>
    </div>
  );
}
