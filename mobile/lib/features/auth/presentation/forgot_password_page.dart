import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/constants/colors.dart';
import '../../../core/providers/auth_provider.dart';

class ForgotPasswordPage extends StatefulWidget {
  const ForgotPasswordPage({super.key});

  @override
  State<ForgotPasswordPage> createState() => _ForgotPasswordPageState();
}

class _ForgotPasswordPageState extends State<ForgotPasswordPage> {
  final _formKey    = GlobalKey<FormState>();
  final _correoCtrl = TextEditingController();
  bool   _loading   = false;
  String? _mensaje;

  @override
  void dispose() {
    _correoCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { _loading = true; _mensaje = null; });
    final auth = context.read<AuthProvider>();
    final msg = await auth.forgotPassword(_correoCtrl.text.trim());
    setState(() { _loading = false; _mensaje = msg; });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.softWhite,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        foregroundColor: const Color(0xFF1E3A5F),
        title: const Text(
          'Recuperar contraseña',
          style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(28),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 16),

              // Ícono
              const Center(
                child: Icon(Icons.lock_reset_rounded,
                    color: Color(0xFF00AEEF), size: 64),
              ),
              const SizedBox(height: 20),

              const Text(
                'Ingresa tu correo institucional y te enviaremos las instrucciones para restablecer tu contraseña.',
                textAlign: TextAlign.center,
                style: TextStyle(
                    color: AppColors.textGrey,
                    fontSize: 14,
                    height: 1.5),
              ),
              const SizedBox(height: 32),

              // Mensaje de éxito
              if (_mensaje != null) ...[
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFFE8F8F5),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                        color: const Color(0xFF6AB023).withAlpha(100)),
                  ),
                  child: Text(
                    _mensaje!,
                    style: const TextStyle(
                        color: Color(0xFF1E7A5F),
                        fontSize: 13,
                        fontWeight: FontWeight.w600),
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: 24),
              ],

              // Campo correo
              TextFormField(
                controller: _correoCtrl,
                keyboardType: TextInputType.emailAddress,
                textInputAction: TextInputAction.done,
                onFieldSubmitted: (_) => _submit(),
                decoration: InputDecoration(
                  hintText: 'ejemplo@ucc.edu.co',
                  hintStyle: const TextStyle(
                      color: AppColors.textGrey, fontSize: 14),
                  prefixIcon: const Icon(Icons.mail_outline_rounded,
                      color: AppColors.textGrey, size: 20),
                  filled: true,
                  fillColor: AppColors.lightGrey,
                  border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(14),
                      borderSide: BorderSide.none),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(14),
                    borderSide: const BorderSide(
                        color: Color(0xFF00AEEF), width: 1.5),
                  ),
                  contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16, vertical: 14),
                ),
                validator: (v) =>
                    (v == null || !v.contains('@'))
                        ? 'Ingresa un correo válido'
                        : null,
              ),
              const SizedBox(height: 24),

              SizedBox(
                height: 52,
                child: ElevatedButton(
                  onPressed: _loading ? null : _submit,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF00AEEF),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16)),
                    elevation: 0,
                  ),
                  child: _loading
                      ? const SizedBox(
                          width: 22,
                          height: 22,
                          child: CircularProgressIndicator(
                              color: Colors.white, strokeWidth: 2.5))
                      : const Text(
                          'Enviar instrucciones',
                          style: TextStyle(
                              fontWeight: FontWeight.w800, fontSize: 15),
                        ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
