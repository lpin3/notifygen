import 'crr_create_payload.dart';

class CrrDraft {
  CrrDraft({
    required this.id,
    required this.payload,
    required this.savedAt,
    this.lastError = '',
  });

  final String id;
  final CrrCreatePayload payload;
  final DateTime savedAt;
  final String lastError;

  factory CrrDraft.fromJson(Map<String, dynamic> json) {
    return CrrDraft(
      id: json['id'] as String? ?? '',
      payload: CrrCreatePayload.fromJson(
        json['payload'] as Map<String, dynamic>? ?? <String, dynamic>{},
      ),
      savedAt: DateTime.tryParse(json['savedAt'] as String? ?? '') ??
          DateTime.fromMillisecondsSinceEpoch(0),
      lastError: json['lastError'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return <String, dynamic>{
      'id': id,
      'payload': payload.toJson(),
      'savedAt': savedAt.toIso8601String(),
      'lastError': lastError,
    };
  }

  CrrDraft copyWith({
    String? id,
    CrrCreatePayload? payload,
    DateTime? savedAt,
    String? lastError,
  }) {
    return CrrDraft(
      id: id ?? this.id,
      payload: payload ?? this.payload,
      savedAt: savedAt ?? this.savedAt,
      lastError: lastError ?? this.lastError,
    );
  }
}
