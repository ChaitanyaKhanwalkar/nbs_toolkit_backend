// Widget checks for the Home workflow-card layout at narrow viewport sizes.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nbs_toolkit_frontend/screens/nbs_screens.dart';
import 'package:nbs_toolkit_frontend/theme/nbs_theme.dart';

void main() {
  Future<void> pumpHome(WidgetTester tester, Size size) async {
    tester.view.physicalSize = size;
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      MaterialApp(
        theme: NbsTheme.light(),
        home: HomeDashboard(
          onStartRecommendation: () {},
          onAbout: () {},
          onSelectSite: () {},
          onPollutionScreening: () {},
          onUploadWater: () {},
          onCatalogue: () {},
        ),
      ),
    );
    await tester.pumpAndSettle();
  }

  testWidgets('Home cards do not overflow at 390x844', (tester) async {
    await pumpHome(tester, const Size(390, 844));
    expect(tester.takeException(), isNull);
    expect(find.text('Upload Water Data'), findsOneWidget);
  });

  testWidgets('Home cards do not overflow at 768x1024', (tester) async {
    await pumpHome(tester, const Size(768, 1024));
    expect(tester.takeException(), isNull);
    expect(find.text('Pollution Source Screening'), findsOneWidget);
  });

  testWidgets('Home cards do not overflow at 1280x900', (tester) async {
    await pumpHome(tester, const Size(1280, 900));
    expect(tester.takeException(), isNull);
    expect(find.text('Measured Water Quality'), findsOneWidget);
    expect(find.text('Catalogue'), findsOneWidget);
  });
}
