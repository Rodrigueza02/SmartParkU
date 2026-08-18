"use client";

import { Suspense } from "react";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { getApiBase } from "@/lib/api";
import { Lock, ChevronLeft, Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";

function ResetPasswordContent() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  useEffect(() => {
    if (!token) {
      setError("Token no encontrado. Por favor, solicita un nuevo enlace de recuperación.");
    }
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      setError("Las contraseñas no coinciden");
      return;
    }

    if (password.length < 6) {
      setError("La contraseña debe tener al menos 6 caracteres");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${getApiBase()}/api/v1/auth/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          token: token,
          nueva_password: password 
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Error al restablecer la contraseña");
      }

      setSuccess(true);
    } catch (err: any) {
      setError(err.message || "Error al conectar con el servidor");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-8" style={{ background: '#F4FBFF' }}>
      {/* Burbujas de fondo */}
      <div className="absolute top-[-10%] right-[-5%] w-72 h-72 bg-[#00AEEF]/8 rounded-full blur-[80px]" />
      <div className="absolute bottom-[-10%] left-[-5%] w-72 h-72 bg-[#6AB023]/8 rounded-full blur-[80px]" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md relative z-10"
      >
        {/* Botón de regreso */}
        <button
          onClick={() => router.push("/")}
          className="mb-6 flex items-center gap-2 text-sm font-bold transition-colors"
          style={{ color: "#00AEEF" }}
        >
          <ChevronLeft className="w-4 h-4" />
          Volver al login
        </button>

        {/* Tarjeta principal */}
        <div
          className="bg-white rounded-3xl p-8 shadow-xl border"
          style={{ borderColor: "#00AEEF20", boxShadow: "0 20px 60px rgba(0,174,239,0.10)" }}
        >
          {/* Barra de acento */}
          <div
            className="h-1 w-16 rounded-full mb-6 mx-auto"
            style={{ background: "linear-gradient(90deg, #6AB023, #00AEEF)" }}
          />

          {/* Título */}
          <div className="text-center mb-6">
            <h1 className="text-2xl font-black mb-2" style={{ color: "#1E3A5F" }}>
              Restablecer contraseña
            </h1>
            <p className="text-sm text-gray-500 font-medium">
              Ingresa tu nueva contraseña para acceder a tu cuenta.
            </p>
          </div>

          <AnimatePresence mode="wait">
            {!token && error ? (
              <motion.div
                key="no-token"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="text-center py-8"
              >
                <AlertCircle className="w-16 h-16 mx-auto mb-4 text-red-400" />
                <h2 className="text-lg font-black mb-2" style={{ color: "#1E3A5F" }}>
                  Token no válido
                </h2>
                <p className="text-sm text-gray-500 font-medium mb-6">
                  {error}
                </p>
                <button
                  onClick={() => router.push("/forgot-password")}
                  className="w-full py-3 text-white font-bold rounded-2xl transition-all active:scale-[0.98]"
                  style={{
                    background: "linear-gradient(135deg, #6AB023 0%, #00AEEF 100%)",
                    boxShadow: "0 8px 24px rgba(0,174,239,0.35)",
                  }}
                >
                  Solicitar nuevo enlace
                </button>
              </motion.div>
            ) : success ? (
              <motion.div
                key="success"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="text-center py-8"
              >
                <CheckCircle2 className="w-16 h-16 mx-auto mb-4" style={{ color: "#6AB023" }} />
                <h2 className="text-lg font-black mb-2" style={{ color: "#1E3A5F" }}>
                  ¡Contraseña actualizada!
                </h2>
                <p className="text-sm text-gray-500 font-medium mb-6">
                  Ya puedes iniciar sesión con tu nueva contraseña.
                </p>
                <button
                  onClick={() => router.push("/")}
                  className="w-full py-3 text-white font-bold rounded-2xl transition-all active:scale-[0.98]"
                  style={{
                    background: "linear-gradient(135deg, #6AB023 0%, #00AEEF 100%)",
                    boxShadow: "0 8px 24px rgba(0,174,239,0.35)",
                  }}
                >
                  Ir al login
                </button>
              </motion.div>
            ) : (
              <motion.form
                key="form"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onSubmit={handleSubmit}
                className="flex flex-col gap-5"
              >
                <AnimatePresence>
                  {error && token && (
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

                {/* Nueva contraseña */}
                <div className="space-y-1.5">
                  <label
                    className="text-xs font-bold ml-1 uppercase tracking-widest block"
                    style={{ color: "#1E3A5F" }}
                  >
                    Nueva Contraseña
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
                      onFocus={(e) => {
                        e.target.style.borderColor = "#00AEEF50";
                        e.target.style.background = "#fff";
                      }}
                      onBlur={(e) => {
                        e.target.style.borderColor = "transparent";
                        e.target.style.background = "#f9fafb";
                      }}
                    />
                  </div>
                </div>

                {/* Confirmar contraseña */}
                <div className="space-y-1.5">
                  <label
                    className="text-xs font-bold ml-1 uppercase tracking-widest block"
                    style={{ color: "#1E3A5F" }}
                  >
                    Confirmar Contraseña
                  </label>
                  <div className="relative group">
                    <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                      <Lock className="w-4 h-4 text-gray-300 group-focus-within:text-[#00AEEF] transition-colors" />
                    </div>
                    <input
                      type="password"
                      required
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="••••••••"
                      className="w-full pl-11 pr-4 py-3.5 rounded-2xl text-sm font-medium text-gray-700 placeholder:text-gray-300 outline-none transition-all bg-gray-50 border-2 border-transparent"
                      onFocus={(e) => {
                        e.target.style.borderColor = "#00AEEF50";
                        e.target.style.background = "#fff";
                      }}
                      onBlur={(e) => {
                        e.target.style.borderColor = "transparent";
                        e.target.style.background = "#f9fafb";
                      }}
                    />
                  </div>
                </div>

                {/* Botón submit */}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-4 text-white font-black rounded-2xl flex items-center justify-center gap-2 transition-all active:scale-[0.98] disabled:opacity-60 text-base mt-2"
                  style={{
                    background: "linear-gradient(135deg, #6AB023 0%, #00AEEF 100%)",
                    boxShadow: "0 8px 24px rgba(0,174,239,0.35)",
                  }}
                >
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    "Restablecer contraseña"
                  )}
                </button>
              </motion.form>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </main>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center" style={{ background: '#F4FBFF' }}><Loader2 className="w-8 h-8 animate-spin text-[#00AEEF]" /></div>}>
      <ResetPasswordContent />
    </Suspense>
  );
}
