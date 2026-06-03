enum UserRole {
  student,
  administrative,
  visitor,
  superAdmin,
}

class UserEntity {
  final String id;
  final String email;
  final String name;
  final UserRole role;

  UserEntity({
    required this.id,
    required this.email,
    required this.name,
    required this.role,
  });
}
