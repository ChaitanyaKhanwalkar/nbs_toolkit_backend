/// Verifies the offline location schematic at a narrow mobile width.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nbs_toolkit_frontend/models/recommendation_models.dart';
import 'package:nbs_toolkit_frontend/widgets/location_context_diagram.dart';

void main() {
  testWidgets('no-coordinate mainstem schematic renders without overflow',
      (tester) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final location = LocationContext.fromJson({
      'station': 'Test station',
      'stream_order': 6,
      'coordinates_available': false,
      'context_flags': {
        'mainstem_or_high_order': true,
        'off_channel_required': true,
      },
    });
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(12),
            child: LocationContextDiagram(location: location),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Basin context schematic'), findsOneWidget);
    expect(find.textContaining('Do not build treatment cells'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('verified coordinates select the local site schematic',
      (tester) async {
    final location = LocationContext.fromJson({
      'station': 'Verified station',
      'coordinates_available': true,
      'latitude': 21.7,
      'longitude': 72.9,
      'context_flags': {'off_channel_required': false},
    });
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: LocationContextDiagram(location: location),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Local site schematic'), findsOneWidget);
    expect(find.textContaining('Verified location: 21.7000, 72.9000'),
        findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
