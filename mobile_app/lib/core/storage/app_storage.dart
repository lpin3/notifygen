import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:uuid/uuid.dart';

class AppStorage {
  AppStorage() : _storage = const FlutterSecureStorage();

  static const _apiKeyKey = 'api_key';
  static const _matriculaKey = 'matricula';
  static const _agentNameKey = 'agent_name';
  static const _deviceIdKey = 'device_id';
  static const _draftsKey = 'pending_crr_drafts';

  final FlutterSecureStorage _storage;
  final Uuid _uuid = const Uuid();

  Future<String?> readApiKey() => _storage.read(key: _apiKeyKey);

  Future<void> writeApiKey(String value) =>
      _storage.write(key: _apiKeyKey, value: value);

  Future<String?> readMatricula() => _storage.read(key: _matriculaKey);

  Future<void> writeMatricula(String value) =>
      _storage.write(key: _matriculaKey, value: value);

  Future<String?> readAgentName() => _storage.read(key: _agentNameKey);

  Future<void> writeAgentName(String value) =>
      _storage.write(key: _agentNameKey, value: value);

  Future<List<Map<String, dynamic>>> readPendingDrafts() async {
    final raw = await _storage.read(key: _draftsKey);
    if (raw == null || raw.isEmpty) {
      return <Map<String, dynamic>>[];
    }

    final decoded = jsonDecode(raw);
    if (decoded is! List<dynamic>) {
      return <Map<String, dynamic>>[];
    }

    return decoded
        .whereType<Map>()
        .map((item) => Map<String, dynamic>.from(item))
        .toList();
  }

  Future<void> writePendingDrafts(List<Map<String, dynamic>> drafts) async {
    await _storage.write(key: _draftsKey, value: jsonEncode(drafts));
  }

  Future<String> getOrCreateDeviceId() async {
    final current = await _storage.read(key: _deviceIdKey);
    if (current != null && current.isNotEmpty) {
      return current;
    }

    final newId = _uuid.v4();
    await _storage.write(key: _deviceIdKey, value: newId);
    return newId;
  }

  Future<void> clearSession() async {
    await _storage.delete(key: _apiKeyKey);
    await _storage.delete(key: _matriculaKey);
    await _storage.delete(key: _agentNameKey);
  }
}
