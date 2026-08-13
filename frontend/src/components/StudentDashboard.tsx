'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Leaf, Car, Bike, Zap, AlertTriangle,
  User, MapPin, Navigation, LogOut, ShieldAlert, QrCode, Loader2,
} from 'lucide-react';
import StudentProfile from '@/components/StudentProfile';
import ParkingMap from '@/components/ParkingMap';
import QRAcceso from '@/components/QRAcceso';
import { useAuthStore } from '@/store/authStore';

type SpotStatus = 'available' | 'occupied' | 'vip';
type VehicleType = 'car' | 'moto' | 'scooter';

interface ParkingSpot {
  id: string;
  status: SpotStatus;
  type: VehicleType;
  label: string;
}

const INITIAL_SPOTS: ParkingSpot[] = [
  { id: 'slot_01', status: 'available',  type: 'car',     label: 'C-01' },
  { id: 'slot_02', status: 'available',  type: 'car',     label: 'C-02' },
  { id: 'slot_03', status: 'available',  type: 'car',     label: 'C-03' },
  { id: 'slot_04', status: 'available',  type: 'car',     label: 'C-04' },
  { id: 'slot_05', status: 'available',  type: 'moto',    label: 'M-01' },
  { id: 'slot_06', status: 'available',  type: 'moto',    label: 'M-02' },
  { id: 'slot_07', status: 'available',  type: 'moto',    label: 'M-03' },
  { id: 'slot_08', status: 'available',  type: 'scooter', label: 'B-01' },
  { id: 'slot_09', status: 'available',  type: 'scooter', label: 'B-02' },
  { id: 'slot_10', status: 'vip',        type: 'car',     label: 'V-01' },
];

const UCC = {
  green: '#6AB023',
  blue:  '#00AEEF',
  lime:  '#B5D334',
  navy:  '#1E3A5F',
  cyan:  '#00BCD4',
};

type ViewType = 'map' | 'qr' | 'reservations' | 'panic' | 'history' | 'profile' | 'exit';

const StudentDashboard = ({ user }: { user: any }) => {
  const logout = useAuthStore((state) => state.logout);
  // id_usuario viene del response de login guardado en el store
  const authUser = useAuthStore((s) => s.user);
  const idUsuario: number = authUser?.id_usuario ?? 0;

  const [spots, setSpots] = useState<ParkingSpot[]>(INITIAL_SPOTS);
  const [filter, setFilter] = useState<VehicleType | 'all'>('all');
  const [co2Saved, setCo2Saved] = useState(1240);
  const [view, setView] = useState<ViewType>('map');
  const [accesoActivo, setAccesoActivo] = useState<any>(null);
  const [loadingExit, setLoadingExit] = useState(false);
  const token = useAuthStore((s) => s.token);

  // Simulación de cambios en tiempo real (demo)
  useEffect(() => {
    const interval = setInterval(() => {
      setSpots(current =>
        current.map(spot => {
          if (Math.random() > 0.92) {
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

  // Cargar acceso activo del usuario
  useEffect(() => {
    if (!token || !idUsuario) return;
    
    const fetchAccesoActivo = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/accesos/usuario/${idUsuario}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (response.ok) {
          const accesos = await response.json();
          // Buscar el acceso sin hora de salida (activo)
          const activo = accesos.find((a: any) => !a.hora_salida);
          setAccesoActivo(activo || null);
        }
      } catch (error) {
        console.error('Error al cargar acceso activo:', error);
      }
    };

    fetchAccesoActivo();
    // Actualizar cada 30 segundos
    const interval = setInterval(fetchAccesoActivo, 30000);
    return () => clearInterval(interval);
  }, [token, idUsuario]);

  const handleRegistrarSalida = async () => {
    if (!accesoActivo || !token) return;
    
    setLoadingExit(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/accesos/${accesoActivo.id_acceso}/salida`,
        {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      if (response.ok) {
        setAccesoActivo(null);
        setView('map');
        alert('¡Salida registrada exitosamente! Espacio liberado.');
      } else {
        const error = await response.json();
        alert(error.detail || 'Error al registrar la salida');
      }
    } catch (error) {
      alert('Error al conectar con el servidor');
    } finally {
      setLoadingExit(false);
    }
  };

  const navigationItems: { id: ViewType; label: string; icon: React.ElementType; color?: string }[] = [
    { id: 'map',   label: 'MAPA',   icon: Navigation },
    { id: 'qr',    label: 'QR',     icon: QrCode },
    { id: 'panic', label: 'PÁNICO', icon: ShieldAlert, color: 'text-red-400' },
    { id: 'history', label: 'GREEN', icon: Leaf },
    { id: 'profile', label: 'PERFIL', icon: User },
  ];

  if (view === 'profile') return <StudentProfile user={user} onBack={() => setView('map')} onGoToQR={() => setView('qr')} />;

  return (
    <div className="min-h-screen pb-24 font-sans" style={{ background: '#F4FBFF' }}>

      {/* ── Header ── */}
      <header
        className="px-6 pt-8 pb-5"
        style={{ background: 'linear-gradient(135deg, #1E3A5F 0%, #00AEEF 100%)' }}
      >
        <div className="flex justify-between items-center mb-5">
          <motion.div
            whileTap={{ scale: 0.97 }}
            onClick={() => setView('profile')}
            className="flex items-center gap-3 cursor-pointer"
          >
            <div
              className="w-12 h-12 rounded-2xl flex items-center justify-center shadow"
              style={{ background: 'rgba(255,255,255,0.2)', border: '1.5px solid rgba(255,255,255,0.3)' }}
            >
              <User size={22} className="text-white" />
            </div>
            <div>
              <p className="text-xs text-white/60 font-medium uppercase tracking-wider">Bienvenido</p>
              <h1 className="text-lg font-black text-white leading-tight">
                {user?.nombre || 'Estudiante UCC'}
              </h1>
            </div>
          </motion.div>

          <div className="flex gap-2">
            {accesoActivo && (
              <motion.button
                whileTap={{ scale: 0.92 }}
                onClick={() => setView('exit')}
                className="px-3 h-10 rounded-xl flex items-center justify-center gap-1.5"
                style={{
                  background: view === 'exit' ? 'rgba(255,255,255,0.35)' : 'rgba(181,211,52,0.25)',
                  border: '1px solid rgba(181,211,52,0.4)',
                }}
                title="Registrar salida"
              >
                <MapPin size={16} className="text-[#B5D334]" />
                <span className="text-xs font-bold text-white">Salida</span>
              </motion.button>
            )}
            <motion.button
              whileTap={{ scale: 0.92 }}
              onClick={() => setView('qr')}
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{
                background: view === 'qr' ? 'rgba(255,255,255,0.35)' : 'rgba(255,255,255,0.15)',
                border: '1px solid rgba(255,255,255,0.3)',
              }}
              title="Acceso QR"
            >
              <QrCode size={18} className="text-white" />
            </motion.button>
            <motion.button
              whileTap={{ scale: 0.92 }}
              onClick={() => logout()}
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: 'rgba(255,80,80,0.2)', border: '1px solid rgba(255,80,80,0.3)' }}
            >
              <LogOut size={18} className="text-red-300" />
            </motion.button>
          </div>
        </div>

        {/* Widget CO2 */}
        <motion.div
          initial={{ y: 16, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="rounded-3xl p-5 relative overflow-hidden"
          style={{
            background: 'rgba(255,255,255,0.15)',
            border: '1px solid rgba(255,255,255,0.2)',
            backdropFilter: 'blur(12px)',
          }}
        >
          <div className="flex justify-between items-center">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Leaf size={14} className="text-[#B5D334]" />
                <span className="text-xs font-bold text-white/60 uppercase tracking-widest">
                  Green Impact UCC
                </span>
              </div>
              <div className="flex items-baseline gap-1">
                <motion.span
                  key={co2Saved}
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-3xl font-black text-white"
                >
                  {co2Saved}
                </motion.span>
                <span className="text-sm font-medium text-white/60">g de CO₂ ahorrados</span>
              </div>
            </div>
            <div className="relative w-12 h-12">
              <Leaf size={48} className="text-white/10 absolute inset-0" />
              <Leaf size={48} className="text-[#B5D334] fill-[#B5D334] absolute inset-0 opacity-80" />
            </div>
          </div>
          <div className="mt-3 flex items-center gap-2">
            <div className="h-1.5 flex-1 bg-white/20 rounded-full overflow-hidden">
              <motion.div
                className="h-full rounded-full"
                style={{ background: 'linear-gradient(90deg, #B5D334, #6AB023)' }}
                initial={{ width: 0 }}
                animate={{ width: `${Math.min((co2Saved / 2000) * 100, 100)}%` }}
              />
            </div>
            <span className="text-[9px] font-black text-white/50">META 2KG</span>
          </div>
        </motion.div>
      </header>

      {/* ── Contenido por vista ── */}

        {view === 'map' && (
          <motion.div
            key="map"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {/* Filtros */}
            <section className="px-5 py-4">
              <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-1">
                {[
                  { id: 'all',     label: 'Todos',     icon: MapPin },
                  { id: 'car',     label: 'Automóvil', icon: Car },
                  { id: 'moto',    label: 'Moto',      icon: Bike },
                  { id: 'scooter', label: 'Bicicleta', icon: Zap },
                ].map((type) => (
                  <motion.button
                    key={type.id}
                    whileTap={{ scale: 0.94 }}
                    onClick={() => setFilter(type.id as any)}
                    className="flex items-center gap-2 px-4 py-2.5 rounded-2xl whitespace-nowrap text-sm font-bold transition-all duration-200"
                    style={
                      filter === type.id
                        ? { background: UCC.navy, color: '#fff', boxShadow: '0 4px 14px rgba(30,58,95,0.25)' }
                        : { background: '#fff', color: '#94a3b8', border: '1.5px solid #e2e8f0' }
                    }
                  >
                    <type.icon size={16} />
                    {type.label}
                  </motion.button>
                ))}
              </div>
            </section>

            {/* Mapa IoT */}
            <section className="px-5 pb-4">
              <div className="flex justify-between items-center mb-3">
                <h2 className="text-base font-black" style={{ color: UCC.navy }}>
                  Estado en Tiempo Real
                </h2>
                <span
                  className="text-[10px] font-black px-3 py-1 rounded-full"
                  style={{ background: `${UCC.green}15`, color: UCC.green }}
                >
                  IoT ACTIVO
                </span>
              </div>
              <ParkingMap embedded />
            </section>
          </motion.div>
        )}

        {/* ── Vista QR ── */}
        {view === 'qr' && (
          <div className="px-5 py-6">
            <div className="mb-4">
              <h2 className="text-xl font-black" style={{ color: UCC.navy }}>Acceso QR</h2>
              <p className="text-sm text-gray-400 font-medium mt-0.5">
                Genera tu código para ingresar al parqueadero UCC.
              </p>
            </div>
            <QRAcceso idUsuario={idUsuario} />
          </div>
        )}

        {/* ── Vista Historial Green ── */}
        {view === 'history' && (
          <div className="px-5 py-6">
            <div
              className="rounded-[28px] p-6 border"
              style={{ background: `${UCC.green}10`, borderColor: `${UCC.green}30` }}
            >
              <h2 className="text-xl font-black mb-1" style={{ color: UCC.navy }}>Historial Green</h2>
              <p className="text-sm font-medium mb-6" style={{ color: UCC.green }}>
                Has ahorrado {co2Saved}g de CO₂ este mes.
              </p>
              <div className="space-y-3">
                {[1, 2, 3].map(i => (
                  <div
                    key={i}
                    className="bg-white p-4 rounded-2xl flex justify-between items-center shadow-sm border"
                    style={{ borderColor: '#e2e8f0' }}
                  >
                    <div>
                      <p className="text-sm font-bold" style={{ color: UCC.navy }}>Acceso #{1020 + i}</p>
                      <p className="text-[10px] font-bold text-gray-400 uppercase tracking-tight">
                        24 Mayo, 2026
                      </p>
                    </div>
                    <p className="text-sm font-black" style={{ color: UCC.green }}>+12g CO₂</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ── Vista Salida del Parqueadero ── */}
        {view === 'exit' && (
          <div className="px-5 py-6">
            {accesoActivo ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="rounded-[28px] p-6 border bg-white"
                style={{ borderColor: `${UCC.lime}40`, boxShadow: '0 8px 24px rgba(181,211,52,0.15)' }}
              >
                <div className="flex items-center gap-3 mb-4">
                  <div 
                    className="w-12 h-12 rounded-2xl flex items-center justify-center"
                    style={{ background: `${UCC.lime}20` }}
                  >
                    <MapPin size={24} style={{ color: UCC.green }} />
                  </div>
                  <div>
                    <h2 className="text-xl font-black" style={{ color: UCC.navy }}>Acceso Activo</h2>
                    <p className="text-xs text-gray-400 font-medium">Espacio ocupado</p>
                  </div>
                </div>

                {/* Información del acceso */}
                <div className="space-y-3 mb-6">
                  <div className="bg-gray-50 p-4 rounded-2xl">
                    <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">
                      Espacio Asignado
                    </p>
                    <p className="text-2xl font-black" style={{ color: UCC.navy }}>
                      {accesoActivo.espacio?.label || 'N/A'}
                    </p>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-2xl flex justify-between items-center">
                    <div>
                      <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">
                        Hora de entrada
                      </p>
                      <p className="text-base font-black" style={{ color: UCC.navy }}>
                        {new Date(accesoActivo.hora_entrada).toLocaleTimeString('es-CO', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">
                        ID Acceso
                      </p>
                      <p className="text-base font-black text-gray-600">
                        #{accesoActivo.id_acceso}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Botón de salida */}
                <motion.button
                  whileTap={{ scale: 0.97 }}
                  onClick={handleRegistrarSalida}
                  disabled={loadingExit}
                  className="w-full py-4 text-white font-black rounded-2xl flex items-center justify-center gap-2 transition-all disabled:opacity-60"
                  style={{
                    background: `linear-gradient(135deg, ${UCC.green}, ${UCC.blue})`,
                    boxShadow: '0 8px 24px rgba(0,174,239,0.30)',
                  }}
                >
                  {loadingExit ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      <LogOut size={20} />
                      Registrar Salida del Parqueadero
                    </>
                  )}
                </motion.button>

                <p className="text-xs text-gray-400 text-center mt-3">
                  Al salir, el espacio quedará disponible para otros estudiantes
                </p>
              </motion.div>
            ) : (
              <div className="rounded-[28px] p-8 border text-center" style={{ background: '#f8fafc', borderColor: '#e2e8f0' }}>
                <MapPin size={44} className="mx-auto text-gray-300 mb-3" />
                <h2 className="text-lg font-black text-gray-600 mb-2">Sin Acceso Activo</h2>
                <p className="text-sm text-gray-400 font-medium mb-6">
                  No tienes ningún vehículo en el parqueadero en este momento.
                </p>
                <button 
                  onClick={() => setView('qr')}
                  className="px-6 py-3 rounded-2xl font-bold text-sm"
                  style={{ background: `${UCC.blue}15`, color: UCC.blue }}
                >
                  Generar QR de Ingreso
                </button>
              </div>
            )}
          </div>
        )}

        {/* ── Vista Pánico ── */}
        {view === 'panic' && (
          <div className="px-5 py-6">
            <div className="bg-red-50 rounded-[28px] p-6 border border-red-100 text-center">
              <ShieldAlert size={44} className="mx-auto text-red-400 mb-3" />
              <h2 className="text-xl font-black text-red-800 mb-2">Botón de Pánico</h2>
              <p className="text-red-500 text-sm font-medium mb-6">
                Úsalo solo en emergencias reales dentro del campus UCC.
              </p>
              <button className="w-full bg-red-500 text-white py-5 rounded-2xl font-black text-lg shadow-xl animate-pulse">
                ACTIVAR ALERTA
              </button>
            </div>
          </div>
        )}

      {/* FAB alerta */}
      <div className="fixed bottom-24 right-5">
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setView('panic')}
          className="w-12 h-12 bg-white rounded-full shadow-xl flex items-center justify-center border border-red-100 text-red-400"
        >
          <AlertTriangle size={22} />
        </motion.button>
      </div>

      {/* ── Nav inferior ── */}
      <nav
        className="fixed bottom-0 left-0 right-0 px-4 py-3 flex justify-between items-center z-50 border-t"
        style={{
          background: 'rgba(255,255,255,0.92)',
          backdropFilter: 'blur(16px)',
          borderColor: '#e2e8f0',
        }}
      >
        {navigationItems.map((item) => {
          const isActive = view === item.id;
          return (
            <motion.button
              key={item.id}
              whileTap={{ scale: 0.88 }}
              onClick={() => setView(item.id)}
              className="flex flex-col items-center gap-1 transition-all"
              style={{
                color: isActive ? UCC.blue : item.color ? '#f87171' : '#94a3b8',
              }}
            >
              <div
                className="p-2 rounded-2xl transition-all"
                style={isActive ? { background: `${UCC.blue}15` } : { background: 'transparent' }}
              >
                <item.icon size={21} strokeWidth={isActive ? 2.5 : 1.8} />
              </div>
              <span
                className={`text-[9px] font-black tracking-tight ${isActive ? 'opacity-100' : 'opacity-50'}`}
              >
                {item.label}
              </span>
            </motion.button>
          );
        })}
      </nav>
    </div>
  );
};

export default StudentDashboard;
