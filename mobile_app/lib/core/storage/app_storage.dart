import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:uuid/uuid.dart';

class AppStorage {
  AppStorage() : _storage = const FlutterSecureStorage();

  static const _apiKeyKey = 'api_key';
  static const _matriculaKey = 'matricula';
  static const _deviceIdKey = 'device_id';

  final FlutterSecureStorage _storage;
  final Uuid _uuid = const Uuid();

  Future<String?> readApiKey() => _storage.read(key: _apiKeyKey);

  Future<void> writeApiKey(String value) =>
      _storage.write(key: _apiKeyKey, value: value);

  Future<String?> readMatricula() => _storage.read(key: _matriculaKey);

  Future<void> writeMatricula(String value) =>
      _storage.write(key: _matriculaKey, value: value);

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
  }
}
