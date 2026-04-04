class DeviceActivationResponse {
  DeviceActivationResponse({
    required this.apiKey,
    required this.deviceName,
    required this.imei,
    required this.senhaAlterada,
    required this.assinaturaUrl,
  });

  final String apiKey;
  final String deviceName;
  final String imei;
  final bool senhaAlterada;
  final String? assinaturaUrl;

  factory DeviceActivationResponse.fromJson(Map<String, dynamic> json) {
    final dispositivo = (json['dispositivo'] as Map<String, dynamic>? ?? <String, dynamic>{});
    return DeviceActivationResponse(
      apiKey: dispositivo['api_key'] as String? ?? '',
      deviceName: dispositivo['nome'] as String? ?? '',
      imei: dispositivo['imei'] as String? ?? '',
      senhaAlterada: json['senha_alterada'] as bool? ?? false,
      assinaturaUrl: json['assinatura_url'] as String?,
    );
  }
}
