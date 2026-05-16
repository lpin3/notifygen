import 'package:dio/dio.dart';

import '../../../core/http/api_client.dart';
import '../models/crr_create_payload.dart';
import '../models/crr_summary.dart';
import '../models/enquadramento_item.dart';

class CrrService {
  CrrService({
    required ApiClient apiClient,
  }) : _apiClient = apiClient;

  final ApiClient _apiClient;

  Future<List<CrrSummary>> listarCrrs() async {
    try {
      final response = await _apiClient.get(
        'crr/',
        authenticated: true,
        includeMatricula: true,
      );

      final data = response.data as Map<String, dynamic>;
      final crrs = (data['crrs'] as List<dynamic>? ?? <dynamic>[])
          .whereType<Map<String, dynamic>>()
          .map(CrrSummary.fromJson)
          .toList();
      return crrs;
    } on DioException catch (error) {
      throw Exception(_extractMessage(error));
    }
  }

  Future<List<CrrSummary>> buscarCrrs({
    String numeroCrr = '',
    String placa = '',
    String marca = '',
    String modelo = '',
    String data = '',
  }) async {
    try {
      final queryParameters = <String, dynamic>{};
      if (numeroCrr.trim().isNotEmpty) {
        queryParameters['numeroCrr'] = numeroCrr.trim();
      }
      if (placa.trim().isNotEmpty) {
        queryParameters['placa'] = placa.trim();
      }
      if (marca.trim().isNotEmpty) {
        queryParameters['marca'] = marca.trim();
      }
      if (modelo.trim().isNotEmpty) {
        queryParameters['modelo'] = modelo.trim();
      }
      if (data.trim().isNotEmpty) {
        queryParameters['data'] = data.trim();
      }

      final response = await _apiClient.get(
        'crr/buscar/',
        authenticated: true,
        queryParameters: queryParameters,
      );
      final dataMap = response.data as Map<String, dynamic>;
      final crrs = (dataMap['crrs'] as List<dynamic>? ?? <dynamic>[])
          .whereType<Map<String, dynamic>>()
          .map(CrrSummary.fromJson)
          .toList();
      return crrs;
    } on DioException catch (error) {
      throw Exception(_extractMessage(error));
    }
  }

  Future<String> obterProximoNumero() async {
    try {
      final response = await _apiClient.get(
        'crr/proximo-numero/',
        authenticated: true,
      );
      final data = response.data as Map<String, dynamic>;
      return data['proximo_numero'] as String? ?? '';
    } on DioException catch (error) {
      throw Exception(_extractMessage(error));
    }
  }

  Future<Map<String, dynamic>> criarCrr(CrrCreatePayload payload) async {
    try {
      final response = await _apiClient.post(
        'crr/criar/',
        authenticated: true,
        data: payload.toJson(),
      );
      return response.data as Map<String, dynamic>;
    } on DioException catch (error) {
      throw Exception(_extractMessage(error));
    }
  }

  Future<List<EnquadramentoItem>> listarEnquadramentos() async {
    try {
      final response = await _apiClient.get(
        'enquadramentos/',
        authenticated: true,
      );

      final data = response.data as Map<String, dynamic>;
      final itens = (data['enquadramentos'] as List<dynamic>? ?? <dynamic>[])
          .whereType<Map<String, dynamic>>()
          .map(EnquadramentoItem.fromJson)
          .toList();
      return itens;
    } on DioException catch (error) {
      throw Exception(_extractMessage(error));
    }
  }

  Future<Map<String, dynamic>> statusDispositivo() async {
    try {
      final response = await _apiClient.get(
        'status/',
        authenticated: true,
        includeMatricula: true,
      );
      return response.data as Map<String, dynamic>;
    } on DioException catch (error) {
      throw Exception(_extractMessage(error));
    }
  }

  String _extractMessage(DioException error) {
    final data = error.response?.data;
    if (data is Map<String, dynamic>) {
      return data['erro'] as String? ??
          data['mensagem'] as String? ??
          _flattenErrors(data['erros']) ??
          'Falha na comunicacao com a API.';
    }
    return error.message ?? 'Falha na comunicacao com a API.';
  }

  String? _flattenErrors(Object? value) {
    if (value is String && value.trim().isNotEmpty) {
      return value;
    }
    if (value is List) {
      final items = value
          .map(_flattenErrors)
          .whereType<String>()
          .where((item) => item.trim().isNotEmpty)
          .toList();
      if (items.isNotEmpty) {
        return items.join('\n');
      }
    }
    if (value is Map) {
      final messages = <String>[];
      value.forEach((key, item) {
        final message = _flattenErrors(item);
        if (message != null && message.trim().isNotEmpty) {
          messages.add('$key: $message');
        }
      });
      if (messages.isNotEmpty) {
        return messages.join('\n');
      }
    }
    return null;
  }
}
