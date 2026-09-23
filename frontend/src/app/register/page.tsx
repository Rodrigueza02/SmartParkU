"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Mail, Lock, User as UserIcon, ChevronRight, Loader2, ArrowLeft, 
  IdCard, Car, Bike, Zap, Users, Briefcase, UserPlus, CreditCard 
} from "lucide-react";
import { useRouter } from "next/navigation";
import { getApiBase } from "@/lib/api";

const ROLES_DISPONIBLES = [
  { value: 'Estudiante', label: 'Estudiante', icon: UserPlus, color: '#00AEEF' },
  { value: 'Docente', label: 'Docente', icon: Briefcase, color: '#6AB023' },
  { value: 'Administrativo', label: 'Administrativo', icon: Users, color: '#1E3A5F' },
  { value: 'Invitado', label: 'Invitado', icon: UserIcon, color: '#B5D334' },
  { value: 'VIP', label: 'VIP', icon: CreditCard, color: '#1E3A5F' },
] as const;

const TIPOS_VEHICULO = [
  { value: 'carro', label: 'Carro', icon: Car, color: '#00AEEF' },
  { value: 'moto', label: 'Motocicleta', icon: Bike, color: '#6AB023' },
  { value: 'bicicleta', label: 'Bicicleta', icon: Zap, color: '#B5D334' },
  { value: 'vip', label: 'VIP', icon: Car, color: '#1E3A5F' },
] as const;

export default function RegisterPage() {
  const [nombre, setNombre] = useState("");
  const [correo, setCorreo] = useState("");
  const [password, setPassword] = useState("");
  const [carnetId, setCarnetId] = useState("");
  const [rol, setRol] = useState<string>("Estudiante");
  const [tipoVehiculo, setTipoVehiculo] = useState<string>("");
  const [placaVehiculo, setPlacaVehiculo] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    
    // Validación: si se seleccionó tipo de vehículo, la placa es obligatoria
    if (tipoVehiculo && !placaVehiculo) {
      setError("Si seleccionas un tipo de vehículo, debes ingresar la placa");
      setLoading(false);
      return;
    }
    
    try {
      const body: any = {
        nombre,
        correo,
        password,
        rol,
      };
      
      if (carnetId) body.carnet_id = carnetId;
      if (tipoVehiculo) body.tipo_vehiculo = tipoVehiculo;
      if (placaVehiculo) body.placa_vehiculo = placaVehiculo;
      
      const response = await fetch(`${getApiBase()}/api/v1/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || "Error al crear la cuenta");
      }
      
      setSuccess(true);
      setTimeout(() => {
        router.push("/");
      }, 2500);
      
    } catch (err: any) {
      setError(err.message || "Error al conectar con el servidor");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#F4FBFF' }}>
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="bg-white rounded-3xl p-8 shadow-xl text-center max-w-md"
        >
          <div className="w-20 h-20 mx-auto mb-4 rounded-full flex items-center justify-center"
               style={{ background: 'linear-gradient(135deg, #6AB023, #00AEEF)' }}>
            <UserIcon className="w-10 h-10 text-white" />
          </div>
          <h2 className="text-2xl font-black mb-2" style={{ color: '#1E3A5F' }}>
            ¡Cuenta Creada!
          </h2>
          <p className="text-gray-600 font-medium">
            Tu cuenta ha sido creada exitosamente. Redirigiendo al login...
          </p>
        </motion.div>
      </div>
    );
  }

  return (
    <main className="min-h-screen flex">
      {/* Panel izquierdo - branding (solo desktop) */}
      <div
        className="hidden lg:flex lg:w-1/2 flex-col items-center justify-center p-16 relative overflow-hidden"
        style={{ background: "linear-gradient(145deg, #1E3A5F 0%, #00AEEF 60%, #6AB023 100%)" }}
      >
        <div className="absolute top-[-80px] left-[-80px] w-72 h-72 rounded-full border-[40px] border-white/10" />
        <div className="absolute bottom-[-60px] right-[-60px] w-56 h-56 rounded-full border-[30px] border-white/10" />
        
        <div className="relative z-10 text-center space-y-6">
          <h1 className="text-7xl font-black tracking-tighter text-white drop-shadow-lg">
            Smart<span className="text-[#B5D334]">Park</span>U
          </h1>
          <p className="text-white/80 text-xl font-medium">
            Únete a la comunidad UCC
          </p>
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 mt-8">
            <p className="text-white text-sm leading-relaxed">
              Crea tu cuenta para acceder al sistema de parqueadero inteligente
              de la Universidad Cooperativa de Colombia - Campus Pasto
            </p>
          </div>
        </div>
      </div>

      {/* Panel derecho - formulario */}
      <div className="flex-1 flex flex-col items-center justify-center p-8 bg-[#F8FAFC] relative overflow-hidden">
        <div className="absolute top-[-10%] right-[-5%] w-72 h-72 bg-[#00AEEF]/8 rounded-full blur-[80px]" />
        <div className="absolute bottom-[-10%] left-[-5%] w-72 h-72 bg-[#6AB023]/8 rounded-full blur-[80px]" />

        <div className="w-full max-w-md relative z-10 max-h-screen overflow-y-auto py-6">
          {/* Botón volver */}
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={() => router.push("/")}
            className="flex items-center gap-2 mb-6 text-sm font-bold"
            style={{ color: '#00AEEF' }}
          >
            <ArrowLeft size={18} />
            Volver al login
          </motion.button>

          {/* Tarjeta de formulario */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-3xl p-8 shadow-xl border"
            style={{ borderColor: "#00AEEF20", boxShadow: "0 20px 60px rgba(0,174,239,0.10)" }}
          >
            <div className="text-center mb-6">
              <h2 className="text-3xl font-black" style={{ color: '#1E3A5F' }}>
                Crear Cuenta
              </h2>
              <p className="text-gray-500 text-sm mt-2 font-medium">
                Completa tus datos para registrarte
              </p>
            </div>

            <form onSubmit={handleRegister} className="flex flex-col gap-4">
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

              {/* Nombre completo */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold ml-1 uppercase tracking-widest block" style={{ color: "#1E3A5F" }}>
                  Nombre Completo *
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                    <UserIcon className="w-4 h-4 text-gray-300 group-focus-within:text-[#00AEEF] transition-colors" />
                  </div>
                  <input
                    type="text"
                    required
                    minLength={3}
                    value={nombre}
                    onChange={(e) => setNombre(e.target.value)}
                    placeholder="Juan Pérez García"
                    className="w-full pl-11 pr-4 py-3.5 rounded-2xl text-sm font-medium text-gray-700 placeholder:text-gray-300 outline-none transition-all bg-gray-50 border-2 border-transparent focus:border-[#00AEEF50] focus:bg-white"
                  />
                </div>
              </div>

              {/* Correo */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold ml-1 uppercase tracking-widest block" style={{ color: "#1E3A5F" }}>
                  Correo Institucional *
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
                    className="w-full pl-11 pr-4 py-3.5 rounded-2xl text-sm font-medium text-gray-700 placeholder:text-gray-300 outline-none transition-all bg-gray-50 border-2 border-transparent focus:border-[#00AEEF50] focus:bg-white"
                  />
                </div>
              </div>

              {/* Carnet ID */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold ml-1 uppercase tracking-widest block" style={{ color: "#1E3A5F" }}>
                  Documento / Carnet <span className="text-gray-400 normal-case">(Opcional)</span>
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                    <IdCard className="w-4 h-4 text-gray-300 group-focus-within:text-[#00AEEF] transition-colors" />
                  </div>
                  <input
                    type="text"
                    value={carnetId}
                    onChange={(e) => setCarnetId(e.target.value)}
                    placeholder="123456789"
                    className="w-full pl-11 pr-4 py-3.5 rounded-2xl text-sm font-medium text-gray-700 placeholder:text-gray-300 outline-none transition-all bg-gray-50 border-2 border-transparent focus:border-[#00AEEF50] focus:bg-white"
                  />
                </div>
              </div>

              {/* Contraseña */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold ml-1 uppercase tracking-widest block" style={{ color: "#1E3A5F" }}>
                  Contraseña *
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                    <Lock className="w-4 h-4 text-gray-300 group-focus-within:text-[#00AEEF] transition-colors" />
                  </div>
                  <input
                    type="password"
                    required
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Mínimo 6 caracteres"
                    className="w-full pl-11 pr-4 py-3.5 rounded-2xl text-sm font-medium text-gray-700 placeholder:text-gray-300 outline-none transition-all bg-gray-50 border-2 border-transparent focus:border-[#00AEEF50] focus:bg-white"
                  />
                </div>
              </div>

              {/* Selector de Rol */}
              <div className="space-y-2">
                <label className="text-xs font-bold ml-1 uppercase tracking-widest block" style={{ color: "#1E3A5F" }}>
                  Rol *
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {ROLES_DISPONIBLES.map((rolItem) => {
                    const Icon = rolItem.icon;
                    const isSelected = rol === rolItem.value;
                    return (
                      <motion.button
                        key={rolItem.value}
                        type="button"
                        whileTap={{ scale: 0.96 }}
                        onClick={() => setRol(rolItem.value)}
                        className="flex flex-col items-center gap-1.5 p-3 rounded-xl border-2 transition-all"
                        style={
                          isSelected
                            ? {
                                borderColor: rolItem.color,
                                background: `${rolItem.color}15`,
                              }
                            : {
                                borderColor: '#e2e8f0',
                                background: '#fff',
                              }
                        }
                      >
                        <Icon
                          size={20}
                          style={{ color: isSelected ? rolItem.color : '#94a3b8' }}
                          strokeWidth={isSelected ? 2.5 : 2}
                        />
                        <span
                          className="text-[10px] font-bold text-center leading-tight"
                          style={{ color: isSelected ? rolItem.color : '#94a3b8' }}
                        >
                          {rolItem.label}
                        </span>
                      </motion.button>
                    );
                  })}
                </div>
              </div>

              {/* Tipo de Vehículo (Opcional) */}
              <div className="space-y-2">
                <label className="text-xs font-bold ml-1 uppercase tracking-widest block" style={{ color: "#1E3A5F" }}>
                  Tipo de Vehículo <span className="text-gray-400 normal-case">(Opcional)</span>
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {TIPOS_VEHICULO.map((tipo) => {
                    const Icon = tipo.icon;
                    const isSelected = tipoVehiculo === tipo.value;
                    return (
                      <motion.button
                        key={tipo.value}
                        type="button"
                        whileTap={{ scale: 0.96 }}
                        onClick={() => setTipoVehiculo(isSelected ? "" : tipo.value)}
                        className="flex flex-col items-center gap-1.5 p-3 rounded-xl border-2 transition-all"
                        style={
                          isSelected
                            ? {
                                borderColor: tipo.color,
                                background: `${tipo.color}15`,
                              }
                            : {
                                borderColor: '#e2e8f0',
                                background: '#fff',
                              }
                        }
                      >
                        <Icon
                          size={20}
                          style={{ color: isSelected ? tipo.color : '#94a3b8' }}
                          strokeWidth={isSelected ? 2.5 : 2}
                        />
                        <span
                          className="text-[10px] font-bold"
                          style={{ color: isSelected ? tipo.color : '#94a3b8' }}
                        >
                          {tipo.label}
                        </span>
                      </motion.button>
                    );
                  })}
                </div>
              </div>

              {/* Placa del Vehículo (condicional) */}
              {tipoVehiculo && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-1.5"
                >
                  <label className="text-xs font-bold ml-1 uppercase tracking-widest block" style={{ color: "#1E3A5F" }}>
                    Placa del Vehículo *
                  </label>
                  <div className="relative group">
                    <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                      <CreditCard className="w-4 h-4 text-gray-300 group-focus-within:text-[#00AEEF] transition-colors" />
                    </div>
                    <input
                      type="text"
                      required={!!tipoVehiculo}
                      value={placaVehiculo}
                      onChange={(e) => setPlacaVehiculo(e.target.value.toUpperCase())}
                      placeholder="ABC123"
                      className="w-full pl-11 pr-4 py-3.5 rounded-2xl text-sm font-medium text-gray-700 placeholder:text-gray-300 outline-none transition-all bg-gray-50 border-2 border-transparent focus:border-[#00AEEF50] focus:bg-white uppercase"
                    />
                  </div>
                </motion.div>
              )}

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
                  <>
                    Crear Cuenta
                    <ChevronRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </form>
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-center text-sm text-gray-400 font-medium mt-6"
          >
            ¿Ya tienes cuenta?{" "}
            <button
              onClick={() => router.push("/")}
              className="font-bold hover:underline"
              style={{ color: "#00AEEF" }}
            >
              Inicia sesión
            </button>
          </motion.p>
        </div>
      </div>
    </main>
  );
}
