/** @type {import('next').NextConfig} */
const nextConfig = {
  // Ignorar errores de TypeScript y ESLint durante el build de Docker
  // Los errores se siguen viendo en el editor (VSCode), solo se omiten en producción
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig;
