class AgentProfile {
  const AgentProfile({
    required this.agentName,
    required this.matricula,
    required this.deviceName,
    required this.deviceId,
    required this.deviceActive,
    required this.deviceActivated,
    required this.passwordChanged,
  });

  final String agentName;
  final String matricula;
  final String deviceName;
  final String deviceId;
  final bool deviceActive;
  final bool deviceActivated;
  final bool passwordChanged;

  factory AgentProfile.fromJson(Map<String, dynamic> json) {
    final agente = json['agente'] as Map<String, dynamic>? ?? <String, dynamic>{};
    final dispositivo =
        json['dispositivo'] as Map<String, dynamic>? ?? <String, dynamic>{};

    return AgentProfile(
      agentName: agente['nome'] as String? ?? '',
      matricula: agente['matricula'] as String? ?? '',
      deviceName: dispositivo['nome'] as String? ?? '',
      deviceId: dispositivo['device_id'] as String? ??
          dispositivo['imei'] as String? ??
          '',
      deviceActive: dispositivo['ativo'] as bool? ?? false,
      deviceActivated: dispositivo['ativado'] as bool? ?? false,
      passwordChanged: agente['senha_alterada'] as bool? ?? false,
    );
  }
}
