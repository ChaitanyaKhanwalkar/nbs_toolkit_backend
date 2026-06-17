import 'package:flutter/material.dart';

import '../models/recommendation_models.dart';
import '../theme/nbs_theme.dart';
import '../widgets/app_card.dart';

const _maxContentWidth = 1160.0;

class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key, required this.onStart});

  final VoidCallback onStart;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: NbsColors.deepNavy,
      body: Stack(
        children: [
          const Positioned.fill(
            child: DecoratedBox(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    NbsColors.deepNavy,
                    NbsColors.riverBlue,
                    NbsColors.deepNavy,
                  ],
                ),
              ),
              child: CustomPaint(
                painter: _RiverContourPainter(),
                child: SizedBox.expand(),
              ),
            ),
          ),
          SafeArea(
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 720),
                child: Padding(
                  padding: const EdgeInsets.all(28),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        width: 72,
                        height: 72,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [
                              NbsColors.riverBlue,
                              NbsColors.riverTeal,
                            ],
                          ),
                          border: Border.all(
                            color: Colors.white24,
                          ),
                          borderRadius: BorderRadius.circular(8),
                          boxShadow: [
                            BoxShadow(
                              color:
                                  NbsColors.riverTeal.withValues(alpha: 0.22),
                              blurRadius: 24,
                              offset: const Offset(0, 10),
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.water_drop_outlined,
                          color: NbsColors.textOnDark,
                          size: 38,
                        ),
                      ),
                      const SizedBox(height: 28),
                      Text(
                        'NbS Toolkit',
                        style:
                            Theme.of(context).textTheme.displaySmall?.copyWith(
                                  color: Colors.white,
                                  fontWeight: FontWeight.w800,
                                ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        'Guided by Nature, Powered by Science',
                        style:
                            Theme.of(context).textTheme.headlineSmall?.copyWith(
                                  color: const Color(0xFFE0F2FE),
                                  fontWeight: FontWeight.w600,
                                ),
                      ),
                      const SizedBox(height: 14),
                      Text(
                        'Narmada Basin Decision Support Prototype',
                        style:
                            Theme.of(context).textTheme.titleMedium?.copyWith(
                                  color: const Color(0xFFBFD7EA),
                                  fontWeight: FontWeight.w500,
                                ),
                      ),
                      const SizedBox(height: 36),
                      SizedBox(
                        width: 180,
                        child: ElevatedButton.icon(
                          onPressed: onStart,
                          icon: const Icon(Icons.arrow_forward),
                          label: const Text('Get Started'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: NbsColors.wetlandGreen,
                            foregroundColor: Colors.white,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class HomeDashboard extends StatelessWidget {
  const HomeDashboard({
    super.key,
    required this.onStartRecommendation,
    required this.onAbout,
  });

  final VoidCallback onStartRecommendation;
  final VoidCallback onAbout;

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'NbS Toolkit',
      actions: [
        TextButton.icon(
          onPressed: onAbout,
          icon: const Icon(Icons.science_outlined),
          label: const Text('Method'),
        ),
      ],
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const _RiverIntelligenceHero(),
          const SizedBox(height: 18),
          LayoutBuilder(
            builder: (context, constraints) {
              final isWide = constraints.maxWidth > 860;
              final cards = [
                _ActionCard(
                  title: 'Measured Water Quality',
                  description: 'Active - start a recommendation from lab values.',
                  icon: Icons.analytics_outlined,
                  color: NbsColors.researchBlue,
                  onTap: onStartRecommendation,
                  emphasized: true,
                ),
                const _ActionCard(
                  title: 'Select Narmada Site/Station',
                  description: 'Next build',
                  icon: Icons.place_outlined,
                  color: NbsColors.riverTeal,
                ),
                const _ActionCard(
                  title: 'Pollution Source Screening',
                  description: 'Next build',
                  icon: Icons.manage_search_outlined,
                  color: NbsColors.wetlandGreen,
                ),
                const _ActionCard(
                  title: 'Upload Water Data',
                  description: 'Next build',
                  icon: Icons.upload_file_outlined,
                  color: NbsColors.warningAmber,
                ),
              ];
              return GridView.count(
                crossAxisCount: isWide ? 4 : 1,
                crossAxisSpacing: 14,
                mainAxisSpacing: 14,
                childAspectRatio: isWide ? 1.45 : 4.1,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                children: cards,
              );
            },
          ),
          const SizedBox(height: 18),
          const _StatusPanel(),
        ],
      ),
    );
  }
}

class WaterQualityEntryScreen extends StatefulWidget {
  const WaterQualityEntryScreen({
    super.key,
    required this.onRun,
    required this.onBack,
    this.errorMessage,
  });

  final void Function(double bod, double tss, double nitrateN, double ph) onRun;
  final VoidCallback onBack;
  final String? errorMessage;

  @override
  State<WaterQualityEntryScreen> createState() => _WaterQualityEntryScreenState();
}

class _WaterQualityEntryScreenState extends State<WaterQualityEntryScreen> {
  final _formKey = GlobalKey<FormState>();
  final _bodController = TextEditingController();
  final _tssController = TextEditingController();
  final _nitrateController = TextEditingController();
  final _phController = TextEditingController();

  @override
  void dispose() {
    _bodController.dispose();
    _tssController.dispose();
    _nitrateController.dispose();
    _phController.dispose();
    super.dispose();
  }

  void _useDemoValues() {
    _bodController.text = '45';
    _tssController.text = '180';
    _nitrateController.text = '18';
    _phController.text = '7.4';
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    widget.onRun(
      double.parse(_bodController.text),
      double.parse(_tssController.text),
      double.parse(_nitrateController.text),
      double.parse(_phController.text),
    );
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'Water quality entry',
      leading: BackButton(onPressed: widget.onBack),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SectionTitle(
            title: 'Measured water-quality inputs',
            subtitle:
                'Enter field or lab values using the current Narmada demo standards vocabulary.',
          ),
          const SizedBox(height: 18),
          const _SetupStatusCard(),
          const SizedBox(height: 10),
          const _ReadinessRow(),
          const SizedBox(height: 12),
          const _ParameterHelperStrip(),
          const SizedBox(height: 14),
          if (widget.errorMessage != null) ...[
            _AlertBanner(
              icon: Icons.error_outline,
              color: Theme.of(context).colorScheme.error,
              title: 'Recommendation run failed',
              message: widget.errorMessage!,
            ),
            const SizedBox(height: 16),
          ],
          AppCard(
            padding: const EdgeInsets.all(14),
            borderColor: NbsColors.riverTeal.withValues(alpha: 0.22),
            artwork: const _BoxArtwork(motif: _ArtworkMotif.lab),
            child: Form(
              key: _formKey,
              child: Column(
                children: [
                  Row(
                    children: [
                      Container(
                        width: 38,
                        height: 38,
                        decoration: BoxDecoration(
                          color: NbsColors.riverTeal.withValues(alpha: 0.10),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Icon(
                          Icons.science_outlined,
                          color: NbsColors.riverTeal,
                          size: 21,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          'Water-quality lab panel',
                          style:
                              Theme.of(context).textTheme.titleMedium?.copyWith(
                                    color: NbsColors.deepNavy,
                                    fontWeight: FontWeight.w900,
                                  ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  LayoutBuilder(
                    builder: (context, constraints) {
                          final isWide = constraints.maxWidth > 780;
                          return GridView.count(
                            crossAxisCount: isWide ? 4 : 1,
                            crossAxisSpacing: 10,
                            mainAxisSpacing: 10,
                            childAspectRatio: isWide ? 2.35 : 4.35,
                            shrinkWrap: true,
                            physics: const NeverScrollableScrollPhysics(),
                        children: [
                          _NumberField(
                            controller: _bodController,
                            label: 'BOD',
                            suffix: 'mg/L',
                            helper: 'Organic load indicator',
                          ),
                          _NumberField(
                            controller: _tssController,
                            label: 'TSS',
                            suffix: 'mg/L',
                            helper: 'Suspended solids indicator',
                          ),
                          _NumberField(
                            controller: _nitrateController,
                            label: 'Nitrate-N',
                            suffix: 'mg/L',
                            helper: 'Nutrient load indicator',
                          ),
                          _NumberField(
                            controller: _phController,
                            label: 'pH',
                            suffix: 'pH units',
                            helper: 'Acidity/alkalinity indicator',
                          ),
                        ],
                      );
                    },
                  ),
                  const SizedBox(height: 14),
                  LayoutBuilder(
                    builder: (context, constraints) {
                      final isWide = constraints.maxWidth > 620;
                      final buttons = [
                        OutlinedButton.icon(
                          onPressed: _useDemoValues,
                          icon: const Icon(Icons.dataset_outlined),
                          label: const Text('Use Demo Narmada Values'),
                        ),
                        ElevatedButton.icon(
                          onPressed: _submit,
                          icon: const Icon(Icons.play_arrow),
                          label: const Text('Run Recommendation Engine'),
                        ),
                      ];
                      if (!isWide) {
                        return Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            buttons[0],
                            const SizedBox(height: 10),
                            buttons[1],
                          ],
                        );
                      }
                      return Row(
                        children: [
                          Expanded(child: buttons[0]),
                          const SizedBox(width: 12),
                          Expanded(child: buttons[1]),
                        ],
                      );
                    },
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class LoadingScreen extends StatelessWidget {
  const LoadingScreen({super.key});

  static const steps = [
    'Normalize input',
    'Check standards',
    'Classify need',
    'Filter candidates',
    'Build MCDA',
    'Run TOPSIS',
    'Score confidence',
    'Assemble',
  ];

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'Recommendation engine',
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 640),
          child: AppCard(
            artwork: const _BoxArtwork(motif: _ArtworkMotif.waves),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const SizedBox(
                      width: 32,
                      height: 32,
                      child: CircularProgressIndicator(strokeWidth: 3),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Text(
                        'Running staged scientific workflow',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.w800,
                            ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                const _WorkflowTimeline(steps: steps),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class ResultsScreen extends StatelessWidget {
  const ResultsScreen({
    super.key,
    required this.response,
    required this.onViewDetail,
    required this.onNewRun,
    required this.onHome,
    required this.onAbout,
  });

  final RecommendationResponse response;
  final ValueChanged<RecommendationItem> onViewDetail;
  final VoidCallback onNewRun;
  final VoidCallback onHome;
  final VoidCallback onAbout;

  @override
  Widget build(BuildContext context) {
    final bundle = response.recommendationAssemblyBundle;
    final recommendations = bundle?.recommendations ?? [];
    final topRecommendation =
        recommendations.isNotEmpty ? recommendations.first : null;

    return AppScaffold(
      title: 'Recommendation results',
      actions: [
        TextButton.icon(
          onPressed: onAbout,
          icon: const Icon(Icons.info_outline),
          label: const Text('Method'),
        ),
        TextButton.icon(
          onPressed: onHome,
          icon: const Icon(Icons.dashboard_outlined),
          label: const Text('Dashboard'),
        ),
      ],
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _ResultsHero(
            response: response,
            bundle: bundle,
            topRecommendation: topRecommendation,
          ),
          const SizedBox(height: 14),
          if (response.weightsStatus == 'temporary_not_expert_validated') ...[
            const _AlertBanner.compact(
              icon: Icons.warning_amber_outlined,
              color: NbsColors.warningAmber,
              title: 'Provisional Ranking',
              message:
                  'Criteria weights are temporary and not expert validated.',
            ),
            const SizedBox(height: 14),
          ],
          _ResultsMetricStrip(
            response: response,
            bundle: bundle,
          ),
          if (response.exceedances.isNotEmpty) ...[
            const SizedBox(height: 14),
            _DetailSection(
              title: 'Detected standard exceedances',
              child: _ReadableBulletList(
                values: [
                  for (final exceedance in response.exceedances)
                    exceedance.summary,
                ],
              ),
            ),
          ],
          if (response.globalGaps.isNotEmpty) ...[
            const SizedBox(height: 14),
            _DetailSection(
              title: 'Data gaps and limitations',
              child: _ReadableBulletList(values: response.globalGaps),
            ),
          ],
          const SizedBox(height: 16),
          for (final item in recommendations)
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: RecommendationCard(
                item: item,
                onViewDetail: () => onViewDetail(item),
              ),
            ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: onNewRun,
            icon: const Icon(Icons.restart_alt),
            label: const Text('Run Another Recommendation'),
          ),
        ],
      ),
    );
  }
}

class RecommendationCard extends StatelessWidget {
  const RecommendationCard({
    super.key,
    required this.item,
    required this.onViewDetail,
  });

  final RecommendationItem item;
  final VoidCallback onViewDetail;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      padding: const EdgeInsets.all(14),
      borderColor: NbsColors.researchBlue.withValues(alpha: 0.13),
      artwork: const _BoxArtwork(motif: _ArtworkMotif.ranking),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final isWide = constraints.maxWidth > 720;
          final scoreChips = Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _MetricChip(
                label: 'Match',
                value: item.matchPercent,
                color: NbsColors.researchBlue,
              ),
              _MetricChip(
                label: 'Confidence',
                value: item.confidencePercent,
                color: NbsColors.wetlandGreen,
              ),
              _MetricChip(
                label: _displayConfidenceLabel(item.confidenceLabel),
                value: 'Confidence label',
                color: NbsColors.riverTeal,
                inverted: true,
              ),
            ],
          );
          final detailButton = TextButton.icon(
            onPressed: onViewDetail,
            icon: const Icon(Icons.open_in_new, size: 18),
            label: const Text('View Scientific Detail'),
          );

          return Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _RankBlock(rank: item.rank),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.nbsName,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: NbsColors.deepNavy,
                            fontWeight: FontWeight.w800,
                          ),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      'Ranked by TOPSIS closeness - Confidence calculated separately',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: NbsColors.mutedGrey,
                          ),
                    ),
                    const SizedBox(height: 10),
                    if (isWide)
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                scoreChips,
                                const SizedBox(height: 10),
                                _ScoreBar(
                                  label: 'Match score',
                                  value: item.matchScore,
                                  color: NbsColors.researchBlue,
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 10),
                          detailButton,
                        ],
                      )
                    else ...[
                      scoreChips,
                      const SizedBox(height: 10),
                      _ScoreBar(
                        label: 'Match score',
                        value: item.matchScore,
                        color: NbsColors.researchBlue,
                      ),
                      const SizedBox(height: 8),
                      Align(
                        alignment: Alignment.centerLeft,
                        child: detailButton,
                      ),
                    ],
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class DetailScreen extends StatelessWidget {
  const DetailScreen({
    super.key,
    required this.item,
    required this.onBack,
    this.citations = const [],
  });

  final RecommendationItem item;
  final VoidCallback onBack;
  final List<Citation> citations;

  @override
  Widget build(BuildContext context) {
    final warnings = _uniqueStrings([
      ...item.warnings,
      ...item.evidenceSummary.warnings,
      ...item.evidenceSummary.cautionFlags,
    ]);
    final citationsById = {for (final citation in citations) citation.id: citation};
    final technicalNotes = _uniqueStrings([
      ...item.notes,
      ...item.evidenceSummary.notes,
    ]);

    return AppScaffold(
      title: 'Scientific detail',
      leading: BackButton(onPressed: onBack),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _ReportHeader(
            item: item,
          ),
          const SizedBox(height: 16),
          _DetailSection(
            title: 'A. Decision summary',
            child: Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                StatusPill(label: 'Rank', value: '#${item.rank ?? '-'}'),
                StatusPill(label: 'NbS ID', value: '${item.nbsId ?? '-'}'),
                StatusPill(
                  label: 'Weights',
                  value: _displayStatus(item.weightsStatus),
                  color: item.expertValidated
                      ? NbsColors.wetlandGreen
                      : NbsColors.warningAmber,
                ),
                StatusPill(
                  label: 'Expert validation',
                  value: item.expertValidated
                      ? 'Expert validated'
                      : 'Expert validation pending',
                  color: item.expertValidated
                      ? NbsColors.wetlandGreen
                      : NbsColors.warningAmber,
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          _DetailSection(
            title: 'B. Score interpretation',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: [
                    StatusPill(label: 'Match score', value: item.matchPercent),
                    StatusPill(
                      label: 'TOPSIS closeness',
                      value: item.topsisPercent,
                    ),
                    StatusPill(
                      label: 'Confidence score',
                      value: item.confidencePercent,
                      color: NbsColors.wetlandGreen,
                    ),
                    StatusPill(
                      label: 'Confidence label',
                      value: _displayConfidenceLabel(item.confidenceLabel),
                      color: NbsColors.wetlandGreen,
                    ),
                    StatusPill(
                      label: 'Ranking method',
                      value: _displayMethod(item.rankingMethod),
                    ),
                    StatusPill(
                      label: 'Confidence method',
                      value: _displayMethod(item.confidenceMethod),
                    ),
                  ],
                ),
                const SizedBox(height: 14),
                _ScoreBar(
                  label: 'TOPSIS closeness',
                  value: item.topsisCloseness,
                  color: NbsColors.researchBlue,
                ),
                const SizedBox(height: 10),
                _ScoreBar(
                  label: 'Confidence',
                  value: item.confidenceScore,
                  color: NbsColors.wetlandGreen,
                ),
                const SizedBox(height: 14),
                const _ReadableBulletList(
                  values: [
                    'Match score is TOPSIS closeness.',
                    'Confidence is calculated separately and does not change rank.',
                    'Plant matches do not affect rank.',
                    'Site suitability is provisional metadata completeness only.',
                    'Temporary weights are not expert validated.',
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          _DetailSection(
            title: 'C. Why recommended',
            child: _ReadableBulletList(
              values: _uniqueStrings(item.whyRecommended),
              emptyText: 'No reasons were returned for this item.',
            ),
          ),
          const SizedBox(height: 14),
          _DetailSection(
            title: 'D. Per-criterion breakdown',
            child: item.criteriaBreakdown.isEmpty
                ? const Text(
                    'No comparable numeric criteria were available for this run.',
                  )
                : Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      for (final criterion in item.criteriaBreakdown) ...[
                        _ScoreBar(
                          label:
                              '${criterion.label} (weight ${(criterion.weight * 100).toStringAsFixed(0)}%)',
                          value: criterion.normalizedValue,
                          color: NbsColors.researchBlue,
                        ),
                        const SizedBox(height: 10),
                      ],
                    ],
                  ),
          ),
          const SizedBox(height: 14),
          _DetailSection(
            title: 'E. Evidence and sources',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _TextBlockList(
                  title: 'Explanation',
                  values: _uniqueStrings(item.explanation),
                  emptyText: 'No explanation text returned.',
                ),
                const SizedBox(height: 12),
                Text(
                  'Evidence source IDs',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                ),
                const SizedBox(height: 8),
                _SourceIdWrap(sourceIds: item.evidenceSummary.sourceIds),
                const SizedBox(height: 12),
                Text(
                  'Citations',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                ),
                const SizedBox(height: 8),
                _CitationList(
                  sourceIds: item.evidenceSummary.sourceIds,
                  citationsById: citationsById,
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          _DetailSection(
            title: 'F. Scientific cautions',
            child: _ReadableBulletList(
              values: warnings,
              emptyText: 'No scientific cautions returned for this item.',
            ),
          ),
          const SizedBox(height: 14),
          _DetailSection(
            title: 'G. Data gaps',
            child: _ReadableBulletList(
              values: _uniqueStrings(item.dataGaps),
              emptyText: 'No data gaps were reported for this item.',
            ),
          ),
          const SizedBox(height: 14),
          _DetailSection(
            title: 'H. Plant support',
            child: item.plantMatches.isEmpty
                ? const Text(
                    'No explicit plant mapping is available yet for this NbS option.',
                  )
                : Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      for (final plant in item.plantMatches)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: Text(
                            '${plant['scientific_name'] ?? 'Unknown plant'} - '
                            '${plant['common_name'] ?? 'No common name'}',
                          ),
                        ),
                    ],
                  ),
          ),
          const SizedBox(height: 14),
          _DetailSection(
            title: 'I. Implementation guidance',
            child: Text(
              item.implementationSummary ??
                  'No implementation guidance is available yet for this NbS option.',
            ),
          ),
          const SizedBox(height: 14),
          _TechnicalNotesCard(notes: technicalNotes),
        ],
      ),
    );
  }
}

class MethodAboutScreen extends StatelessWidget {
  const MethodAboutScreen({super.key, required this.onBack});

  final VoidCallback onBack;

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'Method and scope',
      leading: BackButton(onPressed: onBack),
      child: const Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SectionTitle(
            title: 'Method and limitations',
            subtitle:
                'A concise reference for interpreting the staged recommendation output.',
          ),
          SizedBox(height: 16),
          _MethodCard(
            title: 'What the tool does',
            body:
                'The toolkit converts measured water-quality indicators into treatment needs, screens feasible Nature-based Solution options, and assembles evidence-linked recommendations.',
          ),
          SizedBox(height: 12),
          _MethodCard(
            title: 'Ranking method',
            body:
                'TOPSIS compares candidate options against ideal best and worst cases. The displayed match score is the TOPSIS closeness value.',
          ),
          SizedBox(height: 12),
          _MethodCard(
            title: 'Confidence',
            body:
                'Confidence is calculated separately from ranking. It reflects data quality, evidence completeness, criteria coverage, provisional weights, and caution flags.',
          ),
          SizedBox(height: 12),
          _MethodCard(
            title: 'Current limitations',
            body:
                'Criteria weights are temporary and not expert validated. Health-risk classification, AHP expert weighting, and broader site validation remain pending.',
          ),
          SizedBox(height: 12),
          _MethodCard(
            title: 'Decision-support boundary',
            body:
                'This tool supports decision-making. It does not replace expert engineering design, site survey, or regulatory approval.',
            highlighted: true,
          ),
        ],
      ),
    );
  }
}

class AppScaffold extends StatelessWidget {
  const AppScaffold({
    super.key,
    required this.title,
    required this.child,
    this.leading,
    this.actions,
  });

  final String title;
  final Widget child;
  final Widget? leading;
  final List<Widget>? actions;

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    final horizontalPadding = width < 640 ? 14.0 : 24.0;
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        leading: leading,
        actions: actions,
      ),
      body: SafeArea(
        child: Stack(
          children: [
            const Positioned.fill(child: _RiverContourBackground()),
            SingleChildScrollView(
              padding: EdgeInsets.symmetric(
                horizontal: horizontalPadding,
                vertical: 18,
              ),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: _maxContentWidth),
                  child: child,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _RiverContourBackground extends StatelessWidget {
  const _RiverContourBackground();

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.white,
            NbsColors.softBackground,
            Color(0xFFEFF7FB),
          ],
        ),
      ),
      child: CustomPaint(
        painter: _RiverContourPainter(),
        child: const SizedBox.expand(),
      ),
    );
  }
}

class _RiverContourPainter extends CustomPainter {
  const _RiverContourPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final riverPaint = Paint()
      ..color = NbsColors.riverTeal.withValues(alpha: 0.075)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.6;
    final contourPaint = Paint()
      ..color = NbsColors.riverBlue.withValues(alpha: 0.045)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.0;
    final glowPaint = Paint()
      ..color = NbsColors.researchBlue.withValues(alpha: 0.055)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 34);

    for (var index = 0; index < 5; index++) {
      final offset = index * 64.0;
      final path = Path()
        ..moveTo(-80, size.height * 0.18 + offset)
        ..cubicTo(
          size.width * 0.20,
          size.height * 0.04 + offset,
          size.width * 0.45,
          size.height * 0.34 + offset,
          size.width + 80,
          size.height * 0.18 + offset,
        );
      canvas.drawPath(path, riverPaint);
    }

    canvas.drawCircle(Offset(size.width * 0.82, size.height * 0.08), 120, glowPaint);

    for (var index = 0; index < 7; index++) {
      final inset = 40.0 + (index * 42.0);
      final rect = Rect.fromLTWH(
        size.width - inset - 220,
        50 + index * 34,
        260 + index * 22,
        110 + index * 12,
      );
      canvas.drawOval(rect, contourPaint);
    }

    final ridgePaint = Paint()
      ..color = NbsColors.wetlandGreen.withValues(alpha: 0.055)
      ..style = PaintingStyle.fill;
    final ridge = Path()
      ..moveTo(0, size.height)
      ..lineTo(size.width * 0.10, size.height - 34)
      ..lineTo(size.width * 0.23, size.height - 18)
      ..lineTo(size.width * 0.34, size.height - 48)
      ..lineTo(size.width * 0.49, size.height - 22)
      ..lineTo(size.width * 0.61, size.height - 58)
      ..lineTo(size.width * 0.78, size.height - 28)
      ..lineTo(size.width, size.height - 48)
      ..lineTo(size.width, size.height)
      ..close();
    canvas.drawPath(ridge, ridgePaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

enum _ArtworkMotif { waves, lab, ranking, report, forest }

class _BoxArtwork extends StatelessWidget {
  const _BoxArtwork({
    required this.motif,
  });

  final _ArtworkMotif motif;

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: CustomPaint(
        painter: _BoxArtworkPainter(motif: motif),
        child: const SizedBox.expand(),
      ),
    );
  }
}

class _BoxArtworkPainter extends CustomPainter {
  const _BoxArtworkPainter({
    required this.motif,
  });

  final _ArtworkMotif motif;

  @override
  void paint(Canvas canvas, Size size) {
    const base = NbsColors.riverBlue;
    const accent = NbsColors.researchBlue;
    final stroke = Paint()
      ..color = base.withValues(alpha: 0.055)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.3;
    final accentStroke = Paint()
      ..color = accent.withValues(alpha: 0.08)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.6;
    final fill = Paint()
      ..color = accent.withValues(alpha: 0.045)
      ..style = PaintingStyle.fill;

    switch (motif) {
      case _ArtworkMotif.waves:
        for (var index = 0; index < 4; index++) {
          final y = size.height * 0.28 + index * 28;
          final path = Path()
            ..moveTo(size.width * 0.46, y)
            ..cubicTo(
              size.width * 0.62,
              y - 30,
              size.width * 0.76,
              y + 30,
              size.width + 32,
              y - 4,
            );
          canvas.drawPath(path, index.isEven ? accentStroke : stroke);
        }
        canvas.drawCircle(
          Offset(size.width * 0.82, size.height * 0.18),
          58,
          fill,
        );
      case _ArtworkMotif.lab:
        final right = size.width - 34;
        final top = size.height * 0.20;
        canvas.drawRRect(
          RRect.fromRectAndRadius(
            Rect.fromLTWH(right - 86, top, 54, 98),
            const Radius.circular(7),
          ),
          stroke,
        );
        canvas.drawLine(
          Offset(right - 74, top + 30),
          Offset(right - 44, top + 30),
          accentStroke,
        );
        for (var index = 0; index < 5; index++) {
          final x = right - 132 + index * 18;
          canvas.drawLine(
            Offset(x, size.height - 30),
            Offset(x + 22, size.height - 90),
            stroke,
          );
        }
        canvas.drawCircle(Offset(right - 110, top + 18), 18, fill);
      case _ArtworkMotif.ranking:
        final start = Offset(size.width * 0.52, size.height * 0.70);
        final points = [
          start,
          Offset(size.width * 0.64, size.height * 0.52),
          Offset(size.width * 0.76, size.height * 0.58),
          Offset(size.width * 0.90, size.height * 0.34),
        ];
        final path = Path()..moveTo(points.first.dx, points.first.dy);
        for (final point in points.skip(1)) {
          path.lineTo(point.dx, point.dy);
        }
        canvas.drawPath(path, accentStroke);
        for (final point in points) {
          canvas.drawCircle(point, 5.5, fill);
          canvas.drawCircle(point, 5.5, accentStroke);
        }
        for (var index = 0; index < 4; index++) {
          final h = 24.0 + index * 13.0;
          canvas.drawRRect(
            RRect.fromRectAndRadius(
              Rect.fromLTWH(size.width - 70 + index * 14, size.height - h, 7, h),
              const Radius.circular(3),
            ),
            fill,
          );
        }
      case _ArtworkMotif.report:
        for (var index = 0; index < 5; index++) {
          final y = 26.0 + index * 18.0;
          canvas.drawLine(
            Offset(size.width * 0.58, y),
            Offset(size.width - 28, y),
            stroke,
          );
        }
        canvas.drawCircle(
          Offset(size.width - 70, size.height - 42),
          40,
          accentStroke,
        );
        canvas.drawCircle(
          Offset(size.width - 70, size.height - 42),
          24,
          stroke,
        );
      case _ArtworkMotif.forest:
        final path = Path()
          ..moveTo(size.width * 0.58, size.height)
          ..lineTo(size.width * 0.65, size.height - 42)
          ..lineTo(size.width * 0.72, size.height - 16)
          ..lineTo(size.width * 0.80, size.height - 54)
          ..lineTo(size.width * 0.89, size.height - 20)
          ..lineTo(size.width, size.height - 44)
          ..lineTo(size.width, size.height)
          ..close();
        canvas.drawPath(path, fill);
    }
  }

  @override
  bool shouldRepaint(covariant _BoxArtworkPainter oldDelegate) {
    return oldDelegate.motif != motif;
  }
}

class _RiverIntelligenceHero extends StatelessWidget {
  const _RiverIntelligenceHero();

  @override
  Widget build(BuildContext context) {
    return AppCard(
      borderColor: NbsColors.researchBlue.withValues(alpha: 0.14),
      artwork: const _BoxArtwork(motif: _ArtworkMotif.waves),
      padding: const EdgeInsets.all(24),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final isWide = constraints.maxWidth > 760;
          final titleBlock = Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Narmada River Intelligence',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      color: NbsColors.deepNavy,
                      fontWeight: FontWeight.w900,
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                'Evidence-linked NbS recommendations from measured water quality.',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: NbsColors.mutedGrey,
                      height: 1.35,
                    ),
              ),
              const SizedBox(height: 16),
              const Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _HeroChip(label: 'Narmada demo', color: NbsColors.riverTeal),
                  _HeroChip(label: 'TOPSIS', color: NbsColors.researchBlue),
                  _HeroChip(
                    label: 'Provisional weights',
                    color: NbsColors.warningAmber,
                  ),
                  _HeroChip(
                    label: 'Local prototype',
                    color: NbsColors.wetlandGreen,
                  ),
                ],
              ),
            ],
          );
          final iconBlock = Container(
            width: isWide ? 132 : 72,
            height: isWide ? 132 : 72,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [Color(0xFFEAF3FF), Color(0xFFE8FBF8)],
              ),
              border: Border.all(
                color: NbsColors.researchBlue.withValues(alpha: 0.16),
              ),
              borderRadius: BorderRadius.circular(8),
              boxShadow: [
                BoxShadow(
                  color: NbsColors.deepNavy.withValues(alpha: 0.08),
                  blurRadius: 22,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: const Icon(
              Icons.water_outlined,
              color: NbsColors.riverBlue,
              size: 44,
            ),
          );
          if (!isWide) {
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                iconBlock,
                const SizedBox(height: 18),
                titleBlock,
              ],
            );
          }
          return Row(
            children: [
              Expanded(child: titleBlock),
              const SizedBox(width: 24),
              iconBlock,
            ],
          );
        },
      ),
    );
  }
}

class _HeroChip extends StatelessWidget {
  const _HeroChip({required this.label, required this.color});

  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 7),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.09),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withValues(alpha: 0.24)),
      ),
      child: Text(
        label,
        style: TextStyle(color: color, fontWeight: FontWeight.w800),
      ),
    );
  }
}

class _ParameterHelperStrip extends StatelessWidget {
  const _ParameterHelperStrip();

  @override
  Widget build(BuildContext context) {
    return const Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        _HeroChip(label: 'Organic load', color: NbsColors.researchBlue),
        _HeroChip(label: 'Solids', color: NbsColors.riverTeal),
        _HeroChip(label: 'Nutrients', color: NbsColors.wetlandGreen),
        _HeroChip(label: 'pH balance', color: NbsColors.warningAmber),
      ],
    );
  }
}

class _WorkflowTimeline extends StatelessWidget {
  const _WorkflowTimeline({required this.steps});

  final List<String> steps;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        for (var index = 0; index < steps.length; index++)
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Column(
                children: [
                  Container(
                    width: 28,
                    height: 28,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: NbsColors.riverTeal.withValues(alpha: 0.12),
                      border: Border.all(
                        color: NbsColors.riverTeal.withValues(alpha: 0.35),
                      ),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      '${index + 1}',
                      style: const TextStyle(
                        color: NbsColors.deepNavy,
                        fontWeight: FontWeight.w900,
                        fontSize: 12,
                      ),
                    ),
                  ),
                  if (index != steps.length - 1)
                    Container(
                      width: 1,
                      height: 26,
                      color: NbsColors.cardBorder,
                    ),
                ],
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(
                    steps[index],
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: NbsColors.deepNavy,
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                ),
              ),
            ],
          ),
      ],
    );
  }
}

class _ResultsHero extends StatelessWidget {
  const _ResultsHero({
    required this.response,
    required this.bundle,
    required this.topRecommendation,
  });

  final RecommendationResponse response;
  final RecommendationAssemblyBundle? bundle;
  final RecommendationItem? topRecommendation;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      borderColor: NbsColors.researchBlue.withValues(alpha: 0.14),
      artwork: const _BoxArtwork(motif: _ArtworkMotif.ranking),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Ranking dashboard',
                      style:
                          Theme.of(context).textTheme.headlineSmall?.copyWith(
                                color: NbsColors.deepNavy,
                                fontWeight: FontWeight.w900,
                              ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      topRecommendation == null
                          ? 'No ranked recommendations were returned for this run.'
                          : 'Top recommendation: ${topRecommendation!.nbsName}',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: NbsColors.mutedGrey,
                            height: 1.35,
                          ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'The count may change because only options with evidence for detected treatment needs are ranked.',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: NbsColors.mutedGrey,
                          ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              _HeaderBadge(
                label: 'Method',
                value: _displayMethod(bundle?.rankingMethod ?? 'topsis'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              _DashboardMetricCard(
                label: 'Eligible ranked NbS options',
                value: '${response.recommendationCount}',
                icon: Icons.format_list_numbered,
                color: NbsColors.deepNavy,
              ),
              _DashboardMetricCard(
                label: 'Top match',
                value: topRecommendation?.matchPercent ?? 'N/A',
                icon: Icons.trending_up,
                color: NbsColors.researchBlue,
              ),
              _DashboardMetricCard(
                label: 'Confidence',
                value: topRecommendation?.confidencePercent ?? 'N/A',
                icon: Icons.verified_outlined,
                color: NbsColors.wetlandGreen,
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _ResultsMetricStrip extends StatelessWidget {
  const _ResultsMetricStrip({
    required this.response,
    required this.bundle,
  });

  final RecommendationResponse response;
  final RecommendationAssemblyBundle? bundle;

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 10,
      runSpacing: 10,
      children: [
        StatusPill(
          label: 'Workflow',
          value: response.stepCompleted ?? 'Unknown',
          color: NbsColors.riverTeal,
        ),
        StatusPill(
          label: 'Weights',
          value: _displayStatus(response.weightsStatus),
          color: response.expertValidated
              ? NbsColors.wetlandGreen
              : NbsColors.warningAmber,
        ),
        StatusPill(
          label: 'Expert validation',
          value: response.expertValidated
              ? 'Expert validated'
              : 'Expert validation pending',
          color: response.expertValidated
              ? NbsColors.wetlandGreen
              : NbsColors.warningAmber,
        ),
        StatusPill(
          label: 'Confidence method',
          value: _displayMethod(bundle?.confidenceMethod),
          color: NbsColors.wetlandGreen,
        ),
      ],
    );
  }
}

class _DashboardMetricCard extends StatelessWidget {
  const _DashboardMetricCard({
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
  });

  final String label;
  final String value;
  final IconData icon;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 210,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.07),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withValues(alpha: 0.18)),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 22),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: NbsColors.mutedGrey,
                        fontWeight: FontWeight.w700,
                      ),
                ),
                Text(
                  value,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: NbsColors.deepNavy,
                        fontWeight: FontWeight.w900,
                      ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ScoreBar extends StatelessWidget {
  const _ScoreBar({
    required this.label,
    required this.value,
    required this.color,
  });

  final String label;
  final double? value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final progress = value == null ? 0.0 : value!.clamp(0.0, 1.0).toDouble();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                label,
                style: Theme.of(context).textTheme.labelMedium?.copyWith(
                      color: NbsColors.mutedGrey,
                      fontWeight: FontWeight.w700,
                    ),
              ),
            ),
            Text(
              value == null
                  ? 'N/A'
                  : '${(progress * 100).toStringAsFixed(1)}%',
              style: TextStyle(color: color, fontWeight: FontWeight.w900),
            ),
          ],
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(999),
          child: LinearProgressIndicator(
            value: progress,
            minHeight: 7,
            color: color,
            backgroundColor: color.withValues(alpha: 0.12),
          ),
        ),
      ],
    );
  }
}

class _ReportHeader extends StatelessWidget {
  const _ReportHeader({required this.item});

  final RecommendationItem item;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      borderColor: NbsColors.researchBlue.withValues(alpha: 0.14),
      artwork: const _BoxArtwork(motif: _ArtworkMotif.report),
      padding: const EdgeInsets.all(20),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _RankBlock(rank: item.rank),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.nbsName,
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        color: NbsColors.deepNavy,
                        fontWeight: FontWeight.w900,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Scientific report card - ${_displayStatus(item.weightsStatus)}',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: NbsColors.mutedGrey,
                      ),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _HeroChip(
                      label: _displayMethod(item.rankingMethod),
                      color: NbsColors.researchBlue,
                    ),
                    _HeroChip(
                      label: _displayMethod(item.confidenceMethod),
                      color: NbsColors.wetlandGreen,
                    ),
                    _HeroChip(
                      label: item.expertValidated
                          ? 'Expert validated'
                          : 'Expert validation pending',
                      color: item.expertValidated
                          ? NbsColors.wetlandGreen
                          : NbsColors.warningAmber,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _StatusPanel extends StatelessWidget {
  const _StatusPanel();

  @override
  Widget build(BuildContext context) {
    return const AppCard(
      padding: EdgeInsets.all(18),
      artwork: _BoxArtwork(motif: _ArtworkMotif.forest),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SectionTitle(
            title: 'Scientific system status',
            subtitle:
                'Current readiness for local prototype decision-support use.',
          ),
          SizedBox(height: 16),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              StatusPill(
                label: 'Backend',
                value: 'Connected',
                color: NbsColors.wetlandGreen,
              ),
              StatusPill(label: 'Dataset', value: 'Narmada demo'),
              StatusPill(label: 'Method', value: 'TOPSIS'),
              StatusPill(
                label: 'Weights',
                value: 'Provisional',
                color: NbsColors.warningAmber,
              ),
              StatusPill(
                label: 'Expert validation',
                value: 'Pending',
                color: NbsColors.warningAmber,
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _SetupStatusCard extends StatelessWidget {
  const _SetupStatusCard();

  @override
  Widget build(BuildContext context) {
    return const AppCard(
      padding: EdgeInsets.all(16),
      artwork: _BoxArtwork(motif: _ArtworkMotif.lab),
      child: Wrap(
        spacing: 10,
        runSpacing: 10,
        children: [
          StatusPill(label: 'Use case', value: 'Inland discharge'),
          StatusPill(label: 'Basin', value: 'Narmada demo'),
          StatusPill(label: 'Input mode', value: 'Manual measured values'),
          StatusPill(label: 'Location context', value: 'Not selected'),
          StatusPill(label: 'Pollution source', value: 'Not selected'),
        ],
      ),
    );
  }
}

class _ReadinessRow extends StatelessWidget {
  const _ReadinessRow();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.white.withValues(alpha: 0.16)),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.check_circle_outline,
            size: 18,
            color: NbsColors.riverTeal,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              '4 parameters ready · Inland discharge · Manual measured values',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: NbsColors.textOnDark,
                    fontWeight: FontWeight.w800,
                  ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ActionCard extends StatelessWidget {
  const _ActionCard({
    required this.title,
    required this.description,
    required this.icon,
    required this.color,
    this.onTap,
    this.emphasized = false,
  });

  final String title;
  final String description;
  final IconData icon;
  final Color color;
  final VoidCallback? onTap;
  final bool emphasized;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: AppCard(
        padding: const EdgeInsets.all(16),
        artwork: _BoxArtwork(
          motif: emphasized ? _ArtworkMotif.waves : _ArtworkMotif.forest,
        ),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: color.withValues(alpha: emphasized ? 0.16 : 0.10),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, color: color),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                  ),
                  const SizedBox(height: 5),
                  Text(
                    description,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: NbsColors.mutedGrey,
                        ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _NumberField extends StatelessWidget {
  const _NumberField({
    required this.controller,
    required this.label,
    required this.suffix,
    required this.helper,
  });

  final TextEditingController controller;
  final String label;
  final String suffix;
  final String helper;

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      keyboardType: const TextInputType.numberWithOptions(decimal: true),
      decoration: InputDecoration(
        labelText: label,
        suffixText: suffix,
        helperText: helper,
        prefixIcon: Icon(
          label == 'pH'
              ? Icons.water_drop_outlined
              : Icons.speed_outlined,
          color: NbsColors.riverBlue,
        ),
      ),
      validator: (value) {
        final parsed = double.tryParse(value?.trim() ?? '');
        if (parsed == null) {
          return 'Enter a numeric value';
        }
        if (parsed.isNaN || parsed.isInfinite) {
          return 'Enter a finite value';
        }
        if (label == 'pH' && (parsed < 0 || parsed > 14)) {
          return 'pH should be between 0 and 14';
        }
        if (label != 'pH' && parsed < 0) {
          return 'Value cannot be negative';
        }
        return null;
      },
    );
  }
}

class _RankBlock extends StatelessWidget {
  const _RankBlock({required this.rank});

  final int? rank;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 54,
      height: 72,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [NbsColors.deepNavy, NbsColors.riverBlue],
        ),
        border: Border.all(color: NbsColors.riverBlue),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            '#${rank ?? '-'}',
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.w900,
              fontSize: 16,
            ),
          ),
          const Text(
            'rank',
            style: TextStyle(color: Color(0xFFBFD7EA), fontSize: 11),
          ),
        ],
      ),
    );
  }
}

class _HeaderBadge extends StatelessWidget {
  const _HeaderBadge({
    required this.label,
    required this.value,
  });

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
      decoration: BoxDecoration(
        color: NbsColors.researchBlue.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: NbsColors.researchBlue.withValues(alpha: 0.18),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  color: NbsColors.mutedGrey,
                  fontWeight: FontWeight.w700,
                ),
          ),
          Text(
            value,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: NbsColors.deepNavy,
                  fontWeight: FontWeight.w800,
                ),
          ),
        ],
      ),
    );
  }
}

class _MetricChip extends StatelessWidget {
  const _MetricChip({
    required this.label,
    required this.value,
    required this.color,
    this.inverted = false,
  });

  final String label;
  final String value;
  final Color color;
  final bool inverted;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: color.withValues(alpha: inverted ? 0.06 : 0.08),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withValues(alpha: 0.16)),
      ),
      child: Text(
        inverted ? label : '$label: $value',
        style: TextStyle(color: color, fontWeight: FontWeight.w800),
      ),
    );
  }
}

class _AlertBanner extends StatelessWidget {
  const _AlertBanner({
    required this.icon,
    required this.color,
    required this.title,
    required this.message,
  }) : compact = false;

  const _AlertBanner.compact({
    required this.icon,
    required this.color,
    required this.title,
    required this.message,
  }) : compact = true;

  final IconData icon;
  final Color color;
  final String title;
  final String message;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(compact ? 10 : 14),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: compact ? 0.95 : 0.98),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withValues(alpha: 0.38)),
        boxShadow: [
          BoxShadow(
            color: NbsColors.deepNavy.withValues(alpha: 0.10),
            blurRadius: 16,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: compact ? 20 : 24),
          const SizedBox(width: 10),
          Expanded(
            child: RichText(
              text: TextSpan(
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: NbsColors.deepNavy,
                    ),
                children: [
                  TextSpan(
                    text: '$title - ',
                    style: TextStyle(color: color, fontWeight: FontWeight.w800),
                  ),
                  TextSpan(text: message),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _DetailSection extends StatelessWidget {
  const _DetailSection({required this.title, required this.child});

  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      padding: const EdgeInsets.all(16),
      borderColor: NbsColors.researchBlue.withValues(alpha: 0.12),
      artwork: const _BoxArtwork(motif: _ArtworkMotif.report),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 4,
            height: 34,
            decoration: BoxDecoration(
              color: NbsColors.riverTeal,
              borderRadius: BorderRadius.circular(8),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w900,
                        color: NbsColors.deepNavy,
                      ),
                ),
                const SizedBox(height: 10),
                child,
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _TextBlockList extends StatelessWidget {
  const _TextBlockList({
    required this.title,
    required this.values,
    required this.emptyText,
  });

  final String title;
  final List<String> values;
  final String emptyText;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w800,
              ),
        ),
        const SizedBox(height: 8),
        _ReadableBulletList(values: values, emptyText: emptyText),
      ],
    );
  }
}

class _ReadableBulletList extends StatelessWidget {
  const _ReadableBulletList({
    required this.values,
    this.emptyText = 'No items returned.',
  });

  final List<String> values;
  final String emptyText;

  @override
  Widget build(BuildContext context) {
    if (values.isEmpty) {
      return Text(emptyText);
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (final value in values)
          Padding(
            padding: const EdgeInsets.only(bottom: 7),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('- '),
                Expanded(child: Text(_readableText(value))),
              ],
            ),
          ),
      ],
    );
  }
}

class _SourceIdWrap extends StatelessWidget {
  const _SourceIdWrap({required this.sourceIds});

  final List<int> sourceIds;

  @override
  Widget build(BuildContext context) {
    if (sourceIds.isEmpty) {
      return const Text('No evidence source IDs returned.');
    }
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        for (final sourceId in sourceIds)
          Chip(
            label: Text('Source $sourceId'),
            visualDensity: VisualDensity.compact,
            labelStyle: const TextStyle(
              color: NbsColors.deepNavy,
              fontWeight: FontWeight.w800,
            ),
            backgroundColor: NbsColors.researchBlue.withValues(alpha: 0.08),
            side: BorderSide(
              color: NbsColors.researchBlue.withValues(alpha: 0.22),
            ),
          ),
      ],
    );
  }
}

class _CitationList extends StatelessWidget {
  const _CitationList({
    required this.sourceIds,
    required this.citationsById,
  });

  final List<int> sourceIds;
  final Map<int, Citation> citationsById;

  @override
  Widget build(BuildContext context) {
    final resolved = [
      for (final sourceId in sourceIds)
        if (citationsById[sourceId] != null) citationsById[sourceId]!,
    ];
    if (resolved.isEmpty) {
      return const Text('No resolved citations returned for this item.');
    }
    final textTheme = Theme.of(context).textTheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (final citation in resolved)
          Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '[${citation.id}] ${citation.display}',
                  style: textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                if (citation.type != null || citation.license != null)
                  Text(
                    [
                      if (citation.type != null) citation.type!,
                      if (citation.license != null) 'License: ${citation.license!}',
                    ].join(' • '),
                    style: textTheme.bodySmall?.copyWith(
                      color: NbsColors.mutedGrey,
                    ),
                  ),
                if (citation.url != null)
                  Text(
                    citation.url!,
                    style: textTheme.bodySmall?.copyWith(
                      color: NbsColors.researchBlue,
                    ),
                  ),
              ],
            ),
          ),
      ],
    );
  }
}

class _TechnicalNotesCard extends StatelessWidget {
  const _TechnicalNotesCard({required this.notes});

  final List<String> notes;

  @override
  Widget build(BuildContext context) {
    if (notes.isEmpty) {
      return const SizedBox.shrink();
    }
    return AppCard(
      padding: EdgeInsets.zero,
      child: ExpansionTile(
        tilePadding: const EdgeInsets.symmetric(horizontal: 16),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        title: const Text(
          'Technical notes',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
        children: [_ReadableBulletList(values: notes.map(_readableText).toList())],
      ),
    );
  }
}

class _MethodCard extends StatelessWidget {
  const _MethodCard({
    required this.title,
    required this.body,
    this.highlighted = false,
  });

  final String title;
  final String body;
  final bool highlighted;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      padding: const EdgeInsets.all(16),
      borderColor: highlighted
          ? NbsColors.warningAmber.withValues(alpha: 0.22)
          : NbsColors.riverTeal.withValues(alpha: 0.14),
      artwork: _BoxArtwork(
        motif: highlighted ? _ArtworkMotif.report : _ArtworkMotif.forest,
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 34,
            height: 34,
            decoration: BoxDecoration(
              color: (highlighted ? NbsColors.warningAmber : NbsColors.riverTeal)
                  .withValues(alpha: 0.10),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              highlighted
                  ? Icons.warning_amber_outlined
                  : Icons.check_circle_outline,
              size: 20,
              color: highlighted ? NbsColors.warningAmber : NbsColors.riverTeal,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                ),
                const SizedBox(height: 6),
                Text(body),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

String _displayStatus(String? value) {
  return switch (value) {
    'temporary_not_expert_validated' => 'Temporary weights',
    'expert_validated' => 'Expert validated',
    'weights_missing' => 'Weights missing',
    'invalid_weights' => 'Invalid weights',
    null || '' => 'Unknown',
    _ => _titleFromSnake(value),
  };
}

String _displayMethod(String? value) {
  return switch (value) {
    'topsis' => 'TOPSIS',
    'rule_based_v1' => 'Rule-based confidence',
    null || '' => 'Unknown',
    _ => _titleFromSnake(value),
  };
}

String _displayConfidenceLabel(String? value) {
  return switch (value) {
    'high' => 'High confidence',
    'medium' => 'Medium confidence',
    'low' => 'Low confidence',
    null || '' => 'Unlabelled confidence',
    _ => _titleFromSnake(value),
  };
}

String _titleFromSnake(String value) {
  return value
      .split('_')
      .where((part) => part.isNotEmpty)
      .map((part) => '${part[0].toUpperCase()}${part.substring(1)}')
      .join(' ');
}

String _readableText(String value) {
  return value
      .replaceAll('temporary_not_expert_validated', 'temporary weights')
      .replaceAll('topsis_closeness', 'TOPSIS closeness')
      .replaceAll('match_score', 'match score')
      .replaceAll('confidence_score', 'confidence score')
      .replaceAll('rank_confidence_plants_v1', 'rank, confidence, and plant assembly')
      .replaceAll('rule_based_v1', 'rule-based confidence')
      .replaceAll('_', ' ');
}

List<String> _uniqueStrings(Iterable<String> values) {
  final result = <String>[];
  for (final value in values) {
    final trimmed = value.trim();
    if (trimmed.isNotEmpty && !result.contains(trimmed)) {
      result.add(trimmed);
    }
  }
  return result;
}
