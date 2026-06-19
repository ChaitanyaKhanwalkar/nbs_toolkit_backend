import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/recommendation_models.dart';

class SiteOption {
  SiteOption({
    required this.regionId,
    required this.station,
    this.streamOrder,
    this.dischargeCms,
    this.drainageAreaKm2,
  });

  final int regionId;
  final String station;
  final int? streamOrder;
  final double? dischargeCms;
  final double? drainageAreaKm2;

  factory SiteOption.fromJson(Map<String, dynamic> json) => SiteOption(
        regionId: (json['region_id'] as num).toInt(),
        station: json['station']?.toString() ?? 'Station',
        streamOrder: (json['stream_order_strahler'] as num?)?.toInt(),
        dischargeCms: (json['nat_discharge_cms'] as num?)?.toDouble(),
        drainageAreaKm2: (json['drainage_area_km2'] as num?)?.toDouble(),
      );
}

class UploadedWaterCsv {
  UploadedWaterCsv({
    required this.observations,
    required this.unknownParameters,
  });

  final List<Map<String, dynamic>> observations;
  final List<String> unknownParameters;
}

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
    return runContextualRecommendation(
      observations: [
        {'parameter': 'bod', 'value': bod, 'unit': 'mg_l', 'source_id': 101},
        {'parameter': 'tss', 'value': tss, 'unit': 'mg_l', 'source_id': 101},
        {'parameter': 'nitrate_n', 'value': nitrateN, 'unit': 'mg_l', 'source_id': 102},
        {'parameter': 'ph', 'value': ph, 'unit': 'ph_units', 'source_id': 102},
      ],
    );
  }

  Future<RecommendationResponse> runContextualRecommendation({
    required List<Map<String, dynamic>> observations,
    int? regionId,
    String? station,
    String useCase = 'discharge_inland',
    Map<String, dynamic> context = const {},
  }) async {
    final uri = Uri.parse('$_baseUrl/api/v1/recommend');
    late final http.Response response;
    try {
      response = await _client
          .post(
            uri,
            headers: const {'Content-Type': 'application/json'},
            body: jsonEncode({
              'use_case': useCase,
              'selected_parameters': [
                for (final row in observations) row['parameter'],
              ],
              'measured_observations': observations,
              if (regionId != null) 'region_id': regionId,
              if (station != null) 'station': station,
              'context': context,
            }),
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

  Future<List<SiteOption>> listSites() async {
    final response = await _client
        .get(Uri.parse('$_baseUrl/api/v1/sites/options'))
        .timeout(const Duration(seconds: 20));
    if (response.statusCode != 200) {
      throw RecommendationApiException('Could not load Narmada sites.');
    }
    final decoded = jsonDecode(response.body);
    return decoded is List
        ? decoded
            .whereType<Map<String, dynamic>>()
            .map(SiteOption.fromJson)
            .toList()
        : <SiteOption>[];
  }

  Future<int> pollutionSourceCount(int regionId) async {
    final response = await _client
        .get(Uri.parse('$_baseUrl/api/v1/pollution/regions/$regionId'))
        .timeout(const Duration(seconds: 20));
    if (response.statusCode != 200) {
      return 0;
    }
    final decoded = jsonDecode(response.body);
    final rows = decoded is Map<String, dynamic> ? decoded['pollution_sources'] : null;
    return rows is List ? rows.length : 0;
  }

  Future<UploadedWaterCsv> uploadWaterCsv({
    required List<int> bytes,
    required String filename,
    String useCase = 'discharge_inland',
  }) async {
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$_baseUrl/api/v1/water/upload?use_case=$useCase'),
    )..files.add(http.MultipartFile.fromBytes('file', bytes, filename: filename));
    final streamed = await _client.send(request).timeout(const Duration(seconds: 30));
    final response = await http.Response.fromStream(streamed);
    if (response.statusCode != 200) {
      throw RecommendationApiException('CSV upload failed: ${response.body}');
    }
    final decoded = jsonDecode(response.body);
    final rows = decoded is Map<String, dynamic> ? decoded['observations'] : null;
    final unknown = decoded is Map<String, dynamic>
        ? decoded['unknown_parameters']
        : null;
    return UploadedWaterCsv(
      observations: rows is List
          ? rows.whereType<Map<String, dynamic>>().toList()
          : <Map<String, dynamic>>[],
      unknownParameters: unknown is List
          ? unknown.map((value) => value.toString()).toList()
          : <String>[],
    );
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
