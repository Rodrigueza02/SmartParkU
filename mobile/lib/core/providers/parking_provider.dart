import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/parking_slot_model.dart';
import '../services/parking_service.dart';

class ParkingProvider extends ChangeNotifier {
  final ParkingService _service = ParkingService();

  Map<String, ParkingSlot> _slots = {};
  bool _connected = false;
  StreamSubscription? _sub;

  Map<String, ParkingSlot> get slots => _slots;
  bool get connected => _connected;

  int get totalLibre   => _slots.values.where((s) => s.isLibre).length;
  int get totalOcupado => _slots.values.where((s) => !s.isLibre).length;

  void connect(String token) {
    _service.connect(token);
    _connected = true;
    _sub = _service.slotsStream.listen((slots) {
      _slots = slots;
      notifyListeners();
    });
    notifyListeners();
  }

  void disconnect() {
    _sub?.cancel();
    _service.disconnect();
    _connected = false;
    notifyListeners();
  }

  Future<Map<String, dynamic>> generarQR({
    required int idUsuario,
    required String token,
    int? idVehiculo,
  }) =>
      _service.generarQR(idUsuario: idUsuario, token: token, idVehiculo: idVehiculo);

  Future<Map<String, dynamic>> escanearQR({
    required String qrToken,
    required String token,
  }) =>
      _service.escanearQR(qrToken: qrToken, token: token);

  Future<Map<String, dynamic>> registrarSalida({
    required int accesoId,
    required String token,
  }) =>
      _service.registrarSalida(accesoId: accesoId, token: token);

  @override
  void dispose() {
    disconnect();
    _service.dispose();
    super.dispose();
  }
}
