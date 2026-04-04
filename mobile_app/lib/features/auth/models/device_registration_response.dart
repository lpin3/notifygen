class DeviceRegistrationResponse {
  DeviceRegistrationResponse({
    required this.success,
    required this.message,
    required this.isNewDevice,
  });

  final bool success;
  final String message;
  final bool isNewDevice;

  factory DeviceRegistrationResponse.fromJson(Map<String, dynamic> json) {
    return DeviceRegistrationResponse(
      success: json['sucesso'] as bool? ?? false,
      message: json['mensagem'] as String? ?? '',
      isNewDevice: json['novo'] as bool? ?? false,
    );
  }
}
