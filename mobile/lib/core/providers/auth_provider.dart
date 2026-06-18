import 'package:flutter/foundation.dart';
import '../models/user_model.dart';
import '../services/auth_service.dart';

enum AuthStatus { unknown, authenticated, unauthenticated }

class AuthProvider extends ChangeNotifier {
  final AuthService _service = AuthService();

  AuthStatus _status = AuthStatus.unknown;
  UserModel?  _user;
  String?     _error;
  bool        _loading = false;

  AuthStatus get status  => _status;
  UserModel? get user    => _user;
  String?    get error   => _error;
  bool       get loading => _loading;

  AuthProvider() {
    _tryRestoreSession();
  }

  Future<void> _tryRestoreSession() async {
    final saved = await _service.getSavedSession();
    if (saved != null) {
      _user   = saved;
      _status = AuthStatus.authenticated;
    } else {
      _status = AuthStatus.unauthenticated;
    }
    notifyListeners();
  }

  Future<bool> login(String correo, String password) async {
    _loading = true;
    _error   = null;
    notifyListeners();
    try {
      _user   = await _service.login(correo, password);
      _status = AuthStatus.authenticated;
      _loading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error   = e.toString().replaceFirst('Exception: ', '');
      _status  = AuthStatus.unauthenticated;
      _loading = false;
      notifyListeners();
      return false;
    }
  }

  Future<String> forgotPassword(String correo) async {
    try {
      return await _service.forgotPassword(correo);
    } catch (e) {
      return e.toString().replaceFirst('Exception: ', '');
    }
  }

  Future<String> resetPassword(String token, String nuevaPassword) async {
    try {
      return await _service.resetPassword(token, nuevaPassword);
    } catch (e) {
      return e.toString().replaceFirst('Exception: ', '');
    }
  }

  Future<void> logout() async {
    await _service.logout();
    _user   = null;
    _status = AuthStatus.unauthenticated;
    notifyListeners();
  }

  Future<String?> getToken() => _service.getToken();
}
