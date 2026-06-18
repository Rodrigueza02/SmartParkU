/// Constantes de API para SmartParkU Mobile
class ApiConstants {
  // Cambiar a la IP real cuando se pruebe en dispositivo físico.
  // En emulador Android usar 10.0.2.2 (que apunta al localhost del host).
  static const String baseUrl = 'http://10.0.2.2:8000';
  static const String wsUrl   = 'ws://10.0.2.2:8000/api/v1/parking/ws/parking';

  // Endpoints
  static const String login          = '$baseUrl/api/v1/auth/login';
  static const String forgotPassword = '$baseUrl/api/v1/auth/forgot-password';
  static const String resetPassword  = '$baseUrl/api/v1/auth/reset-password';
  static const String qrGenerar      = '$baseUrl/api/v1/qr/generar';
  static const String qrEscanear     = '$baseUrl/api/v1/qr/escanear';
  static const String parkingSlots   = '$baseUrl/api/v1/parking/slots';
  static const String accesoSalida   = '$baseUrl/api/v1/accesos'; // + /{id}/salida
}
