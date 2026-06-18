/**
 * SmartParkU - Parking Store (Zustand)
 * Mantiene el estado en tiempo real del parqueadero recibido via WebSocket.
 *
 * Flujo: Raspberry Pi → HiveMQ → Backend → WebSocket → este store → UI
 *
 * Cuando el backend no está disponible, se muestran los 10 slots predefinidos
 * de la UCC en estado "libre" para que la UI no quede en blanco.
 */
import { create } from 'zustand';

// ─── Tipos ────────────────────────────────────────────────────────────────────

export type SlotStatus  = 'libre' | 'ocupado';
export type VehicleType = 'carro' | 'moto' | 'bicicleta' | 'vip';

export interface ParkingSlot {
  slot:         string;
  label:        string;        // Etiqueta visual: "C-01", "M-01", "V-01", etc.
  status:       SlotStatus;
  tipo:         VehicleType;
  distancia_cm: number | null;
  updated_at:   string | null;
}

// ─── Slots Predefinidos (10 slots fijos UCC Pasto) ───────────────────────────
// Sincronizado con mqtt_client.SLOTS_DEFINICION del backend
const SLOTS_FALLBACK: Record<string, ParkingSlot> = Object.fromEntries(
  [
    { slot_id: 'slot_01', label: 'C-01', tipo: 'carro'     as VehicleType },
    { slot_id: 'slot_02', label: 'C-02', tipo: 'carro'     as VehicleType },
    { slot_id: 'slot_03', label: 'C-03', tipo: 'carro'     as VehicleType },
    { slot_id: 'slot_04', label: 'C-04', tipo: 'carro'     as VehicleType },
    { slot_id: 'slot_05', label: 'M-01', tipo: 'moto'      as VehicleType },
    { slot_id: 'slot_06', label: 'M-02', tipo: 'moto'      as VehicleType },
    { slot_id: 'slot_07', label: 'M-03', tipo: 'moto'      as VehicleType },
    { slot_id: 'slot_08', label: 'B-01', tipo: 'bicicleta' as VehicleType },
    { slot_id: 'slot_09', label: 'B-02', tipo: 'bicicleta' as VehicleType },
    { slot_id: 'slot_10', label: 'V-01', tipo: 'vip'       as VehicleType },
  ].map(s => [
    s.slot_id,
    { slot: s.slot_id, label: s.label, status: 'libre' as SlotStatus, tipo: s.tipo, distancia_cm: null, updated_at: null },
  ])
);

interface ParkingState {
  slots:          Record<string, ParkingSlot>;
  totalLibre:     number;
  totalOcupado:   number;
  entradaLibre:   boolean;
  ultimoSensorCm: number | null;
  timestamp:      string | null;

  wsStatus: 'disconnected' | 'connecting' | 'connected' | 'error';
  wsError:  string | null;

  connect:      () => void;
  disconnect:   () => void;
  controlServo: (accion: 'abrir' | 'cerrar') => Promise<{ ok: boolean; error?: string }>;
}

// ─── WebSocket singleton ──────────────────────────────────────────────────────
let ws:             WebSocket | null = null;
let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
let reconnectDelay  = 3000;
const MAX_DELAY     = 30_000;
let intentionalClose = false;   // bandera para no reconectar cuando es un cierre limpio

const WS_URL   = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/v1/parking/ws/parking';
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ─── Store ────────────────────────────────────────────────────────────────────
export const useParkingStore = create<ParkingState>((set, get) => ({

  // Inicializar con los 10 slots predefinidos para que la UI no quede vacía
  slots:          SLOTS_FALLBACK,
  totalLibre:     10,
  totalOcupado:   0,
  entradaLibre:   true,
  ultimoSensorCm: null,
  timestamp:      null,
  wsStatus:       'disconnected',
  wsError:        null,

  connect: () => {
    // Evitar conexiones duplicadas
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return;

    set({ wsStatus: 'connecting', wsError: null });

    try {
      ws = new WebSocket(WS_URL);
    } catch {
      // En SSR o entornos sin WebSocket, no hacer nada
      set({ wsStatus: 'error', wsError: 'WebSocket no disponible en este entorno.' });
      return;
    }

    ws.onopen = () => {
      reconnectDelay = 3000; // resetear backoff al conectar exitosamente
      set({ wsStatus: 'connected', wsError: null });
      if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.ping) return; // ignorar pings de keep-alive

        const rawEspacios: Record<string, any> = data.espacios || {};
        const slots: Record<string, ParkingSlot> = {};

        Object.entries(rawEspacios).forEach(([id, info]: [string, any]) => {
          // Preservar label del fallback si el backend no lo manda
          const fallback = SLOTS_FALLBACK[id];
          slots[id] = {
            slot:         id,
            label:        info.label        ?? fallback?.label        ?? id,
            status:       info.status       ?? 'libre',
            tipo:         info.tipo         ?? fallback?.tipo         ?? 'carro',
            distancia_cm: info.distancia_cm ?? null,
            updated_at:   info.updated_at   ?? null,
          };
        });

        // Si el backend mandó datos vacíos, mantener el fallback
        const finalSlots = Object.keys(slots).length > 0 ? slots : get().slots;

        set({
          slots:          finalSlots,
          totalLibre:     data.total_libre      ?? Object.values(finalSlots).filter(s => s.status === 'libre').length,
          totalOcupado:   data.total_ocupado    ?? Object.values(finalSlots).filter(s => s.status === 'ocupado').length,
          entradaLibre:   data.entrada_libre    ?? true,
          ultimoSensorCm: data.ultimo_sensor_cm ?? null,
          timestamp:      data.timestamp        ?? null,
        });
      } catch {
        // payload malformado, ignorar silenciosamente
      }
    };

    ws.onerror = () => {
      set({ wsStatus: 'error', wsError: 'Backend no disponible. Mostrando datos de referencia.' });
    };

    ws.onclose = () => {
      ws = null;
      set({ wsStatus: 'disconnected' });

      // Solo reconectar si no fue un cierre intencional (ej. cleanup de useEffect)
      if (intentionalClose) {
        intentionalClose = false;
        return;
      }

      // Reconexión con backoff exponencial: 3s → 6s → 12s → 24s → 30s (máx)
      reconnectTimer = setTimeout(() => {
        reconnectDelay = Math.min(reconnectDelay * 2, MAX_DELAY);
        get().connect();
      }, reconnectDelay);
    };
  },

  disconnect: () => {
    intentionalClose = true;
    if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }
    reconnectDelay = 3000;
    if (ws) { ws.close(); ws = null; }
    set({ wsStatus: 'disconnected' });
  },

  controlServo: async (accion: 'abrir' | 'cerrar') => {
    try {
      // Obtener token del authStore para el header Authorization
      const { token } = (await import('./authStore')).useAuthStore.getState();
      const res = await fetch(`${API_BASE}/api/v1/parking/servo?accion=${accion}`, {
        method: 'POST',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      });
      if (!res.ok) {
        const err = await res.json();
        return { ok: false, error: err.detail || 'Error del servidor' };
      }
      return { ok: true };
    } catch {
      return { ok: false, error: 'Backend no disponible' };
    }
  },
}));
