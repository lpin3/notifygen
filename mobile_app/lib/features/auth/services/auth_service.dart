import 'package:dio/dio.dart';

import '../../../core/http/api_client.dart';
import '../../../core/storage/app_storage.dart';
import '../models/device_activation_response.dart';
import '../models/device_registration_response.dart';

class AuthService {
  AuthService({
    required ApiClient apiClient,
    required AppStorage storage,
  })  : _apiClient = apiClient,
        _storage = storage;

  final ApiClient _apiClient;
  final AppStorage _storage;

  ApiClient get apiClient => _apiClient;

  AppStorage get storage => _storage;

  Future<String> getOrCreateDeviceId() => _storage.getOrCreateDeviceId();

  Future<DeviceRegistrationResponse> registerDevice({
    required String deviceName,
    required String deviceId,
  }) async {
    try {
      final response = await _apiClient.post(
        'registrar/',
        data: <String, dynamic>{
          'nome': deviceName,
          'device_id': deviceId,
          'imei': deviceId,
        },
      );

      return DeviceRegistrationResponse.fromJson(
        response.data as Map<String, dynamic>,
      );
    } on DioException catch (error) {
      throw Exception(_extractMessage(error));
    }
  }

  Future<DeviceActivationResponse> activateDevice({
    required String code,
    required String matricula,
    required String senha,
  }) async {
    try {
      final response = await _apiClient.post(
        'ativar/',
        data: <String, dynamic>{
          'codigo': code,
          'matricula': matricula,
          'senha': senha,
        },
      );

      final parsed = DeviceActivationResponse.fromJson(
        response.data as Map<String, dynamic>,
      );

      await _storage.writeApiKey(parsed.apiKey);
      await _storage.writeMatricula(matricula);
      return parsed;
    } on DioException catch (error) {
      throw Exception(_extractMessage(error));
    }
  }

  Future<void> validateLogin({
    required String apiKey,
    required String matricula,
    required String senha,
  }) async {
    try {
      await _apiClient.post(
        'validar-login/',
        data: <String, dynamic>{
          'api_key': apiKey,
          'matricula': matricula,
          'senha': senha,
        },
      );
    } on DioException catch (error) {
      throw Exception(_extractMessage(error));
    }
  }

  Future<bool> hasSession() async {
    final apiKey = await _storage.readApiKey();
    final matricula = await _storage.readMatricula();
    return (apiKey?.isNotEmpty ?? false) && (matricula?.isNotEmpty ?? false);
  }

  Future<String?> readMatricula() => _storage.readMatricula();

  Future<String?> readApiKey() => _storage.readApiKey();

  Future<void> logout() => _storage.clearSession();

  String _extractMessage(DioException error) {
    final data = error.response?.data;
    if (data is Map<String, dynamic>) {
      return data['erro'] as String? ??
          data['mensagem'] as String? ??
          'Falha na comunicacao com a API.';
    }
    return 'Falha na comunicacao com a API.';
  }
}
