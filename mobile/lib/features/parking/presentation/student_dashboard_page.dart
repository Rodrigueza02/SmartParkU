import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../../../core/constants/colors.dart';
import '../../../core/models/parking_slot_model.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/providers/parking_provider.dart';

class StudentDashboardPage extends StatefulWidget {
  const StudentDashboardPage({super.key});

  @override
  State<StudentDashboardPage> createState() => _StudentDashboardPageState();
}

class _StudentDashboardPageState extends State<StudentDashboardPage> {
  int _tab = 0; // 0 = Mapa, 1 = Mi QR, 2 = Perfil

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final auth    = context.read<AuthProvider>();
      final parking = context.read<ParkingProvider>();
      auth.getToken().then((token) {
        if (token != null) parking.connect(token);
      });
    });
  }

  @override
  void dispose() {
    context.read<ParkingProvider>().disconnect();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final auth    = context.watch<AuthProvider>();
    final parking = context.watch<ParkingProvider>();
    final user    = auth.user!;

    return Scaffold(
      backgroundColor: AppColors.softWhite,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: RichText(
          text: const TextSpan(
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900),
            children: [
              TextSpan(
                  text: 'Smart',
                  style: TextStyle(color: Color(0xFF6AB023))),
              TextSpan(
                  text: 'Park',
                  style: TextStyle(color: Color(0xFF00AEEF))),
              TextSpan(
                  text: 'U',
                  style: TextStyle(color: Color(0xFF1E3A5F))),
            ],
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout_rounded,
                color: Color(0xFF1E3A5F)),
            tooltip: 'Cerrar sesión',
            onPressed: () => context.read<AuthProvider>().logout(),
          ),
        ],
      ),
      body: IndexedStack(
        index: _tab,
        children: [
          _MapaTab(parking: parking),
          _QRTab(user: user),
          _PerfilTab(user: user),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _tab,
        onTap: (i) => setState(() => _tab = i),
        backgroundColor: Colors.white,
        selectedItemColor: const Color(0xFF00AEEF),
        unselectedItemColor: AppColors.textGrey,
        selectedLabelStyle:
            const TextStyle(fontWeight: FontWeight.w700, fontSize: 11),
        items: const [
          BottomNavigationBarItem(
              icon: Icon(Icons.local_parking_rounded), label: 'Mapa'),
          BottomNavigationBarItem(
              icon: Icon(Icons.qr_code_2_rounded), label: 'Mi QR'),
          BottomNavigationBarItem(
              icon: Icon(Icons.person_outline_rounded), label: 'Perfil'),
        ],
      ),
    );
  }
}

// ─── Pestaña Mapa ─────────────────────────────────────────────────────────────

class _MapaTab extends StatelessWidget {
  final ParkingProvider parking;
  const _MapaTab({required this.parking});

  @override
  Widget build(BuildContext context) {
    final slots = parking.slots;

    return Column(
      children: [
        // Contador resumen
        Container(
          color: Colors.white,
          padding:
              const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          child: Row(
            children: [
              _StatChip(
                label: 'Libres',
                value: parking.totalLibre,
                color: const Color(0xFF6AB023),
              ),
              const SizedBox(width: 12),
              _StatChip(
                label: 'Ocupados',
                value: parking.totalOcupado,
                color: AppColors.errorRed,
              ),
              const Spacer(),
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: parking.connected
                      ? const Color(0xFF6AB023)
                      : AppColors.errorRed,
                ),
              ),
              const SizedBox(width: 6),
              Text(
                parking.connected ? 'En vivo' : 'Sin conexión',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: parking.connected
                      ? const Color(0xFF6AB023)
                      : AppColors.errorRed,
                ),
              ),
            ],
          ),
        ),

        // Grilla de cajones
        Expanded(
          child: slots.isEmpty
              ? const Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      CircularProgressIndicator(
                          color: Color(0xFF00AEEF)),
                      SizedBox(height: 14),
                      Text('Conectando al parqueadero...',
                          style: TextStyle(color: AppColors.textGrey)),
                    ],
                  ),
                )
              : GridView.builder(
                  padding: const EdgeInsets.all(16),
                  gridDelegate:
                      const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    mainAxisSpacing: 12,
                    crossAxisSpacing: 12,
                    childAspectRatio: 1.5,
                  ),
                  itemCount: slots.length,
                  itemBuilder: (_, i) {
                    final slot = slots.values.elementAt(i);
                    return _SlotCard(slot: slot);
                  },
                ),
        ),
      ],
    );
  }
}

class _SlotCard extends StatelessWidget {
  final ParkingSlot slot;
  const _SlotCard({required this.slot});

  @override
  Widget build(BuildContext context) {
    final libre = slot.isLibre;
    final color = libre
        ? const Color(0xFF6AB023)
        : AppColors.errorRed;
    final bg = libre
        ? const Color(0xFFF0FAF0)
        : const Color(0xFFFFF0F0);

    final iconMap = {
      'carro':     Icons.directions_car_rounded,
      'moto':      Icons.two_wheeler_rounded,
      'bicicleta': Icons.pedal_bike_rounded,
      'vip':       Icons.star_rounded,
    };

    return Container(
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withAlpha(80)),
      ),
      padding: const EdgeInsets.all(12),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(iconMap[slot.tipo] ?? Icons.local_parking_rounded,
                  color: color, size: 20),
              const Spacer(),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: color.withAlpha(30),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  libre ? 'LIBRE' : 'OCUPADO',
                  style: TextStyle(
                    color: color,
                    fontSize: 9,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 0.8,
                  ),
                ),
              ),
            ],
          ),
          Text(
            slot.label,
            style: TextStyle(
              color: const Color(0xFF1E3A5F),
              fontSize: 20,
              fontWeight: FontWeight.w900,
            ),
          ),
        ],
      ),
    );
  }
}

class _StatChip extends StatelessWidget {
  final String label;
  final int    value;
  final Color  color;
  const _StatChip(
      {required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) => Container(
        padding:
            const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: color.withAlpha(20),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            Text(
              value.toString(),
              style: TextStyle(
                  color: color,
                  fontWeight: FontWeight.w900,
                  fontSize: 18),
            ),
            const SizedBox(width: 6),
            Text(
              label,
              style: TextStyle(
                  color: color,
                  fontWeight: FontWeight.w600,
                  fontSize: 12),
            ),
          ],
        ),
      );
}

// ─── Pestaña QR ───────────────────────────────────────────────────────────────

class _QRTab extends StatefulWidget {
  final dynamic user;
  const _QRTab({required this.user});

  @override
  State<_QRTab> createState() => _QRTabState();
}

class _QRTabState extends State<_QRTab> {
  bool   _loading       = false;
  String? _error;
  Map<String, dynamic>? _qrData;   // respuesta de /qr/generar
  Map<String, dynamic>? _acceso;   // respuesta de /qr/escanear
  bool   _showScanner   = false;

  Future<void> _generarQR() async {
    setState(() { _loading = true; _error = null; _qrData = null; _acceso = null; });
    try {
      final token   = await context.read<AuthProvider>().getToken();
      final parking = context.read<ParkingProvider>();
      final data = await parking.generarQR(
        idUsuario: widget.user.idUsuario as int,
        token: token!,
      );
      setState(() { _qrData = data; });
    } catch (e) {
      setState(() { _error = e.toString().replaceFirst('Exception: ', ''); });
    } finally {
      setState(() { _loading = false; });
    }
  }

  Future<void> _escanear(String scannedToken) async {
    setState(() { _showScanner = false; _loading = true; _error = null; });
    try {
      final token   = await context.read<AuthProvider>().getToken();
      final parking = context.read<ParkingProvider>();
      final data = await parking.escanearQR(
        qrToken: scannedToken,
        token: token!,
      );
      setState(() { _acceso = data; _qrData = null; });
    } catch (e) {
      setState(() { _error = e.toString().replaceFirst('Exception: ', ''); });
    } finally {
      setState(() { _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_showScanner) {
      return _QRScannerView(onDetect: _escanear,
          onCancel: () => setState(() => _showScanner = false));
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SizedBox(height: 8),
          const Text(
            'Acceso al parqueadero',
            style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w900,
                color: Color(0xFF1E3A5F)),
          ),
          const SizedBox(height: 6),
          const Text(
            'Genera tu QR para ingresar o escanea el QR que ya tienes.',
            style: TextStyle(color: AppColors.textGrey, fontSize: 13),
          ),
          const SizedBox(height: 28),

          // Error
          if (_error != null) ...[
            _ErrorBanner(_error!),
            const SizedBox(height: 16),
          ],

          // Acceso confirmado
          if (_acceso != null) ...[
            _AccesoConfirmado(acceso: _acceso!),
            const SizedBox(height: 20),
            _OutlineBtn(
              label: 'Nuevo acceso',
              icon: Icons.refresh_rounded,
              onPressed: () => setState(() { _acceso = null; }),
            ),
          ] else if (_qrData != null) ...[
            // QR generado
            _QRImageCard(qrData: _qrData!),
            const SizedBox(height: 16),
            _PrimaryBtn(
              label: 'Escanear QR en la entrada',
              icon: Icons.qr_code_scanner_rounded,
              onPressed: () => setState(() => _showScanner = true),
            ),
            const SizedBox(height: 10),
            _OutlineBtn(
              label: 'Generar nuevo QR',
              icon: Icons.refresh_rounded,
              onPressed: _generarQR,
            ),
          ] else ...[
            // Estado inicial
            _PrimaryBtn(
              label: _loading ? 'Generando...' : 'Generar mi QR',
              icon: Icons.qr_code_2_rounded,
              onPressed: _loading ? null : _generarQR,
              loading: _loading,
            ),
            const SizedBox(height: 12),
            _OutlineBtn(
              label: 'Escanear QR existente',
              icon: Icons.qr_code_scanner_rounded,
              onPressed: () => setState(() => _showScanner = true),
            ),
          ],
        ],
      ),
    );
  }
}

class _QRScannerView extends StatelessWidget {
  final void Function(String) onDetect;
  final VoidCallback onCancel;
  const _QRScannerView(
      {required this.onDetect, required this.onCancel});

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        MobileScanner(
          onDetect: (capture) {
            final barcode = capture.barcodes.firstOrNull;
            if (barcode?.rawValue != null) {
              onDetect(barcode!.rawValue!);
            }
          },
        ),
        Positioned(
          top: 40,
          left: 16,
          child: SafeArea(
            child: ElevatedButton.icon(
              onPressed: onCancel,
              icon: const Icon(Icons.arrow_back_rounded),
              label: const Text('Cancelar'),
              style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.black54,
                  foregroundColor: Colors.white),
            ),
          ),
        ),
        const Center(
          child: Padding(
            padding: EdgeInsets.only(top: 120),
            child: Text(
              'Apunta la cámara al código QR',
              style: TextStyle(color: Colors.white70, fontSize: 14),
            ),
          ),
        ),
      ],
    );
  }
}

class _QRImageCard extends StatelessWidget {
  final Map<String, dynamic> qrData;
  const _QRImageCard({required this.qrData});

  @override
  Widget build(BuildContext context) {
    final b64 = (qrData['qr_image_base64'] as String?)
        ?.replaceFirst('data:image/png;base64,', '');
    final label   = qrData['label']   as String? ?? '-';
    final mensaje = qrData['mensaje'] as String? ?? '';

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: const BorderSide(color: Color(0xFF00AEEF), width: 1.5)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Text(
              'Espacio asignado: $label',
              style: const TextStyle(
                  fontWeight: FontWeight.w800,
                  fontSize: 16,
                  color: Color(0xFF1E3A5F)),
            ),
            const SizedBox(height: 16),
            if (b64 != null)
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.memory(
                  base64Decode(b64),
                  width: 220,
                  height: 220,
                  fit: BoxFit.contain,
                ),
              ),
            const SizedBox(height: 12),
            Text(
              mensaje,
              style: const TextStyle(
                  color: AppColors.textGrey, fontSize: 12),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _AccesoConfirmado extends StatelessWidget {
  final Map<String, dynamic> acceso;
  const _AccesoConfirmado({required this.acceso});

  @override
  Widget build(BuildContext context) {
    final label    = acceso['label']    as String? ?? '-';
    final mensaje  = acceso['mensaje']  as String? ?? '✅ Acceso registrado.';

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFFF0FAF0),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
            color: const Color(0xFF6AB023).withAlpha(100)),
      ),
      child: Column(
        children: [
          const Icon(Icons.check_circle_rounded,
              color: Color(0xFF6AB023), size: 56),
          const SizedBox(height: 12),
          Text(
            label,
            style: const TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.w900,
                color: Color(0xFF1E3A5F)),
          ),
          const SizedBox(height: 8),
          Text(
            mensaje,
            textAlign: TextAlign.center,
            style: const TextStyle(
                color: Color(0xFF1E7A5F),
                fontWeight: FontWeight.w600,
                fontSize: 13),
          ),
        ],
      ),
    );
  }
}

class _ErrorBanner extends StatelessWidget {
  final String message;
  const _ErrorBanner(this.message);

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: const Color(0xFFFFEDED),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.errorRed.withAlpha(80)),
        ),
        child: Text(
          message,
          style: const TextStyle(
              color: AppColors.errorRed,
              fontWeight: FontWeight.w600,
              fontSize: 13),
          textAlign: TextAlign.center,
        ),
      );
}

class _PrimaryBtn extends StatelessWidget {
  final String   label;
  final IconData icon;
  final VoidCallback? onPressed;
  final bool loading;
  const _PrimaryBtn(
      {required this.label,
      required this.icon,
      this.onPressed,
      this.loading = false});

  @override
  Widget build(BuildContext context) => SizedBox(
        height: 52,
        child: ElevatedButton.icon(
          onPressed: onPressed,
          icon: loading
              ? const SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(
                      color: Colors.white, strokeWidth: 2))
              : Icon(icon),
          label: Text(label,
              style: const TextStyle(
                  fontWeight: FontWeight.w800, fontSize: 14)),
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF00AEEF),
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14)),
            elevation: 0,
          ),
        ),
      );
}

class _OutlineBtn extends StatelessWidget {
  final String   label;
  final IconData icon;
  final VoidCallback? onPressed;
  const _OutlineBtn(
      {required this.label, required this.icon, this.onPressed});

  @override
  Widget build(BuildContext context) => SizedBox(
        height: 48,
        child: OutlinedButton.icon(
          onPressed: onPressed,
          icon: Icon(icon, size: 18),
          label: Text(label,
              style: const TextStyle(
                  fontWeight: FontWeight.w700, fontSize: 13)),
          style: OutlinedButton.styleFrom(
            foregroundColor: const Color(0xFF1E3A5F),
            side: const BorderSide(color: Color(0xFF1E3A5F)),
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14)),
          ),
        ),
      );
}

// ─── Pestaña Perfil ───────────────────────────────────────────────────────────

class _PerfilTab extends StatelessWidget {
  final dynamic user;
  const _PerfilTab({required this.user});

  @override
  Widget build(BuildContext context) {
    final rolColors = {
      'SuperAdmin':     AppColors.superAdminAccent,
      'Administrativo': AppColors.adminAccent,
      'Estudiante':     AppColors.studentAccent,
      'Visitante':      AppColors.visitorAccent,
    };
    final rolColor =
        rolColors[user.rol as String] ?? AppColors.textGrey;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SizedBox(height: 20),
          // Avatar
          Center(
            child: CircleAvatar(
              radius: 44,
              backgroundColor: const Color(0xFF00AEEF).withAlpha(30),
              child: const Icon(Icons.person_rounded,
                  color: Color(0xFF00AEEF), size: 48),
            ),
          ),
          const SizedBox(height: 16),
          Center(
            child: Text(
              user.nombre as String,
              style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.w900,
                  color: Color(0xFF1E3A5F)),
            ),
          ),
          const SizedBox(height: 6),
          Center(
            child: Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 14, vertical: 5),
              decoration: BoxDecoration(
                color: rolColor.withAlpha(30),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                user.rol as String,
                style: TextStyle(
                    color: rolColor,
                    fontWeight: FontWeight.w700,
                    fontSize: 13),
              ),
            ),
          ),
          const SizedBox(height: 32),

          // Info card
          Card(
            elevation: 0,
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
                side: BorderSide(color: Colors.grey.shade200)),
            color: Colors.white,
            child: Column(
              children: [
                _InfoRow(
                    icon: Icons.badge_outlined,
                    label: 'ID de usuario',
                    value: '#${user.idUsuario}'),
                const Divider(height: 1),
                _InfoRow(
                    icon: Icons.verified_user_outlined,
                    label: 'Estado',
                    value: user.estado as String),
              ],
            ),
          ),
          const SizedBox(height: 28),

          // Cerrar sesión
          SizedBox(
            height: 50,
            child: ElevatedButton.icon(
              onPressed: () => context.read<AuthProvider>().logout(),
              icon: const Icon(Icons.logout_rounded),
              label: const Text('Cerrar sesión',
                  style: TextStyle(
                      fontWeight: FontWeight.w700, fontSize: 14)),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.errorRed,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14)),
                elevation: 0,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String   label;
  final String   value;
  const _InfoRow(
      {required this.icon, required this.label, required this.value});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
        child: Row(
          children: [
            Icon(icon, color: const Color(0xFF00AEEF), size: 20),
            const SizedBox(width: 12),
            Text(label,
                style: const TextStyle(
                    color: AppColors.textGrey, fontSize: 13)),
            const Spacer(),
            Text(value,
                style: const TextStyle(
                    fontWeight: FontWeight.w700,
                    fontSize: 13,
                    color: Color(0xFF1E3A5F))),
          ],
        ),
      );
}
