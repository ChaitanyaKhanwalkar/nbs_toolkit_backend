import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/recommendation_models.dart';

class RecommendationApi {
  RecommendationApi({
    http.Client? client,
    String? baseUrl,
  })  : _client = client ?? http.Client(),
        _baseUrl = _cleanBaseUrl(
          baseUrl ??
              const String.fromEnvironment(
                'API_BASE_URL',
                defaultValue: 'http://127.0.0.1:8000',
              ),
        );

  final http.Client _client;
  final String _baseUrl;

  Future<RecommendationResponse> runRecommendation({
    required double bod,
    required double tss,
    required double nitrateN,
    required double ph,
  }) async {
    final uri = Uri.parse('$_baseUrl/api/v1/recommend');
    late final http.Response response;
    try {
      response = await _client
          .post(
            uri,
            headers: const {'Content-Type': 'application/json'},
            body: jsonEncode(_requestBody(
              bod: bod,
              tss: tss,
              nitrateN: nitrateN,
              ph: ph,
            )),
          )
          .timeout(const Duration(seconds: 35));
    } on RecommendationApiException {
      rethrow;
    } on TimeoutException {
      throw RecommendationApiException(
        'Backend not reachable. Check backend server and API_BASE_URL.',
      );
    } on http.ClientException {
      throw RecommendationApiException(
        'Backend not reachable. Check backend server and API_BASE_URL.',
      );
    } on Object {
      throw RecommendationApiException(
        'Backend not reachable. Check backend server and API_BASE_URL.',
      );
    }

    final bodyText = response.body;
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw RecommendationApiException(
        'Backend returned ${response.statusCode}. Check backend server and API_BASE_URL.',
      );
    }

    final decoded = jsonDecode(bodyText);
    if (decoded is! Map<String, dynamic>) {
      throw RecommendationApiException('Backend response was not a valid object.');
    }

    final parsed = RecommendationResponse.fromJson(decoded);
    if (parsed.workflowStatus == 'failed' || parsed.errors.isNotEmpty) {
      throw RecommendationApiException(
        parsed.errors.isNotEmpty
            ? parsed.errors.join('\n')
            : 'Recommendation workflow failed safely.',
      );
    }
    return parsed;
  }

  Map<String, dynamic> _requestBody({
    required double bod,
    required double tss,
    required double nitrateN,
    required double ph,
  }) {
    return {
      'use_case': 'discharge_inland',
      'selected_parameters': ['bod', 'tss', 'nitrate_n', 'ph'],
      'measured_observations': [
        {'parameter': 'bod', 'value': bod, 'unit': 'mg_l', 'source_id': 101},
        {'parameter': 'tss', 'value': tss, 'unit': 'mg_l', 'source_id': 101},
        {
          'parameter': 'nitrate_n',
          'value': nitrateN,
          'unit': 'mg_l',
          'source_id': 102,
        },
        {'parameter': 'ph', 'value': ph, 'unit': 'ph_units', 'source_id': 102},
      ],
      // No weights are sent on purpose: the backend supplies transparent,
      // provisional default criteria weights (single source of truth in
      // backend/app/core/default_weights.py) so there is one place to swap in
      // the supervisor's expert AHP weights later.
    };
  }
}

String _cleanBaseUrl(String rawBaseUrl) {
  var cleaned = rawBaseUrl.trim();
  while (cleaned.endsWith('/')) {
    cleaned = cleaned.substring(0, cleaned.length - 1);
  }
  if (cleaned.isEmpty || cleaned.contains(' ') || cleaned.contains('%20')) {
    throw RecommendationApiException(
      'Backend not reachable. Check backend server and API_BASE_URL.',
    );
  }
  if (cleaned.endsWith('/api/v1/recommend')) {
    cleaned = cleaned.substring(0, cleaned.length - '/api/v1/recommend'.length);
  }
  return cleaned;
}

class RecommendationApiException implements Exception {
  RecommendationApiException(this.message);

  final String message;

  @override
  String toString() => message;
}
