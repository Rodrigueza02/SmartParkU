/**
 * Obtiene la URL base del backend.
 * Usa NEXT_PUBLIC_API_URL si está definida (build time),
 * de lo contrario usa el hostname del navegador (runtime).
 */
export function getApiBase(): string {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (typeof window !== 'undefined') {
    return `http://${window.location.hostname}:8000`;
  }
  return 'http://localhost:8000';
}
