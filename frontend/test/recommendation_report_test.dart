/// Verifies the structured recommendation report and portable export formats.
library;

import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:nbs_toolkit_frontend/models/recommendation_models.dart';
import 'package:nbs_toolkit_frontend/services/recommendation_report.dart';

void main() {
  final response = RecommendationResponse.fromJson({
    'workflow_status': 'completed',
    'use_case': 'discharge_inland',
    'global_gaps': ['Confirm design flow.'],
    'location_context': {
      'station': 'Test station',
      'district': 'Test district',
      'coordinates_available': false,
      'context_flags': {'site_context_incomplete': true},
    },
    'design_readiness': {
      'level': 'planning_level_result',
      'short_label': 'Ready for planning',
      'explanation': 'Engineering design is still required.',
      'reasons': ['The core screening panel is available.'],
      'missing_inputs': ['Design flow'],
      'required_next_steps': ['Confirm design flow.'],
      'input_checklist': [
        {
          'key': 'design_flow',
          'label': 'Flow rate / design flow',
          'status': 'missing'
        },
      ],
    },
    'ranked_trains': [
      {
        'train_id': 3,
        'name': 'DEWATS modular train',
        'rank': 1,
        'match_score': 0.78,
        'confidence_score': 0.52,
        'confidence_label': 'medium',
        'why_recommended': ['Suitable for decentralized sewage treatment.'],
        'pretreatment_requirements': ['Screening and settling required.'],
        'data_gaps': ['Confirm hydraulic loading.'],
        'caveats': ['Keep the train off-channel.'],
        'all_use_case_verdicts': {
          'drinking': {'verdict': 'unknown'},
          'irrigation': {'verdict': 'marginal'},
          'discharge_inland': {'verdict': 'pass'},
        },
        'pollutant_gap_breakdown': [
          {'parameter': 'bod', 'gap_status': 'exceeds_target'},
        ],
        'evidence_source_ids': [14],
      },
    ],
    'component_recommendations': [
      {
        'nbs_id': 17,
        'name': 'Planted gravel filter',
        'role': 'polishing',
        'suitability_basis': 'Context screen',
        'standalone_suitability': 'only_as_part_of_train',
        'standalone_guidance': 'Use within the train.',
        'planting_guidance': 'Planting guidance requires local validation.',
        'source_ids': [14],
      },
    ],
    'citations': [
      {'id': 14, 'short': 'CPHEEO treatment guidance'},
    ],
    'input_summary': {
      'observation_count': 1,
      'selected_parameters': ['bod'],
      'data_used': [
        {'parameter': 'bod', 'value': 80, 'unit': 'mg_l'},
      ],
      'context': {'workflow_mode': 'uploaded_water_quality'},
    },
  });

  test('builds complete JSON report structure', () {
    final report = RecommendationReport.fromResponse(response);
    final decoded = jsonDecode(report.json) as Map<String, dynamic>;

    expect(decoded['project_input_summary'], isA<Map<String, dynamic>>());
    expect(decoded['location_context']['station'], 'Test station');
    expect(decoded['design_readiness']['short_label'], 'Ready for planning');
    expect(
      decoded['recommended_treatment_train']['name'],
      'DEWATS modular train',
    );
    expect(decoded['individual_nbs_components'], isNotEmpty);
    expect(decoded['evidence_records'], isNotEmpty);
    expect(decoded['disclaimer'], planningLevelDisclaimer);
  });

  test('builds row-oriented CSV and concise copy summary', () {
    final report = RecommendationReport.fromResponse(response);

    expect(report.csv, startsWith('"section","item","field","value"'));
    expect(report.csv, contains('"recommended_treatment_train"'));
    expect(report.csv, contains('"design_readiness"'));
    expect(report.csv, contains('"location_context"'));
    expect(report.csv, contains('"evidence_records"'));
    expect(report.summary, contains('DEWATS modular train'));
    expect(report.summary, contains('Technical match: 78.0%'));
    expect(report.summary, contains('Design readiness: Ready for planning'));
    expect(report.summary, contains(planningLevelDisclaimer));
  });
}
