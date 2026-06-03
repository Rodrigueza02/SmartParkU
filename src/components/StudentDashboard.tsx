'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Leaf, 
  Car, 
  Bike, 
  Zap, 
  AlertTriangle, 
  ChevronRight, 
  User,
  MapPin,
  Clock,
  Navigation,
  LogOut,
  Calendar,
  ShieldAlert
} from 'lucide-react';
import UCCSwitch from '@/components/UCCSwitch';
import StudentProfile from '@/components/StudentProfile';
import ParkingMap from '@/components/ParkingMap';
import { useAuthStore } from '@/store/authStore';

// --- Tipos y Mock Data ---
type SpotStatus = 'available' | 'occupied' | 'vip';
type VehicleType = 'car' | 'moto' | 'scooter';

interface ParkingSpot {
  id: string;
  status: SpotStatus;
  type: VehicleType;
  label: string;
}

const INITIAL_SPOTS: ParkingSpot[] = [
  { id: 'C-01', status: 'available', type: 'car', label: 'C-01' },
  { id: 'C-02', status: 'available', type: 'car', label: 'C-02' },
  { id: 'C-03', status: 'available', type: 'car', label: 'C-03' },
  { id: 'C-04', status: 'available', type: 'car', label: 'C-04' },
  { id: 'M-01', status: 'available', type: 'moto', label: 'M-01' },
  { id: 'M-02', status: 'available', type: 'moto', label: 'M-02' },
  { id: 'M-03', status: 'available', type: 'moto', label: 'M-03' },
  { id: 'B-01', status: 'available', type: 'scooter', label: 'B-01' },
  { id: 'B-02', status: 'available', type: 'scooter', label: 'B-02' },
  { id: 'V-01', status: 'vip', type: 'car', label: 'V-01' },
];

const StudentDashboard = ({ user }: { user: any }) => {
  const logout = useAuthStore((state) => state.logout);
  const [spots, setSpots] = useState<ParkingSpot[]>(INITIAL_SPOTS);
  const [filter, setFilter] = useState<VehicleType | 'all'>('all');
  const [co2Saved, setCo2Saved] = useState(1240); // Gramos de CO2
  const [view, setView] = useState<'map' | 'profile' | 'reservations' | 'panic' | 'history'>('map');

  // Simulación de tiempo real IoT
  useEffect(() => {
    const interval = setInterval(() => {
      setSpots(currentSpots => 
        currentSpots.map(spot => {
          if (Math.random() > 0.92) { // 8% de probabilidad de cambio
            const newStatus: SpotStatus = Math.random() > 0.5 ? 'available' : 'occupied';
            return { ...spot, status: spot.status === 'vip' ? 'vip' : newStatus };
          }
          return spot;
        })
      );
      setCo2Saved(prev => prev + Math.floor(Math.random() * 2));
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const filteredSpots = spots.filter(s => filter === 'all' || s.type === filter);

  const navigationItems = [
    { id: 'map', label: 'MAPA IOT', icon: Navigation },
    { id: 'reservations', label: 'RESERVAS', icon: Calendar },
    { id: 'panic', label: 'PÁNICO', icon: ShieldAlert, color: 'text-red-500' },
    { id: 'history', label: 'GREEN', icon: Leaf },
    { id: 'profile', label: 'PERFIL', icon: User },
  ];

  if (view === 'profile') {
    return <StudentProfile user={user} onBack={() => setView('map')} />;
  }

  return (
    <div className="min-h-screen bg-[#FDFDFD] pb-24 font-sans text-slate-800">
      {/* 1. Header Sostenible & Perfil */}
      <header className="px-6 pt-8 pb-4">
        <div className="flex justify-between items-center mb-6">
          <motion.div 
            whileTap={{ scale: 0.98 }}
            onClick={() => setView('profile')}
            className="flex items-center gap-3 cursor-pointer group"
          >
            <div className="w-12 h-12 rounded-2xl bg-[#A3E4D7] flex items-center justify-center text-white shadow-sm group-hover:shadow-md transition-all">
              <User size={24} />
            </div>
            <div>
              <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Bienvenido de nuevo</p>
              <h1 className="text-xl font-bold group-hover:text-teal-600 transition-colors">{user?.nombre || 'Estudiante UCC'}</h1>
            </div>
          </motion.div>
          <div className="flex gap-2">
            <motion.button 
              whileTap={{ scale: 0.95 }}
              className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center border border-slate-100"
            >
              <Zap size={20} className="text-yellow-500 fill-yellow-500" />
            </motion.button>
            <motion.button 
              whileTap={{ scale: 0.95 }}
              onClick={() => logout()}
              className="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center border border-red-100 text-red-500"
              title="Cerrar sesión"
            >
              <LogOut size={20} />
            </motion.button>
          </div>
        </div>

        {/* Widget Green Impact (RF11) */}
        <motion.div 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="bg-white rounded-3xl p-5 shadow-xl shadow-slate-200/40 border border-[#A3E4D7]/30 relative overflow-hidden"
        >
          <div className="flex justify-between items-center relative z-10">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Leaf size={16} className="text-[#A3E4D7]" />
                <span className="text-xs font-bold text-slate-400 uppercase tracking-tighter">Green Impact UCC</span>
              </div>
              <div className="flex items-baseline gap-1">
                <motion.span 
                  key={co2Saved}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-3xl font-black text-slate-800"
                >
                  {co2Saved}
                </motion.span>
                <span className="text-sm font-medium text-slate-500">g de CO₂ ahorrados</span>
              </div>
            </div>
            
            {/* Icono de hoja que se llena gradualmente */}
            <div className="relative w-14 h-14">
              <Leaf size={56} className="text-slate-100 absolute inset-0" />
              <motion.div 
                className="absolute inset-0 overflow-hidden"
                initial={{ height: "0%" }}
                animate={{ height: `${Math.min((co2Saved / 2000) * 100, 100)}%` }}
                style={{ bottom: 0, top: 'auto' }}
              >
                <Leaf size={56} className="text-[#A3E4D7] fill-[#A3E4D7]" />
              </motion.div>
            </div>
          </div>
          <div className="mt-4 flex items-center gap-2">
            <div className="h-1.5 flex-1 bg-slate-50 rounded-full overflow-hidden">
              <motion.div 
                className="h-full bg-gradient-to-r from-[#A3E4D7] to-teal-400"
                initial={{ width: 0 }}
                animate={{ width: `${Math.min((co2Saved / 2000) * 100, 100)}%` }}
              />
            </div>
            <span className="text-[10px] font-bold text-slate-400">META 2KG</span>
          </div>
        </motion.div>
      </header>

      {view === 'map' && (
        <>
          {/* 2. Filtro de Vehículos (RF05) */}
          <section className="px-6 py-4">
            <div className="flex gap-3 overflow-x-auto scrollbar-hide pb-2">
              {[
                { id: 'all', label: 'Todos', icon: MapPin },
                { id: 'car', label: 'Automóvil', icon: Car },
                { id: 'moto', label: 'Moto', icon: Bike },
                { id: 'scooter', label: 'Scooter', icon: Zap },
              ].map((type) => (
                <motion.button
                  key={type.id}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setFilter(type.id as any)}
                  className={`flex items-center gap-2 px-5 py-3 rounded-2xl whitespace-nowrap transition-all duration-300 ${
                    filter === type.id 
                      ? 'bg-slate-800 text-white shadow-lg' 
                      : 'bg-white text-slate-500 border border-slate-100 shadow-sm'
                  }`}
                >
                  <type.icon size={18} />
                  <span className="text-sm font-semibold">{type.label}</span>
                </motion.button>
              ))}
            </div>
          </section>

          {/* 3. Interactive Parking Map (RF05, RF06, RF07) */}
          <section className="px-6 py-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold">Estado en Tiempo Real</h2>
            </div>

            <ParkingMap embedded />
          </section>
        </>
      )}

      {view === 'history' && (
        <section className="px-6 py-8">
          <div className="bg-emerald-50 rounded-[32px] p-8 border border-emerald-100">
            <h2 className="text-2xl font-black text-emerald-800 mb-4">Historial Green</h2>
            <p className="text-emerald-600 font-medium">Has ahorrado {co2Saved}g de CO₂ este mes.</p>
            <div className="mt-8 space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="bg-white p-4 rounded-2xl flex justify-between items-center shadow-sm">
                  <div>
                    <p className="text-sm font-bold text-slate-800">Reserva #{1020 + i}</p>
                    <p className="text-[10px] text-slate-400 font-bold uppercase tracking-tighter">24 Mayo, 2026</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-black text-emerald-500">+12g CO₂</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {view === 'reservations' && (
        <section className="px-6 py-8">
          <div className="bg-white rounded-[32px] p-8 border border-slate-100 shadow-xl shadow-slate-200/40">
            <h2 className="text-2xl font-black text-slate-800 mb-2">Mis Reservas</h2>
            <p className="text-slate-400 text-sm font-medium mb-8">No tienes reservas activas en este momento.</p>
            <motion.button 
              whileTap={{ scale: 0.95 }}
              onClick={() => setView('map')}
              className="w-full bg-[#A3E4D7] text-white py-4 rounded-2xl font-bold"
            >
              Explorar Mapa
            </motion.button>
          </div>
        </section>
      )}

      {view === 'panic' && (
        <section className="px-6 py-8">
          <div className="bg-red-50 rounded-[32px] p-8 border border-red-100 text-center">
            <ShieldAlert size={48} className="mx-auto text-red-400 mb-4" />
            <h2 className="text-2xl font-black text-red-800 mb-2">Botón de Pánico</h2>
            <p className="text-red-600 text-sm font-medium mb-8">Usa este botón solo en caso de emergencia real dentro del campus.</p>
            <button className="w-full bg-red-500 text-white py-5 rounded-2xl font-black text-lg shadow-xl shadow-red-200 animate-pulse">
              ACTIVAR ALERTA
            </button>
          </div>
        </section>
      )}

      {/* 4. Botón de Emergencia Sutil (RF12) */}
      <div className="fixed bottom-24 right-6">
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="w-14 h-14 bg-white rounded-full shadow-2xl flex items-center justify-center border border-red-50/50 text-red-400"
        >
          <AlertTriangle size={24} />
        </motion.button>
      </div>

      {/* Navegación Inferior Estilo App Premium */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white/80 backdrop-blur-xl border-t border-slate-50 px-4 py-4 flex justify-between items-center z-50 shadow-[0_-10px_30px_rgba(0,0,0,0.02)]">
        {navigationItems.map((item) => (
          <motion.button
            key={item.id}
            whileTap={{ scale: 0.9 }}
            onClick={() => setView(item.id as any)}
            className={`flex flex-col items-center gap-1.5 transition-all ${
              view === item.id 
                ? 'text-[#70C1B3]' 
                : item.color || 'text-slate-300'
            }`}
          >
            <div className={`p-2 rounded-2xl transition-colors ${
              view === item.id ? 'bg-[#A3E4D7]/10' : 'bg-transparent'
            }`}>
              <item.icon size={22} strokeWidth={view === item.id ? 2.5 : 2} />
            </div>
            <span className={`text-[9px] font-black tracking-tighter ${
              view === item.id ? 'opacity-100' : 'opacity-60'
            }`}>
              {item.label}
            </span>
          </motion.button>
        ))}
      </nav>
    </div>
  );
};

export default StudentDashboard;
