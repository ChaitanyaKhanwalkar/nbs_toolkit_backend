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

  Future<void> pumpSetup(
    WidgetTester tester,
    Size size,
    String mode,
  ) async {
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

  testWidgets('pollution selectors stack without overflow at 390x844',
      (tester) async {
    await pumpSetup(
      tester,
      const Size(390, 844),
      'Pollution Source Screening',
    );
    expect(find.text('Pollution source context'), findsOneWidget);
    expect(find.text('Intervention position'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('upload workflow fits at 768x1024', (tester) async {
    await pumpSetup(tester, const Size(768, 1024), 'Upload Water Data');
    expect(find.text('Copy template'), findsOneWidget);
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
        'context': {
          'workflow_mode': 'manual_measured_water_quality',
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
    await tester.ensureVisible(find.text('NbS Components'));
    await tester.tap(find.text('NbS Components'));
    await tester.pumpAndSettle();

    expect(find.text('How to read this section'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
