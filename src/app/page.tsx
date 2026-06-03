"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mail, Lock, ChevronRight, Loader2 } from "lucide-react";
import ParkingIllustration from "@/components/ParkingIllustration";
import UCCSwitch from "@/components/UCCSwitch";
import StudentDashboard from "@/components/StudentDashboard";
import { useAuthStore } from "@/store/authStore";

export default function LoginPage() {
  const [correo, setCorreo] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  const { token, user, setAuth, logout } = useAuthStore();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/v1/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ correo, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Error al iniciar sesión");
      }

      const { access_token, nombre, rol, estado } = data;
      setAuth(access_token, { nombre, rol, estado });
    } catch (err: any) {
      setError(err.message || "Error al conectar con el servidor");
    } finally {
      setLoading(false);
    }
  };

  // Si ya hay un usuario autenticado y es Estudiante, mostrar el Dashboard
  if (token && user?.rol === "Estudiante") {
    return <StudentDashboard user={user} />;
  }

  return (
    <main className="min-h-screen relative overflow-hidden flex flex-col items-center justify-center p-6 bg-[#F8FAFC]">
      {/* Background Decorative Elements — burbujas UCC */}
      <div className="absolute inset-0 z-0 overflow-hidden">
        <div className="absolute top-[-15%] left-[-10%] w-[45%] h-[45%] bg-[#00AEEF]/15 rounded-full blur-[130px] animate-pulse" />
        <div className="absolute bottom-[-15%] right-[-10%] w-[45%] h-[45%] bg-[#6AB023]/15 rounded-full blur-[130px]" />
        <div className="absolute top-[40%] right-[-5%] w-[25%] h-[25%] bg-[#B5D334]/10 rounded-full blur-[100px]" />
      </div>

      <div className="w-full max-w-md relative z-10 flex flex-col gap-10">

        {/* Top Section: Illustration & Title */}
        <section className="flex flex-col items-center text-center">
          <ParkingIllustration />

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6, type: "spring", stiffness: 100 }}
            className="mt-6"
          >
            {/* Título bicolor: SMART verde UCC / PARKU azul UCC */}
            <h1 className="text-5xl font-black tracking-tighter font-sans">
              <span style={{ color: "#6AB023" }}>Smart</span>
              <span style={{ color: "#00AEEF" }}>Park</span>
              <span
                style={{ color: "#00AEEF" }}
                className="inline-block hover:rotate-12 transition-transform cursor-default"
              >
                U
              </span>
            </h1>
            <p className="text-[#1E3A5F]/70 mt-3 font-medium tracking-wide text-lg">
              El futuro del parqueo{" "}
              <span style={{ color: "#6AB023" }} className="font-bold">
                inteligente
              </span>
            </p>
          </motion.div>
        </section>

        {/* Form Section with Glassmorphism */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="bg-white/80 backdrop-blur-xl p-8 rounded-[2.5rem] shadow-[0_20px_50px_rgba(0,174,239,0.1)] border border-[#00AEEF]/10"
        >
          <form onSubmit={handleLogin} className="flex flex-col gap-6">
            <div className="flex flex-col gap-4">
              {/* Error Message */}
              <AnimatePresence>
                {error && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="bg-red-50 text-red-600 p-4 rounded-2xl text-sm font-semibold border border-red-100 text-center"
                  >
                    {error}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Input: Correo Institucional */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold ml-2 uppercase tracking-widest" style={{ color: "#1E3A5F" }}>
                  Correo Institucional
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none">
                    <Mail className="w-5 h-5 text-gray-400 group-focus-within:text-[#00AEEF] transition-colors" />
                  </div>
                  <input
                    type="email"
                    required
                    value={correo}
                    onChange={(e) => setCorreo(e.target.value)}
                    placeholder="ejemplo@ucc.edu.co"
                    className="w-full pl-14 pr-6 py-4 bg-gray-50/60 border-2 border-transparent rounded-2xl focus:bg-white focus:border-[#00AEEF]/50 focus:ring-4 focus:ring-[#00AEEF]/10 outline-none transition-all placeholder:text-gray-300 text-gray-700 font-medium"
                  />
                </div>
              </div>

              {/* Input: Contraseña */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold ml-2 uppercase tracking-widest" style={{ color: "#1E3A5F" }}>
                  Contraseña
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none">
                    <Lock className="w-5 h-5 text-gray-400 group-focus-within:text-[#00AEEF] transition-colors" />
                  </div>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-14 pr-6 py-4 bg-gray-50/60 border-2 border-transparent rounded-2xl focus:bg-white focus:border-[#00AEEF]/50 focus:ring-4 focus:ring-[#00AEEF]/10 outline-none transition-all placeholder:text-gray-300 text-gray-700 font-medium"
                  />
                </div>
              </div>

              <div className="flex justify-between items-center px-1">
                <UCCSwitch />
                <button
                  type="button"
                  className="text-sm font-bold hover:underline decoration-2 underline-offset-4"
                  style={{ color: "#00AEEF" }}
                >
                  ¿Olvidaste tu clave?
                </button>
              </div>
            </div>

            {/* Botón principal — gradiente UCC verde→azul */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-5 text-white font-black rounded-2xl flex items-center justify-center gap-3 transition-all active:scale-[0.98] group disabled:opacity-70 text-lg shadow-lg"
              style={{
                background: "linear-gradient(135deg, #6AB023 0%, #00AEEF 100%)",
                boxShadow: "0 10px 25px rgba(0,174,239,0.3)",
              }}
            >
              {loading ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                <>
                  Entrar al Campus
                  <ChevronRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="text-center space-y-4"
        >
          <p className="text-gray-400 text-sm font-medium">
            ¿No tienes cuenta?{" "}
            <span
              className="font-bold cursor-pointer hover:underline"
              style={{ color: "#6AB023" }}
            >
              Solicita acceso
            </span>
          </p>
          <div className="flex items-center justify-center gap-4 text-[10px] font-bold uppercase tracking-[0.2em]" style={{ color: "#1E3A5F", opacity: 0.4 }}>
            <span>Sostenible</span>
            <div className="w-1 h-1 rounded-full" style={{ background: "#B5D334" }} />
            <span>Inteligente</span>
            <div className="w-1 h-1 rounded-full" style={{ background: "#00AEEF" }} />
            <span>UCC 2026</span>
          </div>
        </motion.div>
      </div>
    </main>
  );
}
