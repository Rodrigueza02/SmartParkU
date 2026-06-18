import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/providers/auth_provider.dart';
import 'core/providers/parking_provider.dart';
import 'features/auth/presentation/login_page.dart';
import 'features/parking/presentation/student_dashboard_page.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => ParkingProvider()),
      ],
      child: const SmartParkUApp(),
    ),
  );
}

class SmartParkUApp extends StatelessWidget {
  const SmartParkUApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SmartParkU',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        fontFamily: 'Roboto',
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF00AEEF),
          brightness: Brightness.light,
        ),
        scaffoldBackgroundColor: const Color(0xFFFDFDFD),
      ),
      home: const _AuthGate(),
    );
  }
}

/// Decide qué pantalla mostrar según el estado de autenticación.
class _AuthGate extends StatelessWidget {
  const _AuthGate();

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();

    switch (auth.status) {
      case AuthStatus.unknown:
        // Splash mientras se restaura la sesión guardada
        return const Scaffold(
          body: Center(
            child: CircularProgressIndicator(color: Color(0xFF00AEEF)),
          ),
        );

      case AuthStatus.authenticated:
        // Por ahora todos los roles van al mismo dashboard de estudiante.
        // TODO: agregar AdminDashboardPage para SuperAdmin / Administrativo.
        return const StudentDashboardPage();

      case AuthStatus.unauthenticated:
        return const LoginPage();
    }
  }
}
