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
  MoreVertical,
  Car,
  Bike,
  Zap,
  LogOut,
  Loader2,
  Play,
  Square
} from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { useRouter } from "next/navigation";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { useParkingStore, ParkingSlot } from "@/store/parkingStore";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// --- Tipos ---
type SlotStatus = "libre" | "ocupado";
type VehicleType = "carro" | "moto" | "bicicleta" | "vip";

interface Alerta {
  id: number;
  tipo: string;
  mensaje: string;
  tiempo: string;
  nivel: "Critical" | "Warning";
}

// --- Componentes ---

const AdminHeader = () => {
  const logout = useAuthStore((state) => state.logout);
  const user = useAuthStore((state) => state.user);
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
            Hola, <span style={{ color: '#00AEEF' }}>{user?.nombre || 'Administrador'}</span>
          </h1>
          <span className="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-0.5 rounded-md">
            {user?.rol || 'Administrador'}
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

const UsageAnalysisWidget = ({ slots }: { slots: ParkingSlot[] }) => {
  // Calcular estadísticas reales basadas en los slots
  const totalCarros = slots.filter(s => s.tipo === 'carro' || s.tipo === 'vip').length;
  const totalMotos = slots.filter(s => s.tipo === 'moto').length;
  const totalBicis = slots.filter(s => s.tipo === 'bicicleta').length;
  
  const ocupadosCarros = slots.filter(s => (s.tipo === 'carro' || s.tipo === 'vip') && s.status === 'ocupado').length;
  const ocupadosMotos = slots.filter(s => s.tipo === 'moto' && s.status === 'ocupado').length;
  const ocupadosBicis = slots.filter(s => s.tipo === 'bicicleta' && s.status === 'ocupado').length;

  const total = slots.length;
  const totalOcupados = slots.filter(s => s.status === 'ocupado').length;
  const porcentajeOcupacion = total > 0 ? Math.round((totalOcupados / total) * 100) : 0;

  const USAGE_DATA = [
    { label: "Autos",      value: totalCarros > 0 ? Math.round((ocupadosCarros / totalCarros) * 100) : 0, color: "#6AB023", icon: Car },
    { label: "Motos",      value: totalMotos > 0 ? Math.round((ocupadosMotos / totalMotos) * 100) : 0, color: "#00AEEF", icon: Bike },
    { label: "Bicicletas", value: totalBicis > 0 ? Math.round((ocupadosBicis / totalBicis) * 100) : 0, color: "#B5D334", icon: Zap },
  ];

  let cumulativePercent = 0;

  return (
    <motion.section 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white rounded-[2.5rem] p-6 border border-lightGray shadow-sm"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="font-black text-gray-700 flex items-center gap-2">
          <PieChart className="w-5 h-5" style={{ color: "#6AB023" }} />
          Análisis de Uso
        </h2>
        <span className="text-[10px] font-bold px-3 py-1.5 rounded-full" style={{ background: '#6AB02315', color: '#6AB023' }}>
          EN VIVO
        </span>
      </div>

      <div className="flex flex-col md:flex-row items-center gap-8">
        {/* Gráfico Circular Simplificado */}
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
                  cx="16"
                  cy="16"
                  r="12"
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
            <span className="text-2xl font-black text-gray-800">{porcentajeOcupacion}%</span>
            <span className="text-[8px] font-bold text-gray-400 uppercase">Ocupación</span>
          </div>
        </div>

        <div className="flex-1 grid grid-cols-1 gap-3 w-full">
          {USAGE_DATA.map((item, i) => (
            <div key={i} className="flex items-center justify-between p-3 rounded-2xl bg-gray-50 border border-gray-100">
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

const AlertsWidget = ({ alertas }: { alertas: Alerta[] }) => (
  <section className="flex flex-col gap-4">
    <div className="flex items-center justify-between">
      <h2 className="font-black text-gray-700 flex items-center gap-2">
        <ShieldAlert className="w-5 h-5 text-red-400" />
        Alertas del Sistema
      </h2>
      {alertas.length > 0 && (
        <span className="text-[10px] font-bold px-2 py-1 bg-red-50 text-red-500 rounded-lg animate-pulse">
          {alertas.length} ACTIVAS
        </span>
      )}
    </div>
    
    <div className="flex flex-col gap-3">
      {alertas.length === 0 ? (
        <div className="bg-green-50 border border-green-100 rounded-2xl p-6 text-center">
          <ShieldAlert className="w-10 h-10 mx-auto text-green-400 mb-2" />
          <p className="text-sm font-bold text-green-700">Sin alertas activas</p>
          <p className="text-xs text-green-500 mt-1">Todo funcionando correctamente</p>
        </div>
      ) : (
        alertas.map((alert) => (
          <motion.div 
            key={alert.id}
            whileHover={{ x: 5 }}
            className={cn(
              "p-4 rounded-[1.5rem] border flex items-start gap-4 transition-all",
              alert.nivel === 'Critical' ? "bg-red-50 border-red-100" : "bg-orange-50 border-orange-100"
            )}
          >
            <div className={cn(
              "p-2.5 rounded-xl mt-1",
              alert.nivel === 'Critical' ? "bg-red-500 text-white" : "bg-orange-400 text-white"
            )}>
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <div className="flex justify-between items-center mb-1">
                <span className={cn(
                  "text-[10px] font-black uppercase",
                  alert.nivel === 'Critical' ? "text-red-500" : "text-orange-500"
                )}>{alert.tipo}</span>
                <span className="text-[10px] font-medium text-gray-400 flex items-center gap-1">
                  <Clock className="w-3 h-3" /> {alert.tiempo}
                </span>
              </div>
              <p className="text-sm font-bold text-gray-800 leading-tight">{alert.mensaje}</p>
            </div>
            <MoreVertical className="w-4 h-4 text-gray-400" />
          </motion.div>
        ))
      )}
    </div>
  </section>
);

const AdminMapWidget = ({ slots, onControlServo }: { slots: ParkingSlot[]; onControlServo: (accion: 'abrir' | 'cerrar') => void }) => {
  const [selectedSlot, setSelectedSlot] = useState<ParkingSlot | null>(null);
  const [loadingServo, setLoadingServo] = useState(false);

  const handleControlServo = async (accion: 'abrir' | 'cerrar') => {
    setLoadingServo(true);
    try {
      await onControlServo(accion);
    } finally {
      setLoadingServo(false);
    }
  };

  return (
    <section className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="font-black text-gray-700 flex items-center gap-2">
          <MapIcon className="w-5 h-5" style={{ color: "#6AB023" }} />
          Mapa de Gestión de Cupos
        </h2>
        <div className="flex gap-2">
          <div className="flex items-center gap-1 text-[10px] font-bold text-gray-400">
            <div className="w-2 h-2 rounded-full bg-green-500" /> Libre
          </div>
          <div className="flex items-center gap-1 text-[10px] font-bold text-gray-400">
            <div className="w-2 h-2 rounded-full bg-red-500" /> Ocupado
          </div>
        </div>
      </div>

      {/* Control de talanquera */}
      <div className="bg-white rounded-[2.5rem] p-6 shadow-sm border border-gray-100">
        <h3 className="text-sm font-black text-gray-700 mb-4 flex items-center gap-2">
          <ShieldAlert className="w-4 h-4" style={{ color: "#00AEEF" }} />
          Control de Talanquera
        </h3>
        <div className="flex gap-3">
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={() => handleControlServo('abrir')}
            disabled={loadingServo}
            className="flex-1 py-3 rounded-2xl font-bold text-sm flex items-center justify-center gap-2 transition-all disabled:opacity-60"
            style={{ background: '#6AB02315', color: '#6AB023', border: '2px solid #6AB02330' }}
          >
            {loadingServo ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            Abrir
          </motion.button>
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={() => handleControlServo('cerrar')}
            disabled={loadingServo}
            className="flex-1 py-3 rounded-2xl font-bold text-sm flex items-center justify-center gap-2 transition-all disabled:opacity-60"
            style={{ background: '#ef444415', color: '#ef4444', border: '2px solid #ef444430' }}
          >
            {loadingServo ? <Loader2 className="w-4 h-4 animate-spin" /> : <Square className="w-4 h-4" />}
            Cerrar
          </motion.button>
        </div>
      </div>

      {/* Mapa de slots */}
      <div className="bg-white rounded-[2.5rem] p-8 shadow-sm border border-gray-100 grid grid-cols-2 sm:grid-cols-3 gap-6">
        {slots.map((slot) => (
          <motion.button
            key={slot.slot}
            whileTap={{ scale: 0.95 }}
            onClick={() => setSelectedSlot(slot)}
            className={cn(
              "h-24 rounded-2xl flex flex-col items-center justify-center gap-2 border-2 transition-all relative overflow-hidden",
              slot.status === 'ocupado' && "bg-red-50 border-red-100 text-red-400",
              slot.status === 'libre' && "bg-green-50 border-green-200 text-green-600"
            )}
          >
            <span className="text-[10px] font-black tracking-wider uppercase opacity-60">#{slot.label}</span>
            
            <div className={cn(
              "w-10 h-5 rounded-md",
              slot.status === 'ocupado' && "bg-red-200",
              slot.status === 'libre' && "bg-green-400"
            )} />
            
            <span className="text-[10px] font-black uppercase tracking-widest">{slot.tipo}</span>
          </motion.button>
        ))}
      </div>

      <AnimatePresence>
        {selectedSlot && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="bg-white p-6 rounded-[2rem] border-2 shadow-xl"
            style={{ borderColor: '#e0f4ff' }}
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-black text-gray-800">Cajón {selectedSlot.label}</h3>
                <p className="text-xs text-gray-500">
                  Estado: <span className="font-bold uppercase">{selectedSlot.status}</span>
                </p>
                {selectedSlot.distancia_cm && (
                  <p className="text-xs text-gray-400 mt-1">
                    Sensor: {selectedSlot.distancia_cm.toFixed(1)} cm
                  </p>
                )}
              </div>
              <button 
                onClick={() => setSelectedSlot(null)}
                className="text-gray-400 hover:text-gray-600 font-bold"
              >✕</button>
            </div>

            <div className={cn(
              "p-4 rounded-xl flex items-center gap-3",
              selectedSlot.status === 'ocupado' ? "bg-red-50 text-red-500" : "bg-green-50 text-green-600"
            )}>
              {selectedSlot.status === 'ocupado' ? (
                <>
                  <ShieldAlert className="w-5 h-5" />
                  <p className="text-xs font-bold">Vehículo detectado en este espacio</p>
                </>
              ) : (
                <>
                  <ShieldAlert className="w-5 h-5" />
                  <p className="text-xs font-bold">Espacio disponible para asignar</p>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
};

export default function AdminDashboard() {
  const { token, user } = useAuthStore();
  const { slots: slotsObj, wsStatus, controlServo, connect, disconnect } = useParkingStore();
  const isConnected = wsStatus === 'connected';
  const router = useRouter();
  const [alertas, setAlertas] = useState<Alerta[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Convertir objeto de slots a array
  const slots: ParkingSlot[] = Object.values(slotsObj || {});

  // Protección de ruta
  useEffect(() => {
    if (!token || !user) {
      router.push("/");
      return;
    }
    if (user.rol !== "SuperAdmin" && user.rol !== "Administrativo") {
      router.push("/");
    }
  }, [token, user, router]);

  // Conectar WebSocket al montar el componente
  useEffect(() => {
    connect();
    return () => { disconnect(); };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Cargar datos iniciales
  useEffect(() => {
    if (!token) return;

    const loadInitialData = async () => {
      setLoading(true);
      try {
        // Generar alertas basadas en el estado de los slots
        const alertasGeneradas: Alerta[] = [];
        
        const slotsOcupados = slots.filter(s => s.status === 'ocupado');
        if (slotsOcupados.length >= slots.length * 0.9) {
          alertasGeneradas.push({
            id: 1,
            tipo: "Capacidad",
            mensaje: "Parqueadero cerca de su capacidad máxima (90%)",
            tiempo: "Hace 2 min",
            nivel: "Warning"
          });
        }

        setAlertas(alertasGeneradas);
      } catch (error) {
        console.error('Error al cargar datos:', error);
      } finally {
        setLoading(false);
      }
    };

    loadInitialData();
  }, [token, slots]);

  if (!token || !user) return null;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#F4FBFF' }}>
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-10 h-10 animate-spin" style={{ color: '#00AEEF' }} />
          <p className="text-sm font-bold text-gray-500">Cargando panel administrativo...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-24 font-sans" style={{ background: '#F4FBFF', color: '#1E3A5F' }}>
      <AdminHeader />

      <main className="px-6 py-8 flex flex-col gap-10 max-w-4xl mx-auto">
        
        {/* Estado de conexión WebSocket */}
        <div className="flex items-center justify-between bg-white rounded-2xl p-4 border border-gray-100">
          <div className="flex items-center gap-3">
            <div className={cn(
              "w-3 h-3 rounded-full",
              isConnected ? "bg-green-500 animate-pulse" : "bg-red-500"
            )} />
            <span className="text-sm font-bold text-gray-700">
              {isConnected ? 'Tiempo real activo' : 'Desconectado'}
            </span>
          </div>
          <span className="text-xs text-gray-400 font-medium">
            {slots.length} espacios monitoreados
          </span>
        </div>

        {/* Análisis de Uso */}
        <UsageAnalysisWidget slots={slots} />

        {/* Alertas del Sistema */}
        <AlertsWidget alertas={alertas} />

        {/* Mapa de Gestión */}
        <AdminMapWidget slots={slots} onControlServo={controlServo} />

      </main>

      {/* Bottom Nav */}
      <nav
        className="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-xl border-t px-8 py-4 flex justify-between items-center z-40"
        style={{ borderColor: '#e0f4ff' }}
      >
        <button 
          onClick={() => router.push('/admin/dashboard')}
          className="flex flex-col items-center gap-1.5" style={{ color: '#00AEEF' }}>
          <div className="p-2 rounded-xl" style={{ background: '#00AEEF15' }}>
            <LayoutDashboard className="w-5 h-5" />
          </div>
          <span className="text-[10px] font-black uppercase tracking-tighter">Dashboard</span>
        </button>
        <button 
          onClick={() => router.push('/parking-map')}
          className="flex flex-col items-center gap-1.5 text-gray-400 hover:text-[#00AEEF] transition-colors">
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
        <button 
          onClick={() => router.push('/comparison')}
          className="flex flex-col items-center gap-1.5 text-gray-400 hover:text-[#6AB023] transition-colors">
          <PieChart className="w-5 h-5" />
          <span className="text-[10px] font-bold uppercase tracking-tighter">Reportes</span>
        </button>
        <button 
          onClick={() => router.push('/dashboard')}
          className="flex flex-col items-center gap-1.5 text-gray-400 hover:text-[#6AB023] transition-colors">
          <User className="w-5 h-5" />
          <span className="text-[10px] font-bold uppercase tracking-tighter">Usuarios</span>
        </button>
      </nav>
    </div>
  );
}
