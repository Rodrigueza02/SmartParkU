import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';
import '../constants/api.dart';
import '../models/parking_slot_model.dart';

class ParkingService {
  WebSocketChannel? _channel;
  final _controller = StreamController<Map<String, ParkingSlot>>.broadcast();

  Stream<Map<String, ParkingSlot>> get slotsStream => _controller.stream;

  /// Conecta el WebSocket al backend y emite actualizaciones al stream.
  void connect(String token) {
    _channel?.sink.close();
    // El WS de parking es público, token no requerido para conectarse
    _channel = WebSocketChannel.connect(Uri.parse(ApiConstants.wsUrl));
    _channel!.stream.listen(
      (raw) {
        try {
          final data = jsonDecode(raw as String) as Map<String, dynamic>;
          if (data.containsKey('ping')) return;
          final espacios = data['espacios'] as Map<String, dynamic>? ?? {};
          final slots = espacios.map(
            (id, info) => MapEntry(
              id,
              ParkingSlot.fromJson(id, info as Map<String, dynamic>),
            ),
          );
          _controller.add(slots);
        } catch (_) {}
      },
      onError: (_) {},
      cancelOnError: false,
    );
  }

  void disconnect() {
    _channel?.sink.close();
    _channel = null;
  }

  void dispose() {
    disconnect();
    _controller.close();
  }

  /// Genera un QR de acceso para el usuario.
  Future<Map<String, dynamic>> generarQR({
    required int idUsuario,
    required String token,
    int? idVehiculo,
  }) async {
    final body = <String, dynamic>{'id_usuario': idUsuario};
    if (idVehiculo != null) body['id_vehiculo'] = idVehiculo;

    final response = await http.post(
      Uri.parse(ApiConstants.qrGenerar),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode(body),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    }
    throw Exception(_detail(response.body));
  }

  /// Escanea/valida un token QR y registra el acceso.
  Future<Map<String, dynamic>> escanearQR({
    required String qrToken,
    required String token,
  }) async {
    final response = await http.post(
      Uri.parse(ApiConstants.qrEscanear),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({'qr_token': qrToken}),
    );

    if (response.statusCode == 201) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    }

    final detail = _detail(response.body);
    if (response.statusCode == 409) throw Exception('Espacio ocupado: $detail');
    if (response.statusCode == 410) throw Exception('QR expirado: $detail');
    if (response.statusCode == 401) throw Exception('QR inválido o manipulado.');
    throw Exception(detail);
  }

  /// Registra la hora de salida y libera el espacio.
  Future<Map<String, dynamic>> registrarSalida({
    required int accesoId,
    required String token,
  }) async {
    final response = await http.post(
      Uri.parse('${ApiConstants.accesoSalida}/$accesoId/salida'),
      headers: {'Authorization': 'Bearer $token'},
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    }
    throw Exception(_detail(response.body));
  }

  String _detail(String body) {
    try {
      final data = jsonDecode(body) as Map<String, dynamic>;
      return data['detail'] as String? ?? 'Error desconocido';
    } catch (_) {
      return 'Error al conectar con el servidor';
    }
  }
}
