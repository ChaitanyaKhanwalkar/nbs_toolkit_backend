import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nbs_toolkit_frontend/models/recommendation_models.dart';
import 'package:nbs_toolkit_frontend/screens/nbs_screens.dart';
import 'package:nbs_toolkit_frontend/services/recommendation_api.dart';
import 'package:nbs_toolkit_frontend/theme/nbs_theme.dart';

class _FakeRecommendationApi extends RecommendationApi {
  @override
  Future<List<SiteOption>> listSites() async => [
    SiteOption(regionId: 20, station: 'Test Narmada Station', streamOrder: 5),
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
    expect(find.text('Pollution source context'), findsOneWidget);
    expect(find.text('Intervention position'), findsOneWidget);
    expect(find.text('Narmada site / station'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('upload workflow fits at 768x1024', (tester) async {
    await pumpSetup(tester, const Size(768, 1024), 'Upload Water Data');
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
        'missing_inputs': ['Flow rate / design flow', 'Available land'],
        'required_next_steps': ['Develop an off-channel layout.'],
        'expert_review_required': true,
        'input_checklist': [
          {
            'key': 'design_flow',
            'label': 'Flow rate / design flow',
            'status': 'missing',
          },
          {'key': 'bod', 'label': 'BOD', 'status': 'available'},
          {
            'key': 'site_slope',
            'label': 'Slope',
            'status': 'needs_field_verification',
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
          'treatment_sequence': [
            {'step_order': 1, 'step_label': 'ABR', 'role': 'primary'},
          ],
        },
      ],
      'sizing_estimates': [
        {
          'train_id': 1,
          'train_name': 'DEWATS modular train',
          'basis': 'population_equivalent',
          'estimate_label': 'Approximately 240-400 m2',
          'estimated_area_low_m2': 240,
          'estimated_area_high_m2': 400,
          'land_fit': 'borderline',
          'full_component_coverage': true,
          'inputs_used': ['Population equivalent: 100 people'],
          'missing_inputs': ['Confirm design flow'],
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
    expect(find.text('What we recommend'), findsOneWidget);
    expect(find.text('Pollutant gaps and train coverage'), findsNothing);
    expect(find.text('Report and export'), findsNothing);
    expect(find.text('Design readiness'), findsOneWidget);
    expect(find.text('Expert review needed'), findsOneWidget);
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
    expect(find.text('Sizing and land'), findsOneWidget);
    expect(find.text('Scenario comparison'), findsOneWidget);
    expect(find.textContaining('Flow rate / design flow'), findsWidgets);
    expect(find.text('Print / save as PDF'), findsOneWidget);
    expect(tester.takeException(), isNull);
    await tester.tap(find.byTooltip('Close report preview'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Site and design checks'));
    await tester.tap(find.text('Site and design checks'));
    await tester.pumpAndSettle();
    expect(find.text('Location intelligence'), findsOneWidget);
    expect(find.text('River and intervention context'), findsOneWidget);
    expect(tester.takeException(), isNull);
    expect(find.text('Information still needed before design'), findsWidgets);
    expect(find.text('Flow rate / design flow'), findsWidgets);
    expect(find.textContaining('checked in the field'), findsWidgets);
    expect(tester.takeException(), isNull);
    await tester.ensureVisible(find.text('Sizing'));
    await tester.tap(find.text('Sizing'));
    await tester.pumpAndSettle();
    expect(find.text('Sizing and land estimate'), findsOneWidget);
    expect(find.textContaining('Approximately 240-400 m2'), findsWidgets);
    await tester.ensureVisible(find.text('Compare options'));
    await tester.tap(find.text('Compare options'));
    await tester.pumpAndSettle();
    expect(find.text('Best overall fit'), findsOneWidget);
    expect(find.text('Supporting component comparison'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
