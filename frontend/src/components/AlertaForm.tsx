'use client';

import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Camera, Video, X, Send, AlertTriangle, MapPin, Loader2, CheckCircle2,
} from 'lucide-react';
import { getApiBase } from '@/lib/api';
import { useAuthStore } from '@/store/authStore';

const UCC = {
  green: '#6AB023',
  blue: '#00AEEF',
  navy: '#1E3A5F',
  red: '#EF4444',
};

interface AlertaFormProps {
  onClose: () => void;
  onSuccess?: () => void;
}

const AlertaForm: React.FC<AlertaFormProps> = ({ onClose, onSuccess }) => {
  const [tipo, setTipo] = useState<'seguridad' | 'emergencia' | 'reporte'>('seguridad');
  const [mensaje, setMensaje] = useState('');
  const [ubicacion, setUbicacion] = useState('');
  const [mediaType, setMediaType] = useState<'foto' | 'video' | null>(null);
  const [mediaFile, setMediaFile] = useState<File | null>(null);
  const [mediaPreview, setMediaPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);
  const token = useAuthStore((s) => s.token);

  const handleFileSelect = (file: File, type: 'foto' | 'video') => {
    setMediaFile(file);
    setMediaType(type);
    
    // Crear preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setMediaPreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleRemoveMedia = () => {
    setMediaFile(null);
    setMediaType(null);
    setMediaPreview(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (videoInputRef.current) videoInputRef.current.value = '';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (mensaje.length < 10) {
      setError('El mensaje debe tener al menos 10 caracteres');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('tipo', tipo);
      formData.append('mensaje', mensaje);
      if (ubicacion) formData.append('ubicacion', ubicacion);
      if (mediaType) formData.append('media_type', mediaType);
      if (mediaFile) formData.append('media_file', mediaFile);
      
      const response = await fetch(`${getApiBase()}/api/v1/alertas`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Error al enviar la alerta');
      }
      
      setSuccess(true);
      setTimeout(() => {
        onSuccess?.();
        onClose();
      }, 2000);
      
    } catch (err: any) {
      setError(err.message || 'Error al conectar con el servidor');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-white rounded-3xl p-8 text-center max-w-md mx-auto"
      >
        <div
          className="w-20 h-20 mx-auto mb-4 rounded-full flex items-center justify-center"
          style={{ background: `${UCC.green}20` }}
        >
          <CheckCircle2 size={40} style={{ color: UCC.green }} />
        </div>
        <h3 className="text-2xl font-black mb-2" style={{ color: UCC.navy }}>
          Alerta Enviada
        </h3>
        <p className="text-gray-600 font-medium">
          Tu reporte ha sido enviado al equipo de administración. Recibirás una notificación cuando sea revisado.
        </p>
      </motion.div>
    );
  }

  return (
    <div className="bg-white rounded-3xl p-6 max-w-lg mx-auto relative">
      {/* Botón cerrar */}
      <button
        onClick={onClose}
        className="absolute top-4 right-4 w-8 h-8 rounded-full flex items-center justify-center bg-gray-100 hover:bg-gray-200 transition-colors"
      >
        <X size={18} className="text-gray-600" />
      </button>

      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div
          className="w-12 h-12 rounded-2xl flex items-center justify-center"
          style={{ background: `${UCC.red}20` }}
        >
          <AlertTriangle size={24} style={{ color: UCC.red }} />
        </div>
        <div>
          <h2 className="text-xl font-black" style={{ color: UCC.navy }}>
            Reportar Alerta
          </h2>
          <p className="text-xs text-gray-500 font-medium">
            Notifica situaciones inusuales en el parqueadero
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Error */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="bg-red-50 text-red-600 p-3 rounded-2xl text-sm font-semibold border border-red-100"
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Tipo de alerta */}
        <div className="space-y-2">
          <label className="text-xs font-bold uppercase tracking-widest" style={{ color: UCC.navy }}>
            Tipo de Alerta
          </label>
          <div className="grid grid-cols-3 gap-2">
            {[
              { value: 'seguridad', label: 'Seguridad', color: UCC.blue },
              { value: 'emergencia', label: 'Emergencia', color: UCC.red },
              { value: 'reporte', label: 'Reporte', color: UCC.green },
            ].map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => setTipo(option.value as any)}
                className="py-3 px-2 rounded-xl text-xs font-bold transition-all"
                style={
                  tipo === option.value
                    ? { background: option.color, color: '#fff' }
                    : { background: '#f1f5f9', color: '#64748b' }
                }
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* Mensaje */}
        <div className="space-y-2">
          <label className="text-xs font-bold uppercase tracking-widest" style={{ color: UCC.navy }}>
            Descripción
          </label>
          <textarea
            required
            minLength={10}
            value={mensaje}
            onChange={(e) => setMensaje(e.target.value)}
            placeholder="Describe qué está ocurriendo..."
            rows={4}
            className="w-full px-4 py-3 rounded-2xl text-sm font-medium text-gray-700 placeholder:text-gray-300 outline-none transition-all bg-gray-50 border-2 border-transparent focus:border-[#00AEEF50] focus:bg-white resize-none"
          />
          <p className="text-xs text-gray-400 text-right">
            {mensaje.length} / 500 caracteres
          </p>
        </div>

        {/* Ubicación */}
        <div className="space-y-2">
          <label className="text-xs font-bold uppercase tracking-widest" style={{ color: UCC.navy }}>
            Ubicación <span className="text-gray-400 normal-case">(Opcional)</span>
          </label>
          <div className="relative">
            <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-300" />
            <input
              type="text"
              value={ubicacion}
              onChange={(e) => setUbicacion(e.target.value)}
              placeholder="Ej: Zona A, Puesto 5"
              className="w-full pl-11 pr-4 py-3 rounded-2xl text-sm font-medium text-gray-700 placeholder:text-gray-300 outline-none transition-all bg-gray-50 border-2 border-transparent focus:border-[#00AEEF50] focus:bg-white"
            />
          </div>
        </div>

        {/* Media */}
        <div className="space-y-2">
          <label className="text-xs font-bold uppercase tracking-widest" style={{ color: UCC.navy }}>
            Adjuntar Evidencia <span className="text-gray-400 normal-case">(Opcional)</span>
          </label>
          
          {!mediaFile ? (
            <div className="grid grid-cols-2 gap-2">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0], 'foto')}
                className="hidden"
              />
              <input
                ref={videoInputRef}
                type="file"
                accept="video/*"
                onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0], 'video')}
                className="hidden"
              />
              
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="py-4 rounded-2xl flex flex-col items-center justify-center gap-2 transition-all hover:scale-[1.02]"
                style={{ background: `${UCC.blue}10`, color: UCC.blue }}
              >
                <Camera size={24} />
                <span className="text-xs font-bold">Foto</span>
              </button>
              
              <button
                type="button"
                onClick={() => videoInputRef.current?.click()}
                className="py-4 rounded-2xl flex flex-col items-center justify-center gap-2 transition-all hover:scale-[1.02]"
                style={{ background: `${UCC.green}10`, color: UCC.green }}
              >
                <Video size={24} />
                <span className="text-xs font-bold">Video</span>
              </button>
            </div>
          ) : (
            <div className="relative rounded-2xl overflow-hidden border-2 border-gray-200">
              {mediaType === 'foto' && mediaPreview && (
                <img src={mediaPreview} alt="Preview" className="w-full h-48 object-cover" />
              )}
              {mediaType === 'video' && mediaPreview && (
                <video src={mediaPreview} className="w-full h-48 object-cover" controls />
              )}
              <button
                type="button"
                onClick={handleRemoveMedia}
                className="absolute top-2 right-2 w-8 h-8 rounded-full bg-red-500 text-white flex items-center justify-center hover:bg-red-600 transition-colors"
              >
                <X size={16} />
              </button>
            </div>
          )}
        </div>

        {/* Botón enviar */}
        <button
          type="submit"
          disabled={loading || mensaje.length < 10}
          className="w-full py-4 text-white font-black rounded-2xl flex items-center justify-center gap-2 transition-all active:scale-[0.98] disabled:opacity-60"
          style={{
            background: `linear-gradient(135deg, ${UCC.red}, #dc2626)`,
            boxShadow: '0 8px 24px rgba(239,68,68,0.30)',
          }}
        >
          {loading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              <Send size={20} />
              Enviar Alerta
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default AlertaForm;
