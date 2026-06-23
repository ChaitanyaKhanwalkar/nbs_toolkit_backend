/// Verifies the honest location schematic/fallback at mobile and desktop widths.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nbs_toolkit_frontend/models/recommendation_models.dart';
import 'package:nbs_toolkit_frontend/widgets/location_context_diagram.dart';

void main() {
  testWidgets('no-coordinate mainstem schematic renders without overflow', (
    tester,
  ) async {
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

    expect(find.text('Schematic context view'), findsOneWidget);
    expect(find.textContaining('not a surveyed map'), findsOneWidget);
    expect(find.textContaining('Do not build treatment cells'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('verified coordinates are labelled without inventing geometry', (
    tester,
  ) async {
    final location = LocationContext.fromJson({
      'station': 'Verified station',
      'district': 'Bharuch',
      'basin': 'Narmada',
      'river': 'Narmada River',
      'stream_order': 7,
      'coordinates_available': true,
      'latitude': 21.7,
      'longitude': 72.9,
      'context_flags': {'off_channel_required': false},
    });
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: LocationContextDiagram(location: location)),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Offline geo-context panel'), findsOneWidget);
    expect(find.textContaining('not a surveyed GIS map'), findsOneWidget);
    expect(find.text('Verified stored coordinates'), findsOneWidget);
    expect(find.byKey(const ValueKey('verified-location-map')), findsNothing);
    expect(
      find.textContaining('live map tiles are not required'),
      findsOneWidget,
    );
    expect(_richTextContaining(tester, 'Latitude: 21.70000'), isTrue);
    expect(_richTextContaining(tester, 'Longitude: 72.90000'), isTrue);
    expect(
        _richTextContaining(tester, 'Site/station: Verified station'), isTrue);
    expect(_richTextContaining(tester, 'District: Bharuch'), isTrue);
    expect(_richTextContaining(tester, 'Basin: Narmada'), isTrue);
    expect(_richTextContaining(tester, 'River: Narmada River'), isTrue);
    expect(_richTextContaining(tester, 'Stream order: 7'), isTrue);
    expect(find.text('Open in Google Maps'), findsOneWidget);
    expect(find.text('Open in OpenStreetMap'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('missing location renders the explicit no-map state', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: LocationContextDiagram(location: LocationContext.fromJson({})),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(
      find.text('No verified map location is available for this case.'),
      findsOneWidget,
    );
    expect(find.text('Use the site checklist before design.'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}

bool _richTextContaining(WidgetTester tester, String text) {
  return tester
      .widgetList<RichText>(find.byType(RichText))
      .any((widget) => widget.text.toPlainText().contains(text));
}
