import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nbs_toolkit_frontend/models/recommendation_models.dart';
import 'package:nbs_toolkit_frontend/screens/nbs_screens.dart';
import 'package:nbs_toolkit_frontend/services/recommendation_api.dart';
import 'package:nbs_toolkit_frontend/theme/nbs_theme.dart';

class _FakeRecommendationApi extends RecommendationApi {
  @override
  Future<List<SiteOption>> listSites() async => [
        SiteOption(
            regionId: 20, station: 'Test Narmada Station', streamOrder: 5),
      ];

  @override
  Future<int> pollutionSourceCount(int regionId) async => 2;
}

void main() {
  Future<void> setViewport(WidgetTester tester, Size size) async {
    tester.view.physicalSize = size;
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
  }

  Future<void> pumpSetup(WidgetTester tester, Size size, String mode) async {
    await setViewport(tester, size);
    await tester.pumpWidget(
      MaterialApp(
        theme: NbsTheme.light(),
        home: AnalysisSetupScreen(
          api: _FakeRecommendationApi(),
          mode: mode,
          onRun: (_) {},
          onBack: () {},
        ),
      ),
    );
    await tester.pumpAndSettle();
  }

  testWidgets('pollution selectors stack without overflow at 390x844', (
    tester,
  ) async {
    await pumpSetup(tester, const Size(390, 844), 'Pollution Source Screening');
    expect(find.text('Target use case'), findsOneWidget);
    expect(find.text('Pollution source context'), findsOneWidget);
    expect(find.text('Intervention position'), findsOneWidget);
    expect(find.text('Narmada site / station'), findsOneWidget);
    expect(
      find.text(
        'No site was selected. The result uses only the selected pollution-source context.',
      ),
      findsOneWidget,
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets('upload workflow fits at 768x1024', (tester) async {
    await pumpSetup(tester, const Size(768, 1024), 'Upload Water Data');
    expect(
      find.textContaining('Choose the standard/purpose used to judge'),
      findsOneWidget,
    );
    expect(find.text('Copy template'), findsOneWidget);
    expect(find.text('Example upload format'), findsOneWidget);
    expect(find.text('CSV template'), findsNothing);
    expect(find.textContaining('Blank values remain unknown'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('measured workflow fits at desktop width', (tester) async {
    await pumpSetup(tester, const Size(1280, 900), 'Measured Water Quality');
    expect(find.text('Measured water-quality panel'), findsOneWidget);
    expect(find.text('Faecal coliform'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('target use case is required before recommendation run', (
    tester,
  ) async {
    await pumpSetup(tester, const Size(1280, 900), 'Measured Water Quality');

    await tester.ensureVisible(find.text('Run Recommendation'));
    await tester.tap(find.text('Run Recommendation'));
    await tester.pumpAndSettle();

    expect(
      find.text('Select a target use case before running the recommendation.'),
      findsOneWidget,
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets('municipal fallback pollutant card uses fallback source label', (
    tester,
  ) async {
    await setViewport(tester, const Size(900, 900));
    final response = RecommendationResponse.fromJson({
      'workflow_status': 'completed',
      'use_case': 'discharge_inland',
      'ranked_trains': [
        {
          'train_id': 3,
          'name': 'DEWATS modular train',
          'rank': 1,
          'match_score': 0.78,
          'confidence_score': 0.52,
          'all_use_case_verdicts': {
            'discharge_inland': {'verdict': 'pass'},
          },
          'pollutant_gap_breakdown': [
            {
              'parameter': 'ammonia_n',
              'observed_value': 40,
              'unit': 'mg_l',
              'source': 'canonical',
              'target_threshold': {'limit_high': 50, 'unit': 'mg_l'},
              'gap_status': 'below_target',
              'coverage_category': 'used_in_scoring',
              'train_addresses_parameter': true,
            },
          ],
        },
      ],
      'input_summary': {
        'observation_count': 1,
        'selected_source_type': 'water_type_profile',
        'source_label': 'Municipal influent fallback profile',
        'data_quality_notes': [
          'No measured influent was supplied; user-measured observations override this fallback. Concentrated blackwater is not used as town-scale municipal default.',
        ],
        'data_used': [
          {
            'parameter': 'ammonia_n',
            'value': 40,
            'unit': 'mg_l',
            'source': 'water_type_profile',
            'water_type':
                'Domestic sewage — combined municipal (medium-strong, India)',
          },
        ],
        'context': {
          'workflow_mode': 'pollution_source_screening',
          'pollution_source_type': 'domestic_sewage',
        },
      },
    });

    await tester.pumpWidget(
      MaterialApp(
        theme: NbsTheme.light(),
        home: ResultsScreen(
          response: response,
          onViewDetail: (_) {},
          onNewRun: () {},
          onHome: () {},
          onAbout: () {},
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Why this result'));
    await tester.pumpAndSettle();

    expect(find.text('Municipal influent fallback profile'), findsWidgets);
    expect(find.text('Station and site context'), findsNothing);

    await tester.ensureVisible(find.text('Show technical details'));
    await tester.tap(find.text('Show technical details'));
    await tester.pumpAndSettle();
    expect(
      find.textContaining(
        'Domestic sewage — combined municipal (medium-strong, India)',
      ),
      findsWidgets,
    );
  });

  testWidgets('results component workspace fits at 390x844', (tester) async {
    await setViewport(tester, const Size(390, 844));
    final response = RecommendationResponse.fromJson({
      'workflow_status': 'completed',
      'use_case': 'discharge_inland',
      'location_context': {
        'region_id': 20,
        'station': 'Test Narmada Station',
        'river': 'Narmada',
        'district': 'Test district',
        'stream_order': 5,
        'stream_context': 'Mainstem or high-order river',
        'coordinates_available': false,
        'context_flags': {
          'mainstem_or_high_order': true,
          'off_channel_required': true,
          'site_context_incomplete': true,
        },
        'missing_site_information': ['Verified coordinates'],
        'context_notes': [
          'Off-channel treatment only. Do not build treatment cells inside the river channel.',
        ],
      },
      'design_readiness': {
        'level': 'needs_expert_review',
        'short_label': 'Expert review needed',
        'explanation': 'Mainstem placement requires expert review.',
        'reasons': [
          'Mainstem/high-order placement requires off-channel treatment.',
        ],
        'missing_inputs': ['Treatment design flow', 'Available land'],
        'required_next_steps': ['Develop an off-channel layout.'],
        'expert_review_required': true,
        'input_checklist': [
          {
            'key': 'design_flow',
            'label': 'Treatment design flow',
            'status': 'not_supplied',
          },
          {'key': 'bod', 'label': 'BOD', 'status': 'available'},
          {
            'key': 'site_slope',
            'label': 'Slope',
            'status': 'mapped_context_verify',
          },
        ],
      },
      'ranked_trains': [
        {
          'train_id': 1,
          'name': 'DEWATS modular train',
          'rank': 1,
          'match_score': 0.78,
          'confidence_score': 0.52,
          'confidence_label': 'medium',
          'confidence_explanation': [
            'Four usable water-quality parameters informed this result.',
          ],
          'all_use_case_verdicts': {
            'drinking': {'verdict': 'unknown'},
            'irrigation': {'verdict': 'marginal'},
            'discharge_inland': {'verdict': 'pass'},
          },
          'applicability_result': {'status': 'allowed'},
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
              'criterion_code': 'C2',
              'criterion_name': 'standard_fit',
              'score': 0.7,
              'weight': 0.24,
              'weighted_contribution': 0.08,
              'benefit_or_cost': 'benefit',
              'status': 'known',
            },
            {
              'criterion_code': 'C5',
              'criterion_name': 'health_risk',
              'score': 0.5,
              'weight': 0.1,
              'weighted_contribution': 0.05,
              'benefit_or_cost': 'benefit',
              'status': 'reserved',
            },
          ],
          'train_pathway': [
            {
              'step_order': 1,
              'component_name': 'Settler',
              'component_role': 'primary',
              'nbs_id': null,
            },
            {
              'step_order': 2,
              'component_name': 'ABR',
              'component_role': 'secondary',
              'nbs_id': 17,
            },
          ],
          'treatment_sequence': [
            {'step_order': 1, 'step_label': 'ABR', 'role': 'primary'},
          ],
          'cost_benefit': {
            'screening_cbr': 1.733,
            'display_cbr': '1.73',
            'label': 'Favourable',
            'benefit_score': 0.78,
            'cost_burden_score': 0.45,
            'benefit_drivers': ['C1 treatment fit: 0.82'],
            'cost_drivers': ['C7 footprint burden: 0.30'],
            'caveats': [
              'Screening-level non-monetary ratio. Does not estimate rupee CAPEX/OPEX.',
            ],
            'is_monetary': false,
            'method': 'screening_non_monetary_v1',
            'method_name': 'Cost-Benefit Ratio Analysis - Screening Level',
            'method_disclaimer':
                'Screening-level non-monetary ratio. Does not estimate rupee CAPEX/OPEX.',
            'official_ranking_unchanged': true,
          },
        },
      ],
      'sizing_estimates': [
        {
          'train_id': 1,
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
          'source_ids': [30],
        },
      ],
      'scenario_comparison': {
        'comparison_scope': 'current_ranked_alternatives',
        'current_scenario': {'workflow_mode': 'uploaded_water_quality'},
        'options': [
          {
            'train_id': 1,
            'name': 'DEWATS modular train',
            'rank': 1,
            'technical_match': 0.78,
            'result_confidence': 0.52,
            'design_readiness': 'needs_expert_review',
            'land_demand': 'Approximately 240-400 m2',
            'land_fit': 'borderline',
            'om_intensity': 'Moderate',
            'warnings': ['Keep the train off-channel.'],
            'key_strength': 'Suitable for decentralized treatment.',
            'key_limitation': 'Keep the train off-channel.',
            'when_to_choose':
                'Choose only for an off-channel layout with safe return flow.',
          },
        ],
        'component_options': [
          {
            'nbs_id': 17,
            'name': 'Filter Strip / Vegetated Buffer',
            'role': 'source_control',
            'standalone_suitability': 'source_control_only',
            'applicability_status': 'allowed',
            'key_constraints': ['Not treatment for raw sewage.'],
          },
        ],
        'takeaways': [
          {
            'label': 'Best overall fit',
            'train_id': 1,
            'train_name': 'DEWATS modular train',
            'explanation': 'This is the highest ranked current alternative.',
          },
        ],
        'limitations': ['Run a new case to compare different inputs.'],
      },
      'component_recommendations': [
        {
          'nbs_id': 17,
          'name': 'Filter Strip / Vegetated Buffer',
          'family': 'Stormwater & Green Infrastructure',
          'role': 'source_control',
          'suitability_basis': 'A0-screened context role',
          'standalone_suitability': 'only_as_part_of_train',
          'standalone_guidance':
              'This component supports a treatment train; it is not standalone treatment.',
          'planting_guidance': 'Planting guidance requires local validation.',
          'source_ids': [30],
          'evidence_status': 'eligible',
          'applicability_status': 'allowed',
        },
      ],
      'input_summary': {
        'observation_count': 4,
        'selected_parameters': ['bod', 'cod', 'tss', 'ph'],
        'data_used': [
          {'parameter': 'bod', 'value': 80, 'unit': 'mg_l'},
        ],
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
          'target_available': true,
          'target_limit': {'limit_high': 30, 'unit': 'mg_l'},
          'target_status': 'exceeds_selected_target',
          'coverage_category': 'used_in_scoring',
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
          'parameters': ['COD'],
          'note':
              'Standards coverage note: COD is used as supporting context because no stored target limit is available for discharge to inland surface water.',
        },
        'match_vs_suitability': {
          'explanation':
              'Screening match ranks the train by scored criteria; suitability indicates whether stored evidence confirms the selected use case.',
          'note':
              'Highest screening match has an evidence gap/conditional suitability. Also review the highest confirmed-suitability option: DEWATS modular train.',
        },
        'soil_filter_cautions': [],
        'warnings': [],
      },
    });
    await tester.pumpWidget(
      MaterialApp(
        theme: NbsTheme.light(),
        home: ResultsScreen(
          response: response,
          onViewDetail: (_) {},
          onNewRun: () {},
          onHome: () {},
          onAbout: () {},
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Recommended option'), findsOneWidget);
    expect(find.text('Target and source context'), findsOneWidget);
    expect(find.text('Selected target use case'), findsWidgets);
    expect(find.text('Discharge to inland surface water'), findsWidgets);
    expect(find.text('Pollution source'), findsWidgets);
    expect(find.text('Pollutant gaps and train coverage'), findsNothing);
    expect(find.text('Report and export'), findsNothing);
    expect(find.text('Design readiness'), findsOneWidget);
    expect(find.text('Expert review needed'), findsOneWidget);
    expect(find.byIcon(Icons.warning_amber_outlined), findsWidgets);
    expect(find.text('Estimate land'), findsOneWidget);
    expect(find.text('View diagrams'), findsOneWidget);
    await tester.ensureVisible(find.text('Export'));
    await tester.tap(find.text('Export'));
    await tester.pumpAndSettle();
    expect(find.text('Report and export'), findsOneWidget);
    expect(find.text('Copy summary'), findsOneWidget);
    expect(find.text('Export JSON'), findsOneWidget);
    expect(find.text('Export CSV'), findsOneWidget);
    await tester.tap(find.text('Report preview'));
    await tester.pumpAndSettle();
    expect(find.text('Planning-level report preview'), findsOneWidget);
    expect(find.text('Design readiness'), findsWidgets);
    expect(find.text('Treatment train pathway'), findsOneWidget);
    expect(find.text('Decision X-ray summary'), findsOneWidget);
    expect(find.text('Sizing and land'), findsOneWidget);
    expect(find.text('Scenario comparison'), findsOneWidget);
    expect(find.textContaining('Treatment design flow'), findsWidgets);
    expect(find.text('Print / save as PDF'), findsOneWidget);
    expect(tester.takeException(), isNull);
    await tester.tap(find.byTooltip('Close report preview'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Site and design checks'));
    await tester.tap(find.text('Site and design checks'));
    await tester.pumpAndSettle();
    expect(find.text('Location intelligence'), findsOneWidget);
    expect(find.text('Schematic context view'), findsOneWidget);
    expect(tester.takeException(), isNull);
    expect(find.text('Your input plan'), findsOneWidget);
    expect(find.text('Needed to improve this result'), findsOneWidget);
    expect(find.text('Needed before engineering design'), findsOneWidget);
    expect(find.text('Field checks'), findsOneWidget);
    expect(find.text('Treatment design flow'), findsWidgets);
    expect(find.text('Not supplied'), findsWidgets);
    expect(
      find.text('Available from mapped context; verify in field'),
      findsWidgets,
    );
    expect(tester.takeException(), isNull);
    await tester.ensureVisible(find.text('Sizing'));
    await tester.tap(find.text('Sizing'));
    await tester.pumpAndSettle();
    expect(find.text('Sizing and land estimate'), findsOneWidget);
    expect(find.textContaining('Estimated screening area: 240-400 m²'),
        findsWidgets);
    await tester.ensureVisible(find.text('Compare options'));
    await tester.tap(find.text('Compare options'));
    await tester.pumpAndSettle();
    expect(find.text('Cost-benefit and practicality'), findsOneWidget);
    expect(find.textContaining('does not estimate rupee CAPEX or OPEX'),
        findsOneWidget);
    expect(find.text('Best overall fit'), findsOneWidget);
    expect(find.text('Supporting component comparison'), findsOneWidget);
    await tester.ensureVisible(find.text('Why this result'));
    await tester.tap(find.text('Why this result'));
    await tester.pumpAndSettle();
    expect(
      find.text('Decision X-ray: why this train ranked here'),
      findsOneWidget,
    );
    expect(find.textContaining('C1'), findsWidgets);
    expect(find.textContaining('Treatment fit'), findsWidgets);
    expect(
        find.textContaining('C5 health-risk remains reserved'), findsOneWidget);
    expect(find.textContaining('C5 Health'), findsNothing);
    expect(find.text('Treatment train pathway'), findsOneWidget);
    expect(find.text('Validation notes'), findsWidgets);
    expect(find.textContaining('Standards coverage note'), findsWidgets);
    expect(find.textContaining('Screening match ranks'), findsWidgets);
    expect(find.textContaining('Step 1: Settler'), findsOneWidget);
    expect(find.textContaining('Step 2: Anaerobic Baffled Reactor (ABR)'),
        findsOneWidget);
    expect(find.text('Show technical details'), findsOneWidget);
    expect(find.textContaining('A0 applicability screening'), findsNothing);
    await tester.ensureVisible(find.text('Show technical details'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Show technical details'));
    await tester.pumpAndSettle();
    expect(find.textContaining('site-safety check'), findsOneWidget);
    expect(find.text('Used in scoring'), findsOneWidget);
    expect(
      find.textContaining('The toolkit reads all recognized values'),
      findsOneWidget,
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets('train card shows screening non-monetary cost-benefit panel', (
    tester,
  ) async {
    final response = RecommendationResponse.fromJson({
      'workflow_status': 'completed',
      'use_case': 'discharge_inland',
      'ranked_trains': [
        {
          'train_id': 3,
          'name': 'DEWATS modular train',
          'rank': 1,
          'match_score': 0.78,
          'confidence_score': 0.52,
          'confidence_label': 'medium',
          'applicability_result': {'status': 'allowed'},
          'all_use_case_verdicts': {
            'discharge_inland': {'verdict': 'pass'},
          },
          'cost_benefit': {
            'screening_cbr': 1.733,
            'display_cbr': '1.73',
            'label': 'Favourable',
            'benefit_score': 0.78,
            'cost_burden_score': 0.45,
            'benefit_drivers': ['C1 treatment fit: 0.82'],
            'cost_drivers': ['C7 footprint burden: 0.30'],
            'caveats': [
              'Screening-level non-monetary ratio. Does not estimate rupee CAPEX/OPEX.',
            ],
            'is_monetary': false,
            'method': 'screening_non_monetary_v1',
            'method_name': 'Cost-Benefit Ratio Analysis - Screening Level',
            'method_disclaimer':
                'Screening-level non-monetary ratio. Does not estimate rupee CAPEX/OPEX.',
            'official_ranking_unchanged': true,
          },
        },
      ],
    });
    final train = response.rankedTrains.single;

    await tester.pumpWidget(
      MaterialApp(
        theme: NbsTheme.light(),
        home: Scaffold(
          body: SingleChildScrollView(
            child: TrainRecommendationCard(
              train: train,
              response: response,
              contextOnly: false,
              hasMeasuredData: true,
              citationsById: const {},
              selectedUseCase: 'discharge_inland',
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Cost-Benefit: 1.73 - Favourable'), findsOneWidget);
    await tester.tap(find.textContaining('DEWATS modular train'));
    await tester.pumpAndSettle();
    expect(find.text('Cost-Benefit Ratio Analysis - Screening Level'),
        findsOneWidget);
    expect(find.textContaining('Screening-level, non-monetary'), findsOneWidget);
    expect(find.textContaining('Not a rupee CAPEX/OPEX estimate'), findsOneWidget);
    expect(find.textContaining('ROI'), findsNothing);
  });
}
