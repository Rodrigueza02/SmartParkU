/** @type {import('next').NextConfig} */
const nextConfig = {
  // Modo standalone: genera una carpeta .next/standalone lista para producción
  // Evita el export estático que falla con páginas dinámicas como /reset-password
  output: 'standalone',

  // Ignorar errores de TypeScript y ESLint durante el build
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig;
