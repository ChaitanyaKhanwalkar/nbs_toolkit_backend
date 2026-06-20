/// Educational engineering schematics for treatment and source-control options.
library;

import 'package:flutter/material.dart';

enum NbsDiagramKind {
  verticalFlowWetland,
  horizontalSubsurfaceWetland,
  pondSeries,
  dewats,
  bufferStrip,
  mainstemOffChannel,
}

class NbsDiagramCard extends StatelessWidget {
  const NbsDiagramCard({super.key, required this.kind});

  final NbsDiagramKind kind;

  @override
  Widget build(BuildContext context) {
    final copy = _copy[kind]!;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FBFC),
        border: Border.all(color: const Color(0xFFD7E2E7)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            copy.title,
            style: Theme.of(
              context,
            ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 3),
          Text(
            copy.fit,
            style: Theme.of(
              context,
            ).textTheme.bodySmall?.copyWith(color: const Color(0xFF52636D)),
          ),
          const SizedBox(height: 10),
          AspectRatio(
            aspectRatio: 2.1,
            child: CustomPaint(
              key: ValueKey('nbs-diagram-${kind.name}'),
              painter: _NbsDiagramPainter(kind),
              size: Size.infinite,
            ),
          ),
          const SizedBox(height: 9),
          Text(
            copy.explanation,
            style: Theme.of(
              context,
            ).textTheme.bodyMedium?.copyWith(height: 1.4),
          ),
          const SizedBox(height: 6),
          _DiagramDisclosure(title: 'How it works', values: copy.howItWorks),
          _DiagramDisclosure(title: 'What to watch for', values: copy.watchFor),
        ],
      ),
    );
  }
}

class _DiagramDisclosure extends StatelessWidget {
  const _DiagramDisclosure({required this.title, required this.values});

  final String title;
  final List<String> values;

  @override
  Widget build(BuildContext context) => ExpansionTile(
    tilePadding: EdgeInsets.zero,
    childrenPadding: const EdgeInsets.only(bottom: 8),
    dense: true,
    title: Text(title, style: const TextStyle(fontWeight: FontWeight.w800)),
    children: [
      for (final value in values)
        Padding(
          padding: const EdgeInsets.only(bottom: 5),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Padding(
                padding: EdgeInsets.only(top: 7),
                child: Icon(Icons.circle, size: 5, color: Color(0xFF4D8B63)),
              ),
              const SizedBox(width: 8),
              Expanded(child: Text(value)),
            ],
          ),
        ),
    ],
  );
}

NbsDiagramKind? diagramForTrainName(String? name) {
  final value = (name ?? '').toLowerCase();
  if (value.contains('dewats')) return NbsDiagramKind.dewats;
  if (value.contains('wsp') || value.contains('pond series')) {
    return NbsDiagramKind.pondSeries;
  }
  if (value.contains('vf') || value.contains('vertical flow')) {
    return NbsDiagramKind.verticalFlowWetland;
  }
  if (value.contains('hssf') || value.contains('horizontal subsurface')) {
    return NbsDiagramKind.horizontalSubsurfaceWetland;
  }
  return null;
}

NbsDiagramKind? diagramForComponentName(String? name) {
  final value = (name ?? '').toLowerCase();
  if (value.contains('vertical flow')) {
    return NbsDiagramKind.verticalFlowWetland;
  }
  if (value.contains('horizontal subsurface') || value.contains('hssf')) {
    return NbsDiagramKind.horizontalSubsurfaceWetland;
  }
  if (value.contains('filter strip') ||
      value.contains('buffer') ||
      value.contains('riparian')) {
    return NbsDiagramKind.bufferStrip;
  }
  return null;
}

typedef _DiagramCopy = ({
  String title,
  String fit,
  String explanation,
  List<String> howItWorks,
  List<String> watchFor,
});

const _copy = <NbsDiagramKind, _DiagramCopy>{
  NbsDiagramKind.verticalFlowWetland: (
    title: 'Vertical Flow Wetland',
    fit: 'Secondary treatment or polishing after primary solids removal.',
    explanation:
        'Pre-settled water is dosed across a planted media bed and moves downward to an underdrain. Intermittent loading helps keep the bed oxygenated.',
    howItWorks: [
      'Distribution pipes spread pretreated flow across the bed.',
      'Sand, gravel, biofilm, and plant roots support filtration and treatment.',
      'An underdrain collects treated water for polishing or discharge review.',
    ],
    watchFor: [
      'Provide solids removal before the bed.',
      'Check dosing, resting cycles, media grading, and clogging risk during design.',
    ],
  ),
  NbsDiagramKind.horizontalSubsurfaceWetland: (
    title: 'Horizontal Subsurface Flow Wetland',
    fit: 'Subsurface polishing after primary treatment.',
    explanation:
        'Pretreated water moves horizontally below the surface through planted gravel. The subsurface path limits direct exposure while biofilm and roots support polishing.',
    howItWorks: [
      'An inlet zone distributes flow across the bed width.',
      'Water travels through planted porous media below the surface.',
      'A controlled outlet maintains the intended water level.',
    ],
    watchFor: [
      'Use after effective primary treatment.',
      'Check hydraulic short-circuiting, media clogging, and outlet control.',
    ],
  ),
  NbsDiagramKind.pondSeries: (
    title: 'Waste Stabilization Pond Series',
    fit: 'Land-based staged treatment for suitable small and medium flows.',
    explanation:
        'Wastewater passes through ponds with different treatment roles. The sequence separates solids stabilization, biological treatment, and final pathogen reduction.',
    howItWorks: [
      'Preliminary treatment protects the pond system.',
      'Anaerobic and facultative stages reduce organic load.',
      'Maturation ponds provide final polishing where evidence and design support it.',
    ],
    watchFor: [
      'Confirm adequate land, lining, detention time, and safe setbacks.',
      'Plan for odour, sludge, mosquito, and overflow management.',
    ],
  ),
  NbsDiagramKind.dewats: (
    title: 'DEWATS Modular Flow',
    fit: 'Decentralized sewage treatment or off-channel polishing.',
    explanation:
        'A modular sequence combines solids removal, baffled anaerobic treatment, planted filtration, and polishing. Each unit has a distinct role and must be designed as a train.',
    howItWorks: [
      'Screening and settling remove coarse and settleable solids.',
      'Baffled reactors provide enclosed biological treatment.',
      'Planted filters and polishing units refine the effluent.',
    ],
    watchFor: [
      'Keep the full train accessible for desludging and maintenance.',
      'Do not place treatment units inside the river channel.',
    ],
  ),
  NbsDiagramKind.bufferStrip: (
    title: 'Buffer / Riparian Strip',
    fit:
        'Field and edge-of-field source control before runoff reaches a stream.',
    explanation:
        'Dense vegetation slows shallow runoff before it reaches a drain or stream. This supports sediment trapping and nutrient source control at field edges.',
    howItWorks: [
      'Runoff spreads across a vegetated strip instead of concentrating in one path.',
      'Reduced velocity encourages sediment deposition and infiltration.',
      'Vegetation stabilizes soil and supports nutrient uptake.',
    ],
    watchFor: [
      'Do not use this as treatment for raw sewage.',
      'Maintain flow spreading and avoid recommending invasive plants.',
    ],
  ),
  NbsDiagramKind.mainstemOffChannel: (
    title: 'Drain Interception and Off-channel Treatment',
    fit: 'Mainstem safety layout for intercepted drains and safe return flow.',
    explanation:
        'A polluted drain is intercepted before it enters the main river and routed to a land-based treatment train. Treated flow returns only after monitoring and compliance review.',
    howItWorks: [
      'Intercept the drain at a safe, accessible point.',
      'Route flow to pretreatment and suitable off-channel units.',
      'Monitor the treated return before discharge.',
    ],
    watchFor: [
      'Do not obstruct river conveyance or build cells in the main channel.',
      'Survey levels, flood risk, land ownership, and bypass capacity.',
    ],
  ),
};

class _NbsDiagramPainter extends CustomPainter {
  _NbsDiagramPainter(this.kind);

  final NbsDiagramKind kind;
  static const navy = Color(0xFF17324D);
  static const water = Color(0xFF67B7C7);
  static const green = Color(0xFF4D8B63);
  static const soil = Color(0xFFB99368);
  static const pale = Color(0xFFE8F1F3);

  @override
  void paint(Canvas canvas, Size size) {
    final rect = Offset.zero & size;
    canvas.drawRRect(
      RRect.fromRectAndRadius(rect, const Radius.circular(6)),
      Paint()..color = Colors.white,
    );
    switch (kind) {
      case NbsDiagramKind.verticalFlowWetland:
        _vertical(canvas, size);
      case NbsDiagramKind.horizontalSubsurfaceWetland:
        _horizontal(canvas, size);
      case NbsDiagramKind.pondSeries:
        _pondSeries(canvas, size);
      case NbsDiagramKind.dewats:
        _dewats(canvas, size);
      case NbsDiagramKind.bufferStrip:
        _buffer(canvas, size);
      case NbsDiagramKind.mainstemOffChannel:
        _mainstem(canvas, size);
    }
  }

  void _vertical(Canvas c, Size s) {
    final bed = Rect.fromLTWH(
      s.width * .20,
      s.height * .25,
      s.width * .60,
      s.height * .56,
    );
    c.drawRect(bed, Paint()..color = soil.withValues(alpha: .45));
    c.drawRect(
      Rect.fromLTWH(
        bed.left,
        bed.top + bed.height * .58,
        bed.width,
        bed.height * .42,
      ),
      Paint()..color = pale,
    );
    _plants(c, s, bed.top);
    _pipe(
      c,
      Offset(bed.left, bed.bottom - 8),
      Offset(bed.right, bed.bottom - 8),
    );
    for (final x in [.36, .50, .64]) {
      _arrow(
        c,
        Offset(s.width * x, bed.top + 6),
        Offset(s.width * x, bed.bottom - 18),
      );
    }
    _label(c, s, 'inlet distribution', .03, .12);
    _label(c, s, 'planted sand/gravel', .27, .04);
    _label(c, s, 'vertical flow', .42, .45);
    _label(c, s, 'underdrain', .37, .83);
    _label(c, s, 'to polishing', .79, .70);
  }

  void _horizontal(Canvas c, Size s) {
    final bed = Rect.fromLTWH(
      s.width * .16,
      s.height * .28,
      s.width * .68,
      s.height * .52,
    );
    c.drawRect(bed, Paint()..color = soil.withValues(alpha: .42));
    _plants(c, s, bed.top);
    for (final y in [.46, .60, .72]) {
      _arrow(
        c,
        Offset(bed.left + 10, s.height * y),
        Offset(bed.right - 10, s.height * y),
      );
    }
    _label(c, s, 'inlet zone', .02, .42);
    _label(c, s, 'subsurface gravel bed', .26, .08);
    _label(c, s, 'plant roots', .42, .28);
    _label(c, s, 'horizontal flow', .39, .58);
    _label(c, s, 'outlet', .85, .48);
  }

  void _pondSeries(Canvas c, Size s) {
    const names = [
      'screening',
      'anaerobic',
      'facultative',
      'maturation',
      'discharge',
    ];
    for (var i = 0; i < names.length; i++) {
      final left = s.width * (.02 + i * .195);
      final box = Rect.fromLTWH(
        left,
        s.height * .36,
        s.width * .15,
        s.height * .28,
      );
      c.drawRRect(
        RRect.fromRectAndRadius(box, const Radius.circular(5)),
        Paint()..color = i == 0 ? pale : water.withValues(alpha: .42 + i * .08),
      );
      _label(c, s, names[i], .01 + i * .195, .69, width: .18);
      if (i < names.length - 1) {
        _arrow(
          c,
          Offset(box.right + 2, box.center.dy),
          Offset(box.right + s.width * .04, box.center.dy),
        );
      }
    }
  }

  void _dewats(Canvas c, Size s) {
    const names = [
      'screen/grit',
      'settler',
      'baffled reactor',
      'planted filter',
      'polishing',
    ];
    for (var i = 0; i < names.length; i++) {
      final left = s.width * (.015 + i * .197);
      final box = Rect.fromLTWH(
        left,
        s.height * .32,
        s.width * .155,
        s.height * .32,
      );
      c.drawRRect(
        RRect.fromRectAndRadius(box, const Radius.circular(5)),
        Paint()..color = i == 3 ? green.withValues(alpha: .35) : pale,
      );
      _label(c, s, names[i], .006 + i * .197, .69, width: .18);
      if (i < names.length - 1) {
        _arrow(
          c,
          Offset(box.right + 2, box.center.dy),
          Offset(box.right + s.width * .04, box.center.dy),
        );
      }
    }
  }

  void _buffer(Canvas c, Size s) {
    final ground = Path()
      ..moveTo(0, s.height * .30)
      ..lineTo(s.width, s.height * .68)
      ..lineTo(s.width, s.height)
      ..lineTo(0, s.height)
      ..close();
    c.drawPath(ground, Paint()..color = soil.withValues(alpha: .35));
    c.drawRect(
      Rect.fromLTWH(
        s.width * .75,
        s.height * .64,
        s.width * .25,
        s.height * .24,
      ),
      Paint()..color = water.withValues(alpha: .65),
    );
    for (var i = 0; i < 9; i++) {
      final x = s.width * (.34 + i * .045);
      c.drawLine(
        Offset(x, s.height * (.43 + i * .017)),
        Offset(x, s.height * (.31 + i * .017)),
        Paint()
          ..color = green
          ..strokeWidth = 2,
      );
    }
    _arrow(
      c,
      Offset(s.width * .10, s.height * .36),
      Offset(s.width * .42, s.height * .52),
    );
    _label(c, s, 'field runoff', .02, .14);
    _label(c, s, 'grass/filter strip', .32, .08);
    _label(c, s, 'sediment trapping', .34, .62);
    _label(c, s, 'riparian plants', .58, .32);
    _label(c, s, 'stream', .82, .72);
  }

  void _mainstem(Canvas c, Size s) {
    c.drawRect(
      Rect.fromLTWH(0, s.height * .64, s.width, s.height * .22),
      Paint()..color = water.withValues(alpha: .70),
    );
    final cell = RRect.fromRectAndRadius(
      Rect.fromLTWH(
        s.width * .48,
        s.height * .18,
        s.width * .28,
        s.height * .27,
      ),
      const Radius.circular(6),
    );
    c.drawRRect(cell, Paint()..color = green.withValues(alpha: .32));
    _arrow(
      c,
      Offset(s.width * .18, s.height * .12),
      Offset(s.width * .50, s.height * .30),
    );
    _arrow(
      c,
      Offset(s.width * .70, s.height * .45),
      Offset(s.width * .77, s.height * .66),
    );
    _label(c, s, 'intercepted drain', .02, .04);
    _label(c, s, 'off-channel cell', .49, .22);
    _label(c, s, 'safe return flow', .72, .46);
    _label(c, s, 'main river channel', .34, .76);
  }

  void _plants(Canvas c, Size s, double groundY) {
    for (var i = 0; i < 8; i++) {
      final x = s.width * (.27 + i * .065);
      c.drawLine(
        Offset(x, groundY + 8),
        Offset(x, groundY - 13),
        Paint()
          ..color = green
          ..strokeWidth = 2,
      );
      c.drawLine(
        Offset(x, groundY - 4),
        Offset(x - 5, groundY - 10),
        Paint()
          ..color = green
          ..strokeWidth = 1.5,
      );
    }
  }

  void _pipe(Canvas c, Offset start, Offset end) {
    c.drawLine(
      start,
      end,
      Paint()
        ..color = navy
        ..strokeWidth = 4,
    );
    c.drawCircle(end, 4, Paint()..color = navy);
  }

  void _arrow(Canvas c, Offset start, Offset end) {
    final paint = Paint()
      ..color = navy
      ..strokeWidth = 1.8
      ..style = PaintingStyle.stroke;
    c.drawLine(start, end, paint);
    final direction = (end - start).direction;
    for (final angle in [direction + 2.55, direction - 2.55]) {
      c.drawLine(end, end + Offset.fromDirection(angle, 7), paint);
    }
  }

  void _label(
    Canvas c,
    Size s,
    String text,
    double x,
    double y, {
    double width = .22,
  }) {
    final painter = TextPainter(
      text: TextSpan(
        text: text,
        style: const TextStyle(
          color: navy,
          fontSize: 10,
          fontWeight: FontWeight.w600,
        ),
      ),
      textDirection: TextDirection.ltr,
      maxLines: 2,
      ellipsis: '...',
    )..layout(maxWidth: s.width * width);
    painter.paint(c, Offset(s.width * x, s.height * y));
  }

  @override
  bool shouldRepaint(covariant _NbsDiagramPainter oldDelegate) =>
      oldDelegate.kind != kind;
}
