'use client';

/**
 * QRAcceso.tsx
 * Componente completo para el flujo QR del parqueadero SmartParkU.
 *
 * Pantallas:
 *   idle      → botón "Solicitar QR"
 *   generating → spinner de carga
 *   show_qr   → imagen QR + cuenta regresiva de 10 min + botón "Ya escaneé mi QR"
 *   scanning  → spinner mientras se valida en el backend
 *   success   → confirmación: espacio asignado y hora de entrada
 *   error     → mensaje de error + botón reintentar
 */

import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  QrCode, CheckCircle2, XCircle, Loader2,
  Clock, MapPin, Car, Bike, Zap, RefreshCw,
} from 'lucide-react';
import { useQRStore } from '@/store/qrStore';

const UCC = {
  green: '#6AB023',
  blue:  '#00AEEF',
  lime:  '#B5D334',
  navy:  '#1E3A5F',
};

interface QRAccesoProps {
  idUsuario: number;
  idVehiculo?: number;
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0');
  const s = (seconds % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

function tipoIcon(tipo: string) {
  if (tipo === 'moto')      return <Bike  size={20} />;
  if (tipo === 'bicicleta') return <Zap   size={20} />;
  return <Car size={20} />;
}

// ── Pantallas individuales ─────────────────────────────────────────────────────

const PantallaIdle = ({ onGenerar }: { onGenerar: () => void }) => (
  <motion.div
    key="idle"
    initial={{ opacity: 0, y: 16 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -16 }}
    className="flex flex-col items-center gap-6 py-4"
  >
    <div
      className="w-20 h-20 rounded-3xl flex items-center justify-center shadow-lg"
      style={{ background: `linear-gradient(135deg, ${UCC.navy}, ${UCC.blue})` }}
    >
      <QrCode size={40} className="text-white" />
    </div>

    <div className="text-center space-y-1">
      <h3 className="text-lg font-black" style={{ color: UCC.navy }}>
        Acceso al Parqueadero
      </h3>
      <p className="text-sm font-medium text-gray-400 max-w-[220px] leading-relaxed">
        Genera tu QR para ingresar. Se asigna el primer espacio libre disponible.
      </p>
    </div>

    <motion.button
      whileTap={{ scale: 0.96 }}
      onClick={onGenerar}
      className="w-full max-w-xs py-4 text-white font-black rounded-2xl flex items-center justify-center gap-2 text-base"
      style={{
        background: `linear-gradient(135deg, ${UCC.green}, ${UCC.blue})`,
        boxShadow: '0 8px 24px rgba(0,174,239,0.30)',
      }}
    >
      <QrCode size={20} />
      Solicitar QR de Ingreso
    </motion.button>
  </motion.div>
);

const PantallaCargando = ({ mensaje }: { mensaje: string }) => (
  <motion.div
    key="loading"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    className="flex flex-col items-center gap-5 py-10"
  >
    <Loader2 size={44} className="animate-spin" style={{ color: UCC.blue }} />
    <p className="text-sm font-bold text-gray-500">{mensaje}</p>
  </motion.div>
);

const PantallaQR = ({
  onEscanear,
}: {
  onEscanear: () => void;
}) => {
  const { qrGenerado, secondsLeft } = useQRStore();
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const tickTimer = useQRStore((s) => s.tickTimer);

  // Cuenta regresiva
  useEffect(() => {
    timerRef.current = setInterval(tickTimer, 1000);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [tickTimer]);

  if (!qrGenerado) return null;

  const urgente = secondsLeft < 60;

  return (
    <motion.div
      key="show_qr"
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.96 }}
      className="flex flex-col items-center gap-5"
    >
      {/* Espacio asignado */}
      <div
        className="w-full rounded-2xl px-4 py-3 flex items-center gap-3 border"
        style={{ background: `${UCC.green}12`, borderColor: `${UCC.green}30` }}
      >
        <div
          className="p-2 rounded-xl"
          style={{ background: `${UCC.green}20`, color: UCC.green }}
        >
          {tipoIcon(qrGenerado.tipo)}
        </div>
        <div>
          <p className="text-[10px] font-black uppercase tracking-widest text-gray-400">
            Espacio asignado
          </p>
          <p className="text-base font-black" style={{ color: UCC.navy }}>
            {qrGenerado.label}
            <span className="text-xs font-medium text-gray-400 ml-2 normal-case capitalize">
              {qrGenerado.tipo}
            </span>
          </p>
        </div>
        <div className="ml-auto flex items-center gap-1.5">
          <MapPin size={14} style={{ color: UCC.blue }} />
          <span className="text-xs font-bold" style={{ color: UCC.blue }}>Libre</span>
        </div>
      </div>

      {/* Imagen QR */}
      <div
        className="relative rounded-3xl overflow-hidden border-2 p-4 bg-white shadow-xl"
        style={{ borderColor: `${UCC.blue}25` }}
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={qrGenerado.qr_image_base64}
          alt="Código QR de acceso al parqueadero"
          width={200}
          height={200}
          className="rounded-xl block"
        />
        {/* Línea de escaneo animada */}
        <motion.div
          animate={{ top: ['1rem', '13rem', '1rem'] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute left-4 right-4 h-0.5 z-10 pointer-events-none"
          style={{
            background: `linear-gradient(90deg, transparent, ${UCC.blue}, transparent)`,
            boxShadow: `0 0 8px ${UCC.blue}`,
          }}
        />
      </div>

      {/* Cuenta regresiva */}
      <div
        className="flex items-center gap-2 px-4 py-2 rounded-2xl"
        style={{
          background: urgente ? '#fef2f2' : `${UCC.blue}10`,
          border: `1px solid ${urgente ? '#fca5a5' : `${UCC.blue}25`}`,
        }}
      >
        <Clock
          size={16}
          style={{ color: urgente ? '#ef4444' : UCC.blue }}
          className={urgente ? 'animate-pulse' : ''}
        />
        <span
          className="text-sm font-black tabular-nums"
          style={{ color: urgente ? '#ef4444' : UCC.navy }}
        >
          {formatTime(secondsLeft)}
        </span>
        <span className="text-xs font-medium text-gray-400">
          para expirar
        </span>
      </div>

      {/* Instrucción */}
      <p className="text-xs text-gray-400 font-medium text-center max-w-[220px] leading-relaxed">
        Muestra este QR en el lector de la entrada. El espacio se confirmará automáticamente.
      </p>

      {/* Botón de confirmación manual (para demo/pruebas) */}
      <motion.button
        whileTap={{ scale: 0.96 }}
        onClick={onEscanear}
        className="w-full max-w-xs py-4 text-white font-black rounded-2xl flex items-center justify-center gap-2"
        style={{
          background: `linear-gradient(135deg, ${UCC.navy}, ${UCC.blue})`,
          boxShadow: '0 6px 20px rgba(0,174,239,0.25)',
        }}
      >
        <CheckCircle2 size={20} />
        Confirmar Ingreso
      </motion.button>
    </motion.div>
  );
};

const PantallaExito = ({ onReset }: { onReset: () => void }) => {
  const { acceso } = useQRStore();
  if (!acceso) return null;

  const horaFmt = new Date(acceso.hora_entrada).toLocaleTimeString('es-CO', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <motion.div
      key="success"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0 }}
      className="flex flex-col items-center gap-6 py-4"
    >
      {/* Icono éxito */}
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 260, damping: 20 }}
        className="w-20 h-20 rounded-3xl flex items-center justify-center"
        style={{ background: `${UCC.green}20`, border: `2px solid ${UCC.green}40` }}
      >
        <CheckCircle2 size={44} style={{ color: UCC.green }} />
      </motion.div>

      <div className="text-center">
        <h3 className="text-xl font-black mb-1" style={{ color: UCC.navy }}>
          ¡Bienvenido al campus!
        </h3>
        <p className="text-sm text-gray-400 font-medium">{acceso.mensaje}</p>
      </div>

      {/* Tarjeta de confirmación */}
      <div
        className="w-full rounded-3xl p-5 space-y-3 border"
        style={{ background: '#f8fafc', borderColor: '#e2e8f0' }}
      >
        <div className="flex justify-between items-center">
          <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Espacio</span>
          <span className="text-base font-black" style={{ color: UCC.navy }}>
            {acceso.label}
          </span>
        </div>
        <div className="h-px bg-gray-100" />
        <div className="flex justify-between items-center">
          <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Hora entrada</span>
          <span className="text-base font-black" style={{ color: UCC.navy }}>{horaFmt}</span>
        </div>
        <div className="h-px bg-gray-100" />
        <div className="flex justify-between items-center">
          <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">ID Acceso</span>
          <span className="text-sm font-bold text-gray-500">#{acceso.acceso_id}</span>
        </div>
      </div>

      <motion.button
        whileTap={{ scale: 0.96 }}
        onClick={onReset}
        className="w-full max-w-xs py-3 font-black rounded-2xl text-sm border"
        style={{ color: UCC.blue, borderColor: `${UCC.blue}30`, background: `${UCC.blue}08` }}
      >
        Volver al Dashboard
      </motion.button>
    </motion.div>
  );
};

const PantallaError = ({ onReset }: { onReset: () => void }) => {
  const { error } = useQRStore();

  return (
    <motion.div
      key="error"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="flex flex-col items-center gap-6 py-4"
    >
      <div
        className="w-20 h-20 rounded-3xl flex items-center justify-center"
        style={{ background: '#fef2f2', border: '2px solid #fca5a5' }}
      >
        <XCircle size={44} className="text-red-400" />
      </div>

      <div className="text-center">
        <h3 className="text-lg font-black text-red-700 mb-1">Ocurrió un problema</h3>
        <p className="text-sm text-red-400 font-medium max-w-[240px] leading-relaxed">
          {error || 'Error desconocido. Intenta de nuevo.'}
        </p>
      </div>

      <motion.button
        whileTap={{ scale: 0.96 }}
        onClick={onReset}
        className="w-full max-w-xs py-4 text-white font-black rounded-2xl flex items-center justify-center gap-2"
        style={{ background: 'linear-gradient(135deg, #ef4444, #f97316)' }}
      >
        <RefreshCw size={18} />
        Intentar de nuevo
      </motion.button>
    </motion.div>
  );
};

// ── Componente principal ───────────────────────────────────────────────────────

export default function QRAcceso({ idUsuario, idVehiculo }: QRAccesoProps) {
  const { step, generarQR, escanearQR, reset, qrGenerado } = useQRStore();

  const handleGenerar = () => generarQR(idUsuario, idVehiculo);
  const handleEscanear = () => {
    if (qrGenerado) escanearQR(qrGenerado.qr_token);
  };

  return (
    <div
      className="bg-white rounded-[28px] p-6 shadow-lg border w-full"
      style={{ borderColor: `${UCC.blue}15` }}
    >
      {/* Título */}
      <div className="flex items-center gap-2 mb-6">
        <div
          className="p-2 rounded-xl"
          style={{ background: `${UCC.blue}15`, color: UCC.blue }}
        >
          <QrCode size={18} />
        </div>
        <h2 className="text-base font-black" style={{ color: UCC.navy }}>
          QR de Acceso al Parqueadero
        </h2>
      </div>

      <AnimatePresence mode="wait">
        {step === 'idle' && (
          <PantallaIdle key="idle" onGenerar={handleGenerar} />
        )}
        {step === 'generating' && (
          <PantallaCargando key="generating" mensaje="Buscando espacio libre..." />
        )}
        {step === 'show_qr' && (
          <PantallaQR key="show_qr" onEscanear={handleEscanear} />
        )}
        {step === 'scanning' && (
          <PantallaCargando key="scanning" mensaje="Validando QR y asignando cupo..." />
        )}
        {step === 'success' && (
          <PantallaExito key="success" onReset={reset} />
        )}
        {step === 'error' && (
          <PantallaError key="error" onReset={reset} />
        )}
      </AnimatePresence>
    </div>
  );
}
