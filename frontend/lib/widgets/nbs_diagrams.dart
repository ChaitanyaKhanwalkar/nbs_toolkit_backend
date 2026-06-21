/// Displays original SVG explainers for treatment and source-control options.
library;

import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

enum NbsDiagramKind {
  verticalFlowWetland,
  horizontalSubsurfaceWetland,
  pondSeries,
  dewats,
  bufferStrip,
  mainstemOffChannel,
  vermifilter,
  bioswale,
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
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w900,
                ),
          ),
          const SizedBox(height: 10),
          AspectRatio(
            aspectRatio: 2.1,
            child: SvgPicture.asset(
              copy.asset,
              key: ValueKey('nbs-diagram-${kind.name}'),
              fit: BoxFit.contain,
              semanticsLabel: '${copy.title} process diagram',
            ),
          ),
          const SizedBox(height: 9),
          Text(
            'What it shows',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w900,
                ),
          ),
          const SizedBox(height: 4),
          Text(
            copy.explanation,
            style:
                Theme.of(context).textTheme.bodyMedium?.copyWith(height: 1.4),
          ),
          const SizedBox(height: 6),
          _DiagramDisclosure(title: 'When to use', values: [copy.fit]),
          _DiagramDisclosure(title: 'Watch out for', values: copy.watchFor),
          _DiagramDisclosure(title: 'Design notes', values: copy.howItWorks),
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
                    child:
                        Icon(Icons.circle, size: 5, color: Color(0xFF4D8B63)),
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
  if (value.contains('vermifilter')) return NbsDiagramKind.vermifilter;
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
  if (value.contains('vermifilter')) return NbsDiagramKind.vermifilter;
  if (value.contains('bioswale')) return NbsDiagramKind.bioswale;
  if (value.contains('filter strip') ||
      value.contains('buffer') ||
      value.contains('riparian')) {
    return NbsDiagramKind.bufferStrip;
  }
  return null;
}

typedef _DiagramCopy = ({
  String title,
  String asset,
  String fit,
  String explanation,
  List<String> howItWorks,
  List<String> watchFor,
});

const _copy = <NbsDiagramKind, _DiagramCopy>{
  NbsDiagramKind.verticalFlowWetland: (
    title: 'Vertical Flow Wetland',
    asset: 'assets/diagrams/vf_wetland.svg',
    fit: 'Secondary treatment or polishing after primary solids removal.',
    explanation:
        'Pre-settled water is dosed across a planted media bed and moves downward to an underdrain.',
    howItWorks: [
      'Distribution pipes spread pretreated flow across the bed.',
      'Media, biofilm, and roots support filtration and treatment.',
      'An underdrain collects treated water for polishing or discharge review.',
    ],
    watchFor: [
      'Provide solids removal before the bed.',
      'Check dosing, resting cycles, media grading, and clogging risk.',
    ],
  ),
  NbsDiagramKind.horizontalSubsurfaceWetland: (
    title: 'Horizontal Subsurface Flow Wetland',
    asset: 'assets/diagrams/hssf_wetland.svg',
    fit: 'Subsurface polishing after primary treatment.',
    explanation:
        'Pretreated water moves below the surface through planted gravel toward a controlled outlet.',
    howItWorks: [
      'An inlet zone distributes flow across the bed width.',
      'Water travels through planted porous media below the surface.',
      'A controlled outlet maintains the intended water level.',
    ],
    watchFor: [
      'Use after effective primary treatment.',
      'Check short-circuiting, media clogging, and outlet control.',
    ],
  ),
  NbsDiagramKind.pondSeries: (
    title: 'Waste Stabilization Pond Series',
    asset: 'assets/diagrams/wsp_series.svg',
    fit: 'Land-based staged treatment for suitable small and medium flows.',
    explanation:
        'Wastewater passes through ponds with distinct solids, biological-treatment, and polishing roles.',
    howItWorks: [
      'Preliminary treatment protects the pond system.',
      'Anaerobic and facultative stages reduce organic load.',
      'Maturation ponds provide final polishing where design evidence supports it.',
    ],
    watchFor: [
      'Confirm land, lining, detention time, and safe setbacks.',
      'Plan for odour, sludge, mosquito, and overflow management.',
    ],
  ),
  NbsDiagramKind.dewats: (
    title: 'DEWATS Modular Flow',
    asset: 'assets/diagrams/dewats_flow.svg',
    fit: 'Decentralized sewage treatment or off-channel polishing.',
    explanation:
        'A modular train combines solids removal, baffled treatment, planted filtration, and polishing.',
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
    asset: 'assets/diagrams/buffer_strip.svg',
    fit:
        'Field and edge-of-field source control before runoff reaches a stream.',
    explanation:
        'Dense vegetation slows shallow runoff and supports sediment and nutrient source control.',
    howItWorks: [
      'Runoff spreads across vegetation instead of concentrating.',
      'Lower velocity encourages sediment deposition and infiltration.',
      'Vegetation stabilizes soil and supports nutrient uptake.',
    ],
    watchFor: [
      'Do not use this as treatment for raw sewage.',
      'Maintain flow spreading and avoid invasive plants.',
    ],
  ),
  NbsDiagramKind.mainstemOffChannel: (
    title: 'Drain Interception and Off-channel Treatment',
    asset: 'assets/diagrams/off_channel_safety.svg',
    fit: 'Mainstem safety layout for intercepted drains and safe return flow.',
    explanation:
        'A polluted drain is intercepted before the river and routed to a land-based treatment train.',
    howItWorks: [
      'Intercept the drain at a safe, accessible point.',
      'Route flow to pretreatment and suitable off-channel units.',
      'Monitor treated return flow before discharge.',
    ],
    watchFor: [
      'Do not obstruct river conveyance or build cells in the main channel.',
      'Survey levels, flood risk, land ownership, and bypass capacity.',
    ],
  ),
  NbsDiagramKind.vermifilter: (
    title: 'Vermifilter',
    asset: 'assets/diagrams/vermifilter.svg',
    fit: 'Biological treatment after screening and solids management.',
    explanation:
        'Pretreated wastewater passes through an aerated organic-media bed before collection.',
    howItWorks: [
      'Screened flow is distributed without flooding the media.',
      'Media organisms and biofilm support treatment.',
      'Drainage collects effluent for further polishing.',
    ],
    watchFor: [
      'Protect the bed from toxic or strongly acidic industrial wastewater.',
      'Confirm loading, ventilation, temperature, and solids controls.',
    ],
  ),
  NbsDiagramKind.bioswale: (
    title: 'Bioswale',
    asset: 'assets/diagrams/bioswale.svg',
    fit: 'Conveyance and source control for suitable stormwater runoff.',
    explanation:
        'A shallow vegetated channel slows and filters runoff before controlled discharge or infiltration.',
    howItWorks: [
      'Runoff enters through protected, distributed inlets.',
      'Vegetation and media slow flow and trap sediment.',
      'An overflow route protects the system during larger events.',
    ],
    watchFor: [
      'Do not route untreated sewage into a bioswale.',
      'Verify soils, groundwater separation, and overflow capacity.',
    ],
  ),
};
