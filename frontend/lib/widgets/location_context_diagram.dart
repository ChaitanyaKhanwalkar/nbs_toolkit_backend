/// Shows verified site context without depending on live map tiles.
library;

import 'dart:ui' as ui;

import 'package:flutter/material.dart';

import '../models/recommendation_models.dart';
import '../services/report_platform.dart';
import '../theme/nbs_theme.dart';

class LocationContextDiagram extends StatelessWidget {
  const LocationContextDiagram({
    super.key,
    required this.location,
    this.enableOnlineTiles = false,
  });

  final LocationContext location;

  /// Retained for old callers; live tiles are intentionally not used.
  final bool enableOnlineTiles;

  @override
  Widget build(BuildContext context) {
    final highOrder = location.contextFlags['mainstem_or_high_order'] == true;
    final hasContext = location.coordinatesAvailable ||
        location.station != null ||
        location.river != null ||
        location.district != null ||
        location.basin != null;

    if (!hasContext) {
      return Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: NbsColors.softBackground,
          border: Border.all(color: NbsColors.cardBorder),
          borderRadius: BorderRadius.circular(8),
        ),
        child: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(Icons.location_off_outlined, color: NbsColors.mutedGrey),
            SizedBox(height: 8),
            Text(
              'No verified map location is available for this case.',
              style: TextStyle(fontWeight: FontWeight.w900),
            ),
            SizedBox(height: 4),
            Text('Use the site checklist before design.'),
          ],
        ),
      );
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: NbsColors.cardBorder),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            location.coordinatesAvailable
                ? 'Offline geo-context panel'
                : 'Schematic context view',
            style: Theme.of(
              context,
            ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 4),
          Text(
            location.coordinatesAvailable
                ? 'This panel shows verified stored coordinates and basin context. It is not a surveyed GIS map.'
                : 'Schematic only, not a surveyed map. Verify the site position and levels before design.',
            style: Theme.of(
              context,
            ).textTheme.bodySmall?.copyWith(color: NbsColors.mutedGrey),
          ),
          const SizedBox(height: 12),
          if (location.coordinatesAvailable)
            _OfflineGeoContextPanel(location: location)
          else
            AspectRatio(
              aspectRatio: 2.15,
              child: CustomPaint(
                painter: _LocationContextPainter(
                  showSite: location.station != null,
                  highOrder: highOrder,
                  offChannelRequired:
                      location.contextFlags['off_channel_required'] == true,
                  interventionPosition: location.interventionPosition,
                ),
                child: const SizedBox.expand(),
              ),
            ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              if (location.station != null)
                _ContextLabel(label: 'Site', value: location.station!),
              if (location.district != null)
                _ContextLabel(label: 'District', value: location.district!),
              if (location.basin != null)
                _ContextLabel(label: 'Basin', value: location.basin!),
              if (location.river != null)
                _ContextLabel(label: 'River', value: location.river!),
              if (location.streamOrder != null)
                _ContextLabel(
                  label: 'Stream order',
                  value: _formatNumber(location.streamOrder!),
                ),
            ],
          ),
          if (highOrder) ...[
            const SizedBox(height: 8),
            const Text(
              'Off-channel treatment only. Do not build treatment cells inside the river channel.',
              style: TextStyle(
                color: NbsColors.warningAmber,
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _OfflineGeoContextPanel extends StatelessWidget {
  const _OfflineGeoContextPanel({required this.location});

  final LocationContext location;

  @override
  Widget build(BuildContext context) {
    final latitude = location.latitude;
    final longitude = location.longitude;
    final hasCoordinates = latitude != null && longitude != null;
    final googleUrl = hasCoordinates
        ? 'https://www.google.com/maps/search/?api=1&query=$latitude,$longitude'
        : null;
    final osmUrl = hasCoordinates
        ? 'https://www.openstreetmap.org/?mlat=$latitude&mlon=$longitude#map=15/$latitude/$longitude'
        : null;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: NbsColors.softBackground,
        border: Border.all(color: NbsColors.cardBorder),
        borderRadius: BorderRadius.circular(6),
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final isWide = constraints.maxWidth > 560;
          final marker = const SizedBox(
            width: 84,
            height: 84,
            child: CustomPaint(painter: _CoordinateMarkerPainter()),
          );
          final details = Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Verified stored coordinates',
                style: TextStyle(fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 8),
              _GeoRow(
                label: 'Latitude',
                value: latitude?.toStringAsFixed(5) ?? 'Not available',
              ),
              _GeoRow(
                label: 'Longitude',
                value: longitude?.toStringAsFixed(5) ?? 'Not available',
              ),
              _GeoRow(
                label: 'Site/station',
                value: _valueOrDash(location.station),
              ),
              _GeoRow(
                  label: 'District', value: _valueOrDash(location.district)),
              _GeoRow(label: 'Basin', value: _valueOrDash(location.basin)),
              _GeoRow(label: 'River', value: _valueOrDash(location.river)),
              _GeoRow(
                label: 'Stream order',
                value: location.streamOrder == null
                    ? 'Not available'
                    : _formatNumber(location.streamOrder!),
              ),
              const SizedBox(height: 8),
              Text(
                'Map status: Verified coordinates available; live map tiles are not required for this demo.',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: NbsColors.mutedGrey,
                      fontWeight: FontWeight.w700,
                    ),
              ),
              if (googleUrl != null && osmUrl != null) ...[
                const SizedBox(height: 10),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    OutlinedButton.icon(
                      onPressed: () => openExternalUrl(googleUrl),
                      icon: const Icon(Icons.open_in_new, size: 17),
                      label: const Text('Open in Google Maps'),
                    ),
                    OutlinedButton.icon(
                      onPressed: () => openExternalUrl(osmUrl),
                      icon: const Icon(Icons.open_in_new, size: 17),
                      label: const Text('Open in OpenStreetMap'),
                    ),
                  ],
                ),
              ],
            ],
          );
          return isWide
              ? Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    marker,
                    const SizedBox(width: 16),
                    Expanded(child: details),
                  ],
                )
              : Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [marker, const SizedBox(height: 12), details],
                );
        },
      ),
    );
  }
}

class _GeoRow extends StatelessWidget {
  const _GeoRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 4),
        child: RichText(
          text: TextSpan(
            style: Theme.of(context).textTheme.bodyMedium,
            children: [
              TextSpan(
                text: '$label: ',
                style: const TextStyle(fontWeight: FontWeight.w800),
              ),
              TextSpan(text: value),
            ],
          ),
        ),
      );
}

class _CoordinateMarkerPainter extends CustomPainter {
  const _CoordinateMarkerPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final grid = Paint()
      ..color = NbsColors.cardBorder
      ..strokeWidth = 1;
    final axis = Paint()
      ..color = NbsColors.riverTeal
      ..strokeWidth = 1.6;
    final marker = Paint()..color = NbsColors.warningAmber;

    canvas.drawRRect(
      RRect.fromRectAndRadius(Offset.zero & size, const Radius.circular(8)),
      Paint()..color = Colors.white,
    );
    for (final fraction in const [0.25, 0.5, 0.75]) {
      canvas.drawLine(
        Offset(size.width * fraction, 8),
        Offset(size.width * fraction, size.height - 8),
        grid,
      );
      canvas.drawLine(
        Offset(8, size.height * fraction),
        Offset(size.width - 8, size.height * fraction),
        grid,
      );
    }
    canvas.drawLine(
        Offset(center.dx, 8), Offset(center.dx, size.height - 8), axis);
    canvas.drawLine(
        Offset(8, center.dy), Offset(size.width - 8, center.dy), axis);
    canvas.drawCircle(center, 7, marker);
    canvas.drawCircle(
      center,
      7,
      Paint()
        ..color = Colors.white
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2,
    );
  }

  @override
  bool shouldRepaint(covariant _CoordinateMarkerPainter oldDelegate) => false;
}

class _ContextLabel extends StatelessWidget {
  const _ContextLabel({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 6),
        decoration: BoxDecoration(
          color: Colors.white,
          border: Border.all(color: NbsColors.cardBorder),
          borderRadius: BorderRadius.circular(6),
        ),
        child: Text(
          '$label: $value',
          style: Theme.of(
            context,
          ).textTheme.bodySmall?.copyWith(fontWeight: FontWeight.w700),
        ),
      );
}

class _LocationContextPainter extends CustomPainter {
  const _LocationContextPainter({
    required this.showSite,
    required this.highOrder,
    required this.offChannelRequired,
    required this.interventionPosition,
  });

  final bool showSite;
  final bool highOrder;
  final bool offChannelRequired;
  final String? interventionPosition;

  @override
  void paint(Canvas canvas, Size size) {
    final background = Paint()..color = const Color(0xFFF7FAF9);
    canvas.drawRRect(
      RRect.fromRectAndRadius(Offset.zero & size, const Radius.circular(6)),
      background,
    );

    final river = Paint()
      ..color = NbsColors.riverTeal
      ..strokeWidth = highOrder ? 18 : 11
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final riverPath = ui.Path()
      ..moveTo(size.width * 0.04, size.height * 0.34)
      ..cubicTo(
        size.width * 0.30,
        size.height * 0.16,
        size.width * 0.55,
        size.height * 0.62,
        size.width * 0.96,
        size.height * 0.42,
      );

    canvas.drawPath(riverPath, river);

    final drain = Paint()
      ..color = NbsColors.researchBlue
      ..strokeWidth = 5
      ..style = PaintingStyle.stroke;

    canvas.drawLine(
      Offset(size.width * 0.27, size.height * 0.82),
      Offset(size.width * 0.37, size.height * 0.39),
      drain,
    );

    final interception = Offset(size.width * 0.37, size.height * 0.43);
    canvas.drawCircle(interception, 7, Paint()..color = NbsColors.deepNavy);
    _label(canvas, size, 'Intervention point', 0.32, 0.50);

    if (offChannelRequired) {
      final cellRect = Rect.fromLTWH(
        size.width * 0.46,
        size.height * 0.67,
        size.width * 0.25,
        size.height * 0.20,
      );

      canvas.drawRRect(
        RRect.fromRectAndRadius(cellRect, const Radius.circular(8)),
        Paint()..color = NbsColors.wetlandGreen.withValues(alpha: 0.28),
      );

      canvas.drawRRect(
        RRect.fromRectAndRadius(cellRect, const Radius.circular(8)),
        Paint()
          ..color = NbsColors.wetlandGreen
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2,
      );

      _label(canvas, size, 'Off-channel treatment', 0.49, 0.71);

      final returnFlow = Paint()
        ..color = NbsColors.riverTeal
        ..strokeWidth = 3
        ..style = PaintingStyle.stroke;

      canvas.drawLine(
        Offset(size.width * 0.71, size.height * 0.76),
        Offset(size.width * 0.79, size.height * 0.50),
        returnFlow,
      );

      _label(canvas, size, 'Safe return flow', 0.75, 0.70);
    }

    if (showSite) {
      final marker = Offset(size.width * 0.37, size.height * 0.35);
      canvas.drawCircle(marker, 9, Paint()..color = NbsColors.warningAmber);
      canvas.drawCircle(
        marker,
        9,
        Paint()
          ..color = Colors.white
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2,
      );
      _label(canvas, size, 'Selected site or station', 0.24, 0.14, width: 0.36);
    }

    _label(
      canvas,
      size,
      highOrder ? 'Main river channel' : 'River / drain context',
      0.72,
      0.25,
    );

    _label(canvas, size, 'Drain or wastewater inflow', 0.04, 0.76, width: 0.36);

    if (interventionPosition != null && interventionPosition!.isNotEmpty) {
      _label(canvas, size, interventionPosition!, 0.02, 0.04, width: 0.40);
    }
  }

  void _label(
    Canvas canvas,
    Size size,
    String text,
    double x,
    double y, {
    double width = 0.28,
  }) {
    final painter = TextPainter(
      text: TextSpan(
        text: text,
        style: const TextStyle(
          color: NbsColors.deepNavy,
          fontSize: 11,
          fontWeight: FontWeight.w700,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout(maxWidth: size.width * width);

    painter.paint(canvas, Offset(size.width * x, size.height * y));
  }

  @override
  bool shouldRepaint(covariant _LocationContextPainter oldDelegate) =>
      oldDelegate.showSite != showSite ||
      oldDelegate.highOrder != highOrder ||
      oldDelegate.offChannelRequired != offChannelRequired ||
      oldDelegate.interventionPosition != interventionPosition;
}

String _valueOrDash(String? value) {
  final trimmed = value?.trim();
  if (trimmed == null || trimmed.isEmpty) return 'Not available';
  return trimmed;
}

String _formatNumber(double value) {
  if (value == value.roundToDouble()) return value.toStringAsFixed(0);
  return value.toStringAsFixed(1);
}
