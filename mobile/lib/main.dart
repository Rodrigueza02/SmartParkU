import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/providers/auth_provider.dart';
import 'core/providers/parking_provider.dart';
import 'features/auth/presentation/login_page.dart';
import 'features/parking/presentation/student_dashboard_page.dart';
import 'features/admin/presentation/admin_dashboard_page.dart';

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
      routes: {
        '/login': (context) => const LoginPage(),
        '/student-dashboard': (context) => const StudentDashboardPage(),
        '/admin-dashboard': (context) => const AdminDashboardPage(),
      },
    );
  }
}

/// Decide qué pantalla mostrar según el estado de autenticación y rol del usuario.
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
        // Enrutamiento según el rol del usuario
        final user = auth.currentUser;
        if (user != null &&
            (user.role == 'SuperAdmin' || user.role == 'Administrativo')) {
          // Administradores van al dashboard admin
          return const AdminDashboardPage();
        } else {
          // Estudiantes y otros roles van al dashboard de estudiante
          return const StudentDashboardPage();
        }

      case AuthStatus.unauthenticated:
        return const LoginPage();
    }
  }
}
