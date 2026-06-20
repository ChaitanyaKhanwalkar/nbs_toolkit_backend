import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nbs_toolkit_frontend/widgets/nbs_diagrams.dart';

void main() {
  testWidgets('priority NbS diagram renders at 390x844 without overflow', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            padding: EdgeInsets.all(12),
            child: NbsDiagramCard(kind: NbsDiagramKind.verticalFlowWetland),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(
      find.byKey(const ValueKey('nbs-diagram-verticalFlowWetland')),
      findsOneWidget,
    );
    expect(find.text('Vertical Flow Wetland'), findsOneWidget);
    expect(find.text('How it works'), findsOneWidget);
    expect(find.text('What to watch for'), findsOneWidget);
    await tester.tap(find.text('How it works'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Distribution pipes'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  test('all six required diagram kinds are available', () {
    expect(
      NbsDiagramKind.values,
      containsAll(<NbsDiagramKind>[
        NbsDiagramKind.verticalFlowWetland,
        NbsDiagramKind.horizontalSubsurfaceWetland,
        NbsDiagramKind.pondSeries,
        NbsDiagramKind.dewats,
        NbsDiagramKind.bufferStrip,
        NbsDiagramKind.mainstemOffChannel,
      ]),
    );
  });
}
