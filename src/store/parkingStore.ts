/**
 * SmartParkU - Parking Store (Zustand)
 * Mantiene el estado en tiempo real del parqueadero recibido via WebSocket.
 *
 * Flujo: Raspberry Pi → HiveMQ → Backend → WebSocket → este store → UI
 */
import { create } from 'zustand';

// ─── Tipos ────────────────────────────────────────────────────────────────────

export type SlotStatus = 'libre' | 'ocupado';
export type VehicleType = 'carro' | 'moto' | 'bicicleta' | 'vip';

export interface ParkingSlot {
  slot: string;
  status: SlotStatus;
  tipo: VehicleType;
  distancia_cm: number | null;
  updated_at: string | null;
}

// ─── Slots Predefinidos (10 slots fijos UCC Pasto) ───────────────────────────
export const DEFAULT_SLOTS: Record<string, ParkingSlot> = {
  'C-01': { slot: 'C-01', status: 'libre', tipo: 'carro', distancia_cm: null, updated_at: null },
  'C-02': { slot: 'C-02', status: 'libre', tipo: 'carro', distancia_cm: null, updated_at: null },
  'C-03': { slot: 'C-03', status: 'libre', tipo: 'carro', distancia_cm: null, updated_at: null },
  'C-04': { slot: 'C-04', status: 'libre', tipo: 'carro', distancia_cm: null, updated_at: null },
  'M-01': { slot: 'M-01', status: 'libre', tipo: 'moto', distancia_cm: null, updated_at: null },
  'M-02': { slot: 'M-02', status: 'libre', tipo: 'moto', distancia_cm: null, updated_at: null },
  'M-03': { slot: 'M-03', status: 'libre', tipo: 'moto', distancia_cm: null, updated_at: null },
  'B-01': { slot: 'B-01', status: 'libre', tipo: 'bicicleta', distancia_cm: null, updated_at: null },
  'B-02': { slot: 'B-02', status: 'libre', tipo: 'bicicleta', distancia_cm: null, updated_at: null },
  'V-01': { slot: 'V-01', status: 'libre', tipo: 'vip', distancia_cm: null, updated_at: null },
};

interface ParkingState {
  // Datos del parqueadero
  slots: Record<string, ParkingSlot>;
  totalLibre: number;
  totalOcupado: number;
  entradaLibre: boolean;
  ultimoSensorCm: number | null;
  timestamp: string | null;

  // Estado de la conexión WebSocket
  wsStatus: 'disconnected' | 'connecting' | 'connected' | 'error';
  wsError: string | null;

  // Acciones
  connect: () => void;
  disconnect: () => void;
  controlServo: (angulo: number) => Promise<{ ok: boolean; error?: string }>;
}

// ─── WebSocket singleton ──────────────────────────────────────────────────────
let ws: WebSocket | null = null;
let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

const WS_URL      = process.env.NEXT_PUBLIC_WS_URL  || 'ws://localhost:8000/ws/parking';
const API_BASE    = process.env.NEXT_PUBLIC_API_URL  || 'http://localhost:8000';

// ─── Store ────────────────────────────────────────────────────────────────────
export const useParkingStore = create<ParkingState>((set, get) => ({
  slots: DEFAULT_SLOTS, // Inicializar con los 10 slots predefinidos
  totalLibre: 10,
  totalOcupado: 0,
  entradaLibre: true,
  ultimoSensorCm: null,
  timestamp: null,
  wsStatus: 'disconnected',
  wsError: null,

  connect: () => {
    if (ws && ws.readyState === WebSocket.OPEN) return;

    set({ wsStatus: 'connecting', wsError: null });

    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      set({ wsStatus: 'connected', wsError: null });
      // Limpiar reconexión pendiente si la había
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
      }
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Ignorar pings del servidor
        if (data.ping) return;

        // Transformar espacios del backend al formato del store
        const rawEspacios: Record<string, any> = data.espacios || {};
        const slots: Record<string, ParkingSlot> = {};

        Object.entries(rawEspacios).forEach(([id, info]: [string, any]) => {
          slots[id] = {
            slot:         id,
            status:       info.status     ?? 'libre',
            tipo:         info.tipo       ?? 'carro',
            distancia_cm: info.distancia_cm ?? null,
            updated_at:   info.updated_at ?? null,
          };
        });

        set({
          slots,
          totalLibre:     data.total_libre     ?? 0,
          totalOcupado:   data.total_ocupado   ?? 0,
          entradaLibre:   data.entrada_libre   ?? true,
          ultimoSensorCm: data.ultimo_sensor_cm ?? null,
          timestamp:      data.timestamp       ?? null,
        });
      } catch {
        // payload malformado, ignorar
      }
    };

    ws.onerror = () => {
      set({ wsStatus: 'error', wsError: 'No se pudo conectar al servidor de parqueadero.' });
    };

    ws.onclose = () => {
      set({ wsStatus: 'disconnected' });
      // Reconexión automática cada 5 segundos
      reconnectTimer = setTimeout(() => {
        get().connect();
      }, 5000);
    };
  },

  disconnect: () => {
    if (reconnectTimer) clearTimeout(reconnectTimer);
    if (ws) {
      ws.close();
      ws = null;
    }
    set({ wsStatus: 'disconnected' });
  },

  controlServo: async (angulo: number) => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/parking/servo?angulo=${angulo}`, {
        method: 'POST',
      });
      if (!res.ok) {
        const err = await res.json();
        return { ok: false, error: err.detail || 'Error del servidor' };
      }
      return { ok: true };
    } catch (e) {
      return { ok: false, error: 'No se pudo conectar al backend' };
    }
  },
}));
