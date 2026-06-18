import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export interface AuthUser {
  nombre:     string;
  rol:        string;
  estado:     string;
  id_usuario: number;
}

interface AuthState {
  token: string | null;
  user:  AuthUser | null;
  setAuth: (token: string, user: AuthUser) => void;
  logout:  () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user:  null,
      setAuth: (token, user) => set({ token, user }),
      logout:  () => set({ token: null, user: null }),
    }),
    {
      name: 'smartparku-auth-v2',   // nombre nuevo → invalida caché vieja automáticamente
      storage: createJSONStorage(() => localStorage),
      onRehydrateStorage: () => (state) => {
        // Si el usuario guardado no tiene id_usuario (caché antigua), forzar logout
        if (state?.user && !state.user.id_usuario) {
          state.token = null;
          state.user  = null;
        }
      },
    }
  )
);
