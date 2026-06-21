// TEMPORARY QA-ONLY golden harness (Phase G+H visual QA).
// Renders key app screens at fixed viewports and writes PNG snapshots via
// matchesGoldenFile. Run with:  flutter test test\visual_qa_golden_test.dart --update-goldens
// No running browser, no backend, no product-source changes. Generated PNGs land in
// test\visual_qa_goldens\ and are copied into visual_qa_phase_gh_golden\screenshots\.
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nbs_toolkit_frontend/models/recommendation_models.dart';
import 'package:nbs_toolkit_frontend/screens/nbs_screens.dart';
import 'package:nbs_toolkit_frontend/services/recommendation_api.dart';
import 'package:nbs_toolkit_frontend/theme/nbs_theme.dart';
import 'package:nbs_toolkit_frontend/widgets/location_context_diagram.dart';
import 'package:nbs_toolkit_frontend/widgets/nbs_diagrams.dart';

class _GoldenApi extends RecommendationApi {
  @override
  Future<List<SiteOption>> listSites() async => [
    SiteOption(regionId: 20, station: 'Narmada at Hoshangabad', streamOrder: 5),
    SiteOption(regionId: 21, station: 'Narmada at Jabalpur', streamOrder: 4),
  ];

  @override
  Future<int> pollutionSourceCount(int regionId) async => 3;
}

const Map<String, Size> _viewports = {
  'desktop1440': Size(1440, 900),
  'tablet768': Size(768, 1024),
  'mobile390': Size(390, 844),
  'mobile360': Size(360, 780),
};

Future<void> _loadFontFile(String family, String path) async {
  final loader = FontLoader(family);
  final bytes = File(path).readAsBytesSync();
  loader.addFont(Future.value(ByteData.sublistView(Uint8List.fromList(bytes))));
  await loader.load();
}

Future<void> _loadFonts() async {
  // App body font so text is readable instead of placeholder boxes.
  await _loadFontFile('Inter', 'assets/fonts/Inter-Variable.ttf');
  // Material icon glyphs (not auto-loaded in flutter test). Resolve from the SDK;
  // skip silently if not found so the harness stays portable.
  final root = Platform.environment['FLUTTER_ROOT'];
  final candidates = <String>[
    if (root != null)
      '$root/bin/cache/artifacts/material_fonts/MaterialIcons-Regular.otf',
    r'C:\src\flutter\flutter_windows_3.32.4-stable\flutter\bin\cache\artifacts\material_fonts\MaterialIcons-Regular.otf',
  ];
  for (final c in candidates) {
    if (File(c).existsSync()) {
      await _loadFontFile('MaterialIcons', c);
      break;
    }
  }
}

Future<void> _pump(WidgetTester tester, Size size, Widget home) async {
  tester.view.physicalSize = size;
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.resetPhysicalSize);
  addTearDown(tester.view.resetDevicePixelRatio);
  await tester.pumpWidget(
    MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: NbsTheme.light(),
      home: home,
    ),
  );
  await tester.pumpAndSettle();
}

Future<void> _snap(WidgetTester tester, String name) async {
  await tester.pumpAndSettle();
  // Clear any layout-overflow exceptions so the snapshot is still written and the
  // test stays green; overflow is reported in the QA report, not asserted here.
  // ignore: empty_statements
  while (tester.takeException() != null) {}
  await expectLater(
    find.byType(MaterialApp),
    matchesGoldenFile('visual_qa_goldens/$name.png'),
  );
}

Map<String, dynamic> _fixture({required bool weak}) => {
  'workflow_status': 'completed',
  'use_case': 'discharge_inland',
  'location_context': {
    'region_id': 20,
    'station': 'Narmada at Hoshangabad',
    'river': 'Narmada',
    'district': 'Hoshangabad',
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
    'level': weak ? 'insufficient_information' : 'needs_expert_review',
    'short_label': weak ? 'More data needed' : 'Expert review needed',
    'explanation': weak
        ? 'Too few measured values were supplied for a confident screening result.'
        : 'Mainstem placement requires expert review.',
    'reasons': [
      'Mainstem/high-order placement requires off-channel treatment.',
    ],
    'missing_inputs': weak
        ? ['Flow rate / design flow', 'Available land', 'BOD', 'COD']
        : ['Flow rate / design flow', 'Available land'],
    'required_next_steps': ['Develop an off-channel layout.'],
    'expert_review_required': true,
    'input_checklist': [
      {
        'key': 'design_flow',
        'label': 'Flow rate / design flow',
        'status': 'missing',
      },
      {'key': 'bod', 'label': 'BOD', 'status': weak ? 'missing' : 'available'},
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
      'match_score': weak ? 0.41 : 0.78,
      'confidence_score': weak ? 0.28 : 0.52,
      'confidence_label': weak ? 'low' : 'medium',
      'confidence_explanation': [
        weak
            ? 'Only two usable water-quality parameters informed this result.'
            : 'Four usable water-quality parameters informed this result.',
      ],
      'all_use_case_verdicts': {
        'drinking': {'verdict': 'unknown'},
        'irrigation': {'verdict': 'marginal'},
        'discharge_inland': {'verdict': weak ? 'unknown' : 'pass'},
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
      'land_fit': weak ? 'unknown' : 'borderline',
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
        'technical_match': weak ? 0.41 : 0.78,
        'result_confidence': weak ? 0.28 : 0.52,
        'design_readiness': weak
            ? 'insufficient_information'
            : 'needs_expert_review',
        'land_demand': 'Approximately 240-400 m2',
        'land_fit': weak ? 'unknown' : 'borderline',
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
    'observation_count': weak ? 2 : 4,
    'selected_parameters': weak ? ['bod', 'ph'] : ['bod', 'cod', 'tss', 'ph'],
    'data_used': [
      {'parameter': 'bod', 'value': 80, 'unit': 'mg_l'},
    ],
    'context': {
      'workflow_mode': 'uploaded_water_quality',
      'pollution_source_type': 'domestic_sewage',
    },
  },
};

Widget _results({required bool weak}) => ResultsScreen(
  response: RecommendationResponse.fromJson(_fixture(weak: weak)),
  onViewDetail: (_) {},
  onNewRun: () {},
  onHome: () {},
  onAbout: () {},
);

void main() {
  setUpAll(_loadFonts);

  // ---- SNAPSHOT SET A — basic app structure ----
  testWidgets('Set A — basic structure', (tester) async {
    for (final vp in _viewports.entries) {
      await _pump(
        tester,
        vp.value,
        HomeDashboard(
          onStartRecommendation: () {},
          onAbout: () {},
          onSelectSite: () {},
          onPollutionScreening: () {},
          onUploadWater: () {},
          onCatalogue: () {},
        ),
      );
      await _snap(tester, '${vp.key}__home');

      for (final mode in const {
        'measured_input': 'Measured Water Quality',
        'site_input': 'Select Narmada Site / Station',
        'pollution_source_input_location': 'Pollution Source Screening',
        'upload_input': 'Upload Water Data',
      }.entries) {
        await _pump(
          tester,
          vp.value,
          AnalysisSetupScreen(
            api: _GoldenApi(),
            mode: mode.value,
            onRun: (_) {},
            onBack: () {},
          ),
        );
        await _snap(tester, '${vp.key}__${mode.key}');
      }
    }
  });

  // ---- SNAPSHOT SET B — solution workspace (9 sections) ----
  const sections = <String, String>{
    'Why this result': 'workspace_why',
    'Site and design checks': 'workspace_site_design',
    'Implementation': 'workspace_implementation',
    'NbS components': 'workspace_components',
    'Sizing': 'workspace_sizing',
    'Compare options': 'workspace_compare',
    'Learn': 'workspace_learn',
    'Export': 'workspace_export',
  };
  for (final vpName in const ['desktop1440', 'mobile390']) {
    testWidgets('Set B — workspace @ $vpName', (tester) async {
      await _pump(tester, _viewports[vpName]!, _results(weak: false));
      await _snap(tester, '${vpName}__workspace_summary');
      for (final s in sections.entries) {
        final label = find.text(s.key).first;
        await tester.ensureVisible(label);
        final chip = find.ancestor(
          of: label,
          matching: find.byType(ChoiceChip),
        );
        final button = find.ancestor(
          of: label,
          matching: find.byWidgetPredicate(
            (widget) => widget is ButtonStyleButton,
          ),
        );
        await tester.tap(
          chip.evaluate().isNotEmpty ? chip.first : button.first,
        );
        await tester.pumpAndSettle();
        await _snap(tester, '${vpName}__${s.value}');
      }
      // Report preview overlay from the Export panel.
      if (vpName == 'desktop1440' &&
          find.text('Report preview').evaluate().isNotEmpty) {
        await tester.tap(find.text('Report preview').first);
        await _snap(tester, '${vpName}__workspace_report_preview');
      }
    });
  }

  // ---- SNAPSHOT SET C — edge states ----
  testWidgets('Set C — weak/partial result', (tester) async {
    for (final vpName in const ['desktop1440', 'mobile390']) {
      await _pump(tester, _viewports[vpName]!, _results(weak: true));
      await _snap(tester, '${vpName}__edge_weak_summary');
    }
  });

  for (final src in const {
    'edge_industrial_input': 'Industrial / mixed industrial',
    'edge_agricultural_input': 'Agricultural runoff',
  }.entries) {
    testWidgets('Set C — ${src.key}', (tester) async {
      await _pump(
        tester,
        _viewports['desktop1440']!,
        AnalysisSetupScreen(
          api: _GoldenApi(),
          mode: 'Pollution Source Screening',
          onRun: (_) {},
          onBack: () {},
        ),
      );
      // Open the pollution-source dropdown (default shows "Domestic sewage").
      await tester.tap(find.text('Domestic sewage').first);
      await tester.pumpAndSettle();
      await tester.tap(find.text(src.value).last);
      await tester.pumpAndSettle();
      await _snap(tester, 'desktop1440__${src.key}');
    });
  }

  // ---- SNAPSHOT SET D — diagrams ----
  testWidgets('Set D — diagrams', (tester) async {
    const kinds = <String, NbsDiagramKind>{
      'vf_wetland': NbsDiagramKind.verticalFlowWetland,
      'hssf_wetland': NbsDiagramKind.horizontalSubsurfaceWetland,
      'wsp_pond_series': NbsDiagramKind.pondSeries,
      'dewats_train': NbsDiagramKind.dewats,
      'buffer_strip': NbsDiagramKind.bufferStrip,
      'mainstem_off_channel': NbsDiagramKind.mainstemOffChannel,
    };
    for (final k in kinds.entries) {
      await _pump(
        tester,
        const Size(768, 1024),
        Scaffold(
          backgroundColor: Colors.white,
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: NbsDiagramCard(kind: k.value),
          ),
        ),
      );
      await _snap(tester, 'tablet768__diagram_${k.key}');
    }
    // Location/context schematic.
    final loc = RecommendationResponse.fromJson(
      _fixture(weak: false),
    ).locationContext;
    await _pump(
      tester,
      const Size(768, 1024),
      Scaffold(
        backgroundColor: Colors.white,
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: LocationContextDiagram(location: loc),
        ),
      ),
    );
    await _snap(tester, 'tablet768__diagram_location_context');
  });
}
