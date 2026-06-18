/**
 * qrStore.ts
 * Estado global para el flujo QR del parqueadero.
 * Maneja la generación del QR, el escaneo y el resultado del acceso.
 */

import { create } from 'zustand';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ─── Tipos ────────────────────────────────────────────────────────────────────

export interface QRGenerado {
  espacio_id: number;
  slot_id: string;
  label: string;
  tipo: string;
  qr_token: string;
  qr_image_base64: string; // "data:image/png;base64,..."
  expira_en: string;       // ISO datetime UTC
  mensaje: string;
}

export interface QRAcceso {
  acceso_id: number;
  id_usuario: number;
  id_vehiculo: number | null;
  espacio_id: number;
  slot_id: string;
  label: string;
  hora_entrada: string;
  mensaje: string;
}

type QRStep = 'idle' | 'generating' | 'show_qr' | 'scanning' | 'success' | 'error';

interface QRState {
  step: QRStep;
  qrGenerado: QRGenerado | null;
  acceso: QRAcceso | null;
  error: string | null;
  secondsLeft: number;

  generarQR: (id_usuario: number, id_vehiculo?: number) => Promise<void>;
  escanearQR: (qr_token: string) => Promise<void>;
  reset: () => void;
  tickTimer: () => void;
}

// ─── Store ────────────────────────────────────────────────────────────────────

export const useQRStore = create<QRState>((set, get) => ({
  step: 'idle',
  qrGenerado: null,
  acceso: null,
  error: null,
  secondsLeft: 0,

  generarQR: async (id_usuario, id_vehiculo) => {
    set({ step: 'generating', error: null, qrGenerado: null, acceso: null });
    try {
      const body: Record<string, unknown> = { id_usuario };
      if (id_vehiculo) body.id_vehiculo = id_vehiculo;

      const res = await fetch(`${API_BASE}/api/v1/qr/generar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'No se pudo generar el QR');
      }

      const data: QRGenerado = await res.json();

      // Calcular segundos hasta expiración
      const expira = new Date(data.expira_en);
      const now = new Date();
      const seconds = Math.max(0, Math.floor((expira.getTime() - now.getTime()) / 1000));

      set({ step: 'show_qr', qrGenerado: data, secondsLeft: seconds });
    } catch (e: any) {
      set({ step: 'error', error: e.message || 'Error al generar el QR' });
    }
  },

  escanearQR: async (qr_token) => {
    set({ step: 'scanning', error: null });
    try {
      const res = await fetch(`${API_BASE}/api/v1/qr/escanear`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ qr_token }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'QR inválido o expirado');
      }

      const data: QRAcceso = await res.json();
      set({ step: 'success', acceso: data });
    } catch (e: any) {
      set({ step: 'error', error: e.message || 'Error al escanear el QR' });
    }
  },

  reset: () => set({ step: 'idle', qrGenerado: null, acceso: null, error: null, secondsLeft: 0 }),

  tickTimer: () => {
    const { secondsLeft, step } = get();
    if (step !== 'show_qr') return;
    if (secondsLeft <= 1) {
      set({ step: 'error', error: 'El QR expiró. Genera uno nuevo para ingresar.', secondsLeft: 0 });
    } else {
      set({ secondsLeft: secondsLeft - 1 });
    }
  },
}));
