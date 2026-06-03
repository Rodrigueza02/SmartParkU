"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Car, Bike, Info, X, MapPin, Wifi, WifiOff, Loader2 } from "lucide-react";
import { useParkingStore, ParkingSlot, VehicleType } from "@/store/parkingStore";

type SlotType = "carro" | "moto" | "bicicleta";

interface ParkingMapProps {
  embedded?: boolean;
}

const ParkingMap = ({ embedded = false }: ParkingMapProps) => {
  const {
    slots,
    totalLibre,
    totalOcupado,
    wsStatus,
    timestamp,
    connect,
    disconnect,
  } = useParkingStore();

  const [activeFilter, setActiveFilter] = useState<SlotType | "todos">("todos");
  const [selectedSlot, setSelectedSlot] = useState<ParkingSlot | null>(null);

  // Conectar al WebSocket al montar — delay para evitar el doble-mount de React 18 StrictMode
  useEffect(() => {
    let cancelled = false;
    const timer = setTimeout(() => {
      if (!cancelled) connect();
    }, 100);
    return () => {
      cancelled = true;
      clearTimeout(timer);
      disconnect();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ─── Convertir el Record<string, ParkingSlot> a arrays por tipo ──────────────
  const allSlots = Object.values(slots);

  // Si no hay datos del backend todavía, usar layout estático de UCC
  const carSlots     = allSlots.filter(s => s.tipo === "carro");
  const motoSlots    = allSlots.filter(s => s.tipo === "moto");
  const bikeSlots    = allSlots.filter(s => s.tipo === "bicicleta");

  // ─── Componentes internos ─────────────────────────────────────────────────
  const FilterChip = ({ type, label, icon: Icon }: { type: SlotType | "todos"; label: string; icon: React.ElementType }) => (
    <button
      onClick={() => setActiveFilter(type)}
      className="flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-bold transition-all duration-300"
      style={
        activeFilter === type
          ? { background: '#1E3A5F', color: '#fff', boxShadow: '0 4px 14px rgba(30,58,95,0.25)' }
          : { background: '#fff', color: '#94a3b8', border: '1.5px solid #e2e8f0' }
      }
    >
      <Icon size={16} />
      {label}
    </button>
  );

  const SlotBox = ({ slot }: { slot: ParkingSlot }) => {
    const isFiltered = activeFilter !== "todos" && activeFilter !== slot.tipo;
    const isFree     = slot.status === "libre";

    return (
      <motion.div
        layout
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: isFiltered ? 0.15 : 1, scale: 1, transition: { duration: 0.4 } }}
        whileTap={isFree ? { scale: 0.93 } : {}}
        onClick={() => isFree && setSelectedSlot(slot)}
        className={`relative cursor-pointer rounded-lg border-2 border-white shadow-sm flex flex-col items-center justify-center transition-colors duration-500
          ${slot.tipo === "carro" ? "h-14 w-10" : "h-8 w-7"}
        `}
        style={{ background: isFree ? '#6AB023' : '#ef4444' }}
        title={`Cajón ${slot.slot} — ${slot.status}${slot.distancia_cm ? ` (${slot.distancia_cm} cm)` : ""}`}
      >
        <span className="text-[8px] font-bold text-white opacity-80">{slot.slot}</span>
        {!isFree && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="absolute inset-0 flex items-center justify-center bg-black/10 rounded-lg"
          >
            {slot.tipo === "carro" ? <Car size={12} className="text-white/60" /> : <Bike size={10} className="text-white/60" />}
          </motion.div>
        )}
      </motion.div>
    );
  };

  // ─── Badge de estado de conexión ──────────────────────────────────────────
  const ConnectionBadge = () => {
    const configs = {
      connected:    { icon: Wifi,    color: "text-emerald-500", label: "En vivo" },
      connecting:   { icon: Loader2, color: "text-amber-500 animate-spin", label: "Conectando..." },
      error:        { icon: WifiOff, color: "text-red-400",     label: "Sin señal" },
      disconnected: { icon: WifiOff, color: "text-slate-300",   label: "Desconectado" },
    };
    const { icon: Icon, color, label } = configs[wsStatus];
    return (
      <div className={`flex items-center gap-1.5 text-[10px] font-bold ${color}`}>
        <Icon size={12} />
        {label}
      </div>
    );
  };

  return (
    <div className={`${embedded ? "" : "min-h-screen bg-lightGray p-6"} font-sans select-none`}>
      {/* Header (solo si no está embebido) */}
      {!embedded && (
        <div className="max-w-md mx-auto mb-8">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Mapa UCC Pasto</h1>
              <p className="text-gray-400 text-sm">Disponibilidad en tiempo real</p>
            </div>
            <ConnectionBadge />
          </div>
          <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
            <FilterChip type="todos"      label="Todos"       icon={MapPin} />
            <FilterChip type="carro"      label="Carros"      icon={Car} />
            <FilterChip type="moto"       label="Motos"       icon={Bike} />
            <FilterChip type="bicicleta"  label="Bicicletas"  icon={Bike} />
          </div>
        </div>
      )}

      {/* Mapa */}
      <div
        className={`${
          embedded ? "w-full" : "max-w-4xl mx-auto"
        } bg-white rounded-[32px] p-6 shadow-xl border border-gray-100 overflow-hidden`}
      >
        <div className="flex justify-between items-center mb-6">
          <div className="flex gap-4">
            <div className="text-center">
              <p className="text-2xl font-black" style={{ color: '#6AB023' }}>{totalLibre}</p>
              <p className="text-[9px] font-bold text-gray-400 uppercase tracking-widest">Libres</p>
            </div>
            <div className="w-px bg-gray-100" />
            <div className="text-center">
              <p className="text-2xl font-black text-red-500">{totalOcupado}</p>
              <p className="text-[9px] font-bold text-gray-400 uppercase tracking-widest">Ocupados</p>
            </div>
          </div>
          <ConnectionBadge />
        </div>

        {/* Si no hay datos todavía */}
        {allSlots.length === 0 && (
          <div className="flex flex-col items-center justify-center py-12 gap-3 text-slate-300">
            <Loader2 size={32} className="animate-spin" />
            <p className="text-sm font-medium">Esperando datos del parqueadero...</p>
            <p className="text-[10px]">
              {wsStatus === "error"
                ? "Verifica que el backend esté corriendo en localhost:8000"
                : "Conectando con los sensores IoT"}
            </p>
          </div>
        )}

        {allSlots.length > 0 && (
          <>
            {/* Zona motos + bicicletas */}
            <div className="flex justify-between mb-8 gap-4 max-w-2xl mx-auto">
              <div className="flex-1">
                <h3 className="text-[9px] uppercase tracking-wider text-gray-400 mb-2 font-bold">
                  Motos ({motoSlots.filter(s => s.status === "libre").length} libres)
                </h3>
                <div className="grid grid-cols-5 gap-1.5">
                  {motoSlots.map(s => <SlotBox key={s.slot} slot={s} />)}
                </div>
              </div>
              <div className="flex-1">
                <h3 className="text-[9px] uppercase tracking-wider text-gray-400 mb-2 font-bold text-right">
                  Bicicletas ({bikeSlots.filter(s => s.status === "libre").length} libres)
                </h3>
                <div className="grid grid-cols-4 gap-1.5 justify-end">
                  {bikeSlots.map(s => <SlotBox key={s.slot} slot={s} />)}
                </div>
              </div>
            </div>

            {/* Zona carros (2 filas) */}
            <div className="relative max-w-2xl mx-auto">
              <div className="absolute left-1/2 top-0 bottom-0 w-8 -translate-x-1/2 bg-gray-50/50 flex items-center justify-center">
                <div className="h-full w-px border-l-2 border-dashed border-gray-200" />
              </div>
              <div className="flex justify-between gap-10 px-1">
                <div className="flex flex-col gap-2">
                  {carSlots.slice(0, Math.ceil(carSlots.length / 2)).map(s => (
                    <SlotBox key={s.slot} slot={s} />
                  ))}
                </div>
                <div className="flex flex-col gap-2">
                  {carSlots.slice(Math.ceil(carSlots.length / 2)).map(s => (
                    <SlotBox key={s.slot} slot={s} />
                  ))}
                </div>
              </div>
              <div className="absolute -bottom-4 right-0 flex flex-col items-end gap-1 opacity-20">
                <div className="flex items-center gap-1">
                  <span className="text-[7px] font-bold tracking-widest text-gray-400">
                    ENTRADA / SALIDA
                  </span>
                  <div className="w-3 h-3 border-t-2 border-l-2 border-gray-400 rotate-[135deg]" />
                </div>
              </div>
            </div>
          </>
        )}

        {/* Leyenda */}
        <div className="mt-8 flex justify-between items-center">
          <div className="flex gap-4 items-center">
            <div className="flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full" style={{ background: '#6AB023' }} />
              <span className="text-[9px] text-gray-400 font-medium">Libre</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full bg-red-500" />
              <span className="text-[9px] text-gray-400 font-medium">Ocupado</span>
            </div>
          </div>
          {timestamp && (
            <span className="text-[9px] text-gray-300 font-medium">
              {new Date(timestamp).toLocaleTimeString("es-CO")}
            </span>
          )}
        </div>
      </div>

      {/* Bottom Sheet al seleccionar cajón */}
      <AnimatePresence>
        {selectedSlot && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedSlot(null)}
              className="fixed inset-0 bg-black/20 backdrop-blur-[2px] z-40"
            />
            <motion.div
              initial={{ y: "100%" }}
              animate={{ y: 0 }}
              exit={{ y: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="fixed bottom-0 left-0 right-0 bg-white rounded-t-[40px] p-8 z-50 shadow-2xl"
            >
              <div className="w-12 h-1.5 bg-gray-100 rounded-full mx-auto mb-8" />
              <div className="flex items-start justify-between mb-6">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <div className="p-3 bg-[#A3E4D7]/20 rounded-2xl text-[#70C1B3]">
                      {selectedSlot.tipo === "carro" ? (
                        <Car size={24} />
                      ) : (
                        <Bike size={24} />
                      )}
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-gray-800">
                        Cajón {selectedSlot.slot}
                      </h2>
                      <p className="text-gray-400 text-sm capitalize">
                        Tipo: {selectedSlot.tipo}
                        {selectedSlot.distancia_cm
                          ? ` · ${selectedSlot.distancia_cm} cm`
                          : ""}
                      </p>
                    </div>
                  </div>
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-[#A3E4D7]/20 text-[#70C1B3] text-[10px] font-bold rounded-full uppercase tracking-wider">
                    Disponible
                  </span>
                </div>
                <button
                  onClick={() => setSelectedSlot(null)}
                  className="p-2 hover:bg-gray-50 rounded-full transition-colors"
                >
                  <X size={20} className="text-gray-400" />
                </button>
              </div>

              <div className="bg-gray-50 rounded-3xl p-6 mb-8 border border-gray-100">
                <div className="flex gap-4 items-center">
                  <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center shadow-sm">
                    <Info size={18} className="text-[#70C1B3]" />
                  </div>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    ¿Deseas asegurar tu espacio para mitigar la huella de{" "}
                    <span className="font-bold text-[#70C1B3]">CO₂</span>?
                  </p>
                </div>
              </div>

              <button
                className="w-full text-white font-bold py-5 rounded-[24px] shadow-lg transition-all active:scale-[0.98]"
                style={{ background: 'linear-gradient(135deg, #6AB023, #00AEEF)', boxShadow: '0 8px 24px rgba(0,174,239,0.3)' }}
              >
                Reservar Cupo
              </button>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ParkingMap;
