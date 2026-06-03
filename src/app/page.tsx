"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mail, Lock, ChevronRight, Loader2 } from "lucide-react";
import ParkingIllustration from "@/components/ParkingIllustration";
import UCCSwitch from "@/components/UCCSwitch";
import StudentDashboard from "@/components/StudentDashboard";
import { useAuthStore } from "@/store/authStore";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function LoginPage() {
  const [correo, setCorreo] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const { token, user, setAuth } = useAuthStore();
  const router = useRouter();

  // Redirigir según rol después del login
  useEffect(() => {
    if (!token || !user) return;
    if (user.rol === "SuperAdmin" || user.rol === "Administrativo") {
      router.push("/admin/dashboard");
    }
  }, [token, user, router]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await fetch("http://localhost:8000/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ correo, password }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Error al iniciar sesión");
      const { access_token, nombre, rol, estado } = data;
      setAuth(access_token, { nombre, rol, estado });
    } catch (err: any) {
      setError(err.message || "Error al conectar con el servidor");
    } finally {
      setLoading(false);
    }
  };

  // Estudiante → dashboard embebido en la misma página
  if (token && user?.rol === "Estudiante") return <StudentDashboard user={user} />;

  // Admin/SuperAdmin → useEffect ya hizo el push, mostrar loader mientras redirige
  if (token && (user?.rol === "SuperAdmin" || user?.rol === "Administrativo")) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#F4FBFF' }}>
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-10 h-10 animate-spin" style={{ color: '#00AEEF' }} />
          <p className="text-sm font-bold" style={{ color: '#1E3A5F' }}>Entrando al panel de administración...</p>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen flex">
      {/* ── Panel izquierdo — branding UCC (solo desktop) ── */}
      <div
        className="hidden lg:flex lg:w-1/2 flex-col items-center justify-center p-16 relative overflow-hidden"
        style={{ background: "linear-gradient(145deg, #1E3A5F 0%, #00AEEF 60%, #6AB023 100%)" }}
      >
        {/* Círculos decorativos inspirados en el logo UCC */}
        <div className="absolute top-[-80px] left-[-80px] w-72 h-72 rounded-full border-[40px] border-white/10" />
        <div className="absolute bottom-[-60px] right-[-60px] w-56 h-56 rounded-full border-[30px] border-white/10" />
        <div className="absolute top-1/2 right-[-30px] w-24 h-24 rounded-full bg-[#B5D334]/30" />

        <div className="relative z-10 text-center space-y-8">
          <div>
            <h1 className="text-7xl font-black tracking-tighter text-white drop-shadow-lg">
              Smart<span className="text-[#B5D334]">Park</span>U
            </h1>
            <p className="text-white/70 text-xl font-medium mt-3">
              Parqueo inteligente para la comunidad UCC
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4 text-left mt-8">
            {[
              { label: "Espacios en tiempo real", val: "10" },
              { label: "Conexión IoT activa", val: "MQTT" },
              { label: "Comunidad UCC", val: "2026" },
              { label: "Huella CO₂", val: "↓ Verde" },
            ].map((item) => (
              <div
                key={item.label}
                className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20"
              >
                <p className="text-2xl font-black text-white">{item.val}</p>
                <p className="text-white/60 text-xs font-medium mt-1">{item.label}</p>
              </div>
            ))}
          </div>

          <p className="text-white/40 text-xs uppercase tracking-[0.3em] font-bold mt-8">
            Universidad Cooperativa de Colombia — Pasto
          </p>
        </div>
      </div>

      {/* ── Panel derecho — formulario ── */}
      <div className="flex-1 flex flex-col items-center justify-center p-8 bg-[#F8FAFC] relative overflow-hidden">
        {/* Burbujas de fondo sutiles */}
        <div className="absolute top-[-10%] right-[-5%] w-72 h-72 bg-[#00AEEF]/8 rounded-full blur-[80px]" />
        <div className="absolute bottom-[-10%] left-[-5%] w-72 h-72 bg-[#6AB023]/8 rounded-full blur-[80px]" />

        <div className="w-full max-w-sm relative z-10 flex flex-col gap-8">

          {/* Ilustración + título (visible siempre) */}
          <section className="flex flex-col items-center text-center">
            <ParkingIllustration />
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="mt-5"
            >
              <h1 className="text-4xl font-black tracking-tighter">
                <span style={{ color: "#6AB023" }}>Smart</span>
                <span style={{ color: "#00AEEF" }}>Park</span>
                <span
                  style={{ color: "#00AEEF" }}
                  className="inline-block hover:rotate-12 transition-transform cursor-default"
                >
                  U
                </span>
              </h1>
              <p className="mt-2 font-medium text-base" style={{ color: "#1E3A5F", opacity: 0.6 }}>
                Ingresa a tu campus inteligente
              </p>
            </motion.div>
          </section>

          {/* Tarjeta de formulario */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-white rounded-3xl p-8 shadow-xl border"
            style={{ borderColor: "#00AEEF20", boxShadow: "0 20px 60px rgba(0,174,239,0.10)" }}
          >
            {/* Barra de acento superior */}
            <div
              className="h-1 w-16 rounded-full mb-6 mx-auto"
              style={{ background: "linear-gradient(90deg, #6AB023, #00AEEF)" }}
            />

            <form onSubmit={handleLogin} className="flex flex-col gap-5">
              <AnimatePresence>
                {error && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0 }}
                    className="bg-red-50 text-red-600 p-3 rounded-2xl text-sm font-semibold border border-red-100 text-center"
                  >
                    {error}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Correo */}
              <div className="space-y-1.5">
                <label
                  className="text-xs font-bold ml-1 uppercase tracking-widest block"
                  style={{ color: "#1E3A5F" }}
                >
                  Correo Institucional
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                    <Mail className="w-4 h-4 text-gray-300 group-focus-within:text-[#00AEEF] transition-colors" />
                  </div>
                  <input
                    type="email"
                    required
                    value={correo}
                    onChange={(e) => setCorreo(e.target.value)}
                    placeholder="ejemplo@ucc.edu.co"
                    className="w-full pl-11 pr-4 py-3.5 rounded-2xl text-sm font-medium text-gray-700 placeholder:text-gray-300 outline-none transition-all bg-gray-50 border-2 border-transparent"
                    style={{ ["--tw-ring-color" as any]: "#00AEEF" }}
                    onFocus={(e) => { e.target.style.borderColor = "#00AEEF50"; e.target.style.background = "#fff"; }}
                    onBlur={(e) => { e.target.style.borderColor = "transparent"; e.target.style.background = "#f9fafb"; }}
                  />
                </div>
              </div>

              {/* Contraseña */}
              <div className="space-y-1.5">
                <label
                  className="text-xs font-bold ml-1 uppercase tracking-widest block"
                  style={{ color: "#1E3A5F" }}
                >
                  Contraseña
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                    <Lock className="w-4 h-4 text-gray-300 group-focus-within:text-[#00AEEF] transition-colors" />
                  </div>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-11 pr-4 py-3.5 rounded-2xl text-sm font-medium text-gray-700 placeholder:text-gray-300 outline-none transition-all bg-gray-50 border-2 border-transparent"
                    onFocus={(e) => { e.target.style.borderColor = "#00AEEF50"; e.target.style.background = "#fff"; }}
                    onBlur={(e) => { e.target.style.borderColor = "transparent"; e.target.style.background = "#f9fafb"; }}
                  />
                </div>
              </div>

              <div className="flex justify-between items-center">
                <UCCSwitch />
                <button
                  type="button"
                  className="text-xs font-bold hover:underline underline-offset-4 ml-3 whitespace-nowrap"
                  style={{ color: "#00AEEF" }}
                >
                  ¿Olvidaste tu clave?
                </button>
              </div>

              {/* Botón submit */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 text-white font-black rounded-2xl flex items-center justify-center gap-2 transition-all active:scale-[0.98] disabled:opacity-60 text-base mt-1"
                style={{
                  background: "linear-gradient(135deg, #6AB023 0%, #00AEEF 100%)",
                  boxShadow: "0 8px 24px rgba(0,174,239,0.35)",
                }}
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    Entrar al Campus
                    <ChevronRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </form>
          </motion.div>

          {/* Footer */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
            className="text-center text-sm text-gray-400 font-medium"
          >
            ¿No tienes cuenta?{" "}
            <span className="font-bold cursor-pointer hover:underline" style={{ color: "#6AB023" }}>
              Solicita acceso
            </span>
          </motion.p>
        </div>
      </div>
    </main>
  );
}
