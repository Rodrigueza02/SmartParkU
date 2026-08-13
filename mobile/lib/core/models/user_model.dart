class UserModel {
  final String accessToken;
  final String nombre;
  final String rol;
  final String estado;
  final int idUsuario;

  const UserModel({
    required this.accessToken,
    required this.nombre,
    required this.rol,
    required this.estado,
    required this.idUsuario,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) => UserModel(
        accessToken: json['access_token'] as String,
        nombre:      json['nombre']       as String,
        rol:         json['rol']          as String,
        estado:      json['estado']       as String,
        idUsuario:   json['id_usuario']   as int,
      );

  bool get isAdmin =>
      rol == 'SuperAdmin' || rol == 'Administrativo';

  bool get isEstudiante => rol == 'Estudiante';
}
