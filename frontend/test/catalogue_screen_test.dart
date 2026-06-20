import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nbs_toolkit_frontend/screens/nbs_screens.dart';
import 'package:nbs_toolkit_frontend/services/recommendation_api.dart';
import 'package:nbs_toolkit_frontend/theme/nbs_theme.dart';

class _FakeCatalogueApi extends RecommendationApi {
  @override
  Future<Map<String, dynamic>> loadLearningCatalogue() async => {
        'treatment_trains': [
          {
            'train_id': 1,
            'name': 'Canonical treatment train',
            'intended_role': 'Primary-to-polishing treatment train',
            'sequence_steps': [
              {'step_label': 'Screening'},
              {'step_label': 'Wetland polishing'},
            ],
            'use_case_suitability': [
              {
                'use_case': 'discharge_inland',
                'pass_count': 1,
                'marginal_count': 1,
                'fail_count': 0,
                'unknown_count': 1,
              },
            ],
            'strengths': ['Gravity treatment sequence.'],
            'limitations': ['Validate hydraulic loading.'],
            'pretreatment_needs': ['Screening required.'],
            'om_notes': ['Inspect inlet and outlet.'],
            'components': [
              {'name': 'Wetland', 'role': 'polishing'},
            ],
            'plants': <Map<String, dynamic>>[],
            'source_ids': [14],
          },
        ],
        'nbs_components': [
          {
            'id': 1,
            'solution': 'Constructed Wetland',
            'family': 'Constructed Wetlands',
            'catalogue_role': 'Secondary treatment / polishing component',
            'pollutants_treated': ['bod', 'tss'],
            'where_suitable': ['Off-channel treatment'],
            'where_not_suitable': ['Not an in-channel mainstem cell.'],
            'design_notes': ['Lined media bed.'],
            'maintenance_notes': ['Inspect clogging.'],
            'plants': <Map<String, dynamic>>[],
            'standalone_suitability': 'Context-specific A0 screening required.',
            'source_ids': [14],
          },
        ],
        'plants': [
          {
            'id': 1,
            'plant_species': 'Example invasive plant',
            'invasive': 1,
            'recommendation_status': 'do_not_recommend_invasive',
            'mapped_components': [
              {'name': 'Constructed Wetland', 'basis': 'Canonical mapping'},
            ],
            'source_ids': [14],
          },
        ],
      };
}

void main() {
  Future<void> pumpCatalogue(WidgetTester tester) async {
    tester.view.physicalSize = const Size(1280, 900);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(
      MaterialApp(
        theme: NbsTheme.light(),
        home: CatalogueScreen(api: _FakeCatalogueApi(), onBack: () {}),
      ),
    );
    await tester.pumpAndSettle();
  }

  testWidgets('renders train catalogue and searchable empty state',
      (tester) async {
    await pumpCatalogue(tester);
    expect(find.text('Canonical treatment train'), findsOneWidget);
    await tester.enterText(find.byType(TextField), 'no matching record');
    await tester.pumpAndSettle();
    expect(find.text('No catalogue matches'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('plant catalogue exposes invasive do-not-recommend warning',
      (tester) async {
    await pumpCatalogue(tester);
    await tester.tap(find.text('Plants'));
    await tester.pumpAndSettle();
    expect(find.text('Example invasive plant'), findsOneWidget);
    expect(find.text('Invasive - do not recommend for planting'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
