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
          'label': 'Treatment design flow',
          'status': 'not_supplied',
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
        'criteria_explanation': [
          {
            'criterion_code': 'C1',
            'criterion_name': 'treatment_fit',
            'score': 0.82,
            'weight': 0.24,
            'weighted_contribution': 0.14,
            'benefit_or_cost': 'benefit',
            'status': 'known',
          },
          {
            'criterion_code': 'C7',
            'criterion_name': 'footprint',
            'score': 0.7,
            'weight': 0.1,
            'weighted_contribution': 0.07,
            'benefit_or_cost': 'cost',
            'status': 'known',
          },
          {
            'criterion_code': 'C5',
            'criterion_name': 'health_risk',
            'score': 0.5,
            'weight': 0.1,
            'weighted_contribution': 0.05,
            'status': 'reserved',
          },
        ],
        'train_pathway': [
          {
            'step_order': 1,
            'component_name': 'Settler',
            'component_role': 'primary',
          },
          {
            'step_order': 2,
            'component_name': 'ABR',
            'component_role': 'secondary',
            'nbs_id': 17,
          },
        ],
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
    'sizing_estimates': [
      {
        'train_id': 3,
        'train_name': 'DEWATS modular train',
        'basis': 'design_flow',
        'flow_status': 'supplied',
        'population_status': 'not_supplied',
        'sizing_confidence': 'screening_band',
        'estimate_label': 'Estimated screening area: 240-400 m²',
        'estimated_area_low_m2': 240,
        'estimated_area_high_m2': 400,
        'land_fit': 'borderline',
        'full_component_coverage': true,
        'inputs_used': ['Population equivalent: 100 people'],
        'missing_inputs': ['Confirm peak flow'],
        'key_assumptions': ['The supplied design flow reaches each unit.'],
        'design_caution': 'This is a screening estimate.',
        'source_ids': [14],
      },
    ],
    'scenario_comparison': {
      'comparison_scope': 'current_ranked_alternatives',
      'current_scenario': {'workflow_mode': 'uploaded_water_quality'},
      'options': [
        {
          'train_id': 3,
          'name': 'DEWATS modular train',
          'rank': 1,
          'technical_match': 0.78,
          'result_confidence': 0.52,
          'land_demand': 'Approximately 240-400 m2',
          'land_fit': 'borderline',
          'om_intensity': 'Moderate',
          'selected_use_case_verdict': 'pass',
          'warnings': ['Confirm hydraulic loading.'],
          'key_strength': 'Suitable for decentralized sewage treatment.',
          'key_limitation': 'Confirm hydraulic loading.',
          'when_to_choose':
              'Choose after confirming flow, land, and site conditions.',
        },
      ],
      'component_options': [
        {
          'nbs_id': 17,
          'name': 'Planted gravel filter',
          'role': 'polishing',
          'standalone_suitability': 'only_as_part_of_train',
          'applicability_status': 'allowed',
          'key_constraints': ['Use after primary treatment.'],
        },
      ],
      'takeaways': [
        {
          'label': 'Best overall fit',
          'train_id': 3,
          'train_name': 'DEWATS modular train',
          'explanation': 'This is the highest ranked current alternative.',
        },
      ],
      'limitations': ['Run a new case to compare different inputs.'],
    },
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
      'data_quality_notes': [],
      'selected_source_type': 'user_measured',
      'source_label': 'User-measured observations',
      'context': {
        'workflow_mode': 'uploaded_water_quality',
        'pollution_source_type': 'domestic_sewage',
      },
    },
    'parameter_coverage': [
      {
        'parameter': 'bod',
        'value': 80,
        'unit': 'mg_l',
        'selected_use_case': 'discharge_inland',
        'target_limit': {'limit_high': 30, 'unit': 'mg_l'},
        'target_status': 'exceeds_selected_target',
        'target_available': true,
        'scoring_role': 'used_in_scoring',
        'treatment_evidence_status': 'evidence_supports_treatment',
        'coverage_category': 'used_in_scoring',
        'coverage_label': 'Used in scoring.',
      },
    ],
    'validation_notes': {
      'strict_use': {
        'active': false,
        'warning': null,
        'advanced_treatment_warning': null,
        'blockers': [],
        'pathogen_note': null,
      },
      'salinity': {'active': false, 'warning': null},
      'standards_coverage': {
        'active': true,
        'parameters': ['COD', 'NH4-N'],
        'note':
            'Standards coverage note: COD, NH4-N are used as supporting context because no stored target limit is available for discharge to inland surface water.',
      },
      'match_vs_suitability': {
        'explanation':
            'Screening match ranks the train by scored criteria; suitability indicates whether stored evidence confirms the selected use case.',
        'note': null,
      },
      'soil_filter_cautions': [
        'Conditional: requires confirmed soil/infiltration and groundwater/flood safety checks.',
      ],
      'warnings': [],
    },
  });

  test('builds complete JSON report structure', () {
    final report = RecommendationReport.fromResponse(response);
    final decoded = jsonDecode(report.json) as Map<String, dynamic>;

    expect(decoded['project_input_summary'], isA<Map<String, dynamic>>());
    expect(
      decoded['project_input_summary']['selected_target_use_case'],
      'discharge_inland',
    );
    expect(
      decoded['project_input_summary']['target_use_case_method_note'],
      contains('Target-use-case selection determines standards'),
    );
    expect(decoded['project_input_summary']['pollution_source'],
        'domestic_sewage');
    expect(
      decoded['project_input_summary']['source_label'],
      'User-measured observations',
    );
    expect(decoded['project_input_summary']['parameter_coverage'], isNotEmpty);
    expect(
      decoded['project_input_summary']['parameter_coverage'][0]
          ['selected_use_case'],
      'discharge_inland',
    );
    expect(decoded['location_context']['station'], 'Test station');
    expect(
      decoded['location_context']['map_status'],
      contains('Schematic context'),
    );
    expect(decoded['design_readiness']['short_label'], 'Ready for planning');
    expect(decoded['validation_notes']['standards_coverage']['active'], isTrue);
    expect(
      decoded['design_readiness']['grouped_input_checklist'],
      isA<Map<String, dynamic>>(),
    );
    expect(
      decoded['recommended_treatment_train']['name'],
      'DEWATS modular train — Decentralized Wastewater Treatment System',
    );
    expect(decoded['cost_benefit_and_practicality'], isNotEmpty);
    expect(
      decoded['cost_benefit_and_practicality'][0]['monetary_cost_status'],
      contains('no rupee CAPEX/OPEX values are invented'),
    );
    expect(
      decoded['recommended_treatment_train']['ranking_drivers'],
      isNotEmpty,
    );
    expect(
      decoded['recommended_treatment_train']['criteria_explanation']
          .map((row) => row['criterion_code']),
      isNot(contains('C5')),
    );
    expect(
      decoded['recommended_treatment_train']['treatment_train_pathway'][0]
          ['component_name'],
      'Settler',
    );
    expect(decoded['individual_nbs_components'], isNotEmpty);
    expect(decoded['sizing_and_land'], isNotEmpty);
    expect(decoded['scenario_comparison']['options'], isNotEmpty);
    expect(
      decoded['scenario_comparison']['options'][0]['selected_use_case_verdict'],
      'pass',
    );
    expect(decoded['scenario_comparison']['component_options'], isNotEmpty);
    expect(
      decoded['scenario_comparison']['options'][0]['when_to_choose'],
      contains('confirming flow'),
    );
    expect(decoded['evidence_records'], isNotEmpty);
    expect(decoded['disclaimer'], planningLevelDisclaimer);
  });

  test('builds row-oriented CSV and concise copy summary', () {
    final report = RecommendationReport.fromResponse(response);

    expect(report.baseFileName, 'narmada_nbs_recommendation_report');
    expect(report.csv, startsWith('\uFEFF"section","item","field","value"'));
    expect(report.csv, contains('"recommended_treatment_train"'));
    expect(report.csv, contains('"ranking_drivers"'));
    expect(report.csv, contains('"treatment_train_pathway"'));
    expect(report.csv, contains('"selected_target_use_case"'));
    expect(report.csv, contains('"target_status"'));
    expect(report.csv, contains('"scoring_role"'));
    expect(report.csv, contains('"treatment_evidence_status"'));
    expect(report.csv, contains('"design_readiness"'));
    expect(report.csv, contains('"validation_notes"'));
    expect(report.csv, contains('"standards_coverage.note"'));
    expect(report.csv, contains('"location_context"'));
    expect(report.csv, contains('"sizing_and_land"'));
    expect(report.csv, contains('"scenario_comparison"'));
    expect(report.csv, contains('"evidence_records"'));
    expect(
      report.summary,
      contains(
          'DEWATS modular train — Decentralized Wastewater Treatment System'),
    );
    expect(
      report.summary,
      contains('Selected target use case: Discharge to inland surface water'),
    );
    expect(report.summary, contains('Pollution source: Domestic sewage'));
    expect(report.summary, contains('Screening match: 78.0%'));
    expect(report.summary, contains('Ranking drivers: C1 Treatment fit'));
    expect(
      report.summary,
      contains(
        'Treatment train pathway: Influent/source -> Settler -> Anaerobic Baffled Reactor (ABR)',
      ),
    );
    expect(report.summary, contains('Design readiness: Ready for planning'));
    expect(
      report.summary,
      contains('Sizing and land: Estimated screening area: 240-400 m²'),
    );
    expect(report.summary, contains('Parameter coverage: 1 used in scoring'));
    expect(report.summary, contains('Standards coverage note: COD, NH4-N'));
    expect(
      report.summary,
      contains(
        'Screening match ranks the train by scored criteria; suitability indicates whether stored evidence confirms the selected use case.',
      ),
    );
    expect(report.summary, contains('requires confirmed soil/infiltration'));
    expect(report.summary, contains('Best overall fit'));
    expect(report.summary, contains(planningLevelDisclaimer));
  });

  test('handles missing pathway data without inventing steps', () {
    final partial = RecommendationResponse.fromJson({
      'workflow_status': 'completed',
      'use_case': 'discharge_inland',
      'ranked_trains': [
        {
          'train_id': 1,
          'name': 'Data-limited train',
          'rank': 1,
          'match_score': 0.4,
          'applicability_result': {'status': 'allowed'},
        },
      ],
    });

    final train = partial.rankedTrains.single;
    final report = RecommendationReport.fromResponse(partial);
    final decoded = jsonDecode(report.json) as Map<String, dynamic>;

    expect(train.trainPathway, isEmpty);
    expect(train.criteriaExplanation, isEmpty);
    expect(
      decoded['recommended_treatment_train']['treatment_train_pathway'],
      isEmpty,
    );
  });

  test('summarizes strict-use and salinity validation notes', () {
    final strictResponse = RecommendationResponse.fromJson({
      'workflow_status': 'completed',
      'use_case': 'drinking',
      'design_readiness': {
        'level': 'needs_expert_review',
        'short_label': 'Expert review needed',
        'explanation': 'Strict-use review is required.',
      },
      'ranked_trains': [
        {
          'train_id': 1,
          'name': 'Polishing train',
          'rank': 1,
          'match_score': 0.5,
          'all_use_case_verdicts': {
            'drinking': {'verdict': 'unknown'},
          },
        },
      ],
      'input_summary': {
        'observation_count': 2,
        'selected_parameters': ['ammonia_n', 'ec'],
        'data_used': [
          {'parameter': 'ammonia_n', 'value': 120, 'unit': 'mg_l'},
          {'parameter': 'ec', 'value': 4200, 'unit': 'us_cm'},
        ],
        'context': {'workflow_mode': 'manual_measured_water_quality'},
      },
      'validation_notes': {
        'strict_use': {
          'active': true,
          'warning':
              'Drinking / strict-use screening only. NbS alone must not be used as standalone potable-water treatment.',
          'advanced_treatment_warning':
              'Requires advanced treatment, disinfection, pathogen monitoring, and regulatory validation beyond NbS.',
          'blockers': ['NH4-N'],
          'pathogen_note': null,
        },
        'salinity': {
          'active': true,
          'warning':
              'High EC/salinity exceeds the irrigation target. Ordinary NbS treatment may not reliably remove dissolved salts; consider source control, blending, crop-specific irrigation review, or advanced salinity treatment.',
        },
        'standards_coverage': {'active': false, 'parameters': [], 'note': null},
        'match_vs_suitability': {
          'explanation':
              'Screening match ranks the train by scored criteria; suitability indicates whether stored evidence confirms the selected use case.',
          'note': null,
        },
      },
    });

    final report = RecommendationReport.fromResponse(strictResponse);

    expect(report.summary, contains('NbS alone must not be used'));
    expect(report.summary, contains('Requires advanced treatment'));
    expect(report.summary, contains('Strict-use blockers detected: NH4-N'));
    expect(report.summary, contains('High EC/salinity exceeds'));
  });
}
