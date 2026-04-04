import 'package:dio/dio.dart';

import '../config/app_config.dart';
import '../storage/app_storage.dart';

class ApiClient {
  ApiClient({
    required Dio dio,
    required AppStorage storage,
  })  : _dio = dio,
        _storage = storage {
    _dio.options = BaseOptions(
      baseUrl: AppConfig.baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 20),
      headers: <String, String>{
        'Content-Type': 'application/json',
      },
    );
  }

  final Dio _dio;
  final AppStorage _storage;

  Future<Response<dynamic>> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    bool authenticated = false,
    bool includeMatricula = false,
  }) async {
    return _dio.get<dynamic>(
      path,
      queryParameters: queryParameters,
      options: await _options(
        authenticated: authenticated,
        includeMatricula: includeMatricula,
      ),
    );
  }

  Future<Response<dynamic>> post(
    String path, {
    Object? data,
    bool authenticated = false,
    bool includeMatricula = false,
  }) async {
    return _dio.post<dynamic>(
      path,
      data: data,
      options: await _options(
        authenticated: authenticated,
        includeMatricula: includeMatricula,
      ),
    );
  }

  Future<Response<dynamic>> patch(
    String path, {
    Object? data,
    bool authenticated = false,
    bool includeMatricula = false,
  }) async {
    return _dio.patch<dynamic>(
      path,
      data: data,
      options: await _options(
        authenticated: authenticated,
        includeMatricula: includeMatricula,
      ),
    );
  }

  Future<Options> _options({
    required bool authenticated,
    required bool includeMatricula,
  }) async {
    final headers = <String, String>{};

    if (authenticated) {
      final apiKey = await _storage.readApiKey();
      if (apiKey != null && apiKey.isNotEmpty) {
        headers['X-API-Key'] = apiKey;
      }
    }

    if (includeMatricula) {
      final matricula = await _storage.readMatricula();
      if (matricula != null && matricula.isNotEmpty) {
        headers['X-Matricula'] = matricula;
      }
    }

    return Options(headers: headers);
  }
}
