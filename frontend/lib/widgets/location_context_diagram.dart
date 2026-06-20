/// Draws an offline, data-labelled river and intervention context schematic.
library;

import 'package:flutter/material.dart';

import '../models/recommendation_models.dart';
import '../theme/nbs_theme.dart';

class LocationContextDiagram extends StatelessWidget {
  const LocationContextDiagram({super.key, required this.location});

  final LocationContext location;

  @override
  Widget build(BuildContext context) {
    final highOrder = location.contextFlags['mainstem_or_high_order'] == true;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: NbsColors.researchBlue.withValues(alpha: 0.04),
        border: Border.all(color: NbsColors.cardBorder),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'River and intervention context',
            style: Theme.of(
              context,
            ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 4),
          Text(
            location.coordinatesAvailable
                ? 'The site marker uses verified stored coordinates. Lines and intervention positions are schematic, not surveyed geometry.'
                : 'Verified coordinates are unavailable. This is a schematic context view, not a surveyed map.',
            style: Theme.of(
              context,
            ).textTheme.bodySmall?.copyWith(color: NbsColors.mutedGrey),
          ),
          const SizedBox(height: 12),
          AspectRatio(
            aspectRatio: 2.15,
            child: CustomPaint(
              painter: _LocationContextPainter(
                showSite:
                    location.station != null || location.coordinatesAvailable,
                highOrder: highOrder,
                offChannelRequired:
                    location.contextFlags['off_channel_required'] == true,
                interventionPosition: location.interventionPosition,
              ),
              child: const SizedBox.expand(),
            ),
          ),
          if (location.coordinatesAvailable) ...[
            const SizedBox(height: 8),
            Text(
              'Verified location: ${location.latitude!.toStringAsFixed(4)}, ${location.longitude!.toStringAsFixed(4)}',
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
          ],
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
    final riverPath = Path()
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
    _label(canvas, size, 'intervention point', 0.32, 0.50);

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
      _label(canvas, size, 'off-channel cell', 0.49, 0.71);
      final returnFlow = Paint()
        ..color = NbsColors.riverTeal
        ..strokeWidth = 3
        ..style = PaintingStyle.stroke;
      canvas.drawLine(
        Offset(size.width * 0.71, size.height * 0.76),
        Offset(size.width * 0.79, size.height * 0.50),
        returnFlow,
      );
      _label(canvas, size, 'safe return', 0.75, 0.70);
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
      _label(canvas, size, 'selected site', 0.28, 0.18);
    }
    _label(
      canvas,
      size,
      highOrder ? 'main river' : 'river context',
      0.72,
      0.25,
    );
    _label(canvas, size, 'drain / inflow', 0.08, 0.76);
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
