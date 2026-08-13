import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../constants/api.dart';
import '../models/user_model.dart';

class AuthService {
  static const _tokenKey  = 'smartparku_token';
  static const _userKey   = 'smartparku_user';

  // ── Login ────────────────────────────────────────────────────────────────

  Future<UserModel> login(String correo, String password) async {
    final response = await http.post(
      Uri.parse(ApiConstants.login),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'correo': correo, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      final user = UserModel.fromJson(data);
      await _saveSession(user);
      return user;
    }

    final detail = _extractDetail(response.body);
    throw Exception(detail);
  }

  // ── Forgot password ───────────────────────────────────────────────────────

  Future<String> forgotPassword(String correo) async {
    final response = await http.post(
      Uri.parse(ApiConstants.forgotPassword),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'correo': correo}),
    );
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return data['mensaje'] as String? ?? 'Solicitud enviada.';
  }

  // ── Reset password ────────────────────────────────────────────────────────

  Future<String> resetPassword(String token, String nuevaPassword) async {
    final response = await http.post(
      Uri.parse(ApiConstants.resetPassword),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'token': token, 'nueva_password': nuevaPassword}),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return data['mensaje'] as String? ?? 'Contraseña actualizada.';
    }
    throw Exception(_extractDetail(response.body));
  }

  // ── Sesión persistida ─────────────────────────────────────────────────────

  Future<void> _saveSession(UserModel user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, user.accessToken);
    await prefs.setString(_userKey, jsonEncode({
      'access_token': user.accessToken,
      'nombre':       user.nombre,
      'rol':          user.rol,
      'estado':       user.estado,
      'id_usuario':   user.idUsuario,
    }));
  }

  Future<UserModel?> getSavedSession() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_userKey);
    if (raw == null) return null;
    try {
      return UserModel.fromJson(jsonDecode(raw) as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_userKey);
  }

  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  // ── Helper ────────────────────────────────────────────────────────────────

  String _extractDetail(String body) {
    try {
      final data = jsonDecode(body) as Map<String, dynamic>;
      return data['detail'] as String? ?? 'Error desconocido';
    } catch (_) {
      return 'Error al conectar con el servidor';
    }
  }
}
