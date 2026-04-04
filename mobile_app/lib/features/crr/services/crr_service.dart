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
          'Falha na comunicacao com a API.';
    }
    return 'Falha na comunicacao com a API.';
  }
}
