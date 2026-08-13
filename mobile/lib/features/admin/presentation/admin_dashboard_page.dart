import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/providers/parking_provider.dart';
import '../../../core/constants/colors.dart';

class AdminDashboardPage extends StatefulWidget {
  const AdminDashboardPage({Key? key}) : super(key: key);

  @override
  State<AdminDashboardPage> createState() => _AdminDashboardPageState();
}

class _AdminDashboardPageState extends State<AdminDashboardPage> {
  int _selectedIndex = 0;

  final List<Widget> _pages = [
    const AdminOverviewTab(),
    const AdminMapTab(),
    const AdminReportsTab(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final user = authProvider.currentUser;

    return Scaffold(
      backgroundColor: AppColors.softWhite,
      appBar: AppBar(
        backgroundColor: AppColors.uccNavy,
        elevation: 0,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Panel de Gestión',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: Colors.white.withOpacity(0.7),
              ),
            ),
            Text(
              'Hola, ${user?.name ?? 'Administrador'}',
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ],
        ),
        actions: [
          Stack(
            children: [
              IconButton(
                icon: const Icon(Icons.notifications_outlined, color: Colors.white),
                onPressed: () {
                  // TODO: Mostrar notificaciones
                },
              ),
              Positioned(
                right: 12,
                top: 12,
                child: Container(
                  width: 8,
                  height: 8,
                  decoration: const BoxDecoration(
                    color: Colors.red,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.white),
            onPressed: () async {
              final confirmed = await showDialog<bool>(
                context: context,
                builder: (context) => AlertDialog(
                  title: const Text('Cerrar sesión'),
                  content: const Text('¿Estás seguro que deseas salir?'),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context, false),
                      child: const Text('Cancelar'),
                    ),
                    ElevatedButton(
                      onPressed: () => Navigator.pop(context, true),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                      ),
                      child: const Text('Salir'),
                    ),
                  ],
                ),
              );

              if (confirmed == true && mounted) {
                await authProvider.logout();
                Navigator.pushReplacementNamed(context, '/login');
              }
            },
          ),
        ],
      ),
      body: _pages[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        selectedItemColor: AppColors.uccBlue,
        unselectedItemColor: Colors.grey,
        selectedFontSize: 12,
        unselectedFontSize: 10,
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.map),
            label: 'Mapa',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.analytics),
            label: 'Reportes',
          ),
        ],
      ),
    );
  }
}

// ===== Tab 1: Vista General =====
class AdminOverviewTab extends StatelessWidget {
  const AdminOverviewTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final parkingProvider = Provider.of<ParkingProvider>(context);
    final slots = parkingProvider.parkingSlots;

    // Estadísticas
    final totalSlots = slots.length;
    final occupiedSlots = slots.where((s) => s.status == 'ocupado').length;
    final freeSlots = totalSlots - occupiedSlots;
    final occupancyPercentage =
        totalSlots > 0 ? (occupiedSlots / totalSlots * 100).round() : 0;

    // Estadísticas por tipo
    final carSlots = slots.where((s) => s.type == 'carro' || s.type == 'vip');
    final motoSlots = slots.where((s) => s.type == 'moto');
    final bikeSlots = slots.where((s) => s.type == 'bicicleta');

    final occupiedCars = carSlots.where((s) => s.status == 'ocupado').length;
    final occupiedMotos = motoSlots.where((s) => s.status == 'ocupado').length;
    final occupiedBikes = bikeSlots.where((s) => s.status == 'ocupado').length;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Estado de conexión
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Row(
              children: [
                Container(
                  width: 12,
                  height: 12,
                  decoration: BoxDecoration(
                    color: parkingProvider.isConnected
                        ? AppColors.uccGreen
                        : Colors.red,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    parkingProvider.isConnected
                        ? 'Tiempo real activo'
                        : 'Desconectado',
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: AppColors.uccNavy,
                    ),
                  ),
                ),
                Text(
                  '$totalSlots espacios',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // Tarjetas de estadísticas
          Row(
            children: [
              Expanded(
                child: _StatCard(
                  title: 'Ocupados',
                  value: occupiedSlots.toString(),
                  color: Colors.red,
                  icon: Icons.local_parking,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _StatCard(
                  title: 'Libres',
                  value: freeSlots.toString(),
                  color: AppColors.uccGreen,
                  icon: Icons.check_circle,
                ),
              ),
            ],
          ),

          const SizedBox(height: 12),

          _StatCard(
            title: 'Ocupación Total',
            value: '$occupancyPercentage%',
            color: AppColors.uccBlue,
            icon: Icons.pie_chart,
            isWide: true,
          ),

          const SizedBox(height: 24),

          // Análisis por tipo de vehículo
          const Text(
            'Análisis por Tipo',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppColors.uccNavy,
            ),
          ),

          const SizedBox(height: 16),

          _VehicleTypeCard(
            type: 'Autos',
            icon: Icons.directions_car,
            color: AppColors.uccGreen,
            total: carSlots.length,
            occupied: occupiedCars,
          ),

          const SizedBox(height: 12),

          _VehicleTypeCard(
            type: 'Motos',
            icon: Icons.two_wheeler,
            color: AppColors.uccBlue,
            total: motoSlots.length,
            occupied: occupiedMotos,
          ),

          const SizedBox(height: 12),

          _VehicleTypeCard(
            type: 'Bicicletas',
            icon: Icons.pedal_bike,
            color: AppColors.limeAccent,
            total: bikeSlots.length,
            occupied: occupiedBikes,
          ),

          const SizedBox(height: 24),

          // Alertas del sistema
          const Text(
            'Alertas del Sistema',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppColors.uccNavy,
            ),
          ),

          const SizedBox(height: 16),

          if (occupancyPercentage >= 90)
            _AlertCard(
              type: 'Capacidad',
              message:
                  'Parqueadero cerca de su capacidad máxima ($occupancyPercentage%)',
              severity: 'warning',
            )
          else
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.green[50],
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.green[100]!),
              ),
              child: Row(
                children: [
                  Icon(Icons.check_circle, color: AppColors.uccGreen, size: 32),
                  const SizedBox(width: 16),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Sin alertas activas',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                            color: AppColors.uccGreen,
                          ),
                        ),
                        SizedBox(height: 4),
                        Text(
                          'Todo funcionando correctamente',
                          style: TextStyle(
                            fontSize: 12,
                            color: AppColors.uccGreen,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

// ===== Tab 2: Mapa con Control de Talanquera =====
class AdminMapTab extends StatefulWidget {
  const AdminMapTab({Key? key}) : super(key: key);

  @override
  State<AdminMapTab> createState() => _AdminMapTabState();
}

class _AdminMapTabState extends State<AdminMapTab> {
  bool _loadingServo = false;

  Future<void> _controlServo(BuildContext context, String action) async {
    setState(() => _loadingServo = true);

    try {
      final parkingProvider =
          Provider.of<ParkingProvider>(context, listen: false);
      await parkingProvider.controlServo(action);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Talanquera ${action == 'abrir' ? 'abierta' : 'cerrada'}'),
            backgroundColor: AppColors.uccGreen,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _loadingServo = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final parkingProvider = Provider.of<ParkingProvider>(context);
    final slots = parkingProvider.parkingSlots;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Control de talanquera
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.security, color: AppColors.uccBlue, size: 20),
                    SizedBox(width: 8),
                    Text(
                      'Control de Talanquera',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: AppColors.uccNavy,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: _loadingServo
                            ? null
                            : () => _controlServo(context, 'abrir'),
                        icon: _loadingServo
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : const Icon(Icons.play_arrow),
                        label: const Text('Abrir'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.uccGreen,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: _loadingServo
                            ? null
                            : () => _controlServo(context, 'cerrar'),
                        icon: _loadingServo
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : const Icon(Icons.stop),
                        label: const Text('Cerrar'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.red,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // Mapa de slots
          const Text(
            'Mapa de Gestión',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppColors.uccNavy,
            ),
          ),

          const SizedBox(height: 16),

          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 3,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                childAspectRatio: 1.2,
              ),
              itemCount: slots.length,
              itemBuilder: (context, index) {
                final slot = slots[index];
                final isOccupied = slot.status == 'ocupado';

                return InkWell(
                  onTap: () {
                    showModalBottomSheet(
                      context: context,
                      shape: const RoundedRectangleBorder(
                        borderRadius:
                            BorderRadius.vertical(top: Radius.circular(20)),
                      ),
                      builder: (context) => _SlotDetailSheet(slot: slot),
                    );
                  },
                  child: Container(
                    decoration: BoxDecoration(
                      color: isOccupied ? Colors.red[50] : Colors.green[50],
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: isOccupied ? Colors.red[100]! : Colors.green[200]!,
                        width: 2,
                      ),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          '#${slot.label}',
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            color: Colors.grey[600],
                          ),
                        ),
                        const SizedBox(height: 4),
                        Container(
                          width: 32,
                          height: 16,
                          decoration: BoxDecoration(
                            color: isOccupied ? Colors.red[200] : AppColors.uccGreen,
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          slot.type.toUpperCase(),
                          style: TextStyle(
                            fontSize: 8,
                            fontWeight: FontWeight.bold,
                            color: isOccupied ? Colors.red : AppColors.uccGreen,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

// ===== Tab 3: Reportes (Placeholder) =====
class AdminReportsTab extends StatelessWidget {
  const AdminReportsTab({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.analytics, size: 64, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            'Reportes',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Próximamente: estadísticas y reportes',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }
}

// ===== Widgets Auxiliares =====

class _StatCard extends StatelessWidget {
  final String title;
  final String value;
  final Color color;
  final IconData icon;
  final bool isWide;

  const _StatCard({
    required this.title,
    required this.value,
    required this.color,
    required this.icon,
    this.isWide = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  value,
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: AppColors.uccNavy,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _VehicleTypeCard extends StatelessWidget {
  final String type;
  final IconData icon;
  final Color color;
  final int total;
  final int occupied;

  const _VehicleTypeCard({
    required this.type,
    required this.icon,
    required this.color,
    required this.total,
    required this.occupied,
  });

  @override
  Widget build(BuildContext context) {
    final percentage = total > 0 ? (occupied / total * 100).round() : 0;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              type,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: AppColors.uccNavy,
              ),
            ),
          ),
          Text(
            '$percentage%',
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: AppColors.uccNavy,
            ),
          ),
        ],
      ),
    );
  }
}

class _AlertCard extends StatelessWidget {
  final String type;
  final String message;
  final String severity;

  const _AlertCard({
    required this.type,
    required this.message,
    required this.severity,
  });

  @override
  Widget build(BuildContext context) {
    final isWarning = severity == 'warning';
    final bgColor = isWarning ? Colors.orange[50] : Colors.red[50];
    final borderColor = isWarning ? Colors.orange[100] : Colors.red[100];
    final iconColor = isWarning ? Colors.orange : Colors.red;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor!),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: iconColor,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.warning, color: Colors.white, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  type.toUpperCase(),
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: iconColor,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  message,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: Colors.grey[800],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SlotDetailSheet extends StatelessWidget {
  final dynamic slot;

  const _SlotDetailSheet({required this.slot});

  @override
  Widget build(BuildContext context) {
    final isOccupied = slot.status == 'ocupado';

    return Container(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Cajón ${slot.label}',
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: AppColors.uccNavy,
                ),
              ),
              IconButton(
                onPressed: () => Navigator.pop(context),
                icon: const Icon(Icons.close),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Estado: ${slot.status.toUpperCase()}',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
          if (slot.distanciaCm != null) ...[
            const SizedBox(height: 4),
            Text(
              'Sensor: ${slot.distanciaCm.toStringAsFixed(1)} cm',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[500],
              ),
            ),
          ],
          const SizedBox(height: 20),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: isOccupied ? Colors.red[50] : Colors.green[50],
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                Icon(
                  isOccupied ? Icons.warning : Icons.check_circle,
                  color: isOccupied ? Colors.red : AppColors.uccGreen,
                  size: 24,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    isOccupied
                        ? 'Vehículo detectado en este espacio'
                        : 'Espacio disponible para asignar',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: isOccupied ? Colors.red[700] : Colors.green[700],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
