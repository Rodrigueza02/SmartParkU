import 'package:flutter/material.dart';
import '../../../core/constants/colors.dart';
import '../../domain/entities/user_role.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> with SingleTickerProviderStateMixin {
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  bool _isLoading = false;
  
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    );
    _fadeAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeIn,
    );
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _handleLogin() async {
    setState(() => _isLoading = true);
    
    // Simulación de validación de backend
    await Future.delayed(const Duration(seconds: 2));
    
    // Lógica de detección de roles (simulada por email para la demo)
    UserRole selectedRole;
    String email = _emailController.text.toLowerCase();
    
    if (email.contains('admin')) {
      selectedRole = UserRole.administrative;
    } else if (email.contains('super')) {
      selectedRole = UserRole.superAdmin;
    } else if (email.contains('visit')) {
      selectedRole = UserRole.visitor;
    } else {
      selectedRole = UserRole.student;
    }

    setState(() => _isLoading = false);
    
    if (mounted) {
      _navigateToDashboard(selectedRole);
    }
  }

  void _navigateToDashboard(UserRole role) {
    // Aquí se implementaría la transición Hero o Fade-in al Dashboard
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Login exitoso como ${role.name}'),
        backgroundColor: AppColors.primaryGreen,
      ),
    );
    // Redirección simulada
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.softWhite,
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [AppColors.mintPastel, AppColors.softWhite],
          ),
        ),
        child: FadeTransition(
          opacity: _fadeAnimation,
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 30),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Logo / Branding UCC
                  _buildBranding(),
                  const SizedBox(height: 40),
                  
                  // Login Card
                  _buildLoginCard(),
                  
                  const SizedBox(height: 20),
                  TextButton(
                    onPressed: () {},
                    child: const Text(
                      '¿Olvidaste tu contraseña?',
                      style: TextStyle(color: AppColors.textGrey),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildBranding() {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.5),
            shape: BoxShape.circle,
          ),
          child: const Icon(
            Icons.eco_rounded,
            size: 80,
            color: AppColors.primaryGreen,
          ),
        ),
        const SizedBox(height: 16),
        const Text(
          'SmartParkU',
          style: TextStyle(
            fontSize: 32,
            fontWeight: FontWeight.bold,
            color: AppColors.textDark,
            letterSpacing: 1.2,
          ),
        ),
        const Text(
          'Parqueo Inteligente y Eco-friendly',
          style: TextStyle(
            fontSize: 14,
            color: AppColors.textGrey,
          ),
        ),
      ],
    );
  }

  Widget _buildLoginCard() {
    return Container(
      padding: const EdgeInsets.all(30),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Bienvenido',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: AppColors.textDark,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Ingresa con tu cuenta institucional',
            style: TextStyle(color: AppColors.textGrey),
          ),
          const SizedBox(height: 30),
          
          // Email Field
          _buildTextField(
            controller: _emailController,
            label: 'Correo UCC',
            icon: Icons.email_outlined,
          ),
          const SizedBox(height: 20),
          
          // Password Field
          _buildTextField(
            controller: _passwordController,
            label: 'Contraseña',
            icon: Icons.lock_outline,
            isPassword: true,
          ),
          const SizedBox(height: 40),
          
          // Login Button
          SizedBox(
            width: double.infinity,
            height: 55,
            child: ElevatedButton(
              onPressed: _isLoading ? null : _handleLogin,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primaryGreen,
                foregroundColor: Colors.white,
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
              ),
              child: _isLoading
                  ? const CircularProgressIndicator(color: Colors.white)
                  : const Text(
                      'Iniciar Sesión',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    bool isPassword = false,
  }) {
    return TextField(
      controller: controller,
      obscureText: isPassword,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon, color: AppColors.primaryGreen),
        filled: true,
        fillColor: AppColors.lightGrey,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        labelStyle: const TextStyle(color: AppColors.textGrey),
      ),
    );
  }
}
