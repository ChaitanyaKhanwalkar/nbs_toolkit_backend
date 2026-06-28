import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/services.dart';

import '../models/recommendation_models.dart';
import '../services/recommendation_api.dart';
import '../services/recommendation_report.dart';
import '../services/report_platform.dart';
import '../theme/nbs_theme.dart';
import '../widgets/app_card.dart';
import '../widgets/location_context_diagram.dart';
import '../widgets/nbs_diagrams.dart';

const _maxContentWidth = 1160.0;
const _csvTemplate =
    'parameter,value,unit\nBOD,30,mg/L\nCOD,100,mg/L\nTSS,80,mg/L\npH,7.2,';
const _targetUseCaseLabels = {
  'discharge_inland': 'Discharge to inland surface water',
  'irrigation': 'Irrigation reuse',
  'drinking': 'Drinking / strict-use screening',
};

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
                            colors: [NbsColors.riverBlue, NbsColors.riverTeal],
                          ),
                          border: Border.all(color: Colors.white24),
                          borderRadius: BorderRadius.circular(8),
                          boxShadow: [
                            BoxShadow(
                              color: NbsColors.riverTeal.withValues(
                                alpha: 0.22,
                              ),
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
    required this.onSelectSite,
    required this.onPollutionScreening,
    required this.onUploadWater,
    required this.onCatalogue,
  });

  final VoidCallback onStartRecommendation;
  final VoidCallback onAbout;
  final VoidCallback onSelectSite;
  final VoidCallback onPollutionScreening;
  final VoidCallback onUploadWater;
  final VoidCallback onCatalogue;

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'NbS Toolkit',
      actions: [
        TextButton.icon(
          onPressed: onCatalogue,
          icon: const Icon(Icons.menu_book_outlined),
          label: const Text('Catalogue'),
        ),
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
                  title: 'Start with measured values',
                  description: 'Enter lab or field water-quality values.',
                  icon: Icons.analytics_outlined,
                  color: NbsColors.researchBlue,
                  onTap: onStartRecommendation,
                  emphasized: true,
                ),
                _ActionCard(
                  title: 'Start from a Narmada station',
                  description: 'Use stored station and site context.',
                  icon: Icons.place_outlined,
                  color: NbsColors.riverTeal,
                  onTap: onSelectSite,
                ),
                _ActionCard(
                  title: 'Start from pollution source',
                  description:
                      'Screen domestic, agricultural, or industrial source contexts.',
                  icon: Icons.manage_search_outlined,
                  color: NbsColors.wetlandGreen,
                  onTap: onPollutionScreening,
                ),
                _ActionCard(
                  title: 'Upload a water-quality file',
                  description:
                      'Upload a CSV file with parameter and value columns.',
                  icon: Icons.upload_file_outlined,
                  color: NbsColors.warningAmber,
                  onTap: onUploadWater,
                ),
              ];
              if (!isWide) {
                return Column(
                  children: [
                    for (var index = 0; index < cards.length; index++) ...[
                      cards[index],
                      if (index != cards.length - 1) const SizedBox(height: 12),
                    ],
                  ],
                );
              }
              return GridView.count(
                crossAxisCount: 4,
                crossAxisSpacing: 14,
                mainAxisSpacing: 14,
                childAspectRatio: 1.45,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                children: cards,
              );
            },
          ),
          const SizedBox(height: 18),
          const _HowItWorksStrip(),
          const SizedBox(height: 18),
          const _StatusPanel(),
        ],
      ),
    );
  }
}

class _ManualParameter {
  const _ManualParameter(this.controller, this.parameter, this.unit);

  final TextEditingController controller;
  final String parameter;
  final String unit;
}

class AnalysisInput {
  AnalysisInput({
    required this.observations,
    required this.regionId,
    required this.station,
    required this.context,
    required this.useCase,
  });

  final List<Map<String, dynamic>> observations;
  final int? regionId;
  final String? station;
  final Map<String, dynamic> context;
  final String useCase;
}

class AnalysisSetupScreen extends StatefulWidget {
  const AnalysisSetupScreen({
    super.key,
    required this.api,
    required this.mode,
    required this.onRun,
    required this.onBack,
    this.errorMessage,
  });

  final RecommendationApi api;
  final String mode;
  final ValueChanged<AnalysisInput> onRun;
  final VoidCallback onBack;
  final String? errorMessage;

  @override
  State<AnalysisSetupScreen> createState() => _AnalysisSetupScreenState();
}

class _AnalysisSetupScreenState extends State<AnalysisSetupScreen> {
  final _formKey = GlobalKey<FormState>();
  final _bod = TextEditingController();
  final _cod = TextEditingController();
  final _tss = TextEditingController();
  final _ammonia = TextEditingController();
  final _nitrate = TextEditingController();
  final _phosphate = TextEditingController();
  final _ph = TextEditingController();
  final _do = TextEditingController();
  final _tds = TextEditingController();
  final _ec = TextEditingController();
  final _turbidity = TextEditingController();
  final _faecalColiform = TextEditingController();
  final _designFlow = TextEditingController();
  final _populationEquivalent = TextEditingController();
  final _availableLand = TextEditingController();
  List<SiteOption> _sites = [];
  SiteOption? _site;
  String? _targetUseCase;
  String _source = 'domestic_sewage';
  String _position = 'off_channel_or_stp_polishing';
  List<Map<String, dynamic>>? _uploaded;
  List<String> _uploadUnknownParameters = [];
  CsvValidationSummary? _csvValidation;
  String? _uploadName;
  int? _pollutionCount;
  String? _localError;
  bool _loadingSites = true;
  bool _uploading = false;

  bool get _isMeasuredMode => widget.mode == 'Measured Water Quality';
  bool get _isSiteMode => widget.mode.startsWith('Select Narmada');
  bool get _isPollutionMode => widget.mode == 'Pollution Source Screening';
  bool get _isUploadMode => widget.mode == 'Upload Water Data';

  @override
  void initState() {
    super.initState();
    widget.api.listSites().then((value) {
      if (mounted) {
        setState(() {
          _sites = value;
          _loadingSites = false;
        });
      }
    }).catchError((_) {
      if (mounted) setState(() => _loadingSites = false);
    });
  }

  @override
  void dispose() {
    _bod.dispose();
    _cod.dispose();
    _tss.dispose();
    _ammonia.dispose();
    _nitrate.dispose();
    _phosphate.dispose();
    _ph.dispose();
    _do.dispose();
    _tds.dispose();
    _ec.dispose();
    _turbidity.dispose();
    _faecalColiform.dispose();
    _designFlow.dispose();
    _populationEquivalent.dispose();
    _availableLand.dispose();
    super.dispose();
  }

  Future<void> _chooseCsv() async {
    if (_targetUseCase == null) {
      setState(
        () => _localError =
            'Select a target use case before running the recommendation.',
      );
      return;
    }
    final picked = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: const ['csv'],
      withData: true,
    );
    final file = picked?.files.single;
    if (file?.bytes == null) {
      return;
    }
    setState(() {
      _uploading = true;
      _localError = null;
    });
    try {
      final result = await widget.api.uploadWaterCsv(
        bytes: file!.bytes!,
        filename: file.name,
        useCase: _targetUseCase!,
      );
      if (mounted) {
        setState(() {
          _uploaded = result.observations;
          _uploadUnknownParameters = result.unknownParameters;
          _csvValidation = result.validationSummary;
          _uploadName = file.name;
        });
      }
    } on RecommendationApiException catch (error) {
      if (mounted) {
        setState(() {
          _uploaded = null;
          _uploadUnknownParameters = [];
          _csvValidation = error.csvValidationSummary;
          _uploadName = file?.name;
          _localError = error.message;
        });
      }
    } on Object {
      if (mounted) {
        setState(
          () => _localError =
              'CSV could not be read. Check the file format and try again.',
        );
      }
    } finally {
      if (mounted) {
        setState(() => _uploading = false);
      }
    }
  }

  Future<void> _selectSite(SiteOption? value) async {
    setState(() {
      _site = value;
      _pollutionCount = null;
    });
    if (value != null) {
      final count = await widget.api.pollutionSourceCount(value.regionId);
      if (mounted && _site?.regionId == value.regionId) {
        setState(() => _pollutionCount = count);
      }
    }
  }

  void _submit() {
    setState(() => _localError = null);
    if (_targetUseCase == null) {
      setState(
        () => _localError =
            'Select a target use case before running the recommendation.',
      );
      return;
    }
    if (_isSiteMode && _site == null) {
      setState(() => _localError = 'Select a Narmada site/station first.');
      return;
    }
    if (_isUploadMode && _uploaded == null) {
      setState(
        () => _localError =
            'Upload a CSV first, or use the Measured Water Quality workflow for manual entry.',
      );
      return;
    }
    if (_isMeasuredMode && !(_formKey.currentState?.validate() ?? false)) {
      return;
    }
    final observations = _uploaded ??
        (_isMeasuredMode ? _manualObservations() : <Map<String, dynamic>>[]);
    if (_isMeasuredMode && observations.isEmpty) {
      setState(() => _localError = 'Enter at least one measured parameter.');
      return;
    }
    if (_isUploadMode && _uploaded!.isEmpty) {
      setState(
        () => _localError =
            'The CSV contains no numeric observations. Blank values are unknown, but at least one measured value is needed.',
      );
      return;
    }
    widget.onRun(
      AnalysisInput(
        observations: observations,
        regionId: _site?.regionId,
        station: _site?.station,
        useCase: _targetUseCase!,
        context: <String, dynamic>{
          'workflow_mode': _workflowModeKey,
          if (!_isSiteMode) 'pollution_source_type': _source,
          if (!_isSiteMode) 'intervention_position': _position,
          if (_site?.streamOrder != null) 'stream_order': _site!.streamOrder,
          if (_pollutionCount != null)
            'pollution_source_record_count': _pollutionCount,
          if (_optionalNumber(_designFlow) != null)
            'design_flow_m3_d': _optionalNumber(_designFlow),
          if (_optionalNumber(_populationEquivalent) != null)
            'population_equivalent': _optionalNumber(_populationEquivalent),
          if (_optionalNumber(_availableLand) != null)
            'available_land_m2': _optionalNumber(_availableLand),
          if (_isUploadMode && _uploadUnknownParameters.isNotEmpty)
            'uploaded_unknown_parameters': _uploadUnknownParameters,
          if (_isUploadMode && _csvValidation != null)
            'csv_validation_summary': _csvValidation!.toJson(),
          if (_isUploadMode && _uploadName != null)
            'uploaded_filename': _uploadName,
        },
      ),
    );
  }

  String get _workflowModeKey {
    if (_isSiteMode) return 'site_context_only';
    if (_isPollutionMode) return 'pollution_source_screening';
    if (_isUploadMode) return 'uploaded_water_quality';
    return 'manual_measured_water_quality';
  }

  List<Map<String, dynamic>> _manualObservations() {
    final fields = [
      _ManualParameter(_bod, 'bod', 'mg_l'),
      _ManualParameter(_cod, 'cod', 'mg_l'),
      _ManualParameter(_tss, 'tss', 'mg_l'),
      _ManualParameter(_ammonia, 'ammonia_n', 'mg_l'),
      _ManualParameter(_nitrate, 'nitrate_n', 'mg_l'),
      _ManualParameter(_phosphate, 'phosphate_p', 'mg_l'),
      _ManualParameter(_ph, 'ph', 'ph_units'),
      _ManualParameter(_do, 'do', 'mg_l'),
      _ManualParameter(_tds, 'tds', 'mg_l'),
      _ManualParameter(_ec, 'ec', 'us_cm'),
      _ManualParameter(_turbidity, 'turbidity', 'ntu'),
      _ManualParameter(_faecalColiform, 'faecal_coliform', 'mpn_100ml'),
    ];
    return [
      for (final field in fields)
        if (field.controller.text.trim().isNotEmpty)
          {
            'parameter': field.parameter,
            'value': double.parse(field.controller.text.trim()),
            'unit': field.unit,
          },
    ];
  }

  double? _optionalNumber(TextEditingController controller) {
    final value = controller.text.trim();
    return value.isEmpty ? null : double.tryParse(value);
  }

  String get _modeSubtitle {
    if (_isSiteMode) {
      return 'Pick a Narmada monitoring station to run a location-context recommendation.';
    }
    if (_isPollutionMode) {
      return 'Choose a site when known, then screen source pressure, risk, and pretreatment needs.';
    }
    if (_isUploadMode) {
      return 'Upload a CSV with parameter, value, and unit columns for a broader water-quality panel.';
    }
    return 'Enter measured lab/field values. Leave optional fields blank if not available.';
  }

  String get _runButtonLabel {
    if (_isSiteMode) return 'Run Site Context Recommendation';
    if (_isPollutionMode) return 'Run Pollution Screening';
    if (_isUploadMode) return 'Run Uploaded-Data Recommendation';
    return 'Run Recommendation';
  }

  String get _sourceScreeningGuidance {
    switch (_source) {
      case 'industrial_or_mixed_industrial':
        return 'Source-risk focus: characterize industrial chemistry and provide ETP/CETP treatment, including neutralization where required. NbS can then serve as polishing, buffer, or source-control support.';
      case 'high_agriculture_only_no_water_data':
        return 'Source-risk focus: control nutrients, erosion, and sediment at farm and drainage scale first. Consider only intercepted off-channel runoff for polishing.';
      default:
        return 'Source-risk focus: provide screening and primary/biological treatment for collected sewage, then assess NbS units for secondary treatment and polishing.';
    }
  }

  Widget _targetUseCaseSelector() => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          DropdownButtonFormField<String>(
            isExpanded: true,
            initialValue: _targetUseCase,
            decoration: const InputDecoration(
              labelText: 'Target use case',
              prefixIcon: Icon(Icons.fact_check_outlined),
            ),
            items: const [
              DropdownMenuItem(
                value: 'discharge_inland',
                child: Text('Discharge to inland surface water'),
              ),
              DropdownMenuItem(
                value: 'irrigation',
                child: Text('Irrigation reuse'),
              ),
              DropdownMenuItem(
                value: 'drinking',
                child: Text('Drinking / strict-use screening'),
              ),
            ],
            onChanged: (value) => setState(() => _targetUseCase = value),
          ),
          const SizedBox(height: 8),
          const Text(
            'Choose the standard/purpose used to judge whether the treated water meets the target. This is different from pollution source.',
          ),
        ],
      );

  Widget _siteSelector() => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          DropdownButtonFormField<SiteOption>(
            isExpanded: true,
            initialValue: _site,
            decoration: InputDecoration(
              labelText: _loadingSites
                  ? 'Loading stations...'
                  : 'Narmada site / station',
              prefixIcon: const Icon(Icons.place_outlined),
            ),
            items: [
              for (final site in _sites)
                DropdownMenuItem(
                  value: site,
                  child: Text(
                    site.station,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
            ],
            onChanged: _selectSite,
          ),
          if (_pollutionCount != null)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text(
                'The toolkit found $_pollutionCount stored pollution-source records for this area.',
              ),
            ),
          if (_site != null) ...[
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                if (_site!.streamOrder != null)
                  _ContextChip(
                    label: 'Stream order',
                    value: '${_site!.streamOrder}',
                  ),
                if (_site!.dischargeCms != null)
                  _ContextChip(
                    label: 'River discharge context',
                    value: '${_site!.dischargeCms!.toStringAsFixed(1)} m³/s',
                  ),
                if (_site!.drainageAreaKm2 != null)
                  _ContextChip(
                    label: 'Drainage area',
                    value: '${_site!.drainageAreaKm2!.toStringAsFixed(0)} km²',
                  ),
              ],
            ),
          ],
        ],
      );

  Widget _sourceAndPositionSelectors() => LayoutBuilder(
        builder: (context, constraints) {
          final sourceField = DropdownButtonFormField<String>(
            isExpanded: true,
            initialValue: _source,
            decoration: const InputDecoration(
              labelText: 'Pollution source context',
            ),
            items: const [
              DropdownMenuItem(
                value: 'domestic_sewage',
                child: Text('Domestic sewage'),
              ),
              DropdownMenuItem(
                value: 'high_agriculture_only_no_water_data',
                child: Text('Agricultural runoff'),
              ),
              DropdownMenuItem(
                value: 'industrial_or_mixed_industrial',
                child: Text('Industrial / mixed industrial'),
              ),
            ],
            onChanged: (value) => setState(() => _source = value!),
          );
          final positionField = DropdownButtonFormField<String>(
            isExpanded: true,
            initialValue: _position,
            decoration:
                const InputDecoration(labelText: 'Intervention position'),
            items: const [
              DropdownMenuItem(
                value: 'off_channel_or_stp_polishing',
                child: Text('Off-channel / STP polishing'),
              ),
              DropdownMenuItem(value: 'in_channel', child: Text('In-channel')),
              DropdownMenuItem(
                value: 'standalone_primary_treatment',
                child: Text('Standalone primary treatment'),
              ),
            ],
            onChanged: (value) => setState(() => _position = value!),
          );
          if (constraints.maxWidth < 680) {
            return Column(
              children: [
                sourceField,
                const SizedBox(height: 12),
                positionField
              ],
            );
          }
          return Row(
            children: [
              Expanded(child: sourceField),
              const SizedBox(width: 12),
              Expanded(child: positionField),
            ],
          );
        },
      );

  Widget _planningInputsPanel() => AppCard(
        padding: EdgeInsets.zero,
        child: ExpansionTile(
          tilePadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
          childrenPadding: const EdgeInsets.fromLTRB(14, 0, 14, 14),
          leading: const Icon(
            Icons.square_foot_outlined,
            color: NbsColors.researchBlue,
          ),
          title: const Text(
            'Optional sizing information',
            style: TextStyle(fontWeight: FontWeight.w800),
          ),
          subtitle: const Text(
            'Add flow, people served, or available land when known.',
          ),
          children: [
            LayoutBuilder(
              builder: (context, constraints) {
                final fields = [
                  _NumberField(
                    controller: _designFlow,
                    label: 'Design flow',
                    suffix: 'm³/day',
                    helper: 'Average flow to be treated',
                    requiredField: false,
                  ),
                  _NumberField(
                    controller: _populationEquivalent,
                    label: 'People served',
                    suffix: '',
                    helper: 'Population equivalent',
                    requiredField: false,
                  ),
                  _NumberField(
                    controller: _availableLand,
                    label: 'Available land',
                    suffix: 'm²',
                    helper: 'Usable treatment area',
                    requiredField: false,
                  ),
                ];
                if (constraints.maxWidth < 760) {
                  return Column(
                    children: [
                      for (var index = 0; index < fields.length; index++) ...[
                        fields[index],
                        if (index < fields.length - 1)
                          const SizedBox(height: 10),
                      ],
                    ],
                  );
                }
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    for (var index = 0; index < fields.length; index++) ...[
                      Expanded(child: fields[index]),
                      if (index < fields.length - 1) const SizedBox(width: 10),
                    ],
                  ],
                );
              },
            ),
            const SizedBox(height: 8),
            Text(
              'These values support screening-level land guidance only. Final sizing still needs pollutant loads, levels, soil, and a site survey.',
              style: Theme.of(
                context,
              ).textTheme.bodySmall?.copyWith(color: NbsColors.mutedGrey),
            ),
          ],
        ),
      );

  Widget _uploadPanel() => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          OutlinedButton.icon(
            onPressed: _uploading ? null : _chooseCsv,
            icon: const Icon(Icons.upload_file),
            label: Text(
              _uploading
                  ? 'Analyzing CSV...'
                  : _uploadName ?? 'Upload Water CSV',
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Example upload format',
            style: Theme.of(
              context,
            ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 6),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: NbsColors.deepNavy.withValues(alpha: 0.05),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: NbsColors.cardBorder),
            ),
            child: const SelectableText(
              _csvTemplate,
              style: TextStyle(fontFamily: 'monospace'),
            ),
          ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: () async {
              await Clipboard.setData(const ClipboardData(text: _csvTemplate));
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                      content: Text('Example upload format copied.')),
                );
              }
            },
            icon: const Icon(Icons.copy_outlined),
            label: const Text('Copy template'),
          ),
          const SizedBox(height: 6),
          Text(
            'The unit column is optional for now. Values must be numeric. Blank values remain unknown and are never converted to zero.',
            style: Theme.of(
              context,
            ).textTheme.bodySmall?.copyWith(color: NbsColors.mutedGrey),
          ),
          const SizedBox(height: 6),
          Text(
            'Unsupported parameters and nonnumeric rows are skipped and reported below; skipped rows reduce result confidence.',
            style: Theme.of(
              context,
            ).textTheme.bodySmall?.copyWith(color: NbsColors.mutedGrey),
          ),
          const SizedBox(height: 6),
          Text(
            'Accepted aliases include BOD/BOD5, COD, TSS, NH4-N, NO3-N, PO4-P/TP, pH, DO, TDS, EC, turbidity, and faecal coliform/FC.',
            style: Theme.of(
              context,
            ).textTheme.bodySmall?.copyWith(color: NbsColors.mutedGrey),
          ),
          if (_csvValidation != null) ...[
            const SizedBox(height: 12),
            _CsvValidationPanel(
              summary: _csvValidation!,
              observations: _uploaded ?? const [],
            ),
          ],
        ],
      );

  Widget _manualPanel() {
    final fields = [
      _NumberField(
        controller: _bod,
        label: 'BOD',
        suffix: 'mg/L',
        helper: 'Organic load',
        requiredField: false,
      ),
      _NumberField(
        controller: _cod,
        label: 'COD',
        suffix: 'mg/L',
        helper: 'Chemical oxygen demand',
        requiredField: false,
      ),
      _NumberField(
        controller: _tss,
        label: 'TSS',
        suffix: 'mg/L',
        helper: 'Suspended solids',
        requiredField: false,
      ),
      _NumberField(
        controller: _ammonia,
        label: 'NH4-N',
        suffix: 'mg/L',
        helper: 'Ammoniacal nitrogen',
        requiredField: false,
      ),
      _NumberField(
        controller: _nitrate,
        label: 'Nitrate-N',
        suffix: 'mg/L',
        helper: 'As nitrogen',
        requiredField: false,
      ),
      _NumberField(
        controller: _phosphate,
        label: 'PO4-P / TP',
        suffix: 'mg/L',
        helper: 'Phosphorus',
        requiredField: false,
      ),
      _NumberField(
        controller: _ph,
        label: 'pH',
        suffix: '',
        helper: 'Acidity / alkalinity',
        requiredField: false,
      ),
      _NumberField(
        controller: _do,
        label: 'DO',
        suffix: 'mg/L',
        helper: 'Dissolved oxygen',
        requiredField: false,
      ),
      _NumberField(
        controller: _tds,
        label: 'TDS',
        suffix: 'mg/L',
        helper: 'Dissolved solids',
        requiredField: false,
      ),
      _NumberField(
        controller: _ec,
        label: 'EC',
        suffix: 'uS/cm',
        helper: 'Conductivity',
        requiredField: false,
      ),
      _NumberField(
        controller: _turbidity,
        label: 'Turbidity',
        suffix: 'NTU',
        helper: 'Clarity indicator',
        requiredField: false,
      ),
      _NumberField(
        controller: _faecalColiform,
        label: 'Faecal coliform',
        suffix: 'MPN/100mL',
        helper: 'Pathogen indicator',
        requiredField: false,
      ),
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Measured water-quality panel',
          style: Theme.of(
            context,
          ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
        ),
        const SizedBox(height: 6),
        Text(
          'The engine uses all filled parameters. Optional blanks are treated as unknown, not zero.',
          style: Theme.of(
            context,
          ).textTheme.bodySmall?.copyWith(color: NbsColors.mutedGrey),
        ),
        const SizedBox(height: 10),
        LayoutBuilder(
          builder: (context, constraints) {
            final isWide = constraints.maxWidth > 900;
            return GridView.count(
              crossAxisCount: isWide ? 3 : 1,
              crossAxisSpacing: 10,
              mainAxisSpacing: 10,
              childAspectRatio: isWide ? 3.2 : 4.6,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              children: fields,
            );
          },
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'Recommendation inputs',
      actions: [
        IconButton(onPressed: widget.onBack, icon: const Icon(Icons.close)),
      ],
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              widget.mode,
              style: Theme.of(
                context,
              ).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w900),
            ),
            const SizedBox(height: 6),
            Text(
              _modeSubtitle,
              style: Theme.of(
                context,
              ).textTheme.bodyMedium?.copyWith(color: NbsColors.mutedGrey),
            ),
            const SizedBox(height: 16),
            _targetUseCaseSelector(),
            const SizedBox(height: 16),
            _siteSelector(),
            if (_isPollutionMode && _site == null) ...[
              const SizedBox(height: 8),
              const _InfoNote(
                icon: Icons.info_outline,
                text:
                    'No site was selected. The result uses only the selected pollution-source context.',
              ),
            ],
            const SizedBox(height: 14),
            if (!_isSiteMode) ...[
              _sourceAndPositionSelectors(),
              const SizedBox(height: 18),
            ],
            _planningInputsPanel(),
            const SizedBox(height: 18),
            if (_isUploadMode) ...[_uploadPanel(), const SizedBox(height: 18)],
            if (_isMeasuredMode) ...[
              _manualPanel(),
              const SizedBox(height: 18),
            ],
            if (_isSiteMode) ...[
              _InfoNote(
                icon: Icons.account_tree_outlined,
                text:
                    'This workflow uses station, stream-order, and basin context. Add lab values from the Measured Water Quality workflow when available.',
              ),
              const SizedBox(height: 18),
            ],
            if (_isPollutionMode) ...[
              _InfoNote(
                icon: Icons.warning_amber_outlined,
                text: _sourceScreeningGuidance,
              ),
              const SizedBox(height: 18),
            ],
            if (widget.errorMessage != null || _localError != null)
              Padding(
                padding: const EdgeInsets.only(top: 12),
                child: Text(
                  _localError ?? widget.errorMessage!,
                  style: const TextStyle(color: Colors.red),
                ),
              ),
            FilledButton.icon(
              onPressed: _submit,
              icon: const Icon(Icons.science_outlined),
              label: Text(_runButtonLabel),
            ),
          ],
        ),
      ),
    );
  }
}

class _CsvValidationPanel extends StatelessWidget {
  const _CsvValidationPanel({
    required this.summary,
    required this.observations,
  });

  final CsvValidationSummary summary;
  final List<Map<String, dynamic>> observations;

  @override
  Widget build(BuildContext context) {
    final messages = [...summary.warnings, ...summary.errors];
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color:
            (summary.isValid ? NbsColors.wetlandGreen : NbsColors.warningAmber)
                .withValues(alpha: 0.07),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: (summary.isValid
                  ? NbsColors.wetlandGreen
                  : NbsColors.warningAmber)
              .withValues(alpha: 0.28),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            summary.isValid
                ? 'Uploaded water-quality data accepted'
                : 'No usable water-quality values found',
            style: const TextStyle(fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _ContextChip(label: 'Rows read', value: '${summary.rowsRead}'),
              _ContextChip(label: 'Values used', value: '${summary.rowsUsed}'),
              _ContextChip(
                label: 'Blank values',
                value: '${summary.blankValues}',
              ),
              _ContextChip(
                label: 'Values not used',
                value:
                    '${summary.unknownParameters.length + summary.nonNumericValues.length + summary.blankParameters}',
              ),
            ],
          ),
          if (observations.isNotEmpty) ...[
            const SizedBox(height: 10),
            Text(
              'Water-quality values recognized',
              style: Theme.of(
                context,
              ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 5),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final row in observations)
                  Chip(
                    label: Text(
                      '${_displayParameter(row['parameter']?.toString(), fallback: row['display_name']?.toString())} = ${row['value']}${_displayUnitSuffix(row['unit'])}',
                    ),
                  ),
              ],
            ),
          ],
          if (messages.isNotEmpty) ...[
            const SizedBox(height: 10),
            _ReadableBulletList(values: messages),
          ],
        ],
      ),
    );
  }
}

class _ContextChip extends StatelessWidget {
  const _ContextChip({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) => Chip(
        avatar: const Icon(Icons.info_outline, size: 16),
        label: Text('$label: $value'),
      );
}

class _InfoNote extends StatelessWidget {
  const _InfoNote({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: NbsColors.riverTeal.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: NbsColors.riverTeal.withValues(alpha: 0.18)),
      ),
      child: Row(
        children: [
          Icon(icon, color: NbsColors.riverTeal),
          const SizedBox(width: 10),
          Expanded(child: Text(text)),
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
  State<WaterQualityEntryScreen> createState() =>
      _WaterQualityEntryScreenState();
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
    this.previousScenarios = const [],
  });

  final RecommendationResponse response;
  final ValueChanged<RecommendationItem> onViewDetail;
  final VoidCallback onNewRun;
  final VoidCallback onHome;
  final VoidCallback onAbout;
  final List<RecommendationResponse> previousScenarios;

  @override
  Widget build(BuildContext context) {
    final bundle = response.recommendationAssemblyBundle;
    final trains = response.rankedTrains;
    final components = response.componentRecommendations;
    final topTrain = trains.isNotEmpty ? trains.first : null;
    final sourceLocationGuidance = _cleanContextGuidance(
      _sourceLocationGuidance(trains),
      response,
    );
    final contextOnly = response.inputSummary.isContextOnly;
    final hasMeasuredData = response.inputSummary.observationCount > 0;
    final dataGaps = _cleanDataGaps(response, topTrain);
    final whyReasons = _topRecommendationReasons(
      response,
      topTrain,
      sourceLocationGuidance,
    );
    final practicalRecommendation = _practicalRecommendation(
      response,
      topTrain,
    );
    final keyCaution = _keyCaution(response, topTrain);
    final workspaceKey = GlobalKey<_SolutionWorkspaceState>();
    final summaryNextSteps = _uniqueStrings([
      ...response.designReadiness.requiredNextSteps,
      ...sourceLocationGuidance,
      if (!hasMeasuredData) 'Confirm recent water-quality values.',
      'Check flow, land, and site conditions.',
      'Review the option with a qualified engineer before design.',
    ]).take(3).toList();
    final summaryWarning = _majorSummaryWarning(response, topTrain, dataGaps);

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
          Text(
            'Solution Workspace',
            style: Theme.of(
              context,
            ).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 6),
          Text(
            'Review the recommendation by decision stage. Summary opens first.',
            style: Theme.of(
              context,
            ).textTheme.bodyMedium?.copyWith(color: NbsColors.mutedGrey),
          ),
          const SizedBox(height: 14),
          _SolutionWorkspace(
            key: workspaceKey,
            panels: [
              _WorkspacePanel(
                label: 'Summary',
                icon: Icons.dashboard_outlined,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _DetailSection(
                      title: 'Recommended option',
                      child: Text(
                        topTrain == null
                            ? practicalRecommendation
                            : 'We recommend ${topTrain.name} for this screening case. $practicalRecommendation',
                        style:
                            Theme.of(context).textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.w800,
                                  height: 1.4,
                                ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    _SummaryDecisionMetrics(
                      response: response,
                      train: topTrain,
                    ),
                    const SizedBox(height: 12),
                    _TargetAndSourceSummary(response: response),
                    const SizedBox(height: 12),
                    _DetailSection(
                      title: 'What this means',
                      child: Text(
                        '$keyCaution ${response.designReadiness.explanation}',
                      ),
                    ),
                    if (summaryWarning != null) ...[
                      const SizedBox(height: 12),
                      _AlertBanner.compact(
                        icon: Icons.warning_amber_outlined,
                        color: NbsColors.warningAmber,
                        title: 'Important warning',
                        message: summaryWarning,
                      ),
                    ],
                    const SizedBox(height: 12),
                    _DetailSection(
                      title: 'What you should do next',
                      child: _NumberedActionList(
                        values: summaryNextSteps,
                        emptyText:
                            'Review the result with a qualified practitioner before design.',
                      ),
                    ),
                    const SizedBox(height: 12),
                    _SummaryNavigation(
                      onWhy: () => workspaceKey.currentState?.select(1),
                      onChecks: () => workspaceKey.currentState?.select(2),
                      onSizing: () => workspaceKey.currentState?.select(5),
                      onCompare: () => workspaceKey.currentState?.select(6),
                      onLearn: () => workspaceKey.currentState?.select(7),
                      onExport: () => workspaceKey.currentState?.select(8),
                    ),
                  ],
                ),
              ),
              _WorkspacePanel(
                label: 'Why this result',
                icon: Icons.lightbulb_outline,
                child: _WhyResultWorkspace(
                  response: response,
                  bundle: bundle,
                  trains: trains,
                  topTrain: topTrain,
                  reasons: whyReasons,
                  contextOnly: contextOnly,
                  hasMeasuredData: hasMeasuredData,
                ),
              ),
              _WorkspacePanel(
                label: 'Site and design checks',
                icon: Icons.engineering_outlined,
                child: _SiteDesignChecksWorkspace(response: response),
              ),
              _WorkspacePanel(
                label: 'Implementation',
                icon: Icons.construction_outlined,
                child: _ImplementationWorkspace(
                  response: response,
                  train: topTrain,
                  sourceLocationGuidance: sourceLocationGuidance,
                ),
              ),
              _WorkspacePanel(
                label: 'NbS components',
                icon: Icons.spa_outlined,
                child: _NbsComponentsWorkspace(
                  train: topTrain,
                  components: components,
                  filteredComponents: response.filteredComponents,
                  citationsById: response.citationsById,
                ),
              ),
              _WorkspacePanel(
                label: 'Sizing',
                icon: Icons.square_foot_outlined,
                child: _SizingWorkspace(response: response),
              ),
              _WorkspacePanel(
                label: 'Compare options',
                icon: Icons.compare_arrows_outlined,
                child: _ComparisonWorkspace(
                  response: response,
                  previousScenarios: previousScenarios,
                ),
              ),
              _WorkspacePanel(
                label: 'Learn',
                icon: Icons.menu_book_outlined,
                child: _LearnWorkspace(
                  response: response,
                  bundle: bundle,
                  train: topTrain,
                ),
              ),
              _WorkspacePanel(
                label: 'Export',
                icon: Icons.file_download_outlined,
                child: _ReportExportPanel(response: response),
              ),
            ],
          ),
          const SizedBox(height: 14),
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

class _WorkspacePanel {
  const _WorkspacePanel({
    required this.label,
    required this.icon,
    required this.child,
  });

  final String label;
  final IconData icon;
  final Widget child;
}

class _SolutionWorkspace extends StatefulWidget {
  const _SolutionWorkspace({super.key, required this.panels});

  final List<_WorkspacePanel> panels;

  @override
  State<_SolutionWorkspace> createState() => _SolutionWorkspaceState();
}

class _SolutionWorkspaceState extends State<_SolutionWorkspace> {
  int selectedIndex = 0;

  void select(int index) {
    if (index >= 0 && index < widget.panels.length) {
      setState(() => selectedIndex = index);
    }
  }

  @override
  Widget build(BuildContext context) {
    final selected = widget.panels[selectedIndex];
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth >= 900) {
          return Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SizedBox(
                width: 210,
                child: Column(
                  children: [
                    for (var index = 0; index < widget.panels.length; index++)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 6),
                        child: SizedBox(
                          width: double.infinity,
                          child: index == selectedIndex
                              ? FilledButton.tonalIcon(
                                  onPressed: () =>
                                      setState(() => selectedIndex = index),
                                  icon: Icon(widget.panels[index].icon),
                                  label: Align(
                                    alignment: Alignment.centerLeft,
                                    child: Text(widget.panels[index].label),
                                  ),
                                )
                              : TextButton.icon(
                                  onPressed: () =>
                                      setState(() => selectedIndex = index),
                                  icon: Icon(widget.panels[index].icon),
                                  label: Align(
                                    alignment: Alignment.centerLeft,
                                    child: Text(widget.panels[index].label),
                                  ),
                                ),
                        ),
                      ),
                  ],
                ),
              ),
              const SizedBox(width: 18),
              Expanded(child: selected.child),
            ],
          );
        }
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  for (var index = 0;
                      index < widget.panels.length;
                      index++) ...[
                    ChoiceChip(
                      selected: index == selectedIndex,
                      avatar: Icon(widget.panels[index].icon, size: 17),
                      label: Text(widget.panels[index].label),
                      onSelected: (_) => setState(() => selectedIndex = index),
                    ),
                    const SizedBox(width: 7),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 14),
            selected.child,
          ],
        );
      },
    );
  }
}

class _SummaryDecisionMetrics extends StatelessWidget {
  const _SummaryDecisionMetrics({required this.response, required this.train});

  final RecommendationResponse response;
  final TrainRecommendation? train;

  @override
  Widget build(BuildContext context) {
    final metrics = [
      (
        Icons.analytics_outlined,
        response.inputSummary.observationCount == 0
            ? 'Context match'
            : 'Screening match',
        train?.matchPercent ?? 'Not available',
        NbsColors.researchBlue,
      ),
      (
        Icons.verified_outlined,
        'Result confidence',
        train == null ? 'Data-limited' : _trainConfidenceDisplay(train!),
        NbsColors.wetlandGreen,
      ),
      (
        Icons.engineering_outlined,
        'Design readiness',
        response.designReadiness.shortLabel,
        NbsColors.warningAmber,
      ),
    ];
    return LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth >= 760
            ? (constraints.maxWidth - 20) / 3
            : constraints.maxWidth;
        return Wrap(
          spacing: 10,
          runSpacing: 10,
          children: [
            for (final metric in metrics)
              SizedBox(
                width: width,
                child: AppCard(
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(metric.$1, color: metric.$4),
                      const SizedBox(width: 9),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              metric.$2,
                              style: Theme.of(context)
                                  .textTheme
                                  .bodySmall
                                  ?.copyWith(color: NbsColors.mutedGrey),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              metric.$3,
                              style: const TextStyle(
                                fontWeight: FontWeight.w900,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
          ],
        );
      },
    );
  }
}

class _TargetAndSourceSummary extends StatelessWidget {
  const _TargetAndSourceSummary({required this.response});

  final RecommendationResponse response;

  @override
  Widget build(BuildContext context) {
    final source = response.inputSummary.context['pollution_source_type'];
    return _DetailSection(
      title: 'Target and source context',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              StatusPill(
                label: 'Selected target use case',
                value: _targetUseCaseLabel(response.useCase),
                color: NbsColors.researchBlue,
              ),
              StatusPill(
                label: 'Pollution source',
                value: _pollutionSourceLabel(source?.toString()),
                color: NbsColors.riverTeal,
              ),
            ],
          ),
          const SizedBox(height: 8),
          const Text(
            'Source type tells where pollution comes from. Target use case tells which standard is checked.',
          ),
        ],
      ),
    );
  }
}

class _SummaryNavigation extends StatelessWidget {
  const _SummaryNavigation({
    required this.onWhy,
    required this.onChecks,
    required this.onSizing,
    required this.onCompare,
    required this.onLearn,
    required this.onExport,
  });

  final VoidCallback onWhy;
  final VoidCallback onChecks;
  final VoidCallback onSizing;
  final VoidCallback onCompare;
  final VoidCallback onLearn;
  final VoidCallback onExport;

  @override
  Widget build(BuildContext context) => Wrap(
        spacing: 8,
        runSpacing: 8,
        children: [
          OutlinedButton.icon(
            onPressed: onWhy,
            icon: const Icon(Icons.lightbulb_outline),
            label: const Text('Why this result?'),
          ),
          OutlinedButton.icon(
            onPressed: onChecks,
            icon: const Icon(Icons.fact_check_outlined),
            label: const Text('Check site and design'),
          ),
          OutlinedButton.icon(
            onPressed: onCompare,
            icon: const Icon(Icons.compare_arrows_outlined),
            label: const Text('Compare options'),
          ),
          OutlinedButton.icon(
            onPressed: onSizing,
            icon: const Icon(Icons.square_foot_outlined),
            label: const Text('Estimate land'),
          ),
          OutlinedButton.icon(
            onPressed: onLearn,
            icon: const Icon(Icons.schema_outlined),
            label: const Text('View diagrams'),
          ),
          OutlinedButton.icon(
            onPressed: onExport,
            icon: const Icon(Icons.file_download_outlined),
            label: const Text('Export report'),
          ),
        ],
      );
}

class _WhyResultWorkspace extends StatelessWidget {
  const _WhyResultWorkspace({
    required this.response,
    required this.bundle,
    required this.trains,
    required this.topTrain,
    required this.reasons,
    required this.contextOnly,
    required this.hasMeasuredData,
  });

  final RecommendationResponse response;
  final RecommendationAssemblyBundle? bundle;
  final List<TrainRecommendation> trains;
  final TrainRecommendation? topTrain;
  final List<String> reasons;
  final bool contextOnly;
  final bool hasMeasuredData;

  @override
  Widget build(BuildContext context) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _DetailSection(
            title: 'Why this is the current recommendation',
            child: _ReadableBulletList(
              values: reasons.take(4).toList(),
              emptyText:
                  'The toolkit could not produce a ranked explanation for this run.',
            ),
          ),
          const SizedBox(height: 14),
          _PollutantGapPanel(
            train: topTrain,
            selectedUseCase: response.useCase,
          ),
          if (trains.isNotEmpty) ...[
            const SizedBox(height: 14),
            _DetailSection(
              title: 'How it compares with alternatives',
              child: _TopTrainComparison(trains: trains.take(3).toList()),
            ),
          ],
          const SizedBox(height: 14),
          for (final train in trains)
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: TrainRecommendationCard(
                train: train,
                contextOnly: contextOnly,
                hasMeasuredData: hasMeasuredData,
                citationsById: response.citationsById,
                selectedUseCase: response.useCase,
              ),
            ),
          AppCard(
            padding: EdgeInsets.zero,
            child: ExpansionTile(
              tilePadding: const EdgeInsets.symmetric(horizontal: 14),
              childrenPadding: const EdgeInsets.fromLTRB(14, 0, 14, 14),
              title: const Text(
                'Show technical details',
                style: TextStyle(fontWeight: FontWeight.w800),
              ),
              subtitle: const Text(
                'View method, confidence basis, and evidence records.',
              ),
              children: [
                _DataUsedPanel(response: response),
                const SizedBox(height: 12),
                _DataConfidenceGuide(
                  train: topTrain,
                  methodLabel: _confidenceMethodLabel(response, bundle),
                  dataLimited: contextOnly || !hasMeasuredData,
                ),
                const SizedBox(height: 12),
                _EvidenceWorkspace(
                  response: response,
                  bundle: bundle,
                  train: topTrain,
                ),
              ],
            ),
          ),
        ],
      );
}

class _SiteDesignChecksWorkspace extends StatelessWidget {
  const _SiteDesignChecksWorkspace({required this.response});

  final RecommendationResponse response;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _LocationWorkspace(location: response.locationContext),
        const SizedBox(height: 16),
        _DesignReadinessWorkspace(readiness: response.designReadiness),
        if (response.sizingEstimates.isNotEmpty) ...[
          const SizedBox(height: 16),
          _DetailSection(
            title: 'Land check for the top option',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  response.sizingEstimates.first.estimateLabel,
                  style: const TextStyle(fontWeight: FontWeight.w900),
                ),
                const SizedBox(height: 6),
                Text(_landFitSentence(response.sizingEstimates.first.landFit)),
                const SizedBox(height: 6),
                const Text(
                  'This is an early screening check. Use the Sizing and land section for its evidence limits and missing inputs.',
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }
}

class _SizingWorkspace extends StatelessWidget {
  const _SizingWorkspace({required this.response});

  final RecommendationResponse response;

  @override
  Widget build(BuildContext context) {
    final estimates = response.sizingEstimates;
    final top = estimates.isEmpty ? null : estimates.first;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _DetailSection(
          title: 'Sizing and land estimate',
          child: Text(
            'Provide design flow for hydraulic-loading evidence, or population/PE for per-person evidence. The toolkit never converts one into the other.',
          ),
        ),
        const SizedBox(height: 14),
        if (top == null)
          const _DetailSection(
            title: 'Estimated land need',
            child: Text(
              'The toolkit does not have enough information to estimate a footprint.',
            ),
          )
        else
          _SizingEstimateCard(estimate: top, isTop: true),
        if (estimates.length > 1) ...[
          const SizedBox(height: 14),
          AppCard(
            padding: EdgeInsets.zero,
            child: ExpansionTile(
              tilePadding: const EdgeInsets.symmetric(horizontal: 14),
              childrenPadding: const EdgeInsets.fromLTRB(14, 0, 14, 14),
              title: const Text(
                'View alternative land estimates',
                style: TextStyle(fontWeight: FontWeight.w800),
              ),
              children: [
                for (final estimate in estimates.skip(1))
                  Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: _SizingEstimateCard(estimate: estimate),
                  ),
              ],
            ),
          ),
        ],
      ],
    );
  }
}

class _SizingEstimateCard extends StatelessWidget {
  const _SizingEstimateCard({required this.estimate, this.isTop = false});

  final SizingEstimate estimate;
  final bool isTop;

  @override
  Widget build(BuildContext context) => AppCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              isTop
                  ? 'Estimated land need for ${estimate.trainName}'
                  : estimate.trainName,
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
            ),
            const SizedBox(height: 8),
            _ReadableBulletList(
              values: _sizingEstimateLines(estimate),
              emptyText: estimate.estimateLabel,
            ),
            const SizedBox(height: 8),
            Text(
              _landFitSentence(estimate.landFit),
              style: const TextStyle(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 10),
            _TextBlockList(
              title: 'To calculate area, provide',
              values: estimate.missingInputs,
              emptyText:
                  'The screening inputs are present; detailed design inputs are still required.',
            ),
            const SizedBox(height: 10),
            Text(
              'This is a screening estimate, not final design.',
              style: Theme.of(
                context,
              ).textTheme.bodySmall?.copyWith(color: NbsColors.mutedGrey),
            ),
            const SizedBox(height: 8),
            ExpansionTile(
              tilePadding: EdgeInsets.zero,
              childrenPadding: const EdgeInsets.only(bottom: 8),
              expandedAlignment: Alignment.centerLeft,
              expandedCrossAxisAlignment: CrossAxisAlignment.start,
              title: const Text(
                'Show calculations and assumptions',
                style: TextStyle(fontWeight: FontWeight.w800),
              ),
              children: [
                SizedBox(
                  width: double.infinity,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _TextBlockList(
                        title: 'Inputs used',
                        values: estimate.inputsUsed,
                        emptyText:
                            'No flow, population, or land value was supplied.',
                      ),
                      const SizedBox(height: 10),
                      _TextBlockList(
                        title: 'Key assumptions',
                        values: estimate.keyAssumptions,
                        emptyText:
                            'No calculation assumptions apply because an area was not estimated.',
                      ),
                      const SizedBox(height: 10),
                      Text(
                        'Footprint basis: ${_calculationDetailLabel(estimate.basis)}',
                        textAlign: TextAlign.left,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Sizing confidence: ${_calculationDetailLabel(estimate.sizingConfidence)}',
                        textAlign: TextAlign.left,
                      ),
                      const SizedBox(height: 8),
                      Text(estimate.designCaution, textAlign: TextAlign.left),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      );
}

class _ComparisonWorkspace extends StatelessWidget {
  const _ComparisonWorkspace({
    required this.response,
    required this.previousScenarios,
  });

  final RecommendationResponse response;
  final List<RecommendationResponse> previousScenarios;

  @override
  Widget build(BuildContext context) {
    final comparison = response.scenarioComparison;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _DetailSection(
          title: 'Compare options',
          child: Text(
            'Compare the current treatment trains without changing their scientific rank. Run another case to compare different water-quality, site, or land inputs.',
          ),
        ),
        if (comparison.takeaways.isNotEmpty) ...[
          const SizedBox(height: 14),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              for (final takeaway in comparison.takeaways)
                SizedBox(
                  width: 280,
                  child: AppCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          takeaway.label,
                          style: const TextStyle(
                            fontWeight: FontWeight.w900,
                            color: NbsColors.riverTeal,
                          ),
                        ),
                        const SizedBox(height: 5),
                        Text(
                          takeaway.trainName ?? 'Current option',
                          style: const TextStyle(fontWeight: FontWeight.w800),
                        ),
                        const SizedBox(height: 5),
                        Text(takeaway.explanation),
                      ],
                    ),
                  ),
                ),
            ],
          ),
        ],
        const SizedBox(height: 14),
        for (final option in comparison.options.take(3))
          Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: _ComparisonOptionCard(response: response, option: option),
          ),
        if (comparison.options.length > 3)
          AppCard(
            padding: EdgeInsets.zero,
            child: ExpansionTile(
              tilePadding: const EdgeInsets.symmetric(horizontal: 14),
              childrenPadding: const EdgeInsets.fromLTRB(14, 0, 14, 14),
              title: Text(
                'Show all ${comparison.options.length} options',
                style: const TextStyle(fontWeight: FontWeight.w800),
              ),
              children: [
                for (final option in comparison.options.skip(3))
                  Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: _ComparisonOptionCard(
                      response: response,
                      option: option,
                    ),
                  ),
              ],
            ),
          ),
        if (comparison.componentOptions.isNotEmpty) ...[
          const SizedBox(height: 14),
          _DetailSection(
            title: 'Supporting component comparison',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'These components support the ranked treatment train. They are not standalone final recommendations.',
                ),
                const SizedBox(height: 8),
                for (final component in comparison.componentOptions)
                  ListTile(
                    contentPadding: EdgeInsets.zero,
                    leading: const Icon(
                      Icons.spa_outlined,
                      color: NbsColors.wetlandGreen,
                    ),
                    title: Text(
                      component.name,
                      style: const TextStyle(fontWeight: FontWeight.w800),
                    ),
                    subtitle: Text(
                      'Role: ${_sentenceFromSnake(component.role)}. '
                      'Standalone use: ${_standaloneUseLabel(component.standaloneSuitability)}. '
                      'Key check: ${component.keyConstraints.isEmpty ? 'confirm soil/infiltration and hydraulic design' : _readableText(component.keyConstraints.first)}',
                    ),
                  ),
              ],
            ),
          ),
        ],
        if (previousScenarios.isNotEmpty) ...[
          const SizedBox(height: 14),
          _DetailSection(
            title: 'Previous cases in this session',
            child: Column(
              children: [
                for (var index = 0; index < previousScenarios.length; index++)
                  _PreviousScenarioRow(
                    index: index,
                    response: previousScenarios[index],
                  ),
              ],
            ),
          ),
        ],
        const SizedBox(height: 14),
        _ReadableBulletList(values: comparison.limitations),
      ],
    );
  }
}

class _ComparisonOptionCard extends StatelessWidget {
  const _ComparisonOptionCard({required this.response, required this.option});

  final RecommendationResponse response;
  final ComparisonOption option;

  @override
  Widget build(BuildContext context) => AppCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                _RankBlock(rank: option.rank),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    option.name,
                    style: Theme.of(
                      context,
                    )
                        .textTheme
                        .titleMedium
                        ?.copyWith(fontWeight: FontWeight.w900),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _MetricChip(
                  label: response.inputSummary.observationCount == 0
                      ? 'Context match'
                      : 'Screening match',
                  value: _optionalPercent(option.technicalMatch),
                  color: NbsColors.researchBlue,
                ),
                _MetricChip(
                  label: 'Confidence',
                  value: _comparisonConfidence(option),
                  color: NbsColors.wetlandGreen,
                ),
                _MetricChip(
                  label: 'Land',
                  value: _landFitShort(option.landFit),
                  color: NbsColors.warningAmber,
                ),
                _MetricChip(
                  label: 'O&M practicality',
                  value: option.omIntensity,
                  color: NbsColors.riverTeal,
                ),
              ],
            ),
            const SizedBox(height: 9),
            Text(
              option.landDemand ??
                  'The land estimate is not available for this option.',
            ),
            if (option.keyStrength != null) ...[
              const SizedBox(height: 8),
              Text('Key strength: ${option.keyStrength}'),
            ],
            if (option.keyLimitation != null) ...[
              const SizedBox(height: 6),
              Text('Key limitation: ${option.keyLimitation}'),
            ],
            const SizedBox(height: 6),
            Text(
              _suitableRoleSentence(option),
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 6),
            const Text(
              'Confirm water-quality, flow, land, and site inputs before design.',
            ),
            if (option.warnings.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                option.warnings.first,
                style: Theme.of(
                  context,
                ).textTheme.bodySmall?.copyWith(color: NbsColors.mutedGrey),
              ),
            ],
          ],
        ),
      );
}

class _PreviousScenarioRow extends StatelessWidget {
  const _PreviousScenarioRow({required this.index, required this.response});

  final int index;
  final RecommendationResponse response;

  @override
  Widget build(BuildContext context) {
    final train =
        response.rankedTrains.isEmpty ? null : response.rankedTrains.first;
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: const Icon(Icons.history),
      title: Text(
        'Previous case ${index + 1}: ${train?.name ?? 'No ranked option'}',
      ),
      subtitle: Text(
        '${_workflowLabelForUser(response.inputSummary.workflowMode)} | ${response.designReadiness.shortLabel} | ${train?.matchPercent ?? 'No match score'}',
      ),
    );
  }
}

class _LearnWorkspace extends StatelessWidget {
  const _LearnWorkspace({
    required this.response,
    required this.bundle,
    required this.train,
  });

  final RecommendationResponse response;
  final RecommendationAssemblyBundle? bundle;
  final TrainRecommendation? train;

  @override
  Widget build(BuildContext context) {
    final diagram = diagramForTrainName(train?.name);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _DetailSection(
          title: 'Learn more',
          child: Text(
            'Open diagrams, treatment-train explanations, and evidence only when you need them. The full searchable catalogue remains available from the dashboard.',
          ),
        ),
        if (diagram != null) ...[
          const SizedBox(height: 14),
          NbsDiagramCard(kind: diagram),
        ],
        if (train != null) ...[
          const SizedBox(height: 14),
          _DetailSection(
            title: 'How the recommended train works',
            child: _LearningPlaceholder(
              train: train!,
              citations: response.citations,
            ),
          ),
        ],
        const SizedBox(height: 14),
        _EvidenceWorkspace(response: response, bundle: bundle, train: train),
      ],
    );
  }
}

String _landFitSentence(String value) => switch (value) {
      'fits' =>
        'The available land appears enough for this early sizing estimate.',
      'borderline' =>
        'The available land may be enough, but layout and site checks could change the result.',
      'likely_too_little_land' =>
        'The available land appears smaller than the complete screening range.',
      _ =>
        'The toolkit cannot confirm land fit with the current inputs and evidence coverage.',
    };

String _landFitShort(String value) => switch (value) {
      'fits' => 'Likely fits',
      'borderline' => 'Borderline',
      'likely_too_little_land' => 'Likely too little',
      _ => 'Needs data',
    };

List<String> _sizingEstimateLines(SizingEstimate estimate) {
  if (estimate.estimatedAreaLowM2 != null ||
      estimate.estimatedAreaHighM2 != null) {
    return [estimate.estimateLabel];
  }
  if (estimate.areaPerPersonBand != null &&
      estimate.areaPerPersonBand!.trim().isNotEmpty) {
    return [
      'Stored screening footprint: ${estimate.areaPerPersonBand}.',
      'Area estimate not calculated because population/PE was not supplied.',
    ];
  }
  if (estimate.missingInputs.isNotEmpty) {
    return ['Area estimate not calculated.'];
  }
  return [estimate.estimateLabel];
}

String _optionalPercent(double? value) =>
    value == null ? 'Not available' : '${(value * 100).toStringAsFixed(1)}%';

String _comparisonConfidence(ComparisonOption option) {
  if (option.confidenceLabel == 'not_assessed' ||
      option.resultConfidence == null ||
      option.resultConfidence! <= 0) {
    return 'Not assessed';
  }
  return _optionalPercent(option.resultConfidence);
}

String _suitableRoleSentence(ComparisonOption option) {
  final text = option.whenToChoose.trim();
  if (text.toLowerCase().startsWith('suitable role:')) {
    return text;
  }
  return 'Suitable role: ${text.isEmpty ? 'Primary-to-polishing treatment train.' : text}';
}

String _workflowLabelForUser(String? mode) => switch (mode) {
      'uploaded_water_quality' => 'Uploaded water-quality data',
      'manual_measured_water_quality' => 'Measured water-quality values',
      'site_context_only' => 'Site context only',
      'pollution_source_screening' => 'Pollution-source screening',
      _ => 'Available inputs',
    };

// Retained for compatibility with older detail layouts.
// ignore: unused_element
class _DataBasisCard extends StatelessWidget {
  const _DataBasisCard({required this.dataBasis, required this.readiness});

  final ({
    String basis,
    String currentSample,
    String confidenceBasis
  }) dataBasis;
  final ({String label, String reason}) readiness;

  @override
  Widget build(BuildContext context) => Container(
        width: double.infinity,
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: NbsColors.researchBlue.withValues(alpha: 0.05),
          borderRadius: BorderRadius.circular(8),
          border:
              Border.all(color: NbsColors.researchBlue.withValues(alpha: 0.18)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Data basis',
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 9,
              runSpacing: 9,
              children: [
                StatusPill(
                  label: 'Data basis',
                  value: dataBasis.basis,
                  color: NbsColors.researchBlue,
                ),
                StatusPill(
                  label: 'Water-quality input',
                  value: dataBasis.currentSample,
                  color: NbsColors.riverTeal,
                ),
                StatusPill(
                  label: 'Design readiness',
                  value: readiness.label,
                  color: NbsColors.warningAmber,
                ),
                StatusPill(
                  label: 'Why this confidence level',
                  value: dataBasis.confidenceBasis,
                  color: NbsColors.wetlandGreen,
                ),
              ],
            ),
          ],
        ),
      );
}

// Retained for compatibility with older detail layouts.
// ignore: unused_element
class _SiteContextSummaryCard extends StatelessWidget {
  const _SiteContextSummaryCard({required this.location});

  final LocationContext location;

  @override
  Widget build(BuildContext context) {
    final offChannel = location.contextFlags['off_channel_required'] == true;
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(
                Icons.location_on_outlined,
                color: NbsColors.riverTeal,
              ),
              const SizedBox(width: 9),
              Expanded(
                child: Text(
                  'Site context',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w900,
                      ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 9),
          Text(
            location.station ??
                location.district ??
                'No site or station selected',
            style: const TextStyle(fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 6),
          Text(
            offChannel
                ? 'Off-channel treatment only. Do not build treatment cells inside the river channel.'
                : 'Site context helps prevent unsafe placement and guides the next field checks.',
          ),
          if (location.contextFlags['site_context_incomplete'] == true) ...[
            const SizedBox(height: 7),
            Text(
              'Where site data is missing, the result remains planning-level.',
              style: Theme.of(
                context,
              ).textTheme.bodySmall?.copyWith(color: NbsColors.mutedGrey),
            ),
          ],
        ],
      ),
    );
  }
}

// Retained for compatibility with older detail layouts.
// ignore: unused_element
class _DesignReadinessSummaryCard extends StatelessWidget {
  const _DesignReadinessSummaryCard({required this.readiness});

  final DesignReadiness readiness;

  @override
  Widget build(BuildContext context) {
    final color = readiness.expertReviewRequired
        ? NbsColors.warningAmber
        : NbsColors.researchBlue;
    return AppCard(
      borderColor: color.withValues(alpha: 0.35),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.engineering_outlined, color: color),
              const SizedBox(width: 9),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Design readiness',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w900,
                          ),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      readiness.shortLabel,
                      style: TextStyle(
                        color: color,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(readiness.explanation),
          if (readiness.requiredNextSteps.isNotEmpty) ...[
            const SizedBox(height: 6),
            ExpansionTile(
              tilePadding: EdgeInsets.zero,
              childrenPadding: const EdgeInsets.only(bottom: 6),
              title: const Text(
                'What to do next',
                style: TextStyle(fontWeight: FontWeight.w800),
              ),
              children: [
                _ReadableBulletList(values: readiness.requiredNextSteps),
              ],
            ),
          ],
        ],
      ),
    );
  }
}

class _LocationWorkspace extends StatelessWidget {
  const _LocationWorkspace({required this.location});

  final LocationContext location;

  @override
  Widget build(BuildContext context) {
    final factors = <String>[
      if (location.station != null)
        'Selected site/station: ${location.station}',
      if (location.basin != null) 'Basin: ${location.basin}',
      if (location.subBasin != null) 'Sub-basin: ${location.subBasin}',
      if (location.river != null) 'River: ${location.river}',
      if (location.district != null) 'District: ${location.district}',
      if (location.streamOrder != null)
        'Stream order: ${location.streamOrder!.toStringAsFixed(location.streamOrder! % 1 == 0 ? 0 : 1)}',
      if (location.streamContext != null)
        'River context: ${location.streamContext}',
      if (location.interventionPosition != null)
        'Intervention position: ${_titleFromSnake(location.interventionPosition!)}',
      if (location.pollutionSourceType != null)
        'Source context: ${_titleFromSnake(location.pollutionSourceType!)}',
      if (location.pollutionSourceRecordCount != null)
        'Linked pollution-source records: ${location.pollutionSourceRecordCount}',
      if (location.riverDischargeCms != null)
        'River discharge context: ${location.riverDischargeCms} m³/s',
      if (location.drainageAreaKm2 != null)
        'Drainage area: ${location.drainageAreaKm2} km²',
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _DetailSection(
          title: 'Location intelligence',
          child: Text(
            'This context helps prevent unsafe recommendations, such as placing treatment cells inside the main river channel.',
          ),
        ),
        const SizedBox(height: 14),
        LocationContextDiagram(location: location),
        const SizedBox(height: 14),
        _DetailSection(
          title: 'Site factors',
          child: _ReadableBulletList(
            values: factors,
            emptyText: 'No verified site profile is available for this run.',
          ),
        ),
        const SizedBox(height: 14),
        _DetailSection(
          title: 'Safety and source context',
          child: _ReadableBulletList(
            values: location.contextNotes,
            emptyText: 'No additional location safety flag was triggered.',
          ),
        ),
        const SizedBox(height: 14),
        _DetailSection(
          title: 'Missing site information',
          child: _ReadableBulletList(
            values: location.missingSiteInformation,
            emptyText: 'No site-profile gap was identified.',
          ),
        ),
      ],
    );
  }
}

class _DesignReadinessWorkspace extends StatelessWidget {
  const _DesignReadinessWorkspace({required this.readiness});

  final DesignReadiness readiness;

  @override
  Widget build(BuildContext context) {
    final grouped = _groupReadinessInputs(readiness.inputChecklist);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _DetailSection(
          title: 'Design readiness: ${readiness.shortLabel}',
          child: Text(
            readiness.explanation,
            style: Theme.of(
              context,
            ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
          ),
        ),
        const SizedBox(height: 14),
        _DetailSection(
          title: 'Why this level',
          child: _ReadableBulletList(
            values: readiness.reasons,
            emptyText: 'No additional readiness reason is recorded.',
          ),
        ),
        const SizedBox(height: 14),
        _DetailSection(
          title: 'Your input plan',
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _ReadinessGroup(
                title: 'Needed to improve this result',
                guidance: 'Start with these inputs first.',
                items: grouped.improveResult,
              ),
              const SizedBox(height: 14),
              _ReadinessGroup(
                title: 'Needed before engineering design',
                guidance:
                    'These items are usually checked before engineering design.',
                items: grouped.beforeDesign,
              ),
              const SizedBox(height: 14),
              _ReadinessGroup(
                title: 'Field checks',
                guidance: 'These should be verified during a site visit.',
                items: grouped.fieldChecks,
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),
        _DetailSection(
          title: 'Required next steps',
          child: _ReadableBulletList(
            values: readiness.requiredNextSteps,
            emptyText: 'Proceed to normal engineering review.',
          ),
        ),
        if (readiness.expertReviewRequired) ...[
          const SizedBox(height: 14),
          const _AlertBanner.compact(
            icon: Icons.warning_amber_outlined,
            color: NbsColors.warningAmber,
            title: 'Expert review recommended',
            message:
                'Safety, site-risk, or preliminary-design conditions require qualified expert review.',
          ),
        ],
      ],
    );
  }
}

class _ReadinessGroup extends StatelessWidget {
  const _ReadinessGroup({
    required this.title,
    required this.guidance,
    required this.items,
  });

  final String title;
  final String guidance;
  final List<ReadinessInput> items;

  @override
  Widget build(BuildContext context) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontWeight: FontWeight.w900)),
          const SizedBox(height: 3),
          Text(
            guidance,
            style: Theme.of(
              context,
            ).textTheme.bodySmall?.copyWith(color: NbsColors.mutedGrey),
          ),
          const SizedBox(height: 9),
          if (items.isEmpty)
            const Text('No item is currently listed in this group.')
          else
            for (final item in items) _ReadinessChecklistRow(item: item),
        ],
      );
}

class _ReadinessChecklistRow extends StatelessWidget {
  const _ReadinessChecklistRow({required this.item});

  final ReadinessInput item;

  @override
  Widget build(BuildContext context) {
    final (icon, color, label) = switch (item.status) {
      'available' => (
          Icons.check_circle_outline,
          NbsColors.wetlandGreen,
          'Available',
        ),
      'mapped_context_verify' => (
          Icons.travel_explore_outlined,
          NbsColors.warningAmber,
          'Available from mapped context; verify in field',
        ),
      'needs_field_check' => (
          Icons.travel_explore_outlined,
          NbsColors.warningAmber,
          'Needs field check',
        ),
      'not_supplied' => (
          Icons.radio_button_unchecked,
          NbsColors.mutedGrey,
          'Not supplied',
        ),
      'missing_before_engineering_design' => (
          Icons.error_outline,
          NbsColors.warningAmber,
          'Missing before engineering design',
        ),
      'not_required_for_current_screening' => (
          Icons.remove_circle_outline,
          NbsColors.mutedGrey,
          'Not required for current screening',
        ),
      _ => (Icons.radio_button_unchecked, NbsColors.mutedGrey, 'Missing'),
    };
    return Padding(
      padding: const EdgeInsets.only(bottom: 9),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 19, color: color),
          const SizedBox(width: 9),
          Expanded(
            child: Text(
              item.label,
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
          ),
          const SizedBox(width: 8),
          Flexible(
            child: Text(
              label,
              textAlign: TextAlign.end,
              style: TextStyle(color: color, fontWeight: FontWeight.w700),
            ),
          ),
        ],
      ),
    );
  }
}

class _DataUsedPanel extends StatelessWidget {
  const _DataUsedPanel({required this.response});

  final RecommendationResponse response;

  @override
  Widget build(BuildContext context) {
    final inputSummary = response.inputSummary;
    final rows = response.parameterCoverage;
    final sourceLabel = switch (inputSummary.workflowMode) {
      'uploaded_water_quality' => 'Uploaded file',
      'manual_measured_water_quality' => 'Manual user input',
      'site_context_only' => 'Station and site context',
      'pollution_source_screening' => 'Pollution-source and site context',
      _ => 'Available recommendation input',
    };
    return _DetailSection(
      title:
          rows.isEmpty ? 'Data used in screening' : 'Water-quality values used',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Source: $sourceLabel',
            style: const TextStyle(fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              StatusPill(
                label: 'Selected target use case',
                value: _targetUseCaseLabel(response.useCase),
                color: NbsColors.researchBlue,
              ),
              StatusPill(
                label: 'Pollution source',
                value: _pollutionSourceLabel(
                  inputSummary.context['pollution_source_type']?.toString(),
                ),
                color: NbsColors.riverTeal,
              ),
            ],
          ),
          const SizedBox(height: 8),
          if (rows.isEmpty)
            const Text(
              'No recent water-quality file was supplied. Station and site context supports early screening where available.',
            )
          else if (rows.length > 4)
            ExpansionTile(
              tilePadding: EdgeInsets.zero,
              childrenPadding: const EdgeInsets.only(bottom: 8),
              title: Text(
                '${rows.length} water-quality values recognized',
                style: const TextStyle(fontWeight: FontWeight.w800),
              ),
              subtitle: const Text('View values'),
              children: [_ParameterCoverageRows(rows: rows)],
            )
          else
            _ParameterCoverageRows(rows: rows),
          const SizedBox(height: 10),
          Text(
            'The toolkit reads all recognized values. Some values influence the score directly, while others are shown as supporting context until enough target and treatment evidence is available.',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: NbsColors.mutedGrey,
                ),
          ),
          if (inputSummary.workflowMode == 'uploaded_water_quality' &&
              rows.isNotEmpty) ...[
            const SizedBox(height: 10),
            Text(
              'Uploaded values feed pollutant-gap calculations. Similar scores can still occur when different files produce the same standards gap, evidence coverage, and applicability context.',
              style: Theme.of(
                context,
              ).textTheme.bodySmall?.copyWith(color: NbsColors.mutedGrey),
            ),
          ],
        ],
      ),
    );
  }
}

class _PollutantGapPanel extends StatelessWidget {
  const _PollutantGapPanel({
    required this.train,
    required this.selectedUseCase,
  });

  final TrainRecommendation? train;
  final String? selectedUseCase;

  @override
  Widget build(BuildContext context) {
    final rows = train?.pollutantGapBreakdown ?? const <Map<String, dynamic>>[];
    return _DetailSection(
      title: 'Pollutant gaps and train coverage',
      child: rows.isEmpty
          ? const Text(
              'No usable water-quality values were available for target comparison.',
            )
          : Column(
              children: [
                for (final row in rows)
                  Container(
                    width: double.infinity,
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: NbsColors.researchBlue.withValues(alpha: 0.035),
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: NbsColors.cardBorder),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${_displayParameter(row['parameter']?.toString())}: ${row['observed_value'] ?? 'unknown'}${_displayUnitSuffix(row['unit'])}',
                          style: const TextStyle(fontWeight: FontWeight.w800),
                        ),
                        const SizedBox(height: 6),
                        Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: [
                            StatusPill(
                              label: 'Selected target use case',
                              value: _targetUseCaseLabel(selectedUseCase),
                              color: NbsColors.researchBlue,
                            ),
                            StatusPill(
                              label: 'Target status',
                              value: _gapStatusLabel(
                                row['gap_status']?.toString(),
                              ),
                              color: row['gap_status'] == 'exceeds_target'
                                  ? NbsColors.warningAmber
                                  : NbsColors.wetlandGreen,
                            ),
                            StatusPill(
                              label: 'Target limit',
                              value: _targetThresholdLabel(
                                row['target_threshold'],
                                parameter: row['parameter']?.toString(),
                              ),
                            ),
                            StatusPill(
                              label: 'Input source',
                              value: _displayInputSource(
                                row['source']?.toString(),
                              ),
                            ),
                            StatusPill(
                              label: 'Scoring role',
                              value: _coverageLabel(
                                row['coverage_category']?.toString(),
                              ),
                              color:
                                  row['coverage_category'] == 'used_in_scoring'
                                      ? NbsColors.wetlandGreen
                                      : NbsColors.warningAmber,
                            ),
                            StatusPill(
                              label: 'Treatment evidence',
                              value: row['train_addresses_parameter'] == true
                                  ? 'Evidence supports treatment'
                                  : 'Limited treatment evidence',
                              color: row['train_addresses_parameter'] == true
                                  ? NbsColors.wetlandGreen
                                  : NbsColors.warningAmber,
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        if (row['train_addresses_parameter'] != true) ...[
                          const Text(
                            'Current evidence is limited for this parameter.',
                          ),
                          const SizedBox(height: 6),
                        ],
                        Text(_targetGapMessage(row, fallback: row['severity'])),
                      ],
                    ),
                  ),
              ],
            ),
    );
  }
}

class _ImplementationWorkspace extends StatelessWidget {
  const _ImplementationWorkspace({
    required this.response,
    required this.train,
    required this.sourceLocationGuidance,
  });

  final RecommendationResponse response;
  final TrainRecommendation? train;
  final List<String> sourceLocationGuidance;

  @override
  Widget build(BuildContext context) {
    final selectedTrain = train;
    if (selectedTrain == null) {
      return const Text(
        'No treatment train is available for implementation planning.',
      );
    }
    final highOrder = response.inputSummary.context['intervention_position'] ==
            'in_channel' ||
        ((response.inputSummary.context['stream_order'] as num?)?.toDouble() ??
                0) >=
            5;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _DetailSection(
          title: 'What to do first',
          child: _ReadableBulletList(
            values: sourceLocationGuidance,
            emptyText: _implementationSteps(response, selectedTrain).first,
          ),
        ),
        const SizedBox(height: 14),
        _DetailSection(
          title: 'What not to do',
          child: _ReadableBulletList(
            values: _whatNotToDo(response, selectedTrain),
          ),
        ),
        const SizedBox(height: 14),
        _DetailSection(
          title: 'Implementation pathway',
          child: _ImplementationPathway(
            response: response,
            train: selectedTrain,
          ),
        ),
        const SizedBox(height: 14),
        _DetailSection(
          title: 'Recommended treatment sequence',
          child: _TreatmentSequenceVisual(
            response: response,
            train: selectedTrain,
          ),
        ),
        const SizedBox(height: 14),
        if (highOrder) ...[
          const _DetailSection(
            title: 'Mainstem safety schematic',
            child: NbsDiagramCard(kind: NbsDiagramKind.mainstemOffChannel),
          ),
          const SizedBox(height: 14),
        ],
        _DetailSection(
          title: 'Monitoring points',
          child: _ReadableBulletList(values: _monitoringPoints(selectedTrain)),
        ),
      ],
    );
  }
}

// Retained for compatibility with older detail layouts.
// ignore: unused_element
class _ComponentSummary extends StatelessWidget {
  const _ComponentSummary({required this.train, required this.components});

  final TrainRecommendation? train;
  final List<IndividualNbsRecommendation> components;

  @override
  Widget build(BuildContext context) {
    final supporting = components.take(3).toList();
    final limited = components
        .where((item) => item.standaloneSuitability == 'only_as_part_of_train')
        .take(3)
        .toList();
    return _DetailSection(
      title: 'Train and supporting components',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Primary treatment train: ${train?.name ?? 'Not available'}',
            style: const TextStyle(fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 8),
          _ReadableBulletList(
            values: [
              for (final item in supporting)
                '${item.name} - ${_titleFromSnake(item.role)}',
            ],
            emptyText: 'No supporting component screen is available.',
          ),
          if (limited.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              'Not suitable alone: ${limited.map((item) => item.name).join(', ')}.',
              style: Theme.of(
                context,
              ).textTheme.bodySmall?.copyWith(color: NbsColors.mutedGrey),
            ),
          ],
        ],
      ),
    );
  }
}

class _NbsComponentsWorkspace extends StatelessWidget {
  const _NbsComponentsWorkspace({
    required this.train,
    required this.components,
    required this.filteredComponents,
    required this.citationsById,
  });

  final TrainRecommendation? train;
  final List<IndividualNbsRecommendation> components;
  final List<Map<String, dynamic>> filteredComponents;
  final Map<int, Citation> citationsById;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _DetailSection(
          title: 'How to read this section',
          child: Text(
            'The primary recommendation is the treatment train ${train?.name ?? ''}. Individual NbS options below are supporting components and do not replace that train.',
          ),
        ),
        const SizedBox(height: 14),
        if (components.isEmpty)
          const Text(
            'No individual NbS component passed the current screening.',
          )
        else
          for (final component in components.take(10))
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: _IndividualNbsCard(
                component: component,
                citationsById: citationsById,
              ),
            ),
        if (filteredComponents.isNotEmpty) ...[
          const SizedBox(height: 4),
          _DetailSection(
            title: 'Filtered out by applicability screening',
            child: _ReadableBulletList(
              values: [
                for (final row in filteredComponents.take(10))
                  '${row['name'] ?? 'Component'}: ${((row['reasons'] as List?) ?? const [
                        'Not suitable for this context.'
                      ]).join(' ')}',
              ],
            ),
          ),
        ],
        if (train != null) ...[
          const SizedBox(height: 14),
          _DetailSection(
            title: 'Treatment-train learning',
            child: _LearningPlaceholder(
              train: train!,
              citations: citationsById.values.toList(),
            ),
          ),
        ],
      ],
    );
  }
}

class _IndividualNbsCard extends StatelessWidget {
  const _IndividualNbsCard({
    required this.component,
    required this.citationsById,
  });

  final IndividualNbsRecommendation component;
  final Map<int, Citation> citationsById;

  @override
  Widget build(BuildContext context) {
    final diagram = diagramForComponentName(component.name);
    return AppCard(
      padding: EdgeInsets.zero,
      child: ExpansionTile(
        tilePadding: const EdgeInsets.all(14),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        expandedCrossAxisAlignment: CrossAxisAlignment.start,
        title: Text(
          component.name,
          style: const TextStyle(fontWeight: FontWeight.w900),
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 8),
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _MetricChip(
                label: 'Role',
                value: _titleFromSnake(component.role),
                color: NbsColors.riverTeal,
              ),
              _MetricChip(
                label: 'Component suitability',
                value: component.suitabilityScore == null
                    ? 'Context screened'
                    : component.suitabilityPercent,
                color: NbsColors.researchBlue,
              ),
              _MetricChip(
                label: 'Standalone use',
                value: _titleFromSnake(component.standaloneSuitability),
                color: NbsColors.warningAmber,
              ),
            ],
          ),
        ),
        children: [
          _AlertBanner.compact(
            icon: Icons.account_tree_outlined,
            color: NbsColors.warningAmber,
            title: 'Treatment-train boundary',
            message: component.standaloneGuidance,
          ),
          const SizedBox(height: 12),
          if (diagram != null) ...[
            NbsDiagramCard(kind: diagram),
            const SizedBox(height: 12),
          ],
          _TextBlockList(
            title: 'Pollutants addressed by sourced records',
            values: [
              for (final value in component.pollutantsAddressed)
                _displayParameter(value),
            ],
            emptyText: 'No pollutant-specific removal record is available.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Where suitable',
            values: component.whereSuitable,
            emptyText: 'Site suitability requires local validation.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Where not suitable',
            values: component.whereNotSuitable,
            emptyText: 'No extra exclusion is recorded for this case.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Key constraints',
            values: component.keyConstraints,
            emptyText:
                'No extra component-specific constraint is recorded. Confirm site suitability before use.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Plant links',
            values: [
              for (final plant in component.plants)
                plant['plant_species']?.toString() ?? 'Catalogue plant',
            ],
            emptyText: component.plantingGuidance,
          ),
          const SizedBox(height: 12),
          _EvidenceDisclosure(
            sourceIds: component.sourceIds,
            citationsById: citationsById,
          ),
        ],
      ),
    );
  }
}

// Retained for compatibility with older detail layouts.
// ignore: unused_element
class _DataGapsWorkspace extends StatelessWidget {
  const _DataGapsWorkspace({required this.response, required this.groupedData});

  final RecommendationResponse response;
  final Map<String, List<String>> groupedData;

  @override
  Widget build(BuildContext context) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (response.inputSummary.isContextOnly) ...[
            const _AlertBanner.compact(
              icon: Icons.info_outline,
              color: NbsColors.warningAmber,
              title: 'Water-quality input',
              message:
                  'You have not uploaded recent water-quality data for this site. The result uses available site and source context and remains an early screening result.',
            ),
            const SizedBox(height: 14),
          ],
          _DetailSection(
            title: 'Required before design',
            child: _ReadableBulletList(
              values: groupedData['required'] ?? const [],
              emptyText:
                  'No mandatory design input was identified from this payload.',
            ),
          ),
          const SizedBox(height: 14),
          _DetailSection(
            title: 'Useful for better ranking',
            child: _ReadableBulletList(
              values: groupedData['ranking'] ?? const [],
              emptyText: 'No additional ranking input was identified.',
            ),
          ),
          const SizedBox(height: 14),
          _DetailSection(
            title: 'Site / design checks',
            child: _ReadableBulletList(
              values: groupedData['site'] ?? const [],
              emptyText:
                  'Complete normal site survey and preliminary design checks.',
            ),
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
        ],
      );
}

class _EvidenceWorkspace extends StatelessWidget {
  const _EvidenceWorkspace({
    required this.response,
    required this.bundle,
    required this.train,
  });

  final RecommendationResponse response;
  final RecommendationAssemblyBundle? bundle;
  final TrainRecommendation? train;

  @override
  Widget build(BuildContext context) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _DetailSection(
            title: 'Method',
            child: _ReadableBulletList(
              values: [
                'The site-safety check screens placement and safety constraints before ranking.',
                'Target-use-case selection determines standards and AHP-Fuzzy AHP weight set.',
                'After the user selects a target use case, the app applies safety/applicability screening, uses the matching final v1 AHP-Fuzzy AHP ensemble weight set, and ranks treatment trains with TOPSIS.',
                'Confidence uses ${_confidenceMethodLabel(response, bundle).toLowerCase()} and is reported separately from rank.',
                'C5 health-risk and field validation remain future work.',
              ],
            ),
          ),
          const SizedBox(height: 14),
          _DetailSection(
            title: 'Scientific criteria values',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _TextBlockList(
                  title: 'Top-train criteria',
                  values: [
                    for (final item in train?.criteriaBreakdown ??
                        const <Map<String, dynamic>>[])
                      '${_criterionMapLabel(item)}: ${item['data_status'] == 'known' ? ((item['normalized_value'] as num?)?.toDouble() ?? 0).toStringAsFixed(3) : 'Evidence gap'}',
                  ],
                  emptyText: 'No criteria values are available.',
                ),
                const SizedBox(height: 8),
                const Text(
                  'Values are normalized/scored criteria used by TOPSIS; they are not the final weights.',
                ),
                const SizedBox(height: 4),
                const Text(
                  'Weights come from final v1 AHP-Fuzzy AHP ensemble weights.',
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          _DetailSection(
            title: 'Evidence sources',
            child: _EvidenceDisclosure(
              sourceIds: train?.sourceIds ?? const [],
              citationsById: response.citationsById,
              initiallyExpanded: true,
            ),
          ),
          const SizedBox(height: 14),
          const _DetailSection(
            title: 'Decision-support boundary',
            child: _ReadableBulletList(
              values: [
                'This tool supports decision-making and option screening.',
                'It does not replace expert engineering design, site survey, regulatory approval, or monitoring plans.',
                'Health-risk classification requires separate expert data and validation.',
              ],
            ),
          ),
        ],
      );
}

class _ReportExportPanel extends StatelessWidget {
  const _ReportExportPanel({required this.response});

  final RecommendationResponse response;

  Future<void> _copy(BuildContext context, String text, String message) async {
    await Clipboard.setData(ClipboardData(text: text));
    if (context.mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(message)));
    }
  }

  Future<void> _export(
    BuildContext context, {
    required String fileName,
    required String content,
    required String mimeType,
    required String label,
  }) async {
    final downloaded = downloadReportText(fileName, content, mimeType);
    if (!downloaded) {
      await _copy(
        context,
        content,
        '$label prepared and copied to the clipboard.',
      );
    } else if (context.mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('$label downloaded.')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final report = RecommendationReport.fromResponse(response);
    return _DetailSection(
      title: 'Report and export',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Review, copy, or download this planning-level result.'),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              OutlinedButton.icon(
                onPressed: () => _showReportPreview(context, response, report),
                icon: const Icon(Icons.preview_outlined),
                label: const Text('Report preview'),
              ),
              OutlinedButton.icon(
                onPressed: () => _copy(
                  context,
                  report.summary,
                  'Recommendation summary copied.',
                ),
                icon: const Icon(Icons.copy_outlined),
                label: const Text('Copy summary'),
              ),
              OutlinedButton.icon(
                onPressed: () => _export(
                  context,
                  fileName: '${report.baseFileName}.json',
                  content: report.json,
                  mimeType: 'application/json;charset=utf-8',
                  label: 'JSON report',
                ),
                icon: const Icon(Icons.data_object_outlined),
                label: const Text('Export JSON'),
              ),
              OutlinedButton.icon(
                onPressed: () => _export(
                  context,
                  fileName: '${report.baseFileName}.csv',
                  content: report.csv,
                  mimeType: 'text/csv;charset=utf-8',
                  label: 'CSV report',
                ),
                icon: const Icon(Icons.table_view_outlined),
                label: const Text('Export CSV'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

Future<void> _showReportPreview(
  BuildContext context,
  RecommendationResponse response,
  RecommendationReport report,
) async {
  await showDialog<void>(
    context: context,
    builder: (dialogContext) => Dialog(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 780, maxHeight: 760),
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 16, 12, 10),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      'Planning-level report preview',
                      style: Theme.of(dialogContext)
                          .textTheme
                          .titleLarge
                          ?.copyWith(fontWeight: FontWeight.w900),
                    ),
                  ),
                  IconButton(
                    tooltip: 'Close report preview',
                    onPressed: () => Navigator.of(dialogContext).pop(),
                    icon: const Icon(Icons.close),
                  ),
                ],
              ),
            ),
            const Divider(height: 1),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(20),
                child: _ReportPreview(response: response, report: report),
              ),
            ),
            const Divider(height: 1),
            Padding(
              padding: const EdgeInsets.all(12),
              child: Wrap(
                alignment: WrapAlignment.end,
                spacing: 8,
                runSpacing: 8,
                children: [
                  TextButton.icon(
                    onPressed: () {
                      final opened = printReportPage(report.printHtml);
                      ScaffoldMessenger.of(dialogContext).showSnackBar(
                        SnackBar(
                          content: Text(
                            opened
                                ? 'Use the browser print dialog to save as PDF.'
                                : 'Browser print is available in the web app.',
                          ),
                        ),
                      );
                    },
                    icon: const Icon(Icons.print_outlined),
                    label: const Text('Print / save as PDF'),
                  ),
                  FilledButton(
                    onPressed: () => Navigator.of(dialogContext).pop(),
                    child: const Text('Done'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    ),
  );
}

class _ReportPreview extends StatelessWidget {
  const _ReportPreview({required this.response, required this.report});

  final RecommendationResponse response;
  final RecommendationReport report;

  @override
  Widget build(BuildContext context) {
    final train =
        response.rankedTrains.isEmpty ? null : response.rankedTrains.first;
    final values = response.inputSummary.dataUsed;
    final readinessGroups = _groupReadinessInputs(
      response.designReadiness.inputChecklist,
    );
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Narmada NbS recommendation',
          style: Theme.of(
            context,
          ).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w900),
        ),
        const SizedBox(height: 4),
        const Text(
          'Method: Final v1 AHP-Fuzzy AHP weighted TOPSIS. Target-use-case selection determines standards and AHP-Fuzzy AHP weight set.',
        ),
        const SizedBox(height: 16),
        _TextBlockList(
          title: 'Project and input summary',
          values: [
            'Workflow: ${_titleFromSnake(response.inputSummary.workflowMode ?? 'available inputs')}',
            'Selected target use case: ${_targetUseCaseLabel(response.useCase)}',
            'Pollution source: ${_pollutionSourceLabel(response.inputSummary.context['pollution_source_type']?.toString())}',
            'Target use case controls standards and final v1 AHP-Fuzzy AHP weight set.',
            values.isEmpty
                ? 'No recent water-quality values were supplied.'
                : '${values.length} recent water-quality values informed this result.',
          ],
          emptyText: 'No project input summary is available.',
        ),
        const SizedBox(height: 14),
        _TextBlockList(
          title: 'Site context',
          values: [
            if (response.locationContext.station != null)
              'Site/station: ${response.locationContext.station}',
            if (response.locationContext.district != null)
              'District: ${response.locationContext.district}',
            if (response.locationContext.streamContext != null)
              'River context: ${response.locationContext.streamContext}',
            response.locationContext.coordinatesAvailable
                ? 'Map status: verified stored location.'
                : response.locationContext.station != null ||
                        response.locationContext.district != null ||
                        response.locationContext.river != null
                    ? 'Map status: schematic context only, not a surveyed map.'
                    : 'No verified map location is available for this case.',
            ...response.locationContext.contextNotes,
          ],
          emptyText: 'No verified site profile is available for this run.',
        ),
        const SizedBox(height: 14),
        _TextBlockList(
          title: 'Design readiness',
          values: [
            response.designReadiness.shortLabel,
            response.designReadiness.explanation,
            ...response.designReadiness.reasons,
            ...response.designReadiness.requiredNextSteps,
          ],
          emptyText: 'Design-readiness information is unavailable.',
        ),
        const SizedBox(height: 10),
        _TextBlockList(
          title: 'Needed to improve this result',
          values: [
            for (final item in readinessGroups.improveResult)
              '${item.label}: ${_readinessStatusLabel(item.status)}',
          ],
          emptyText: 'No additional input is listed for this group.',
        ),
        const SizedBox(height: 10),
        _TextBlockList(
          title: 'Needed before engineering design',
          values: [
            for (final item in readinessGroups.beforeDesign)
              '${item.label}: ${_readinessStatusLabel(item.status)}',
          ],
          emptyText: 'No additional input is listed for this group.',
        ),
        const SizedBox(height: 10),
        _TextBlockList(
          title: 'Field checks',
          values: [
            for (final item in readinessGroups.fieldChecks)
              '${item.label}: ${_readinessStatusLabel(item.status)}',
          ],
          emptyText: 'No field check is currently listed.',
        ),
        const SizedBox(height: 14),
        _TextBlockList(
          title: 'Recommended treatment train',
          values: train == null
              ? const ['No ranked treatment train is available.']
              : [
                  train.name,
                  'Screening match: ${train.matchPercent}',
                  'Result confidence: ${_trainConfidenceDisplay(train)}',
                  if (train.implementationRole != null)
                    'Role: ${train.implementationRole}',
                ],
          emptyText: 'No ranked treatment train is available.',
        ),
        const SizedBox(height: 14),
        _TextBlockList(
          title: 'Sizing and land',
          values: response.sizingEstimates.isEmpty
              ? const []
              : [
                  'Estimated land need: ${response.sizingEstimates.first.estimateLabel}',
                  _landFitSentence(response.sizingEstimates.first.landFit),
                  response.sizingEstimates.first.designCaution,
                  if (response.sizingEstimates.first.missingInputs.isNotEmpty)
                    'Information to collect next: ${response.sizingEstimates.first.missingInputs.join('; ')}',
                ],
          emptyText:
              'The current inputs and stored evidence are not enough for a bounded land estimate.',
        ),
        const SizedBox(height: 14),
        _TextBlockList(
          title: 'Scenario comparison',
          values: [
            for (final takeaway in response.scenarioComparison.takeaways)
              '${takeaway.label}: ${takeaway.explanation}',
            if (response.scenarioComparison.takeaways.isEmpty)
              ...response.scenarioComparison.limitations,
          ],
          emptyText:
              'No alternative comparison is available for this recommendation.',
        ),
        const SizedBox(height: 14),
        _TextBlockList(
          title: 'Water-quality values used',
          values: [
            for (final row in values)
              '${_displayParameter(row['parameter']?.toString(), fallback: row['display_name']?.toString())}: ${row['value']}${_displayUnitSuffix(row['unit'])}',
          ],
          emptyText: 'No recent water-quality values were supplied.',
        ),
        const SizedBox(height: 14),
        _TextBlockList(
          title: 'Pollutant gaps',
          values: [
            for (final row in train?.pollutantGapBreakdown ??
                const <Map<String, dynamic>>[])
              '${_displayParameter(row['parameter']?.toString())}: ${_gapStatusLabel(row['gap_status']?.toString())}',
          ],
          emptyText: 'No pollutant-gap comparison is available.',
        ),
        const SizedBox(height: 14),
        _TextBlockList(
          title: 'Individual NbS components',
          values: [
            for (final item in response.componentRecommendations)
              '${item.name} - ${_titleFromSnake(item.role)}',
          ],
          emptyText: 'No supporting component passed the current screen.',
        ),
        const SizedBox(height: 14),
        _TextBlockList(
          title: 'Selected-use-case suitability',
          values: [
            if (train != null)
              '${_targetUseCaseLabel(response.useCase)}: ${_suitabilityLabel(train.useCaseVerdicts[response.useCase] ?? 'unknown', contextOnly: response.inputSummary.isContextOnly, hasMeasuredData: response.inputSummary.observationCount > 0)}',
          ],
          emptyText: 'Use-case suitability could not be concluded.',
        ),
        const SizedBox(height: 10),
        _TextBlockList(
          title: 'Other use-case notes',
          values: [
            for (final entry in train?.useCaseVerdicts.entries ??
                const <MapEntry<String, String>>[])
              if (entry.key != response.useCase)
                '${_targetUseCaseLabel(entry.key)}: ${_titleFromSnake(entry.value)}',
          ],
          emptyText: 'No other use-case notes are available.',
        ),
        const SizedBox(height: 14),
        _TextBlockList(
          title: 'Important limitations',
          values: train?.caveats ?? const [],
          emptyText: 'No additional train-specific limitation is recorded.',
        ),
        const SizedBox(height: 14),
        _TextBlockList(
          title: 'Data gaps',
          values: _uniqueStrings([...response.globalGaps, ...?train?.dataGaps]),
          emptyText: 'No data gaps were reported.',
        ),
        const SizedBox(height: 14),
        _TextBlockList(
          title: 'Evidence records',
          values: [
            for (final citation in response.citations)
              '${citation.id}: ${citation.display}',
          ],
          emptyText: 'No resolved evidence record is available.',
        ),
        const SizedBox(height: 16),
        Text(
          report.payload['disclaimer'].toString(),
          style: Theme.of(
            context,
          ).textTheme.bodySmall?.copyWith(fontWeight: FontWeight.w700),
        ),
      ],
    );
  }
}

class TrainRecommendationCard extends StatelessWidget {
  const TrainRecommendationCard({
    super.key,
    required this.train,
    required this.contextOnly,
    required this.hasMeasuredData,
    required this.citationsById,
    required this.selectedUseCase,
  });

  final TrainRecommendation train;
  final bool contextOnly;
  final bool hasMeasuredData;
  final Map<int, Citation> citationsById;
  final String? selectedUseCase;

  @override
  Widget build(BuildContext context) {
    final verdictColors = {
      'pass': NbsColors.wetlandGreen,
      'marginal': NbsColors.warningAmber,
      'fail': Colors.red.shade700,
      'unknown': NbsColors.mutedGrey,
    };
    final selectedVerdict = train.useCaseVerdicts[selectedUseCase] ?? 'unknown';
    final otherUseCaseNotes = train.useCaseVerdicts.entries
        .where((entry) => entry.key != selectedUseCase)
        .map(
          (entry) =>
              '${_targetUseCaseLabel(entry.key)}: ${_suitabilityLabel(entry.value, contextOnly: contextOnly, hasMeasuredData: hasMeasuredData)}',
        )
        .toList();
    return AppCard(
      padding: EdgeInsets.zero,
      borderColor: train.applicabilityStatus == 'conditional'
          ? NbsColors.warningAmber.withValues(alpha: 0.45)
          : NbsColors.researchBlue.withValues(alpha: 0.16),
      child: ExpansionTile(
        tilePadding: const EdgeInsets.all(14),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        expandedCrossAxisAlignment: CrossAxisAlignment.start,
        leading: _RankBlock(rank: train.rank),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              train.name,
              style: const TextStyle(fontWeight: FontWeight.w900),
            ),
            if (train.implementationRole != null) ...[
              const SizedBox(height: 4),
              Text(
                train.implementationRole!,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: NbsColors.riverTeal,
                      fontWeight: FontWeight.w700,
                    ),
              ),
            ],
          ],
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 8),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _MetricChip(
                    label: 'Screening match',
                    value: train.matchPercent,
                    color: NbsColors.researchBlue,
                  ),
                  _MetricChip(
                    label: 'Result confidence',
                    value: _trainConfidenceDisplay(train),
                    color: NbsColors.wetlandGreen,
                  ),
                  if (train.allUseCasesUnknown)
                    const _MetricChip(
                      label: 'Data gap',
                      value: 'Needs data for use-case assessment',
                      color: NbsColors.warningAmber,
                    ),
                  Tooltip(
                    message: selectedVerdict == 'unknown'
                        ? 'The selected target use case cannot be concluded without current water-quality input or sufficient evidence.'
                        : 'Suitability for the selected target use case from available linked evidence.',
                    child: _MetricChip(
                      label: 'Selected-use-case suitability',
                      value: _suitabilityLabel(
                        selectedVerdict,
                        contextOnly: contextOnly,
                        hasMeasuredData: hasMeasuredData,
                      ),
                      color:
                          verdictColors[selectedVerdict] ?? NbsColors.mutedGrey,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                _trainStrength(train),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
        children: [
          if (train.applicabilityStatus == 'conditional')
            const _AlertBanner.compact(
              icon: Icons.warning_amber_outlined,
              color: NbsColors.warningAmber,
              title: 'Conditional recommendation',
              message:
                  'Apply only with the placement, pretreatment, or site checks listed below.',
            ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Why recommended',
            values: [_trainStrength(train)],
            emptyText: 'No additional explanation is recorded.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Key pretreatment / conditions',
            values: _uniqueStrings([
              ...train.pretreatmentRequirements,
              ...train.caveats.take(2),
            ]),
            emptyText: 'No additional train-specific condition is recorded.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Treatment sequence',
            values: [
              for (final step in train.treatmentSequence)
                '${step['step_order']}. ${step['step_label']} (${step['role'] ?? 'step'})',
            ],
            emptyText: 'No treatment sequence is recorded.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Other use-case notes',
            values: otherUseCaseNotes,
            emptyText: 'No other use-case notes are available.',
          ),
          const SizedBox(height: 12),
          _PollutantGapPanel(
            train: train,
            selectedUseCase: selectedUseCase,
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Why this confidence level',
            values: train.confidenceExplanation,
            emptyText: 'No additional confidence explanation is recorded.',
          ),
          const SizedBox(height: 12),
          _EvidenceDisclosure(
            sourceIds: train.sourceIds,
            citationsById: citationsById,
          ),
        ],
      ),
    );
  }
}

class _DataConfidenceGuide extends StatelessWidget {
  const _DataConfidenceGuide({
    required this.train,
    required this.methodLabel,
    required this.dataLimited,
  });

  final TrainRecommendation? train;
  final String methodLabel;
  final bool dataLimited;

  @override
  Widget build(BuildContext context) {
    final fallbackExplanation = dataLimited
        ? 'Data-limited confidence: available source and site context informed this result. Recent measured values would strengthen design-level confirmation.'
        : switch (train?.confidenceLabel) {
            'high' =>
              'Measured data, context, and supporting evidence are substantially available.',
            'medium' =>
              'Partial measured data, context, or supporting evidence are available.',
            _ =>
              'Source/site context only or measured values and evidence are incomplete.',
          };
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: NbsColors.wetlandGreen.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: NbsColors.wetlandGreen.withValues(alpha: 0.18),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.speed_outlined, color: NbsColors.wetlandGreen),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '$methodLabel: ${(train?.confidenceExplanation.isNotEmpty ?? false) ? train!.confidenceExplanation.first : fallbackExplanation}',
                  style: Theme.of(
                    context,
                  ).textTheme.bodySmall?.copyWith(height: 1.4),
                ),
                if ((train?.confidenceExplanation.length ?? 0) > 1) ...[
                  const SizedBox(height: 6),
                  Text(
                    train!.confidenceExplanation.skip(1).join(' '),
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          height: 1.4,
                          color: NbsColors.mutedGrey,
                        ),
                  ),
                ],
                const SizedBox(height: 8),
                const Text(
                  'Screening match = how well the train fits the supplied problem and context.\nResult confidence = how reliable this result is based on data completeness, evidence coverage, and context quality.',
                  style: TextStyle(fontWeight: FontWeight.w700, height: 1.4),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _TopTrainComparison extends StatelessWidget {
  const _TopTrainComparison({required this.trains});

  final List<TrainRecommendation> trains;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth >= 1050
            ? (constraints.maxWidth - 20) / 3
            : constraints.maxWidth >= 680
                ? (constraints.maxWidth - 10) / 2
                : constraints.maxWidth;
        return Wrap(
          spacing: 10,
          runSpacing: 10,
          children: [
            for (final train in trains)
              Container(
                width: width,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: train.rank == 1
                      ? NbsColors.wetlandGreen.withValues(alpha: 0.06)
                      : Colors.white,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: train.rank == 1
                        ? NbsColors.wetlandGreen.withValues(alpha: 0.32)
                        : NbsColors.cardBorder,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '#${train.rank}  ${train.name}',
                      style: const TextStyle(fontWeight: FontWeight.w900),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 7,
                      runSpacing: 7,
                      children: [
                        _MetricChip(
                          label: 'Screening match',
                          value: train.matchPercent,
                          color: NbsColors.researchBlue,
                        ),
                        _MetricChip(
                          label: 'Result confidence',
                          value: _trainConfidenceDisplay(train),
                          color: NbsColors.wetlandGreen,
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Role',
                      style: Theme.of(context).textTheme.labelMedium?.copyWith(
                            fontWeight: FontWeight.w800,
                          ),
                    ),
                    Text(train.implementationRole ?? 'Role requires review'),
                    const SizedBox(height: 8),
                    Text(
                      'Main strength',
                      style: Theme.of(context).textTheme.labelMedium?.copyWith(
                            fontWeight: FontWeight.w800,
                          ),
                    ),
                    Text(_trainStrength(train)),
                    const SizedBox(height: 8),
                    Text(
                      'Main limitation',
                      style: Theme.of(context).textTheme.labelMedium?.copyWith(
                            fontWeight: FontWeight.w800,
                          ),
                    ),
                    Text(_trainLimitation(train)),
                    if (train.allUseCasesUnknown) ...[
                      const SizedBox(height: 8),
                      const Text(
                        'Needs data for use-case assessment',
                        style: TextStyle(
                          color: NbsColors.warningAmber,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
          ],
        );
      },
    );
  }
}

class _ImplementationPathway extends StatelessWidget {
  const _ImplementationPathway({required this.response, required this.train});

  final RecommendationResponse response;
  final TrainRecommendation train;

  @override
  Widget build(BuildContext context) {
    final steps = _implementationSteps(response, train);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (var index = 0; index < steps.length; index++)
          Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 28,
                  height: 28,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    color: NbsColors.riverTeal.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    '${index + 1}',
                    style: const TextStyle(fontWeight: FontWeight.w800),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(child: Text(steps[index])),
              ],
            ),
          ),
      ],
    );
  }
}

class _TreatmentSequenceVisual extends StatelessWidget {
  const _TreatmentSequenceVisual({required this.response, required this.train});

  final RecommendationResponse response;
  final TrainRecommendation train;

  @override
  Widget build(BuildContext context) {
    final labels = _treatmentSequenceLabels(response, train);
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
        for (var index = 0; index < labels.length; index++) ...[
          Chip(
            avatar: Icon(
              index == labels.length - 1
                  ? Icons.monitor_heart_outlined
                  : Icons.water_drop_outlined,
              size: 16,
            ),
            label: Text(labels[index]),
          ),
          if (index != labels.length - 1)
            const Icon(
              Icons.arrow_forward,
              size: 18,
              color: NbsColors.mutedGrey,
            ),
        ],
      ],
    );
  }
}

class _TopTrainPlantingGuidance extends StatelessWidget {
  const _TopTrainPlantingGuidance({required this.train});

  final TrainRecommendation train;

  @override
  Widget build(BuildContext context) {
    if (train.suitablePlants.isEmpty) {
      return Text(
        train.plantingGuidance ??
            'Confirm planting suitability locally before use.',
      );
    }
    final grouped = _groupPlantMappings(train.suitablePlants);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (final group in grouped.entries) ...[
          Text(
            group.key,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w900,
                  color: NbsColors.riverTeal,
                ),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              for (final plant in group.value)
                Container(
                  width: 290,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: NbsColors.wetlandGreen.withValues(alpha: 0.05),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: NbsColors.wetlandGreen.withValues(alpha: 0.18),
                    ),
                  ),
                  child: Builder(
                    builder: (context) {
                      final names = _plantNames(
                        plant['plant_species']?.toString(),
                      );
                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            names.commonName,
                            style: const TextStyle(fontWeight: FontWeight.w900),
                          ),
                          if (names.scientificName != null)
                            Text(
                              names.scientificName!,
                              style: const TextStyle(
                                fontStyle: FontStyle.italic,
                              ),
                            ),
                          const SizedBox(height: 6),
                          if (plant['native_status'] != null)
                            Text(
                              'Status: ${_titleFromSnake(plant['native_status'].toString())} / non-invasive mapping',
                            ),
                          if (plant['ecological_role'] != null)
                            Text('Function: ${plant['ecological_role']}'),
                          if (plant['nbs'] != null)
                            Text('Suitable placement: ${plant['nbs']}'),
                          const SizedBox(height: 5),
                          Text(
                            plant['basis']?.toString() ??
                                'Evidence and final placement require local validation.',
                            style: Theme.of(context)
                                .textTheme
                                .bodySmall
                                ?.copyWith(color: NbsColors.mutedGrey),
                          ),
                        ],
                      );
                    },
                  ),
                ),
            ],
          ),
          const SizedBox(height: 14),
        ],
        Text(
          'Planting suggestions support treatment performance, habitat, stabilization, and maintenance. Final species selection should be locally validated before implementation.',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: NbsColors.deepNavy,
                fontWeight: FontWeight.w700,
              ),
        ),
      ],
    );
  }
}

class _LearningPlaceholder extends StatelessWidget {
  const _LearningPlaceholder({required this.train, required this.citations});

  final TrainRecommendation train;
  final List<Citation> citations;

  @override
  Widget build(BuildContext context) {
    const items = [
      (
        Icons.account_tree_outlined,
        'Treatment sequence',
        'Open the train-specific treatment flow.',
        'sequence',
      ),
      (
        Icons.layers_outlined,
        'Schematic / cross-section',
        'Open a built-in conceptual treatment cross-section.',
        'schematic',
      ),
      (
        Icons.info_outline,
        'Component explanation',
        'Review component function, placement, and maintenance.',
        'components',
      ),
      (
        Icons.grass_outlined,
        'Planting zones',
        'Review grouped, deduplicated non-invasive plant mappings.',
        'plants',
      ),
      (
        Icons.menu_book_outlined,
        'Curated references',
        'Review the source-review structure for future links.',
        'references',
      ),
    ];
    return Wrap(
      spacing: 10,
      runSpacing: 10,
      children: [
        for (final item in items)
          InkWell(
            borderRadius: BorderRadius.circular(8),
            onTap: () => _openLearningPanel(context, item.$2, item.$4),
            child: Container(
              width: 245,
              constraints: const BoxConstraints(minHeight: 126),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: NbsColors.researchBlue.withValues(alpha: 0.04),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: NbsColors.researchBlue.withValues(alpha: 0.14),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(item.$1, size: 20, color: NbsColors.researchBlue),
                      const Spacer(),
                      const Icon(Icons.open_in_new, size: 16),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    item.$2,
                    style: const TextStyle(fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 5),
                  Text(
                    item.$3,
                    style: Theme.of(
                      context,
                    ).textTheme.bodySmall?.copyWith(color: NbsColors.mutedGrey),
                  ),
                ],
              ),
            ),
          ),
      ],
    );
  }

  Future<void> _openLearningPanel(
    BuildContext context,
    String title,
    String topic,
  ) {
    return showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 880),
          child: SingleChildScrollView(
            child: _LearningDetail(
              topic: topic,
              train: train,
              citations: citations,
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}

class _LearningDetail extends StatelessWidget {
  const _LearningDetail({
    required this.topic,
    required this.train,
    required this.citations,
  });

  final String topic;
  final TrainRecommendation train;
  final List<Citation> citations;

  @override
  Widget build(BuildContext context) {
    final diagram = diagramForTrainName(train.name);
    return switch (topic) {
      'sequence' => _TrainSequenceLearning(train: train),
      'schematic' => diagram == null
          ? const _CrossSectionSchematic()
          : NbsDiagramCard(kind: diagram),
      'components' => _ComponentExplanationList(train: train),
      'plants' => _TopTrainPlantingGuidance(train: train),
      _ => _CuratedReferencesPanel(citations: citations),
    };
  }
}

class _TrainSequenceLearning extends StatelessWidget {
  const _TrainSequenceLearning({required this.train});

  final TrainRecommendation train;

  @override
  Widget build(BuildContext context) {
    final labels = [
      'Source',
      ...train.treatmentSequence
          .map((step) => step['step_label']?.toString() ?? '')
          .where((value) => value.isNotEmpty),
      'Monitoring',
    ];
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
        for (var index = 0; index < labels.length; index++) ...[
          Chip(
            avatar: Icon(
              index == labels.length - 1
                  ? Icons.monitor_heart_outlined
                  : Icons.water_drop_outlined,
              size: 16,
            ),
            label: Text(labels[index]),
          ),
          if (index != labels.length - 1)
            const Icon(
              Icons.arrow_forward,
              size: 18,
              color: NbsColors.mutedGrey,
            ),
        ],
      ],
    );
  }
}

class _CrossSectionSchematic extends StatelessWidget {
  const _CrossSectionSchematic();

  @override
  Widget build(BuildContext context) {
    const stages = [
      (Icons.input, 'Inlet', 'Controlled inflow'),
      (Icons.filter_alt_outlined, 'Pretreatment', 'Screening / settling'),
      (Icons.layers_outlined, 'Media bed', 'Hydraulic treatment zone'),
      (Icons.grass_outlined, 'Vegetation zone', 'Rooted polishing zone'),
      (Icons.output_outlined, 'Outlet', 'Level-controlled discharge'),
      (Icons.science_outlined, 'Monitoring', 'Sample and inspect'),
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Conceptual cross-section only. Dimensions, media, hydraulics, and planting require site-specific design.',
        ),
        const SizedBox(height: 14),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              for (var index = 0; index < stages.length; index++) ...[
                Container(
                  width: 132,
                  height: 112,
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: index.isEven
                        ? NbsColors.riverTeal.withValues(alpha: 0.09)
                        : NbsColors.wetlandGreen.withValues(alpha: 0.09),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: NbsColors.cardBorder),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(stages[index].$1, color: NbsColors.deepNavy),
                      const SizedBox(height: 7),
                      Text(
                        stages[index].$2,
                        textAlign: TextAlign.center,
                        style: const TextStyle(fontWeight: FontWeight.w800),
                      ),
                      const SizedBox(height: 3),
                      Text(
                        stages[index].$3,
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
                if (index != stages.length - 1)
                  const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 6),
                    child: Icon(
                      Icons.arrow_forward,
                      color: NbsColors.mutedGrey,
                    ),
                  ),
              ],
            ],
          ),
        ),
      ],
    );
  }
}

class _ComponentExplanationList extends StatelessWidget {
  const _ComponentExplanationList({required this.train});

  final TrainRecommendation train;

  @override
  Widget build(BuildContext context) {
    if (train.nbsComponents.isEmpty) {
      return const Text(
        'No linked NbS components are available for explanation.',
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (final component in train.nbsComponents) ...[
          Text(
            component['name']?.toString() ?? 'NbS component',
            style: Theme.of(
              context,
            ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 5),
          Text(_componentExplanation(component, train)),
          const Divider(height: 22),
        ],
      ],
    );
  }
}

class _CuratedReferencesPanel extends StatelessWidget {
  const _CuratedReferencesPanel({required this.citations});

  final List<Citation> citations;

  @override
  Widget build(BuildContext context) {
    final grouped = _groupCitationsForLearning(citations);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'References below come from the evidence records resolved for this recommendation.',
        ),
        const SizedBox(height: 10),
        for (final entry in grouped.entries) ...[
          Text(
            entry.key,
            style: Theme.of(
              context,
            ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 4),
          if (entry.value.isEmpty)
            const Text('No linked source is available in this category.')
          else
            for (final citation in entry.value)
              ListTile(
                dense: true,
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.menu_book_outlined),
                title: Text('Source ID ${citation.id} - ${citation.display}'),
                subtitle: Text(citation.citation ?? citation.type ?? ''),
                trailing: citation.url == null
                    ? null
                    : TextButton.icon(
                        onPressed: () => openExternalUrl(citation.url!),
                        icon: const Icon(Icons.open_in_new, size: 16),
                        label: const Text('Open'),
                      ),
              ),
          const SizedBox(height: 10),
        ],
      ],
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
                label: 'Screening match',
                value: item.matchPercent,
                color: NbsColors.researchBlue,
              ),
              _MetricChip(
                label: 'Result confidence',
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
                      'Screening match uses TOPSIS; result confidence is calculated separately.',
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
                                  label: 'Screening match',
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
                        label: 'Screening match',
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
    final citationsById = {
      for (final citation in citations) citation.id: citation,
    };
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
          _ReportHeader(item: item),
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
                  label: 'Method',
                  value: _displayStatus(item.weightsStatus),
                  color: item.expertValidated
                      ? NbsColors.wetlandGreen
                      : NbsColors.warningAmber,
                ),
                StatusPill(
                  label: 'Method calibration',
                  value: item.expertValidated ? 'Calibrated' : 'Documented',
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
                    StatusPill(
                      label: 'Screening match',
                      value: item.matchPercent,
                    ),
                    StatusPill(
                      label: 'TOPSIS closeness',
                      value: item.topsisPercent,
                    ),
                    StatusPill(
                      label: 'Result confidence',
                      value: item.confidencePercent,
                      color: NbsColors.wetlandGreen,
                    ),
                    StatusPill(
                      label: 'Confidence level',
                      value: _displayConfidenceLabel(item.confidenceLabel),
                      color: NbsColors.wetlandGreen,
                    ),
                    StatusPill(
                      label: 'Ranking method',
                      value: _displayMethod(item.rankingMethod),
                    ),
                    StatusPill(
                      label: 'Confidence method',
                      value: _displayConfidenceMethod(item.confidenceMethod),
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
                  label: 'Result confidence',
                  value: item.confidenceScore,
                  color: NbsColors.wetlandGreen,
                ),
                const SizedBox(height: 14),
                const _ReadableBulletList(
                  values: [
                    'Screening match is TOPSIS closeness for the supplied problem and context.',
                    'Result confidence reflects data completeness, evidence coverage, and context quality; it does not change rank.',
                    'Plant matches do not affect rank.',
                    'Site suitability reflects available metadata and active applicability rules.',
                    'Detailed calibration notes are available in the Method panel.',
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
              emptyText: 'No additional reason is recorded for this item.',
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
                      const Text(
                        'Values are normalized/scored criteria used by TOPSIS; they are not the final weights.',
                      ),
                      const SizedBox(height: 4),
                      const Text(
                        'Weights come from final v1 AHP-Fuzzy AHP ensemble weights.',
                      ),
                      const SizedBox(height: 12),
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
                  emptyText: 'No additional explanation is recorded.',
                ),
                const SizedBox(height: 12),
                Text(
                  'Evidence source IDs',
                  style: Theme.of(
                    context,
                  ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 8),
                _SourceIdWrap(sourceIds: item.evidenceSummary.sourceIds),
                const SizedBox(height: 12),
                Text(
                  'Citations',
                  style: Theme.of(
                    context,
                  ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w800),
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
              emptyText: 'No additional scientific caution is recorded.',
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

class CatalogueScreen extends StatefulWidget {
  const CatalogueScreen({super.key, required this.api, required this.onBack});

  final RecommendationApi api;
  final VoidCallback onBack;

  @override
  State<CatalogueScreen> createState() => _CatalogueScreenState();
}

class _CatalogueScreenState extends State<CatalogueScreen> {
  Map<String, dynamic>? _catalogue;
  String? _error;
  String _query = '';
  int _section = 0;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _error = null);
    try {
      final value = await widget.api.loadLearningCatalogue();
      if (mounted) setState(() => _catalogue = value);
    } catch (error) {
      if (mounted) setState(() => _error = error.toString());
    }
  }

  List<Map<String, dynamic>> _rows(String key) {
    final raw = _catalogue?[key];
    if (raw is! List) return const [];
    final rows = raw.whereType<Map<String, dynamic>>().toList();
    final query = _query.trim().toLowerCase();
    if (query.isEmpty) return rows;
    return rows
        .where((row) => row.values.join(' ').toLowerCase().contains(query))
        .toList();
  }

  Map<int, Citation> get _evidenceById {
    final records = _catalogue?['evidence_records'];
    if (records is! List) return const {};
    return {
      for (final record in records.whereType<Map<String, dynamic>>())
        if (record['id'] is num)
          (record['id'] as num).toInt(): Citation.fromJson(record),
    };
  }

  @override
  Widget build(BuildContext context) {
    final keys = ['treatment_trains', 'nbs_components', 'plants'];
    final rows = _rows(keys[_section]);
    final evidenceById = _evidenceById;
    return AppScaffold(
      title: 'Catalogue & Learning',
      leading: BackButton(onPressed: widget.onBack),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Evidence learning workspace',
            style: Theme.of(
              context,
            ).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 6),
          Text(
            'Explore stored treatment sequences, component evidence, planting mappings, monitoring, and O&M notes.',
            style: Theme.of(
              context,
            ).textTheme.bodyMedium?.copyWith(color: NbsColors.mutedGrey),
          ),
          const SizedBox(height: 14),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              ChoiceChip(
                label: const Text('Treatment Trains'),
                avatar: const Icon(Icons.account_tree_outlined, size: 17),
                selected: _section == 0,
                onSelected: (_) => setState(() => _section = 0),
              ),
              ChoiceChip(
                label: const Text('NbS Components'),
                avatar: const Icon(Icons.water_outlined, size: 17),
                selected: _section == 1,
                onSelected: (_) => setState(() => _section = 1),
              ),
              ChoiceChip(
                label: const Text('Plants'),
                avatar: const Icon(Icons.grass_outlined, size: 17),
                selected: _section == 2,
                onSelected: (_) => setState(() => _section = 2),
              ),
            ],
          ),
          const SizedBox(height: 12),
          TextField(
            decoration: const InputDecoration(
              prefixIcon: Icon(Icons.search),
              labelText: 'Search catalogue',
            ),
            onChanged: (value) => setState(() => _query = value),
          ),
          const SizedBox(height: 14),
          if (_error != null)
            _AlertBanner.compact(
              icon: Icons.error_outline,
              color: Colors.red,
              title: 'Catalogue unavailable',
              message: _error!,
            )
          else if (_catalogue == null)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(28),
                child: CircularProgressIndicator(),
              ),
            )
          else if (rows.isEmpty)
            const _DetailSection(
              title: 'No catalogue matches',
              child: Text('Try a broader search term.'),
            )
          else if (_section == 0)
            for (final row in rows)
              Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: _TrainCatalogueCard(
                  row: row,
                  citationsById: evidenceById,
                ),
              )
          else if (_section == 1)
            for (final row in rows)
              Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: _NbsCatalogueCard(row: row, citationsById: evidenceById),
              )
          else
            _PlantCatalogueGroups(rows: rows, citationsById: evidenceById),
        ],
      ),
    );
  }
}

class _PlantCatalogueGroups extends StatelessWidget {
  const _PlantCatalogueGroups({
    required this.rows,
    required this.citationsById,
  });

  final List<Map<String, dynamic>> rows;
  final Map<int, Citation> citationsById;

  @override
  Widget build(BuildContext context) {
    final recommended = rows
        .where((row) => row['recommendation_status'] == 'recommended')
        .toList();
    final conditional = rows
        .where(
          (row) =>
              row['recommendation_status'] != 'recommended' &&
              row['recommendation_status'] != 'do_not_recommend_invasive',
        )
        .toList();
    final blocked = rows
        .where(
          (row) => row['recommendation_status'] == 'do_not_recommend_invasive',
        )
        .toList();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (recommended.isNotEmpty) ...[
          const SectionTitle(
            title: 'Recommended / suitable plants',
            subtitle:
                'Use only where the mapped component and site conditions apply.',
          ),
          const SizedBox(height: 8),
          for (final row in recommended)
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: _PlantCatalogueCard(
                row: row,
                citationsById: citationsById,
              ),
            ),
        ],
        if (conditional.isNotEmpty) ...[
          const SectionTitle(
            title: 'Conditional / local validation required',
            subtitle: 'Possible use, but confirm locally before planting.',
          ),
          const SizedBox(height: 8),
          for (final row in conditional)
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: _PlantCatalogueCard(
                row: row,
                citationsById: citationsById,
              ),
            ),
        ],
        if (blocked.isNotEmpty) ...[
          const SizedBox(height: 8),
          const SectionTitle(
            title: 'Not recommended / invasive',
            subtitle: 'These records are shown for safety awareness only.',
          ),
          const SizedBox(height: 8),
          for (final row in blocked)
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: _PlantCatalogueCard(
                row: row,
                citationsById: citationsById,
              ),
            ),
        ],
      ],
    );
  }
}

class _TrainCatalogueCard extends StatelessWidget {
  const _TrainCatalogueCard({required this.row, required this.citationsById});

  final Map<String, dynamic> row;
  final Map<int, Citation> citationsById;

  @override
  Widget build(BuildContext context) {
    final steps = _catalogueMaps(row['sequence_steps']);
    final useCases = _catalogueMaps(row['use_case_suitability']);
    final components = _catalogueMaps(row['components']);
    final plants = _catalogueMaps(row['plants']);
    final diagram = diagramForTrainName(row['name']?.toString());
    return AppCard(
      padding: EdgeInsets.zero,
      child: ExpansionTile(
        tilePadding: const EdgeInsets.all(14),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        expandedCrossAxisAlignment: CrossAxisAlignment.start,
        title: Text(
          row['name']?.toString() ?? 'Treatment train',
          style: const TextStyle(fontWeight: FontWeight.w900),
        ),
        subtitle: Text(row['intended_role']?.toString() ?? 'Role not recorded'),
        children: [
          _TextBlockList(
            title: 'What it is',
            values: _uniqueStrings([
              row['intended_role']?.toString() ?? '',
              ..._catalogueStrings(row['strengths']),
            ]),
            emptyText: 'No train description is recorded.',
          ),
          if (diagram != null) ...[
            const SizedBox(height: 12),
            NbsDiagramCard(kind: diagram),
          ],
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'When to use',
            values: _uniqueStrings([
              if (row['scale_context'] != null) row['scale_context'].toString(),
              for (final item in useCases)
                '${_titleFromSnake(item['use_case']?.toString() ?? 'use case')}: pass ${item['pass_count'] ?? 0}, conditional ${item['marginal_count'] ?? 0}, fail ${item['fail_count'] ?? 0}, unknown ${item['unknown_count'] ?? 0}',
            ]),
            emptyText: 'No use-case matrix record is available.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'When not to use',
            values: _catalogueStrings(row['limitations']),
            emptyText: 'Confirm site constraints before selecting this train.',
          ),
          const SizedBox(height: 12),
          Text(
            'Typical sequence',
            style: Theme.of(
              context,
            ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w800),
          ),
          const SizedBox(height: 8),
          _CatalogueFlow(
            steps: [
              for (final step in steps)
                step['step_label']?.toString() ?? 'Stage',
            ],
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Key design checks',
            values: _catalogueStrings(row['pretreatment_needs']),
            emptyText: 'No additional pretreatment requirement is recorded.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'O&M and monitoring checklist',
            values: _catalogueStrings(row['om_notes']),
            emptyText: 'No train-specific O&M record is available.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Components',
            values: [
              for (final item in components)
                '${item['name'] ?? 'Component'} - ${item['role'] ?? 'role not recorded'}',
            ],
            emptyText: 'No linked component is recorded.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Plants / zones',
            values: [
              for (final plant in plants)
                '${plant['plant_species'] ?? 'Plant'} - ${plant['nbs'] ?? 'mapped component'}',
            ],
            emptyText:
                'No safe planting recommendation is available in this toolkit.',
          ),
          const SizedBox(height: 12),
          _EvidenceDisclosure(
            sourceIds: _catalogueSourceIds(row['source_ids']),
            citationsById: citationsById,
            groups: _catalogueEvidenceGroups(row['evidence_groups']),
          ),
        ],
      ),
    );
  }
}

class _NbsCatalogueCard extends StatelessWidget {
  const _NbsCatalogueCard({required this.row, required this.citationsById});

  final Map<String, dynamic> row;
  final Map<int, Citation> citationsById;

  @override
  Widget build(BuildContext context) {
    final plants = _catalogueMaps(row['plants']);
    final diagram = diagramForComponentName(row['solution']?.toString());
    return AppCard(
      padding: EdgeInsets.zero,
      child: ExpansionTile(
        tilePadding: const EdgeInsets.all(14),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        expandedCrossAxisAlignment: CrossAxisAlignment.start,
        title: Text(
          row['solution']?.toString() ?? 'NbS component',
          style: const TextStyle(fontWeight: FontWeight.w900),
        ),
        subtitle: Text(
          '${row['family'] ?? 'Family not recorded'} | ${row['catalogue_role'] ?? 'Role not recorded'}',
        ),
        children: [
          _TextBlockList(
            title: 'Role',
            values: [
              row['catalogue_role']?.toString() ??
                  'Role requires local confirmation.',
            ],
            emptyText: 'Role requires local confirmation.',
          ),
          if (diagram != null) ...[
            const SizedBox(height: 12),
            NbsDiagramCard(kind: diagram),
          ],
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Can it be used alone?',
            values: [
              'Use only after site-safety screening confirms it is suitable.',
            ],
            emptyText: 'Use only after site-safety screening.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Where suitable',
            values: _catalogueStrings(row['where_suitable']),
            emptyText: 'Site suitability requires local validation.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Where not suitable',
            values: _catalogueStrings(row['where_not_suitable']),
            emptyText:
                'Use only after site-safety screening confirms it is suitable.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Pollutants addressed',
            values: [
              for (final value in _catalogueStrings(row['pollutants_treated']))
                _displayParameter(value),
            ],
            emptyText: 'No numeric pollutant-removal record is available.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Cross-section / design notes',
            values: _catalogueStrings(row['design_notes']),
            emptyText: 'No design note is recorded for this component yet.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'O&M notes',
            values: _catalogueStrings(row['maintenance_notes']),
            emptyText:
                'No maintenance note is recorded for this component yet.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Plant links',
            values: [
              for (final plant in plants)
                plant['plant_species']?.toString() ?? 'Mapped plant',
            ],
            emptyText: 'Confirm planting suitability locally before use.',
          ),
          const SizedBox(height: 12),
          _EvidenceDisclosure(
            sourceIds: _catalogueSourceIds(row['source_ids']),
            citationsById: citationsById,
            groups: _catalogueEvidenceGroups(row['evidence_groups']),
          ),
        ],
      ),
    );
  }
}

class _PlantCatalogueCard extends StatelessWidget {
  const _PlantCatalogueCard({required this.row, required this.citationsById});

  final Map<String, dynamic> row;
  final Map<int, Citation> citationsById;

  @override
  Widget build(BuildContext context) {
    final invasive =
        row['recommendation_status'] == 'do_not_recommend_invasive';
    final mappings = _catalogueMaps(row['mapped_components']);
    return AppCard(
      padding: EdgeInsets.zero,
      borderColor:
          invasive ? Colors.red.withValues(alpha: 0.45) : NbsColors.cardBorder,
      child: ExpansionTile(
        tilePadding: const EdgeInsets.all(14),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        expandedCrossAxisAlignment: CrossAxisAlignment.start,
        leading: Icon(
          invasive ? Icons.block_outlined : Icons.grass_outlined,
          color: invasive ? Colors.red : NbsColors.wetlandGreen,
        ),
        title: Text(
          row['plant_species']?.toString() ?? 'Plant species',
          style: const TextStyle(fontWeight: FontWeight.w900),
        ),
        subtitle: Text(
          invasive
              ? 'Not recommended. This species is invasive and should not be used for planting.'
              : 'Possible use, but confirm locally before planting.',
        ),
        children: [
          _TextBlockList(
            title: 'Mapped NbS components',
            values: [
              for (final item in mappings)
                '${item['name'] ?? 'Component'} - ${item['basis'] ?? 'mapping basis not recorded'}',
            ],
            emptyText:
                'No safe planting recommendation is available in this toolkit.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Planting zone and conditions',
            values: _uniqueStrings([
              row['plant_type']?.toString() ?? '',
              row['locational_availability']?.toString() ?? '',
              row['climate_preference']?.toString() ?? '',
              row['soil_type']?.toString() ?? '',
              row['water_needs']?.toString() ?? '',
            ]),
            emptyText: 'Planting conditions require local validation.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Ecological / treatment role',
            values: _uniqueStrings([
              row['ecological_role']?.toString() ?? '',
              row['metals_pollutants']?.toString() ?? '',
              row['evidence_note']?.toString() ?? '',
            ]),
            emptyText: 'No ecological role is recorded.',
          ),
          const SizedBox(height: 12),
          _EvidenceDisclosure(
            sourceIds: _catalogueSourceIds(row['source_ids']),
            citationsById: citationsById,
            groups: _catalogueEvidenceGroups(row['evidence_groups']),
          ),
        ],
      ),
    );
  }
}

class _CatalogueFlow extends StatelessWidget {
  const _CatalogueFlow({required this.steps});

  final List<String> steps;

  @override
  Widget build(BuildContext context) => Wrap(
        spacing: 6,
        runSpacing: 8,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          for (var index = 0; index < steps.length; index++) ...[
            Chip(label: Text(steps[index])),
            if (index < steps.length - 1)
              const Icon(Icons.arrow_forward, size: 17),
          ],
        ],
      );
}

List<Map<String, dynamic>> _catalogueMaps(dynamic value) =>
    value is List ? value.whereType<Map<String, dynamic>>().toList() : const [];

List<String> _catalogueStrings(dynamic value) => value is List
    ? value
        .map((item) => item.toString())
        .where((item) => item.trim().isNotEmpty)
        .toList()
    : const [];

List<int> _catalogueSourceIds(dynamic value) => value is List
    ? value.whereType<num>().map((item) => item.toInt()).toList()
    : const [];

Map<String, List<int>> _catalogueEvidenceGroups(dynamic value) {
  if (value is! Map) return const {};
  return {
    for (final entry in value.entries)
      entry.key.toString(): _catalogueSourceIds(entry.value),
  };
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
                'Weights: final v1 AHP-Fuzzy AHP ensemble criteria weights. Ranking: TOPSIS closeness to ideal-best and ideal-worst treatment-train profiles.',
          ),
          SizedBox(height: 12),
          _MethodCard(
            title: 'Safety screening',
            body:
                'Safety: A0 applicability/safety screening runs before ranking. Ranking uses final v1 AHP-Fuzzy AHP ensemble weights with TOPSIS.',
          ),
          SizedBox(height: 12),
          _MethodCard(
            title: 'Confidence',
            body:
                'Confidence: calculated separately from match score. It reflects data quality, evidence completeness, criteria coverage, and active caution flags.',
          ),
          SizedBox(height: 12),
          _MethodCard(
            title: 'Current limitations',
            body:
                'Boundary: C5 health-risk is reserved for future integration; final engineering design still requires expert review and field validation.',
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
      appBar: AppBar(title: Text(title), leading: leading, actions: actions),
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
          colors: [Colors.white, NbsColors.softBackground, Color(0xFFEFF7FB)],
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

    canvas.drawCircle(
      Offset(size.width * 0.82, size.height * 0.08),
      120,
      glowPaint,
    );

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
  const _BoxArtwork({required this.motif});

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
  const _BoxArtworkPainter({required this.motif});

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
              Rect.fromLTWH(
                size.width - 70 + index * 14,
                size.height - h,
                7,
                h,
              ),
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
                'Narmada NbS Planner',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      color: NbsColors.deepNavy,
                      fontWeight: FontWeight.w900,
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                'Compare nature-based treatment options using water-quality data, site context, and evidence-linked rules.',
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
                  _HeroChip(
                    label: 'Evidence-linked planning',
                    color: NbsColors.wetlandGreen,
                  ),
                  _HeroChip(label: 'Narmada basin', color: NbsColors.riverTeal),
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
              children: [iconBlock, const SizedBox(height: 18), titleBlock],
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

// Retained for compatibility with older detail layouts.
// ignore: unused_element
class _ResultsHero extends StatelessWidget {
  const _ResultsHero({
    required this.response,
    required this.bundle,
    required this.topRecommendation,
  });

  final RecommendationResponse response;
  final RecommendationAssemblyBundle? bundle;
  final TrainRecommendation? topRecommendation;

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
                      'Executive recommendation',
                      style:
                          Theme.of(context).textTheme.headlineSmall?.copyWith(
                                color: NbsColors.deepNavy,
                                fontWeight: FontWeight.w900,
                              ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      topRecommendation == null
                          ? 'No ranked recommendation is available for this run.'
                          : 'Top treatment train: ${topRecommendation!.name}',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: NbsColors.mutedGrey,
                            height: 1.35,
                          ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      topRecommendation?.implementationRole == null
                          ? 'Review the data basis and design-readiness status before proceeding.'
                          : 'Recommended role: ${topRecommendation!.implementationRole}.',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: NbsColors.mutedGrey,
                            height: 1.35,
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
                label: 'Eligible treatment trains',
                value: '${response.rankedTrains.length}',
                icon: Icons.format_list_numbered,
                color: NbsColors.deepNavy,
              ),
              _DashboardMetricCard(
                label: 'Filtered out',
                value: '${response.rejectedOptions.length}',
                icon: Icons.filter_alt_off_outlined,
                color: Colors.red.shade700,
              ),
              _DashboardMetricCard(
                label: 'Conditional',
                value:
                    '${response.rankedTrains.where((row) => row.applicabilityStatus == 'conditional').length}',
                icon: Icons.rule_folder_outlined,
                color: NbsColors.warningAmber,
              ),
              _DashboardMetricCard(
                label: 'Screening match',
                value: topRecommendation?.matchPercent ?? 'N/A',
                icon: Icons.trending_up,
                color: NbsColors.researchBlue,
              ),
              _DashboardMetricCard(
                label: 'Result confidence',
                value: _trainConfidenceDisplay(topRecommendation),
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

// Retained for compatibility with older detail layouts.
// ignore: unused_element
class _ResultsMetricStrip extends StatelessWidget {
  const _ResultsMetricStrip({required this.response, required this.bundle});

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
          value: 'Safety screening to TOPSIS',
          color: NbsColors.riverTeal,
        ),
        StatusPill(
          label: 'Weights',
          value: 'Criteria-weighted',
          color: NbsColors.researchBlue,
        ),
        StatusPill(
          label: 'Confidence method',
          value: _confidenceMethodLabel(response, bundle),
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
              value == null ? 'N/A' : '${(progress * 100).toStringAsFixed(1)}%',
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
                  style: Theme.of(
                    context,
                  ).textTheme.bodyMedium?.copyWith(color: NbsColors.mutedGrey),
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
                      label: _displayConfidenceMethod(item.confidenceMethod),
                      color: NbsColors.wetlandGreen,
                    ),
                    _HeroChip(
                      label: item.expertValidated
                          ? 'Method calibrated'
                          : 'Scientific method',
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

class _HowItWorksStrip extends StatelessWidget {
  const _HowItWorksStrip();

  @override
  Widget build(BuildContext context) {
    const steps = [
      'Add water or site context.',
      'Review the recommended treatment train.',
      'Check site and design readiness.',
      'Compare options and export a report.',
    ];
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'How it works',
            style: Theme.of(
              context,
            ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 12),
          LayoutBuilder(
            builder: (context, constraints) {
              final itemWidth = constraints.maxWidth >= 900
                  ? (constraints.maxWidth - 36) / 4
                  : constraints.maxWidth;
              return Wrap(
                spacing: 12,
                runSpacing: 10,
                children: [
                  for (var index = 0; index < steps.length; index++)
                    SizedBox(
                      width: itemWidth,
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          CircleAvatar(
                            radius: 12,
                            backgroundColor: NbsColors.researchBlue,
                            child: Text(
                              '${index + 1}',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 12,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(child: Text(steps[index])),
                        ],
                      ),
                    ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }
}

class _ParameterCoverageRows extends StatelessWidget {
  const _ParameterCoverageRows({required this.rows});

  final List<Map<String, dynamic>> rows;

  @override
  Widget build(BuildContext context) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (final row in rows)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.science_outlined, size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      row['coverage_category'] == 'skipped'
                          ? row['display_name']?.toString() ??
                              'Skipped input row'
                          : '${_displayParameter(row['parameter']?.toString(), fallback: row['display_name']?.toString())} = ${row['value'] ?? 'unknown'}${_displayUnitSuffix(row['unit'])}',
                    ),
                  ),
                  const SizedBox(width: 8),
                  Flexible(
                    child: Text(
                      _coverageLabel(row['coverage_category']?.toString()),
                      textAlign: TextAlign.end,
                      style: const TextStyle(fontWeight: FontWeight.w800),
                    ),
                  ),
                ],
              ),
            ),
        ],
      );
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
                label: 'Service',
                value: 'App service connected',
                color: NbsColors.wetlandGreen,
              ),
              StatusPill(
                label: 'Database',
                value: 'Narmada evidence database loaded',
              ),
              StatusPill(label: 'Method', value: 'Transparent ranking method'),
              StatusPill(
                label: 'Evidence',
                value: 'Evidence records linked',
                color: NbsColors.riverTeal,
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
    this.requiredField = true,
  });

  final TextEditingController controller;
  final String label;
  final String suffix;
  final String helper;
  final bool requiredField;

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
          label == 'pH' ? Icons.water_drop_outlined : Icons.speed_outlined,
          color: NbsColors.riverBlue,
        ),
      ),
      validator: (value) {
        final raw = value?.trim() ?? '';
        if (raw.isEmpty && !requiredField) {
          return null;
        }
        final parsed = double.tryParse(raw);
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
  const _HeaderBadge({required this.label, required this.value});

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
                style: Theme.of(
                  context,
                ).textTheme.bodyMedium?.copyWith(color: NbsColors.deepNavy),
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
          style: Theme.of(
            context,
          ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w800),
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
    this.emptyText = 'No additional item is recorded.',
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

class _NumberedActionList extends StatelessWidget {
  const _NumberedActionList({required this.values, required this.emptyText});

  final List<String> values;
  final String emptyText;

  @override
  Widget build(BuildContext context) {
    if (values.isEmpty) return Text(emptyText);
    return Column(
      children: [
        for (var index = 0; index < values.length; index++)
          Padding(
            padding: const EdgeInsets.only(bottom: 9),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 24,
                  height: 24,
                  alignment: Alignment.center,
                  decoration: const BoxDecoration(
                    color: NbsColors.researchBlue,
                    shape: BoxShape.circle,
                  ),
                  child: Text(
                    '${index + 1}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                const SizedBox(width: 9),
                Expanded(child: Text(_readableText(values[index]))),
              ],
            ),
          ),
      ],
    );
  }
}

class _SourceIdWrap extends StatelessWidget {
  const _SourceIdWrap({required this.sourceIds, this.citationsById = const {}});

  final List<int> sourceIds;
  final Map<int, Citation> citationsById;

  @override
  Widget build(BuildContext context) {
    if (sourceIds.isEmpty) {
      return const Text('No evidence records are linked.');
    }
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        for (final sourceId in sourceIds)
          Chip(
            label: Text(
              citationsById[sourceId]?.display ?? 'Evidence record $sourceId',
            ),
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

class _EvidenceDisclosure extends StatelessWidget {
  const _EvidenceDisclosure({
    required this.sourceIds,
    required this.citationsById,
    this.groups = const {},
    this.initiallyExpanded = false,
  });

  final List<int> sourceIds;
  final Map<int, Citation> citationsById;
  final Map<String, List<int>> groups;
  final bool initiallyExpanded;

  @override
  Widget build(BuildContext context) {
    final populatedGroups = {
      for (final entry in groups.entries)
        if (entry.value.isNotEmpty) entry.key: entry.value,
    };
    return ExpansionTile(
      initiallyExpanded: initiallyExpanded,
      tilePadding: EdgeInsets.zero,
      childrenPadding: const EdgeInsets.only(bottom: 8),
      title: const Text(
        'View evidence',
        style: TextStyle(fontWeight: FontWeight.w800),
      ),
      subtitle: const Text(
        'Evidence records show the sources used by the toolkit. They support screening and comparison, not final engineering design.',
      ),
      children: [
        if (populatedGroups.isEmpty)
          Align(
            alignment: Alignment.centerLeft,
            child: _SourceIdWrap(
              sourceIds: sourceIds,
              citationsById: citationsById,
            ),
          )
        else
          for (final entry in populatedGroups.entries)
            Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      entry.key,
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.w800,
                          ),
                    ),
                    const SizedBox(height: 7),
                    _SourceIdWrap(
                      sourceIds: entry.value,
                      citationsById: citationsById,
                    ),
                  ],
                ),
              ),
            ),
      ],
    );
  }
}

class _CitationList extends StatelessWidget {
  const _CitationList({required this.sourceIds, required this.citationsById});

  final List<int> sourceIds;
  final Map<int, Citation> citationsById;

  @override
  Widget build(BuildContext context) {
    final resolved = [
      for (final sourceId in sourceIds)
        if (citationsById[sourceId] != null) citationsById[sourceId]!,
    ];
    if (resolved.isEmpty) {
      return const Text('No linked citation is available for this item.');
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
                      if (citation.license != null)
                        'License: ${citation.license!}',
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
        children: [
          _ReadableBulletList(values: notes.map(_readableText).toList()),
        ],
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
              color:
                  (highlighted ? NbsColors.warningAmber : NbsColors.riverTeal)
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

// Retained for compatibility with older detail layouts.
// ignore: unused_element
({String basis, String currentSample, String confidenceBasis}) _dataBasis(
  RecommendationResponse response,
) {
  final mode = response.inputSummary.workflowMode;
  final hasCurrentSample = response.inputSummary.observationCount > 0;
  final parameters = response.inputSummary.selectedParameters.toSet();
  final completePanel = {'bod', 'cod', 'tss', 'ph'}.every(parameters.contains);
  final basis = switch (mode) {
    'uploaded_water_quality' => 'Uploaded data + evidence database',
    'manual_measured_water_quality' => 'Measured values + evidence database',
    'site_context_only' ||
    'pollution_source_screening' =>
      'Station and site context',
    _ => hasCurrentSample ? 'Mixed data basis' : 'Available context data',
  };
  return (
    basis: basis,
    currentSample: hasCurrentSample ? 'Supplied' : 'Not supplied',
    confidenceBasis: response.inputSummary.isContextOnly
        ? 'Low confidence: based on station and site context only.'
        : response.inputSummary.observationCount == 1
            ? 'Reduced because only one usable value was supplied.'
            : mode == 'uploaded_water_quality' && completePanel
                ? 'Based on uploaded values and literature evidence.'
                : hasCurrentSample
                    ? 'Reduced because some key values are missing.'
                    : 'Not enough recent water-quality data.',
  );
}

List<String> _cleanDataGaps(
  RecommendationResponse response,
  TrainRecommendation? train,
) {
  final values = <String>[];
  var currentSampleGap = false;
  for (final value in [
    ...response.globalGaps,
    ...response.missingDataMessages,
    if (train != null) ...train.dataGaps,
  ]) {
    final lower = value.toLowerCase();
    final genericSampleGap = lower.contains('measured water-quality data') ||
        lower.contains('water input data was missing') ||
        lower.contains('water observations') ||
        lower.contains('observation_count') ||
        lower.contains('pass/fail conclusions');
    if (genericSampleGap && response.inputSummary.isContextOnly) {
      currentSampleGap = true;
      continue;
    }
    values.add(value);
  }
  if (response.inputSummary.isContextOnly || currentSampleGap) {
    values.insert(
      0,
      'You have not uploaded recent water-quality data for this site. The result uses available site and source context and remains an early screening result.',
    );
  }
  if (train?.allUseCasesUnknown == true) {
    values.add(
      'Use-case assessment needs recent water-quality values or additional linked performance evidence.',
    );
  }
  return _uniqueStrings(values);
}

List<String> _cleanContextGuidance(
  List<String> guidance,
  RecommendationResponse response,
) {
  final values = <String>[];
  var replacedSampleMessage = false;
  for (final value in guidance) {
    final lower = value.toLowerCase();
    if (lower.contains('measured water-quality data') ||
        lower.contains('treatment pass/fail')) {
      replacedSampleMessage = true;
      continue;
    }
    values.add(value);
  }
  if (response.inputSummary.isContextOnly || replacedSampleMessage) {
    values.insert(
      0,
      'This recommendation uses stored Narmada station and site context where available. No current measured water-quality input was supplied, so design-level conclusions must be checked before implementation.',
    );
  }
  return _uniqueStrings(values);
}

Map<String, List<Map<String, dynamic>>> _groupPlantMappings(
  List<Map<String, dynamic>> plants,
) {
  const groupOrder = [
    'Wetland bed / polishing cell',
    'Buffer strip / riparian edge',
    'Sediment stabilization',
    'Habitat / biodiversity support',
    'Needs local validation',
  ];
  final grouped = <String, List<Map<String, dynamic>>>{};
  final seen = <String, Set<String>>{};
  for (final plant in plants) {
    final text = [
      plant['nbs'],
      plant['ecological_role'],
      plant['basis'],
    ].whereType<Object>().join(' ').toLowerCase();
    final group = text.contains('buffer') || text.contains('riparian')
        ? 'Buffer strip / riparian edge'
        : text.contains('sediment') ||
                text.contains('stabili') ||
                text.contains('erosion')
            ? 'Sediment stabilization'
            : text.contains('habitat') || text.contains('biodiversity')
                ? 'Habitat / biodiversity support'
                : text.contains('wetland') ||
                        text.contains('pond') ||
                        text.contains('polish')
                    ? 'Wetland bed / polishing cell'
                    : 'Needs local validation';
    final speciesKey = (plant['plant_species']?.toString() ?? 'unidentified')
        .trim()
        .toLowerCase();
    if ((seen[group] ??= <String>{}).add(speciesKey)) {
      (grouped[group] ??= <Map<String, dynamic>>[]).add(plant);
    }
  }
  return {
    for (final group in groupOrder)
      if (grouped[group]?.isNotEmpty == true) group: grouped[group]!,
  };
}

({String commonName, String? scientificName}) _plantNames(String? rawName) {
  final value = (rawName ?? 'Mapped plant species').trim();
  final open = value.lastIndexOf('(');
  if (open > 0 && value.endsWith(')')) {
    return (
      commonName: value.substring(0, open).trim(),
      scientificName: value.substring(open + 1, value.length - 1).trim(),
    );
  }
  return (commonName: value, scientificName: null);
}

// Retained for compatibility with older detail layouts.
// ignore: unused_element
({String label, String reason}) _designReadiness(
  RecommendationResponse response,
  TrainRecommendation? train,
) {
  final context = response.inputSummary.context;
  final source = context['pollution_source_type']?.toString() ?? '';
  if (source.contains('industrial')) {
    return (
      label: 'Pretreatment validation required',
      reason:
          'ETP/CETP capacity, industrial chemistry, and pH neutralization must be validated before NbS polishing.',
    );
  }
  if (source.contains('agriculture')) {
    return (
      label: 'Source-control planning required',
      reason:
          'Field and edge-of-field controls must be planned before sizing off-channel polishing for collected runoff.',
    );
  }
  if (response.inputSummary.isContextOnly ||
      response.inputSummary.observationCount == 0) {
    return (
      label: 'Early screening result',
      reason:
          'Screening uses available Narmada station and source context. Recent measured water-quality data are recommended before preliminary design review.',
    );
  }
  if (train?.dataGaps.isNotEmpty == true) {
    return (
      label: 'Planning-level result',
      reason:
          'Measured values support comparison, but reported evidence and site/design gaps require validation before engineering design.',
    );
  }
  return (
    label: 'Planning-level result',
    reason:
        'Measured water-quality data support planning; engineering design and site validation remain required.',
  );
}

String _practicalRecommendation(
  RecommendationResponse response,
  TrainRecommendation? train,
) {
  if (train == null) {
    return 'No ranked recommendation is available; review data gaps and inputs.';
  }
  final context = response.inputSummary.context;
  final source = context['pollution_source_type']?.toString() ?? '';
  final highOrder = context['intervention_position'] == 'in_channel' ||
      ((context['stream_order'] as num?)?.toDouble() ?? 0) >= 5;
  if (source.contains('industrial')) {
    return 'Use ${train.name} only after ETP/CETP treatment and required pH neutralization. Use NbS as controlled polishing or buffering, not standalone industrial treatment.';
  }
  if (source.contains('agriculture')) {
    return 'Start with field and edge-of-field source control. Use ${train.name} only for collected runoff that needs off-channel polishing.';
  }
  if (highOrder) {
    return 'Use ${train.name} only through drain interception or off-channel treatment. Do not build treatment cells inside the main river channel.';
  }
  if (context['intervention_position'] == 'off_channel_or_stp_polishing') {
    if (train.name.toLowerCase().contains('dewats')) {
      return 'Use a DEWATS modular train as an off-channel treatment system. Use it for decentralized sewage treatment or STP polishing. Do not use it as an in-channel river intervention.';
    }
    return 'Use a ${train.name} as an off-channel treatment train. Apply it after primary treatment such as screening and settling. Do not place it directly inside the river channel.';
  }
  return 'Use ${train.name} as ${train.implementationRole?.toLowerCase() ?? 'the selected treatment train'}, following its primary treatment, polishing, and monitoring requirements.';
}

String _keyCaution(
  RecommendationResponse response,
  TrainRecommendation? train,
) {
  if (train == null) return 'No train-specific caution is available.';
  final source =
      response.inputSummary.context['pollution_source_type']?.toString() ?? '';
  if (source.contains('industrial')) {
    return 'Standalone wetland or pond treatment is not appropriate for industrial wastewater; pretreatment and compliance verification are mandatory.';
  }
  if (source.contains('agriculture')) {
    return 'The ranked train is not a complete farm-level design and applies only after runoff is collected or intercepted.';
  }
  if (response.inputSummary.isContextOnly) {
    return 'This is a context-screening recommendation. Confirm recent water quality, flow, land, and site constraints before design.';
  }
  return train.caveats.isNotEmpty
      ? train.caveats.first
      : 'Site survey, hydraulic design, regulatory review, and monitoring remain required.';
}

String? _majorSummaryWarning(
  RecommendationResponse response,
  TrainRecommendation? train,
  List<String> dataGaps,
) {
  final context = response.inputSummary.context;
  final source = context['pollution_source_type']?.toString() ?? '';
  if (source.contains('industrial')) {
    return 'Industrial or mixed wastewater needs ETP/CETP pretreatment. Confirm neutralization when pH is outside the treatment range.';
  }
  if (response.locationContext.contextFlags['off_channel_required'] == true) {
    return 'Treatment must stay off-channel. Do not place treatment cells inside the main river channel.';
  }
  if (response.designReadiness.expertReviewRequired) {
    return 'A qualified specialist should review the safety and site conditions before this option advances.';
  }
  if (response.inputSummary.observationCount == 0 || dataGaps.isNotEmpty) {
    return 'Important data are still missing. Use this result for early screening, not engineering design.';
  }
  if (train?.applicabilityStatus == 'conditional') {
    return 'This option is conditional. Follow the listed pretreatment and site checks before using it.';
  }
  return null;
}

({
  List<ReadinessInput> improveResult,
  List<ReadinessInput> beforeDesign,
  List<ReadinessInput> fieldChecks,
}) _groupReadinessInputs(List<ReadinessInput> items) {
  const improveKeys = {
    'design_flow',
    'available_land',
    'bod',
    'cod',
    'tss',
    'ph',
    'nutrients',
    'do',
    'faecal_coliform___pathogens',
  };
  const fieldKeys = {
    'site_slope',
    'soil_infiltration',
    'flood_risk',
    'om_owner_capacity',
  };
  final improve = <ReadinessInput>[];
  final before = <ReadinessInput>[];
  final field = <ReadinessInput>[];
  for (final item in items) {
    if (improveKeys.contains(item.key)) {
      improve.add(item);
    } else if (fieldKeys.contains(item.key)) {
      field.add(item);
    } else {
      before.add(item);
    }
  }
  return (improveResult: improve, beforeDesign: before, fieldChecks: field);
}

// Retained for compatibility with older detail layouts.
// ignore: unused_element
Map<String, List<String>> _groupDataActions(
  RecommendationResponse response,
  TrainRecommendation? train,
  List<String> dataGaps,
  List<String> nextData,
) {
  final required = <String>[];
  final ranking = <String>[];
  final site = <String>[];
  final csvSummary = response.inputSummary.context['csv_validation_summary'];
  if (csvSummary is Map) {
    for (final warning in (csvSummary['warnings'] as List? ?? const [])) {
      ranking.add('CSV validation: $warning');
    }
    for (final error in (csvSummary['errors'] as List? ?? const [])) {
      required.add('CSV validation: $error');
    }
  }
  if (response.inputSummary.isContextOnly) {
    required.add(
      'Confirm recent measured water quality before design-level treatment pass/fail assessment.',
    );
  }
  final source =
      response.inputSummary.context['pollution_source_type']?.toString() ?? '';
  if (source.contains('industrial')) {
    required.add(
      'Confirm ETP/CETP availability, industrial chemistry, and pH-neutralization requirements.',
    );
  }
  for (final item in [...nextData, ...dataGaps]) {
    final lower = item.toLowerCase();
    if (response.inputSummary.isContextOnly &&
        (lower.contains('current sample') ||
            lower.contains('user-supplied current sample') ||
            lower.contains('pass/fail'))) {
      continue;
    }
    if (lower.contains('land') ||
        lower.contains('slope') ||
        lower.contains('flow') ||
        lower.contains('site') ||
        lower.contains('plant') ||
        lower.contains('hydraulic')) {
      site.add(item);
    } else if (lower.contains('measure') ||
        lower.contains('absent') ||
        lower.contains('water-quality') ||
        lower.contains('nh4') ||
        lower.contains('cod')) {
      ranking.add(item);
    } else {
      required.add(item);
    }
  }
  if (train?.pretreatmentRequirements.isNotEmpty == true) {
    required.add(
      'Validate pretreatment: ${train!.pretreatmentRequirements.first}',
    );
  }
  site.add(
    'Confirm land availability, slope, access, seasonal flow, and maintenance arrangements through site survey.',
  );
  return {
    'required': _uniqueStrings(required),
    'ranking': _uniqueStrings(ranking),
    'site': _uniqueStrings(site),
  };
}

String _componentExplanation(
  Map<String, dynamic> component,
  TrainRecommendation train,
) {
  final name = component['name']?.toString() ?? 'NbS component';
  final text =
      '${component['name'] ?? ''} ${component['family'] ?? ''}'.toLowerCase();
  final step = train.treatmentSequence.cast<Map<String, dynamic>?>().firstWhere(
        (value) => value?['nbs_id'] == component['nbs_id'],
        orElse: () => null,
      );
  final placement = step?['role']?.toString() ?? 'linked treatment stage';
  if (text.contains('wetland') ||
      text.contains('hssf') ||
      text.contains('vertical flow')) {
    return '$name provides media-based and biological polishing for suspended solids, organic matter, and nutrients where site/design evidence supports it. Placement: $placement. Maintain even flow distribution, inspect clogging, and manage vegetation and media condition.';
  }
  if (text.contains('pond') || text.contains('lagoon')) {
    return '$name supports settling and staged biological polishing, with pathogen reduction depending on the complete pond sequence and operating conditions. Placement: $placement. Inspect embankments, sludge accumulation, short-circuiting, and outlet control.';
  }
  if (text.contains('uasb') ||
      text.contains('reactor') ||
      text.contains('anaerobic')) {
    return '$name provides upstream biological treatment for organic loading before downstream polishing. Placement: $placement. Monitor inlet distribution, sludge/scum condition, hydraulic loading, and downstream performance.';
  }
  if (text.contains('soak') || text.contains('infiltration')) {
    return '$name provides controlled on-site infiltration/disposal only where soil, groundwater, loading, and setback checks support it. Placement: $placement. Inspect ponding, clogging, and groundwater protection conditions.';
  }
  return '$name is linked as a $placement. Its pollutant role, hydraulic configuration, and maintenance requirements should be confirmed from the component design record and local site validation.';
}

List<String> _whatNotToDo(
  RecommendationResponse response,
  TrainRecommendation train,
) {
  final context = response.inputSummary.context;
  final source = context['pollution_source_type']?.toString() ?? '';
  if (source.contains('industrial')) {
    return const [
      'Do not use a standalone wetland or pond as primary industrial treatment.',
      'Do not send acidic wastewater to biological or NbS units before neutralization.',
    ];
  }
  if (source.contains('agriculture')) {
    return const [
      'Do not present the ranked train as a complete farm-level design.',
      'Do not bypass field and edge-of-field source controls.',
    ];
  }
  if (context['intervention_position'] == 'in_channel' ||
      ((context['stream_order'] as num?)?.toDouble() ?? 0) >= 5) {
    return const [
      'Do not place treatment cells inside a mainstem or high-order river channel.',
      'Do not obstruct river conveyance or substitute in-channel cells for upstream pollution control.',
    ];
  }
  return train.caveats.isNotEmpty
      ? train.caveats.take(2).toList()
      : const [
          'Do not proceed to construction without site survey, hydraulic checks, and regulatory review.',
        ];
}

List<String> _monitoringPoints(TrainRecommendation train) {
  return _uniqueStrings([
    'Influent/source water before pretreatment.',
    for (final step in train.treatmentSequence)
      'After ${step['step_label'] ?? 'treatment stage'} (${step['role'] ?? 'process step'}).',
    'Final effluent before discharge, reuse, or receiving-water entry.',
    'Hydraulic condition, clogging, vegetation health, sludge/solids, and maintenance records.',
  ]).take(6).toList();
}

List<String> _topRecommendationReasons(
  RecommendationResponse response,
  TrainRecommendation? train,
  List<String> sourceLocationGuidance,
) {
  if (train == null) {
    return const [];
  }
  final supportedUses = train.useCaseVerdicts.entries
      .where((entry) => entry.value == 'pass' || entry.value == 'marginal')
      .map((entry) => _titleFromSnake(entry.key))
      .toList();
  final components = train.nbsComponents
      .map((component) => component['name']?.toString() ?? '')
      .where((name) => name.isNotEmpty)
      .take(2)
      .toList();
  final reasons = <String>[
    for (final exceedance in response.exceedances.take(2))
      'Pollutant gap: ${exceedance.summary}',
    if (sourceLocationGuidance.isNotEmpty)
      'Context: ${sourceLocationGuidance.first}',
    if (train.implementationRole != null)
      'Intended role: ${train.implementationRole}.',
    if (components.isNotEmpty)
      'Treatment function: ${components.join(' followed by ')} provide the linked treatment and polishing stages.',
    if (supportedUses.isNotEmpty)
      'Suitability strength: available linked evidence supports ${supportedUses.join(', ')} assessment.',
    if (train.pretreatmentRequirements.isNotEmpty)
      'Pretreatment: ${train.pretreatmentRequirements.first}',
    if (train.caveats.isNotEmpty) 'Key limitation: ${train.caveats.first}',
    if (train.caveats.isEmpty && train.dataGaps.isNotEmpty)
      'Key limitation: ${train.dataGaps.first}',
  ];
  final unique = _uniqueStrings(reasons);
  if (unique.length < 4) {
    unique.add(_practicalRecommendation(response, train));
  }
  return unique.take(6).toList();
}

String _trainStrength(TrainRecommendation train) {
  final supported = train.useCaseVerdicts.entries
      .where((entry) => entry.value == 'pass' || entry.value == 'marginal')
      .map((entry) => _titleFromSnake(entry.key))
      .toList();
  if (supported.isNotEmpty) {
    return 'Available evidence supports ${supported.join(', ')} assessment.';
  }
  if (train.nbsComponents.isNotEmpty) {
    return '${train.nbsComponents.first['name']} supports the stated ${train.implementationRole?.toLowerCase() ?? 'treatment'} role.';
  }
  return 'Eligible for contextual comparison under current applicability rules.';
}

String _trainLimitation(TrainRecommendation train) {
  if (train.allUseCasesUnknown) {
    return 'Needs data for use-case assessment.';
  }
  if (train.caveats.isNotEmpty) {
    return train.caveats.first;
  }
  if (train.dataGaps.isNotEmpty) {
    return train.dataGaps.first;
  }
  return 'Site-specific design and monitoring validation remain required.';
}

// Retained for compatibility with older detail layouts.
// ignore: unused_element
List<String> _nextDataToCollect(
  RecommendationResponse response,
  TrainRecommendation? train,
  List<String> currentGaps,
) {
  final selected = response.inputSummary.selectedParameters
      .map((value) => value.toLowerCase())
      .toSet();
  final context = response.inputSummary.context;
  final source = context['pollution_source_type']?.toString() ?? '';
  final items = <String>[];
  final uploadedUnknown = context['uploaded_unknown_parameters'];

  if (uploadedUnknown is List && uploadedUnknown.isNotEmpty) {
    items.add(
      'Provide measured values for uploaded blank parameters: ${uploadedUnknown.map((value) => value.toString()).join(', ')}. Blanks remain unknown until measured.',
    );
  }

  if (response.inputSummary.observationCount == 0) {
    items.add(
      'Confirm recent BOD, COD, TSS, pH, nutrients, and other source-relevant values before design-level treatment assessment.',
    );
  } else {
    if (!selected.contains('cod')) {
      items.add(
        'COD is absent from the current input; measure it to clarify organic load and pretreatment demand.',
      );
    }
    if (!selected.any((value) => value == 'ammonia_n' || value == 'nh4_n') ||
        !selected.any((value) => value == 'phosphate_p' || value == 'tp')) {
      items.add(
        'NH4-N and PO4-P/TP are incomplete in the current input; collect them for nutrient-treatment design.',
      );
    }
    if (response.useCase == 'drinking' &&
        !selected.contains('faecal_coliform')) {
      items.add(
        'Faecal coliform is absent from the current input; measure it for drinking or reuse risk assessment.',
      );
    }
  }
  if (source.contains('industrial')) {
    items.add(
      'Confirm ETP/CETP availability, industrial chemistry, and upstream pH-neutralization requirements.',
    );
  }
  if (source.contains('agriculture')) {
    items.add(
      'Confirm runoff collection points, seasonal drainage, nutrient sources, erosion pathways, and edge-of-field control locations.',
    );
  }
  if (response.inputSummary.workflowMode == 'site_context_only') {
    items.add(
      'Confirm seasonal flow/discharge, drain or tributary entry points, land availability, and site slope before layout design.',
    );
  }
  for (final gap in currentGaps.take(2)) {
    items.add('Resolve reported gap: $gap');
  }
  if (train != null && train.suitablePlants.isEmpty) {
    items.add(
      'Validate locally suitable non-invasive planting and maintenance requirements for the selected components.',
    );
  }
  return _uniqueStrings(items).take(6).toList();
}

List<String> _implementationSteps(
  RecommendationResponse response,
  TrainRecommendation train,
) {
  final context = response.inputSummary.context;
  final source = context['pollution_source_type']?.toString() ?? '';
  final highOrder = context['intervention_position'] == 'in_channel' ||
      ((context['stream_order'] as num?)?.toDouble() ?? 0) >= 5;
  late final String step2;
  if (source.contains('industrial')) {
    final needsNeutralization = train.pretreatmentRequirements.any(
      (value) => value.toLowerCase().contains('neutral'),
    );
    step2 =
        'Step 2: Provide ETP/CETP treatment${needsNeutralization ? ' and pH neutralization' : ''} before any NbS unit.';
  } else if (source.contains('agriculture')) {
    step2 =
        'Step 2: Implement source control and edge-of-field nutrient, erosion, and sediment measures first.';
  } else if (highOrder) {
    step2 =
        'Step 2: Intercept drains or tributaries and establish off-channel treatment before polishing NbS.';
  } else {
    step2 = train.pretreatmentRequirements.isEmpty
        ? 'Step 2: Confirm source control and any required primary treatment.'
        : 'Step 2: Provide ${train.pretreatmentRequirements.first}';
  }
  return [
    'Step 1: Confirm source, location, flow, seasonal context, and measured water quality.',
    step2,
    'Step 3: Implement ${train.name} as ${train.implementationRole?.toLowerCase() ?? 'the selected treatment role'}.',
    'Step 4: Validate media, hydraulic design, non-invasive planting, land, and maintenance access locally.',
    'Step 5: Monitor influent, intermediate stages, effluent, hydraulic condition, and maintenance performance.',
  ];
}

List<String> _treatmentSequenceLabels(
  RecommendationResponse response,
  TrainRecommendation train,
) {
  final context = response.inputSummary.context;
  final source = context['pollution_source_type']?.toString() ?? '';
  final labels = <String>[];
  if (source.contains('industrial')) {
    labels.addAll(['Industrial source', 'ETP / CETP']);
    if (train.pretreatmentRequirements.any(
      (value) => value.toLowerCase().contains('neutral'),
    )) {
      labels.add('pH neutralization');
    }
  } else if (source.contains('agriculture')) {
    labels.addAll(['Source control', 'Collected runoff']);
  } else if (context['intervention_position'] == 'in_channel' ||
      ((context['stream_order'] as num?)?.toDouble() ?? 0) >= 5) {
    labels.addAll(['Drain / tributary interception', 'Off-channel inlet']);
  } else {
    labels.add('Source');
  }
  labels.addAll(
    train.treatmentSequence
        .map((step) => step['step_label']?.toString() ?? '')
        .where((label) => label.isNotEmpty),
  );
  labels.add('Monitoring');
  return _uniqueStrings(labels);
}

String _displayStatus(String? value) {
  return switch (value) {
    'temporary_not_expert_validated' =>
      'Final v1 AHP-Fuzzy AHP weighted TOPSIS',
    'final_v1_ahp_fuzzy_ensemble' => 'Final v1 AHP-Fuzzy AHP weighted TOPSIS',
    'expert_validated' => 'Expert validated',
    'weights_missing' => 'Weights missing',
    'invalid_weights' => 'Invalid weights',
    null || '' => 'Unknown',
    _ => _titleFromSnake(value),
  };
}

String _displayMethod(String? value) {
  return switch (value) {
    'topsis' => 'Final v1 AHP-Fuzzy AHP weighted TOPSIS',
    'rule_based_v1' => 'Rule-based confidence',
    null || '' => 'Unknown',
    _ => _titleFromSnake(value),
  };
}

String _displayConfidenceMethod(String? value) {
  return switch (value) {
    'rule_based_v1' => 'Rule-based confidence',
    null || '' => 'Data-limited confidence',
    _ => _titleFromSnake(value),
  };
}

String _confidenceMethodLabel(
  RecommendationResponse response,
  RecommendationAssemblyBundle? bundle,
) {
  if (response.inputSummary.isContextOnly) {
    return 'Context-based confidence';
  }
  if (response.inputSummary.observationCount == 0) {
    return 'Data-limited confidence';
  }
  return _displayConfidenceMethod(bundle?.confidenceMethod);
}

String _suitabilityLabel(
  String verdict, {
  required bool contextOnly,
  required bool hasMeasuredData,
}) {
  if (verdict == 'pass') return 'Suitable';
  if (verdict == 'marginal') return 'Conditional';
  if (verdict == 'fail') return 'Not suitable alone';
  if (contextOnly) {
    return 'Needs measured values';
  }
  if (!hasMeasuredData) {
    return 'Needs water-quality data';
  }
  return 'Evidence gap';
}

String _gapStatusLabel(String? status) {
  return switch (status) {
    'below_target' => 'Within selected target',
    'near_target' => 'Near target',
    'exceeds_target' => 'Exceeds selected target',
    _ => 'Used as supporting context',
  };
}

String _targetThresholdLabel(dynamic value, {String? parameter}) {
  if (value is! Map) return _missingTargetLabel(parameter);
  final low = value['limit_low'];
  final high = value['limit_high'];
  final unit = _displayUnit(value['unit']);
  if (low != null && high != null) return '$low-$high $unit'.trim();
  if (high != null) return '<= $high $unit'.trim();
  if (low != null) return '>= $low $unit'.trim();
  return _missingTargetLabel(parameter);
}

String _missingTargetLabel(String? parameter) {
  if (_isPhosphorusParameter(parameter)) {
    return 'No stored target limit for phosphate/TP under the selected use case.';
  }
  return 'Not stored for this use case';
}

String _targetGapMessage(Map<String, dynamic> row, {dynamic fallback}) {
  if (row['gap_status'] == 'not_assessed') {
    final parameter = row['parameter']?.toString();
    if (_isPhosphorusParameter(parameter)) {
      return 'No stored target limit for phosphate/TP under the selected use case.';
    }
    return 'No stored target limit is available for this parameter under the selected use case.';
  }
  final text = fallback?.toString().trim();
  if (text != null && text.isNotEmpty) return text;
  return row['gap_status'] == 'below_target'
      ? 'Target is met.'
      : 'Target is not met; treatment or adjustment is required.';
}

bool _isPhosphorusParameter(String? parameter) {
  final value = parameter?.toLowerCase();
  return value == 'phosphate_p' ||
      value == 'total_p' ||
      value == 'total_phosphorus' ||
      value == 'tp';
}

String _targetUseCaseLabel(String? value) {
  if (value == null || value.trim().isEmpty) return 'Not selected';
  return _targetUseCaseLabels[value] ?? _titleFromSnake(value);
}

String _pollutionSourceLabel(String? value) {
  return switch (value) {
    'domestic_sewage' => 'Domestic sewage',
    'high_agriculture_only_no_water_data' => 'Agricultural runoff',
    'industrial_or_mixed_industrial' => 'Industrial / mixed industrial',
    null || '' => 'Not specified',
    _ => _titleFromSnake(value),
  };
}

List<String> _sourceLocationGuidance(List<TrainRecommendation> trains) {
  final values = <String>[];
  for (final train in trains.take(3)) {
    values.addAll(train.sourceLocationGuidance);
  }
  return _uniqueStrings(values);
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

Map<String, List<Citation>> _groupCitationsForLearning(
    List<Citation> citations) {
  final grouped = <String, List<Citation>>{
    'Technical guidance': [],
    'Implementation and O&M': [],
    'Case examples': [],
    'Planting guidance': [],
  };
  for (final citation in citations) {
    final text =
        '${citation.type ?? ''} ${citation.display} ${citation.citation ?? ''}'
            .toLowerCase();
    if (text.contains('plant') || text.contains('vegetation')) {
      grouped['Planting guidance']!.add(citation);
    } else if (text.contains('case') || text.contains('example')) {
      grouped['Case examples']!.add(citation);
    } else if (text.contains('operation') ||
        text.contains('maintenance') ||
        text.contains('o&m') ||
        text.contains('om ')) {
      grouped['Implementation and O&M']!.add(citation);
    } else {
      grouped['Technical guidance']!.add(citation);
    }
  }
  return grouped;
}

String _titleFromSnake(String value) {
  return value
      .split('_')
      .where((part) => part.isNotEmpty)
      .map((part) => '${part[0].toUpperCase()}${part.substring(1)}')
      .join(' ');
}

String _criterionMapLabel(Map<String, dynamic> item) {
  final code = item['criterion_code']?.toString().trim() ?? '';
  final name = item['criterion_name']?.toString().trim() ?? '';
  final label = _criterionNameLabel(name);
  if (code.isEmpty) return label;
  if (label.isEmpty) return code;
  return '$code $label';
}

String _criterionNameLabel(String value) {
  final normalized = value.trim().toLowerCase();
  if (normalized == 'om' ||
      normalized == 'o_m' ||
      normalized == 'om_simplicity') {
    return 'O&M practicality';
  }
  if (normalized.contains('operation') && normalized.contains('maintenance')) {
    return 'O&M practicality';
  }
  if (normalized.contains('o&m')) return 'O&M practicality';
  return _titleFromSnake(value);
}

String _sentenceFromSnake(String value) {
  final text = value.replaceAll('_', ' ').trim().toLowerCase();
  if (text.isEmpty) return 'not recorded';
  return '${text[0].toUpperCase()}${text.substring(1)}';
}

String _calculationDetailLabel(String value) {
  return switch (value) {
    'area_per_person_band' => 'area-per-person band',
    'insufficient_data' => 'insufficient data',
    _ => value.replaceAll('_', '-').trim().toLowerCase(),
  };
}

String _standaloneUseLabel(String? value) => switch (value) {
      'only_as_part_of_train' => 'only as part of a treatment train',
      'can_be_standalone_source_control' => 'source-control measure only',
      'can_be_standalone' => 'possible only after design review',
      null || '' => 'use within the recommended implementation context',
      _ => _sentenceFromSnake(value),
    };

String _readinessStatusLabel(String status) => switch (status) {
      'available' => 'Available',
      'not_supplied' => 'Not supplied',
      'mapped_context_verify' =>
        'Available from mapped context; verify in field',
      'needs_field_check' => 'Needs field check',
      'missing_before_engineering_design' =>
        'Missing before engineering design',
      'not_required_for_current_screening' =>
        'Not required for current screening',
      _ => 'Status unavailable',
    };

String _coverageLabel(String? category) => switch (category) {
      'used_in_scoring' => 'Used in scoring',
      'supporting_context' => 'Used as supporting context',
      'read_not_assessed' => 'Used as supporting context',
      'skipped' => 'Not recognized / skipped',
      _ => 'Coverage not available',
    };

String _displayParameter(String? value, {String? fallback}) {
  return switch (value?.toLowerCase()) {
    'bod' => 'BOD',
    'cod' => 'COD',
    'tss' => 'TSS',
    'ph' => 'pH',
    'do' => 'DO',
    'tds' => 'TDS',
    'ec' => 'EC',
    'ammonia_n' || 'nh4_n' => 'NH4-N',
    'nitrate_n' || 'no3_n' => 'NO3-N',
    'phosphate_p' => 'PO4-P / TP',
    'total_p' || 'total_phosphorus' => 'TP',
    'faecal_coliform' || 'fecal_coliform' => 'Faecal coliform',
    'turbidity' => 'Turbidity',
    null || '' => fallback ?? 'Parameter',
    _ => fallback ?? _titleFromSnake(value!),
  };
}

String _displayUnit(dynamic value) {
  return switch (value?.toString().toLowerCase()) {
    'mg_l' || 'mg/l' => 'mg/L',
    'us_cm' || 'us/cm' || 'umho_cm' || 'umho/cm' => 'µS/cm',
    'mpn_100ml' || 'mpn/100ml' => 'MPN/100 mL',
    'ntu' => 'NTU',
    'ph' || 'ph_units' => 'pH',
    null || '' => '',
    _ => value.toString(),
  };
}

String _displayUnitSuffix(dynamic value) {
  final unit = _displayUnit(value);
  return unit.isEmpty ? '' : ' $unit';
}

String _displayInputSource(String? value) {
  return switch (value) {
    'user_csv' => 'Uploaded file',
    'manual' || 'user_measured' => 'Manual measurement',
    'canonical' || 'station_observations' => 'Station and site context',
    null || '' || 'unknown' => 'Unknown',
    _ => _titleFromSnake(value),
  };
}

String _trainConfidenceDisplay(TrainRecommendation? train) {
  if (train == null) return 'Not available';
  if (train.confidenceScore == null ||
      train.confidenceScore! <= 0 ||
      train.confidenceLabel == 'not_assessed') {
    return 'Data-limited';
  }
  return train.confidencePercent;
}

String _readableText(String value) {
  return value
      .replaceAll('temporary_not_expert_validated', 'criteria-weighted method')
      .replaceAll('topsis_closeness', 'TOPSIS closeness')
      .replaceAll('match_score', 'match score')
      .replaceAll('confidence_score', 'confidence score')
      .replaceAll(
        'rank_confidence_plants_v1',
        'rank, confidence, and plant assembly',
      )
      .replaceAll('rule_based_v1', 'rule-based confidence')
      .replaceAll('_', ' ')
      .replaceAll(';', ', ')
      .replaceAll('Only As Part Of Train', 'Only as part of a train')
      .replaceAll('Secondary Or Polishing', 'Secondary or polishing');
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
