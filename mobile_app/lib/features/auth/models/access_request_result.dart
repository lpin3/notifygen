enum DeviceAccessStatus {
  approved,
  pending,
  blocked,
}

class AccessRequestResult {
  AccessRequestResult({
    required this.status,
    required this.message,
    required this.deviceId,
    required this.deviceName,
    required this.agentMatricula,
    required this.agentName,
    this.apiKey,
    this.requestedAt,
    this.approvedAt,
    this.blockedReason = '',
  });

  final DeviceAccessStatus status;
  final String message;
  final String deviceId;
  final String deviceName;
  final String agentMatricula;
  final String agentName;
  final String? apiKey;
  final String? requestedAt;
  final String? approvedAt;
  final String blockedReason;

  bool get isApproved => status == DeviceAccessStatus.approved;
  bool get isPending => status == DeviceAccessStatus.pending;
  bool get isBlocked => status == DeviceAccessStatus.blocked;

  factory AccessRequestResult.fromJson(Map<String, dynamic> json) {
    final dispositivo =
        json['dispositivo'] as Map<String, dynamic>? ?? <String, dynamic>{};
    final agente = json['agente'] as Map<String, dynamic>? ?? <String, dynamic>{};
    final sessao = json['sessao'] as Map<String, dynamic>? ?? <String, dynamic>{};
    final status = (json['status'] as String? ?? 'pending').toLowerCase();

    return AccessRequestResult(
      status: switch (status) {
        'approved' => DeviceAccessStatus.approved,
        'blocked' => DeviceAccessStatus.blocked,
        _ => DeviceAccessStatus.pending,
      },
      message: json['mensagem'] as String? ?? '',
      deviceId:
          dispositivo['device_id'] as String? ??
          dispositivo['imei'] as String? ??
          '',
      deviceName: dispositivo['nome'] as String? ?? '',
      agentMatricula: agente['matricula'] as String? ?? '',
      agentName: agente['nome'] as String? ?? '',
      apiKey: sessao['api_key'] as String?,
      requestedAt: dispositivo['requested_at'] as String?,
      approvedAt: dispositivo['approved_at'] as String?,
      blockedReason: dispositivo['blocked_reason'] as String? ?? '',
    );
  }
}
