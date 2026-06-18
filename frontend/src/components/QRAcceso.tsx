'use client';

/**
 * QRAcceso.tsx — Flujo QR completo para acceso al parqueadero SmartParkU.
 *
 * Pantalla 1 — "Solicitar QR":  formulario con id_usuario del JWT, botón Generar QR,
 *              muestra <img src={qr_image_base64}> con cuenta regresiva de 10 min.
 * Pantalla 2 — "Escanear QR":   cámara real con html5-qrcode (lazy, no SSR),
 *              llama POST /api/v1/qr/escanear con el qr_token leído.
 * Pantalla 3 — Confirmación:    muestra label, hora_entrada y mensaje de bienvenida.
 *              Errores 409/410  → panel de error con botón "Generar nuevo QR".
 */

import React, { useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import { motion, AnimatePresence } from 'framer-motion';
import {
  QrCode, CheckCircle2, XCircle, Loader2, Clock,
  MapPin, Car, Bike, Zap, RefreshCw, Camera, CameraOff,
  ChevronRight, AlertCircle,
} from 'lucide-react';
import { useQRStore } from '@/store/qrStore';

// Carga lazy del escáner — evita errores de SSR con html5-qrcode
const QRScanner = dynamic(() => import('@/components/QRScanner'), {
  ssr: false,
  loading: () => (
    <div className="flex flex-col items-center gap-3 py-10">
      <Loader2 size={36} className="animate-spin text-[#00AEEF]" />
      <p className="text-xs font-bold text-gray-400">Iniciando cámara...</p>
    </div>
  ),
});

// ─── Constantes de estilo UCC ────────────────────────────────────────────────
const UCC = { green: '#6AB023', blue: '#00AEEF', lime: '#B5D334', navy: '#1E3A5F' };

// ─── Props ────────────────────────────────────────────────────────────────────
interface QRAccesoProps {
  idUsuario: number;
  idVehiculo?: number;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
function formatTime(s: number) {
  const m = Math.floor(s / 60).toString().padStart(2, '0');
  const sec = (s % 60).toString().padStart(2, '0');
  return `${m}:${sec}`;
}

function TipoIcon({ tipo }: { tipo: string }) {
  if (tipo === 'moto')      return <Bike  size={20} />;
  if (tipo === 'bicicleta') return <Zap   size={20} />;
  return <Car size={20} />;
}

// ─────────────────────────────────────────────────────────────────────────────
// PANTALLA 1 — Solicitar QR
// Muestra botón "Generar QR" y, una vez generado, la imagen con cuenta regresiva
// ─────────────────────────────────────────────────────────────────────────────
function PantallaSolicitarQR({ idUsuario, idVehiculo }: QRAccesoProps) {
  const { step, qrGenerado, secondsLeft, generarQR, tickTimer } = useQRStore();
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Arrancar cuenta regresiva cuando hay QR visible
  useEffect(() => {
    if (step === 'show_qr') {
      timerRef.current = setInterval(tickTimer, 1000);
    }
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [step, tickTimer]);

  const urgente = secondsLeft < 60 && secondsLeft > 0;

  // ── Estado: cargando ──
  if (step === 'generating') {
    return (
      <div className="flex flex-col items-center gap-4 py-12">
        <Loader2 size={44} className="animate-spin" style={{ color: UCC.blue }} />
        <p className="text-sm font-bold text-gray-400">Buscando espacio libre...</p>
      </div>
    );
  }

  // ── Estado: QR generado → mostrar imagen ──
  if (step === 'show_qr' && qrGenerado) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex flex-col items-center gap-5"
      >
        {/* Badge espacio asignado */}
        <div
          className="w-full rounded-2xl px-4 py-3 flex items-center gap-3 border"
          style={{ background: `${UCC.green}12`, borderColor: `${UCC.green}30` }}
        >
          <div className="p-2 rounded-xl" style={{ background: `${UCC.green}20`, color: UCC.green }}>
            <TipoIcon tipo={qrGenerado.tipo} />
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
            alt="Código QR de acceso al parqueadero SmartParkU"
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
          <span className="text-sm font-black tabular-nums"
            style={{ color: urgente ? '#ef4444' : UCC.navy }}>
            {formatTime(secondsLeft)}
          </span>
          <span className="text-xs font-medium text-gray-400">para expirar</span>
        </div>

        <p className="text-xs text-gray-400 text-center max-w-[220px] leading-relaxed">
          Presenta este código en el lector de la entrada del parqueadero UCC.
        </p>
      </motion.div>
    );
  }

  // ── Estado: idle → botón principal ──
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center gap-6 py-4"
    >
      <div
        className="w-20 h-20 rounded-3xl flex items-center justify-center shadow-lg"
        style={{ background: `linear-gradient(135deg, ${UCC.navy}, ${UCC.blue})` }}
      >
        <QrCode size={40} className="text-white" />
      </div>

      <div className="text-center space-y-1">
        <h3 className="text-lg font-black" style={{ color: UCC.navy }}>Acceso al Parqueadero</h3>
        <p className="text-sm font-medium text-gray-400 max-w-[220px] leading-relaxed">
          Genera tu QR para ingresar. Se asigna el primer espacio libre disponible.
        </p>
      </div>

      <motion.button
        whileTap={{ scale: 0.96 }}
        onClick={() => generarQR(idUsuario, idVehiculo)}
        className="w-full max-w-xs py-4 text-white font-black rounded-2xl flex items-center justify-center gap-2 text-base"
        style={{
          background: `linear-gradient(135deg, ${UCC.green}, ${UCC.blue})`,
          boxShadow: '0 8px 24px rgba(0,174,239,0.30)',
        }}
      >
        <QrCode size={20} />
        Generar QR de Ingreso
        <ChevronRight size={18} />
      </motion.button>
    </motion.div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// PANTALLA 2 — Escanear QR con cámara
// Activa la cámara trasera del dispositivo, lee el QR y llama al backend
// ─────────────────────────────────────────────────────────────────────────────
function PantallaEscanear() {
  const { escanearQR, reset, step } = useQRStore();
  const [camError, setCamError] = useState<string | null>(null);
  const activo = step === 'camera';

  const handleResult = (token: string) => {
    escanearQR(token);
  };

  // Mientras valida
  if (step === 'scanning') {
    return (
      <div className="flex flex-col items-center gap-4 py-12">
        <Loader2 size={44} className="animate-spin" style={{ color: UCC.blue }} />
        <p className="text-sm font-bold text-gray-400">Validando QR y asignando cupo...</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center gap-5"
    >
      {/* Encabezado */}
      <div className="text-center">
        <div className="flex items-center justify-center gap-2 mb-1">
          <Camera size={18} style={{ color: UCC.blue }} />
          <h3 className="text-base font-black" style={{ color: UCC.navy }}>
            Escanear QR con cámara
          </h3>
        </div>
        <p className="text-xs text-gray-400 font-medium">
          Apunta tu cámara al código QR para ingresar.
        </p>
      </div>

      {/* Error de cámara */}
      {camError ? (
        <div
          className="w-full rounded-2xl p-4 flex items-start gap-3 border"
          style={{ background: '#fef2f2', borderColor: '#fca5a5' }}
        >
          <CameraOff size={20} className="text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-bold text-red-700 mb-0.5">Cámara no disponible</p>
            <p className="text-xs text-red-400 leading-relaxed">{camError}</p>
          </div>
        </div>
      ) : (
        /* Viewfinder de cámara */
        <div
          className="w-full rounded-3xl overflow-hidden border-2 relative"
          style={{ borderColor: `${UCC.blue}30`, maxWidth: 300 }}
        >
          {/* Marco esquinas estilo QR reader */}
          <div className="absolute top-3 left-3 w-8 h-8 border-t-4 border-l-4 rounded-tl-lg z-10"
            style={{ borderColor: UCC.blue }} />
          <div className="absolute top-3 right-3 w-8 h-8 border-t-4 border-r-4 rounded-tr-lg z-10"
            style={{ borderColor: UCC.blue }} />
          <div className="absolute bottom-3 left-3 w-8 h-8 border-b-4 border-l-4 rounded-bl-lg z-10"
            style={{ borderColor: UCC.blue }} />
          <div className="absolute bottom-3 right-3 w-8 h-8 border-b-4 border-r-4 rounded-br-lg z-10"
            style={{ borderColor: UCC.blue }} />

          <QRScanner
            activo={activo}
            onResult={handleResult}
            onError={setCamError}
          />
        </div>
      )}

      {/* Instrucciones */}
      <div
        className="w-full rounded-2xl px-4 py-3 flex items-center gap-3 border"
        style={{ background: `${UCC.blue}08`, borderColor: `${UCC.blue}20` }}
      >
        <AlertCircle size={16} style={{ color: UCC.blue }} className="flex-shrink-0" />
        <p className="text-xs text-gray-500 leading-relaxed">
          Permite el acceso a la cámara cuando el navegador lo solicite.
          El QR se detecta automáticamente.
        </p>
      </div>

      {/* Botón cancelar */}
      <button
        onClick={reset}
        className="text-sm font-bold text-gray-400 hover:text-gray-600 transition-colors py-1"
      >
        Cancelar
      </button>
    </motion.div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// PANTALLA 3 — Confirmación de acceso (éxito)
// Muestra espacio.label, hora_entrada, mensaje de bienvenida
// ─────────────────────────────────────────────────────────────────────────────
function PantallaConfirmacion({ onReset }: { onReset: () => void }) {
  const { acceso } = useQRStore();
  if (!acceso) return null;

  const horaFmt = new Date(acceso.hora_entrada).toLocaleTimeString('es-CO', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: 'spring', stiffness: 240, damping: 22 }}
      className="flex flex-col items-center gap-6 py-2"
    >
      {/* Icono animado */}
      <motion.div
        initial={{ scale: 0, rotate: -15 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: 'spring', stiffness: 260, damping: 18, delay: 0.1 }}
        className="w-24 h-24 rounded-[2rem] flex items-center justify-center shadow-xl"
        style={{
          background: `linear-gradient(135deg, ${UCC.green}30, ${UCC.green}15)`,
          border: `2px solid ${UCC.green}50`,
        }}
      >
        <CheckCircle2 size={52} style={{ color: UCC.green }} />
      </motion.div>

      {/* Título */}
      <div className="text-center space-y-1">
        <motion.h3
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-2xl font-black"
          style={{ color: UCC.navy }}
        >
          ¡Bienvenido al campus!
        </motion.h3>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-sm font-medium text-gray-400 max-w-[220px] leading-relaxed"
        >
          {acceso.mensaje}
        </motion.p>
      </div>

      {/* Tarjeta de detalles */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.35 }}
        className="w-full rounded-3xl border overflow-hidden"
        style={{ borderColor: '#e2e8f0' }}
      >
        {/* Fila: Espacio */}
        <div className="flex justify-between items-center px-5 py-4 bg-white">
          <div className="flex items-center gap-2">
            <MapPin size={15} style={{ color: UCC.blue }} />
            <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">
              Espacio asignado
            </span>
          </div>
          <span
            className="text-lg font-black px-3 py-1 rounded-xl"
            style={{ background: `${UCC.green}15`, color: UCC.green }}
          >
            {acceso.label}
          </span>
        </div>
        <div className="h-px bg-gray-100" />

        {/* Fila: Hora de entrada */}
        <div className="flex justify-between items-center px-5 py-4 bg-white">
          <div className="flex items-center gap-2">
            <Clock size={15} style={{ color: UCC.blue }} />
            <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">
              Hora de entrada
            </span>
          </div>
          <span className="text-base font-black tabular-nums" style={{ color: UCC.navy }}>
            {horaFmt}
          </span>
        </div>
        <div className="h-px bg-gray-100" />

        {/* Fila: ID Acceso */}
        <div className="flex justify-between items-center px-5 py-4 bg-white">
          <div className="flex items-center gap-2">
            <QrCode size={15} style={{ color: UCC.blue }} />
            <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">
              ID Acceso
            </span>
          </div>
          <span className="text-sm font-bold text-gray-500">#{acceso.acceso_id}</span>
        </div>
      </motion.div>

      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        whileTap={{ scale: 0.96 }}
        onClick={onReset}
        className="w-full py-3 font-black rounded-2xl text-sm border"
        style={{ color: UCC.blue, borderColor: `${UCC.blue}30`, background: `${UCC.blue}08` }}
      >
        Volver al Dashboard
      </motion.button>
    </motion.div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// PANTALLA ERROR — 409 espacio ocupado / 410 QR expirado / error genérico
// Siempre incluye botón "Generar nuevo QR"
// ─────────────────────────────────────────────────────────────────────────────
function PantallaError({ onReset }: { onReset: () => void }) {
  const { error } = useQRStore();

  // Detectar tipo de error para mensaje y color personalizado
  const esExpirado  = error?.toLowerCase().includes('expir');
  const esOcupado   = error?.toLowerCase().includes('ocupado');

  const titulo = esExpirado
    ? 'QR Expirado'
    : esOcupado
    ? 'Espacio Ocupado'
    : 'Ocurrió un problema';

  const color = esOcupado ? '#f97316' : '#ef4444'; // naranja para ocupado, rojo para los demás

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center gap-6 py-2"
    >
      {/* Icono */}
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 260, damping: 20 }}
        className="w-20 h-20 rounded-3xl flex items-center justify-center"
        style={{ background: `${color}15`, border: `2px solid ${color}40` }}
      >
        <XCircle size={44} style={{ color }} />
      </motion.div>

      {/* Texto */}
      <div className="text-center space-y-2">
        <h3 className="text-lg font-black" style={{ color }}>
          {titulo}
        </h3>
        <p className="text-sm font-medium text-gray-400 max-w-[240px] leading-relaxed">
          {error || 'No se pudo completar el acceso. Intenta de nuevo.'}
        </p>

        {/* Sugerencia contextual */}
        {(esExpirado || esOcupado) && (
          <div
            className="mt-2 rounded-2xl px-4 py-3 text-xs font-medium leading-relaxed text-left border"
            style={{
              background: esOcupado ? '#fff7ed' : '#fef2f2',
              borderColor: esOcupado ? '#fed7aa' : '#fecaca',
              color: esOcupado ? '#9a3412' : '#991b1b',
            }}
          >
            {esOcupado
              ? '⚡ Otro estudiante tomó ese espacio. Genera un QR nuevo para obtener otro disponible.'
              : '⏱ Pasaron los 10 minutos de validez. Genera un QR nuevo para ingresar.'}
          </div>
        )}
      </div>

      {/* Botón: siempre permite generar nuevo QR */}
      <motion.button
        whileTap={{ scale: 0.96 }}
        onClick={onReset}
        className="w-full max-w-xs py-4 text-white font-black rounded-2xl flex items-center justify-center gap-2"
        style={{
          background: `linear-gradient(135deg, ${UCC.green}, ${UCC.blue})`,
          boxShadow: '0 6px 20px rgba(0,174,239,0.25)',
        }}
      >
        <RefreshCw size={18} />
        Generar nuevo QR
      </motion.button>
    </motion.div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// COMPONENTE PRINCIPAL — orquesta las 3 pantallas con tabs
// ─────────────────────────────────────────────────────────────────────────────
export default function QRAcceso({ idUsuario, idVehiculo }: QRAccesoProps) {
  const { step, reset, setStep } = useQRStore();

  // Tabs solo visibles cuando el flujo no ha terminado ni está en error
  const mostrarTabs = !['success', 'error', 'generating', 'scanning'].includes(step);

  // Tab activo: "generar" o "escanear"
  const tabActivo: 'generar' | 'escanear' =
    step === 'camera' ? 'escanear' : 'generar';

  return (
    <div
      className="bg-white rounded-[28px] shadow-lg border w-full overflow-hidden"
      style={{ borderColor: `${UCC.blue}15` }}
    >
      {/* ── Cabecera ── */}
      <div
        className="px-6 pt-6 pb-4"
        style={{ borderBottom: `1px solid ${UCC.blue}10` }}
      >
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 rounded-xl" style={{ background: `${UCC.blue}15`, color: UCC.blue }}>
            <QrCode size={18} />
          </div>
          <h2 className="text-base font-black" style={{ color: UCC.navy }}>
            QR de Acceso al Parqueadero
          </h2>
        </div>

        {/* Tabs Generar / Escanear */}
        {mostrarTabs && (
          <div
            className="flex rounded-2xl overflow-hidden border"
            style={{ borderColor: '#e2e8f0' }}
          >
            <button
              onClick={() => setStep('idle')}
              className="flex-1 py-2.5 text-xs font-black flex items-center justify-center gap-1.5 transition-all"
              style={
                tabActivo === 'generar'
                  ? { background: UCC.navy, color: '#fff' }
                  : { background: '#f8fafc', color: '#94a3b8' }
              }
            >
              <QrCode size={14} />
              GENERAR QR
            </button>
            <button
              onClick={() => setStep('camera')}
              className="flex-1 py-2.5 text-xs font-black flex items-center justify-center gap-1.5 transition-all"
              style={
                tabActivo === 'escanear'
                  ? { background: UCC.navy, color: '#fff' }
                  : { background: '#f8fafc', color: '#94a3b8' }
              }
            >
              <Camera size={14} />
              ESCANEAR
            </button>
          </div>
        )}
      </div>

      {/* ── Contenido con animación ── */}
      <div className="px-6 pb-8 pt-5">
        <AnimatePresence mode="wait">
          {/* Generar / mostrar QR */}
          {(step === 'idle' || step === 'generating' || step === 'show_qr') && (
            <motion.div key="generar" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <PantallaSolicitarQR idUsuario={idUsuario} idVehiculo={idVehiculo} />
            </motion.div>
          )}

          {/* Escanear con cámara */}
          {(step === 'camera' || step === 'scanning') && (
            <motion.div key="escanear" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <PantallaEscanear />
            </motion.div>
          )}

          {/* Confirmación éxito */}
          {step === 'success' && (
            <motion.div key="success" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <PantallaConfirmacion onReset={reset} />
            </motion.div>
          )}

          {/* Error (409 / 410 / genérico) */}
          {step === 'error' && (
            <motion.div key="error" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <PantallaError onReset={reset} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
