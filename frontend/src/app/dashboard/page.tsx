"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import StudentDashboard from "@/components/StudentDashboard";

export default function DashboardPage() {
  const { user, token } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    // Redirección si no hay token (seguridad básica)
    if (!token) {
      router.push("/");
    }
  }, [token, router]);

  if (!token || !user) {
    return (
      <div className="min-h-screen bg-[#FDFDFD] flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center gap-4">
          <div className="w-12 h-12 bg-[#A3E4D7]/20 rounded-full" />
          <p className="text-slate-400 text-sm font-medium">Cargando SmartParkU...</p>
        </div>
      </div>
    );
  }

  // Si el rol es Estudiante, mostramos el dashboard especializado
  return <StudentDashboard user={user} />;
}
