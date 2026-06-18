class ParkingSlot {
  final String slotId;
  final String label;
  final String tipo;
  final String status;
  final double? distanciaCm;

  const ParkingSlot({
    required this.slotId,
    required this.label,
    required this.tipo,
    required this.status,
    this.distanciaCm,
  });

  bool get isLibre => status == 'libre';

  factory ParkingSlot.fromJson(String id, Map<String, dynamic> json) =>
      ParkingSlot(
        slotId:      id,
        label:       json['label']  as String? ?? id,
        tipo:        json['tipo']   as String? ?? 'carro',
        status:      json['status'] as String? ?? 'libre',
        distanciaCm: (json['distancia_cm'] as num?)?.toDouble(),
      );
}
