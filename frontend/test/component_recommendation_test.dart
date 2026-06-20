import 'package:flutter_test/flutter_test.dart';
import 'package:nbs_toolkit_frontend/models/recommendation_models.dart';

void main() {
  test('parses the separate individual NbS recommendation layer', () {
    final response = RecommendationResponse.fromJson({
      'workflow_status': 'completed',
      'ranked_trains': [
        {'train_id': 1, 'name': 'Primary train', 'rank': 1},
      ],
      'component_recommendation_method': 'a0_screened_component_topsis',
      'component_recommendations': [
        {
          'nbs_id': 17,
          'name': 'Filter Strip / Vegetated Buffer',
          'family': 'Stormwater & Green Infrastructure',
          'component_rank': 1,
          'suitability_score': 0.8,
          'suitability_basis': 'A0-screened component TOPSIS',
          'role': 'source_control',
          'pollutants_addressed': ['tss', 'nitrate'],
          'where_suitable': ['Field edge'],
          'where_not_suitable': ['Untreated industrial wastewater'],
          'standalone_suitability': 'can_be_standalone_source_control',
          'standalone_guidance':
              'Source control only; not standalone wastewater treatment.',
          'key_constraints': ['Validate slope and land.'],
          'plants': [
            {'plant_species': 'Local non-invasive species', 'invasive': 0},
          ],
          'planting_guidance': 'Validate locally.',
          'source_ids': [30],
          'evidence_status': 'eligible',
          'applicability_status': 'allowed',
        },
      ],
      'filtered_components': [
        {
          'nbs_id': 9,
          'name': 'Floating Treatment Wetland',
          'reasons': ['In-channel risk.'],
        },
      ],
      'input_summary': {'context': <String, dynamic>{}},
    });

    expect(response.rankedTrains.single.name, 'Primary train');
    expect(response.componentRecommendations.single.role, 'source_control');
    expect(
      response.componentRecommendations.single.standaloneSuitability,
      'can_be_standalone_source_control',
    );
    expect(response.filteredComponents.single['nbs_id'], 9);
  });
}
