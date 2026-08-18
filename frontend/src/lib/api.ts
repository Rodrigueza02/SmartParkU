/**
 * Obtiene la URL base del backend dinámicamente.
 * Funciona en cualquier red/IP sin necesidad de rebuild.
 * En el servidor (SSR) usa localhost; en el cliente usa el hostname actual.
 */
export function getApiBase(): string {
  if (typeof window === 'undefined') {
    return 'http://localhost:8000';
  }
  return `http://${window.location.hostname}:8000`;
}
