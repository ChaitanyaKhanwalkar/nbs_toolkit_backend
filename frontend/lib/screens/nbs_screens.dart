import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/services.dart';

import '../models/recommendation_models.dart';
import '../services/recommendation_api.dart';
import '../services/recommendation_report.dart';
import '../services/report_platform.dart';
import '../theme/nbs_theme.dart';
import '../widgets/app_card.dart';
import '../widgets/nbs_diagrams.dart';

const _maxContentWidth = 1160.0;
const _csvTemplate =
    'parameter,value,unit\nBOD,30,mg/L\nCOD,100,mg/L\nTSS,80,mg/L\npH,7.2,';

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
                  title: 'Measured Water Quality',
                  description:
                      'Active - start a recommendation from lab values.',
                  icon: Icons.analytics_outlined,
                  color: NbsColors.researchBlue,
                  onTap: onStartRecommendation,
                  emphasized: true,
                ),
                _ActionCard(
                  title: 'Select Narmada Site/Station',
                  description:
                      'Choose a canonical station and load its river context.',
                  icon: Icons.place_outlined,
                  color: NbsColors.riverTeal,
                  onTap: onSelectSite,
                ),
                _ActionCard(
                  title: 'Pollution Source Screening',
                  description:
                      'Screen domestic, agricultural, or industrial context.',
                  icon: Icons.manage_search_outlined,
                  color: NbsColors.wetlandGreen,
                  onTap: onPollutionScreening,
                ),
                _ActionCard(
                  title: 'Upload Water Data',
                  description:
                      'Upload parameter, value, unit CSV data for gap analysis.',
                  icon: Icons.upload_file_outlined,
                  color: NbsColors.warningAmber,
                  onTap: onUploadWater,
                ),
              ];
              if (!isWide) {
                return Column(children: [
                  for (var index = 0; index < cards.length; index++) ...[
                    cards[index],
                    if (index != cards.length - 1) const SizedBox(height: 12),
                  ],
                ]);
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
  });

  final List<Map<String, dynamic>> observations;
  final int? regionId;
  final String? station;
  final Map<String, dynamic> context;
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
  List<SiteOption> _sites = [];
  SiteOption? _site;
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
    super.dispose();
  }

  Future<void> _chooseCsv() async {
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
        setState(() => _localError =
            'CSV could not be read. Check the file format and try again.');
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
    if (_isSiteMode && _site == null) {
      setState(() => _localError = 'Select a Narmada site/station first.');
      return;
    }
    if (_isUploadMode && _uploaded == null) {
      setState(() => _localError =
          'Upload a CSV first, or use the Measured Water Quality workflow for manual entry.');
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
      setState(() => _localError =
          'The CSV contains no numeric observations. Blank values are unknown, but at least one measured value is needed.');
      return;
    }
    widget.onRun(AnalysisInput(
      observations: observations,
      regionId: _site?.regionId,
      station: _site?.station,
      context: <String, dynamic>{
        'workflow_mode': _workflowModeKey,
        if (!_isSiteMode) 'pollution_source_type': _source,
        if (!_isSiteMode) 'intervention_position': _position,
        if (_isSiteMode && _site?.streamOrder != null)
          'stream_order': _site!.streamOrder,
        if (_isUploadMode && _uploadUnknownParameters.isNotEmpty)
          'uploaded_unknown_parameters': _uploadUnknownParameters,
        if (_isUploadMode && _csvValidation != null)
          'csv_validation_summary': _csvValidation!.toJson(),
        if (_isUploadMode && _uploadName != null)
          'uploaded_filename': _uploadName,
      },
    ));
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

  String get _modeSubtitle {
    if (_isSiteMode) {
      return 'Pick a Narmada monitoring station to run a location-context recommendation.';
    }
    if (_isPollutionMode) {
      return 'Screen source pressure and implementation position before detailed design.';
    }
    if (_isUploadMode) {
      return 'Upload a CSV with parameter, value, and unit columns for a broader water-quality panel.';
    }
    return 'Enter measured lab/field values. Leave optional fields blank if not available.';
  }

  String get _runButtonLabel {
    if (_isSiteMode) return 'Run Site Context Recommendation';
    if (_isPollutionMode) return 'Run Pollution Screening';
    if (_isUploadMode) return 'Run CSV-Based Recommendation';
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

  Widget _siteSelector() => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          DropdownButtonFormField<SiteOption>(
            initialValue: _site,
            decoration: InputDecoration(
                labelText: _loadingSites
                    ? 'Loading stations...'
                    : 'Narmada site / station',
                prefixIcon: const Icon(Icons.place_outlined)),
            items: [
              for (final site in _sites)
                DropdownMenuItem(
                    value: site,
                    child: Text('${site.station} (region ${site.regionId})'))
            ],
            onChanged: _selectSite,
          ),
          if (_pollutionCount != null)
            Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                    '$_pollutionCount canonical pollution-source records found for this region.')),
          if (_site != null) ...[
            const SizedBox(height: 8),
            Wrap(spacing: 8, runSpacing: 8, children: [
              if (_site!.streamOrder != null)
                _ContextChip(
                    label: 'Stream order', value: '${_site!.streamOrder}'),
              if (_site!.dischargeCms != null)
                _ContextChip(
                    label: 'Natural discharge',
                    value: '${_site!.dischargeCms!.toStringAsFixed(1)} m3/s'),
              if (_site!.drainageAreaKm2 != null)
                _ContextChip(
                    label: 'Drainage area',
                    value: '${_site!.drainageAreaKm2!.toStringAsFixed(0)} km2'),
            ]),
          ],
        ],
      );

  Widget _sourceAndPositionSelectors() =>
      LayoutBuilder(builder: (context, constraints) {
        final sourceField = DropdownButtonFormField<String>(
            isExpanded: true,
            initialValue: _source,
            decoration:
                const InputDecoration(labelText: 'Pollution source context'),
            items: const [
              DropdownMenuItem(
                  value: 'domestic_sewage', child: Text('Domestic sewage')),
              DropdownMenuItem(
                  value: 'high_agriculture_only_no_water_data',
                  child: Text('Agricultural runoff')),
              DropdownMenuItem(
                  value: 'industrial_or_mixed_industrial',
                  child: Text('Industrial / mixed industrial')),
            ],
            onChanged: (value) => setState(() => _source = value!));
        final positionField = DropdownButtonFormField<String>(
            isExpanded: true,
            initialValue: _position,
            decoration:
                const InputDecoration(labelText: 'Intervention position'),
            items: const [
              DropdownMenuItem(
                  value: 'off_channel_or_stp_polishing',
                  child: Text('Off-channel / STP polishing')),
              DropdownMenuItem(value: 'in_channel', child: Text('In-channel')),
              DropdownMenuItem(
                  value: 'standalone_primary_treatment',
                  child: Text('Standalone primary treatment')),
            ],
            onChanged: (value) => setState(() => _position = value!));
        if (constraints.maxWidth < 680) {
          return Column(children: [
            sourceField,
            const SizedBox(height: 12),
            positionField
          ]);
        }
        return Row(children: [
          Expanded(child: sourceField),
          const SizedBox(width: 12),
          Expanded(child: positionField)
        ]);
      });

  Widget _uploadPanel() => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          OutlinedButton.icon(
              onPressed: _uploading ? null : _chooseCsv,
              icon: const Icon(Icons.upload_file),
              label: Text(_uploading
                  ? 'Analyzing CSV...'
                  : _uploadName ?? 'Upload Water CSV')),
          const SizedBox(height: 8),
          Text('Example upload format',
              style: Theme.of(context)
                  .textTheme
                  .titleSmall
                  ?.copyWith(fontWeight: FontWeight.w800)),
          const SizedBox(height: 6),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
                color: NbsColors.deepNavy.withValues(alpha: 0.05),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: NbsColors.cardBorder)),
            child: const SelectableText(_csvTemplate,
                style: TextStyle(fontFamily: 'monospace')),
          ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: () async {
              await Clipboard.setData(const ClipboardData(text: _csvTemplate));
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
                    content: Text('Example upload format copied.')));
              }
            },
            icon: const Icon(Icons.copy_outlined),
            label: const Text('Copy template'),
          ),
          const SizedBox(height: 6),
          Text(
              'The unit column is optional for now. Values must be numeric. Blank values remain unknown and are never converted to zero.',
              style: Theme.of(context)
                  .textTheme
                  .bodySmall
                  ?.copyWith(color: NbsColors.mutedGrey)),
          const SizedBox(height: 6),
          Text(
              'Unsupported parameters and nonnumeric rows are skipped and reported below; skipped rows reduce result confidence.',
              style: Theme.of(context)
                  .textTheme
                  .bodySmall
                  ?.copyWith(color: NbsColors.mutedGrey)),
          const SizedBox(height: 6),
          Text(
              'Accepted aliases include BOD/BOD5, COD, TSS, NH4-N, NO3-N, PO4-P/TP, pH, DO, TDS, EC, turbidity, and faecal coliform/FC.',
              style: Theme.of(context)
                  .textTheme
                  .bodySmall
                  ?.copyWith(color: NbsColors.mutedGrey)),
          if (_csvValidation != null) ...[
            const SizedBox(height: 12),
            _CsvValidationPanel(
                summary: _csvValidation!, observations: _uploaded ?? const []),
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
          requiredField: false),
      _NumberField(
          controller: _cod,
          label: 'COD',
          suffix: 'mg/L',
          helper: 'Chemical oxygen demand',
          requiredField: false),
      _NumberField(
          controller: _tss,
          label: 'TSS',
          suffix: 'mg/L',
          helper: 'Suspended solids',
          requiredField: false),
      _NumberField(
          controller: _ammonia,
          label: 'NH4-N',
          suffix: 'mg/L',
          helper: 'Ammoniacal nitrogen',
          requiredField: false),
      _NumberField(
          controller: _nitrate,
          label: 'Nitrate-N',
          suffix: 'mg/L',
          helper: 'As nitrogen',
          requiredField: false),
      _NumberField(
          controller: _phosphate,
          label: 'PO4-P / TP',
          suffix: 'mg/L',
          helper: 'Phosphorus',
          requiredField: false),
      _NumberField(
          controller: _ph,
          label: 'pH',
          suffix: '',
          helper: 'Acidity / alkalinity',
          requiredField: false),
      _NumberField(
          controller: _do,
          label: 'DO',
          suffix: 'mg/L',
          helper: 'Dissolved oxygen',
          requiredField: false),
      _NumberField(
          controller: _tds,
          label: 'TDS',
          suffix: 'mg/L',
          helper: 'Dissolved solids',
          requiredField: false),
      _NumberField(
          controller: _ec,
          label: 'EC',
          suffix: 'uS/cm',
          helper: 'Conductivity',
          requiredField: false),
      _NumberField(
          controller: _turbidity,
          label: 'Turbidity',
          suffix: 'NTU',
          helper: 'Clarity indicator',
          requiredField: false),
      _NumberField(
          controller: _faecalColiform,
          label: 'Faecal coliform',
          suffix: 'MPN/100mL',
          helper: 'Pathogen indicator',
          requiredField: false),
    ];
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text('Measured water-quality panel',
          style: Theme.of(context)
              .textTheme
              .titleMedium
              ?.copyWith(fontWeight: FontWeight.w800)),
      const SizedBox(height: 6),
      Text(
          'The engine uses all filled parameters. Optional blanks are treated as unknown, not zero.',
          style: Theme.of(context)
              .textTheme
              .bodySmall
              ?.copyWith(color: NbsColors.mutedGrey)),
      const SizedBox(height: 10),
      LayoutBuilder(builder: (context, constraints) {
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
      }),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'Recommendation inputs',
      actions: [
        IconButton(onPressed: widget.onBack, icon: const Icon(Icons.close))
      ],
      child: Form(
        key: _formKey,
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(widget.mode,
              style: Theme.of(context)
                  .textTheme
                  .headlineSmall
                  ?.copyWith(fontWeight: FontWeight.w900)),
          const SizedBox(height: 6),
          Text(_modeSubtitle,
              style: Theme.of(context)
                  .textTheme
                  .bodyMedium
                  ?.copyWith(color: NbsColors.mutedGrey)),
          const SizedBox(height: 16),
          if (!_isPollutionMode) ...[
            _siteSelector(),
            const SizedBox(height: 14),
          ],
          if (!_isSiteMode) ...[
            _sourceAndPositionSelectors(),
            const SizedBox(height: 18),
          ],
          if (_isUploadMode) ...[
            _uploadPanel(),
            const SizedBox(height: 18),
          ],
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
                child: Text(_localError ?? widget.errorMessage!,
                    style: const TextStyle(color: Colors.red))),
          FilledButton.icon(
              onPressed: _submit,
              icon: const Icon(Icons.science_outlined),
              label: Text(_runButtonLabel)),
        ]),
      ),
    );
  }
}

class _CsvValidationPanel extends StatelessWidget {
  const _CsvValidationPanel(
      {required this.summary, required this.observations});

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
                .withValues(alpha: 0.28)),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(
            summary.isValid
                ? 'Uploaded water-quality data accepted'
                : 'No usable water-quality values found',
            style: const TextStyle(fontWeight: FontWeight.w900)),
        const SizedBox(height: 8),
        Wrap(spacing: 8, runSpacing: 8, children: [
          _ContextChip(label: 'Rows read', value: '${summary.rowsRead}'),
          _ContextChip(label: 'Values used', value: '${summary.rowsUsed}'),
          _ContextChip(label: 'Blank values', value: '${summary.blankValues}'),
          _ContextChip(
              label: 'Values not used',
              value:
                  '${summary.unknownParameters.length + summary.nonNumericValues.length + summary.blankParameters}'),
        ]),
        if (observations.isNotEmpty) ...[
          const SizedBox(height: 10),
          Text('Water-quality values recognized',
              style: Theme.of(context)
                  .textTheme
                  .titleSmall
                  ?.copyWith(fontWeight: FontWeight.w800)),
          const SizedBox(height: 5),
          Wrap(spacing: 8, runSpacing: 8, children: [
            for (final row in observations)
              Chip(
                  label: Text(
                      '${_displayParameter(row['parameter']?.toString(), fallback: row['display_name']?.toString())} = ${row['value']}${_displayUnitSuffix(row['unit'])}')),
          ]),
        ],
        if (messages.isNotEmpty) ...[
          const SizedBox(height: 10),
          _ReadableBulletList(values: messages),
        ],
      ]),
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
      child: Row(children: [
        Icon(icon, color: NbsColors.riverTeal),
        const SizedBox(width: 10),
        Expanded(child: Text(text)),
      ]),
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
  });

  final RecommendationResponse response;
  final ValueChanged<RecommendationItem> onViewDetail;
  final VoidCallback onNewRun;
  final VoidCallback onHome;
  final VoidCallback onAbout;

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
    final nextData = _nextDataToCollect(response, topTrain, dataGaps);
    final readiness = _designReadiness(response, topTrain);
    final practicalRecommendation =
        _practicalRecommendation(response, topTrain);
    final keyCaution = _keyCaution(response, topTrain);
    final groupedData =
        _groupDataActions(response, topTrain, dataGaps, nextData);
    final dataBasis = _dataBasis(response);

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
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('Solution Workspace',
            style: Theme.of(context)
                .textTheme
                .headlineSmall
                ?.copyWith(fontWeight: FontWeight.w900)),
        const SizedBox(height: 6),
        Text(
            'Review the recommendation by decision stage. Summary opens first.',
            style: Theme.of(context)
                .textTheme
                .bodyMedium
                ?.copyWith(color: NbsColors.mutedGrey)),
        const SizedBox(height: 14),
        _SolutionWorkspace(panels: [
          _WorkspacePanel(
            label: 'Summary',
            icon: Icons.dashboard_outlined,
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              _DetailSection(
                  title: 'What this means',
                  child: Text(practicalRecommendation,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w800, height: 1.4))),
              const SizedBox(height: 12),
              _ResultsHero(
                  response: response,
                  bundle: bundle,
                  topRecommendation: topTrain),
              const SizedBox(height: 12),
              _ResultsMetricStrip(response: response, bundle: bundle),
              const SizedBox(height: 10),
              _DataBasisCard(dataBasis: dataBasis, readiness: readiness),
              const SizedBox(height: 10),
              _DataUsedPanel(inputSummary: response.inputSummary),
              const SizedBox(height: 10),
              _PollutantGapPanel(train: topTrain),
              const SizedBox(height: 10),
              _DesignReadinessBanner(readiness: readiness),
              const SizedBox(height: 10),
              _DataConfidenceGuide(
                  train: topTrain,
                  methodLabel: _confidenceMethodLabel(response, bundle),
                  dataLimited: contextOnly || !hasMeasuredData),
              const SizedBox(height: 14),
              _ComponentSummary(train: topTrain, components: components),
              const SizedBox(height: 14),
              _DetailSection(
                  title: 'Why this recommendation?',
                  child: _ReadableBulletList(
                      values: whyReasons,
                      emptyText:
                          'A top recommendation was not available for explanation.')),
              const SizedBox(height: 14),
              _DetailSection(
                  title: 'Important limitation', child: Text(keyCaution)),
              const SizedBox(height: 14),
              _ReportExportPanel(response: response),
            ]),
          ),
          _WorkspacePanel(
            label: 'Ranking',
            icon: Icons.format_list_numbered,
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              const _DetailSection(
                  title: 'Treatment train ranking',
                  child: Text(
                      'The app ranks 8 treatment-train options. Individual NbS components and plant guidance are shown within each train and in the NbS & Plants panel.')),
              if (trains.isNotEmpty) ...[
                const SizedBox(height: 12),
                _DetailSection(
                    title: 'Top-three comparison',
                    child: _TopTrainComparison(trains: trains.take(3).toList()))
              ],
              const SizedBox(height: 12),
              for (final train in trains)
                Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: TrainRecommendationCard(
                        train: train,
                        contextOnly: contextOnly,
                        hasMeasuredData: hasMeasuredData,
                        citationsById: response.citationsById)),
            ]),
          ),
          _WorkspacePanel(
            label: 'Implementation',
            icon: Icons.construction_outlined,
            child: _ImplementationWorkspace(
                response: response,
                train: topTrain,
                sourceLocationGuidance: sourceLocationGuidance),
          ),
          _WorkspacePanel(
            label: 'NbS Components',
            icon: Icons.spa_outlined,
            child: _NbsComponentsWorkspace(
              train: topTrain,
              components: components,
              filteredComponents: response.filteredComponents,
              citationsById: response.citationsById,
            ),
          ),
          _WorkspacePanel(
            label: 'Data gaps',
            icon: Icons.fact_check_outlined,
            child: _DataGapsWorkspace(
                response: response, groupedData: groupedData),
          ),
          _WorkspacePanel(
            label: 'Evidence & method',
            icon: Icons.science_outlined,
            child: _EvidenceWorkspace(
                response: response, bundle: bundle, train: topTrain),
          ),
        ]),
        const SizedBox(height: 14),
        OutlinedButton.icon(
            onPressed: onNewRun,
            icon: const Icon(Icons.restart_alt),
            label: const Text('Run Another Recommendation')),
      ]),
    );
  }
}

class _WorkspacePanel {
  const _WorkspacePanel(
      {required this.label, required this.icon, required this.child});

  final String label;
  final IconData icon;
  final Widget child;
}

class _SolutionWorkspace extends StatefulWidget {
  const _SolutionWorkspace({required this.panels});

  final List<_WorkspacePanel> panels;

  @override
  State<_SolutionWorkspace> createState() => _SolutionWorkspaceState();
}

class _SolutionWorkspaceState extends State<_SolutionWorkspace> {
  int selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    final selected = widget.panels[selectedIndex];
    return LayoutBuilder(builder: (context, constraints) {
      if (constraints.maxWidth >= 900) {
        return Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          SizedBox(
            width: 210,
            child: Column(children: [
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
                                child: Text(widget.panels[index].label)))
                        : TextButton.icon(
                            onPressed: () =>
                                setState(() => selectedIndex = index),
                            icon: Icon(widget.panels[index].icon),
                            label: Align(
                                alignment: Alignment.centerLeft,
                                child: Text(widget.panels[index].label))),
                  ),
                ),
            ]),
          ),
          const SizedBox(width: 18),
          Expanded(child: selected.child),
        ]);
      }
      return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(children: [
            for (var index = 0; index < widget.panels.length; index++) ...[
              ChoiceChip(
                selected: index == selectedIndex,
                avatar: Icon(widget.panels[index].icon, size: 17),
                label: Text(widget.panels[index].label),
                onSelected: (_) => setState(() => selectedIndex = index),
              ),
              const SizedBox(width: 7),
            ],
          ]),
        ),
        const SizedBox(height: 14),
        selected.child,
      ]);
    });
  }
}

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
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Data basis',
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(fontWeight: FontWeight.w900)),
          const SizedBox(height: 10),
          Wrap(spacing: 9, runSpacing: 9, children: [
            StatusPill(
                label: 'Data basis',
                value: dataBasis.basis,
                color: NbsColors.researchBlue),
            StatusPill(
                label: 'Water-quality input',
                value: dataBasis.currentSample,
                color: NbsColors.riverTeal),
            StatusPill(
                label: 'Design readiness',
                value: readiness.label,
                color: NbsColors.warningAmber),
            StatusPill(
                label: 'Why this confidence level',
                value: dataBasis.confidenceBasis,
                color: NbsColors.wetlandGreen),
          ]),
        ]),
      );
}

class _DataUsedPanel extends StatelessWidget {
  const _DataUsedPanel({required this.inputSummary});

  final RecommendationInputSummary inputSummary;

  @override
  Widget build(BuildContext context) {
    final rows = inputSummary.dataUsed;
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
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('Source: $sourceLabel',
            style: const TextStyle(fontWeight: FontWeight.w800)),
        const SizedBox(height: 8),
        if (rows.isEmpty)
          const Text(
              'No recent water-quality file was supplied. Station and site context supports early screening where available.')
        else if (rows.length > 4)
          ExpansionTile(
            tilePadding: EdgeInsets.zero,
            childrenPadding: const EdgeInsets.only(bottom: 8),
            title: Text('${rows.length} water-quality values recognized',
                style: const TextStyle(fontWeight: FontWeight.w800)),
            subtitle: const Text('View values'),
            children: [_WaterValueChips(rows: rows)],
          )
        else
          _WaterValueChips(rows: rows),
        if (inputSummary.workflowMode == 'uploaded_water_quality' &&
            rows.isNotEmpty) ...[
          const SizedBox(height: 10),
          Text(
            'Uploaded values feed pollutant-gap calculations. Similar scores can still occur when different files produce the same standards gap, evidence coverage, and applicability context.',
            style: Theme.of(context)
                .textTheme
                .bodySmall
                ?.copyWith(color: NbsColors.mutedGrey),
          ),
        ],
      ]),
    );
  }
}

class _PollutantGapPanel extends StatelessWidget {
  const _PollutantGapPanel({required this.train});

  final TrainRecommendation? train;

  @override
  Widget build(BuildContext context) {
    final rows = train?.pollutantGapBreakdown ?? const <Map<String, dynamic>>[];
    return _DetailSection(
      title: 'Pollutant gaps and train coverage',
      child: rows.isEmpty
          ? const Text(
              'No usable water-quality values were available for target comparison.')
          : Column(children: [
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
                        Wrap(spacing: 8, runSpacing: 8, children: [
                          StatusPill(
                            label: 'Target status',
                            value:
                                _gapStatusLabel(row['gap_status']?.toString()),
                            color: row['gap_status'] == 'exceeds_target'
                                ? NbsColors.warningAmber
                                : NbsColors.wetlandGreen,
                          ),
                          StatusPill(
                              label: 'Use-case target',
                              value: _targetThresholdLabel(
                                  row['target_threshold'])),
                          StatusPill(
                              label: 'Input source',
                              value: _displayInputSource(
                                  row['source']?.toString())),
                          StatusPill(
                            label: 'Train evidence',
                            value: row['train_addresses_parameter'] == true
                                ? 'Addresses parameter'
                                : 'Not demonstrated',
                            color: row['train_addresses_parameter'] == true
                                ? NbsColors.wetlandGreen
                                : NbsColors.warningAmber,
                          ),
                        ]),
                        const SizedBox(height: 6),
                        Text(row['severity']?.toString() ?? 'Not assessed.',
                            style: Theme.of(context).textTheme.bodySmall),
                      ]),
                ),
            ]),
    );
  }
}

class _WaterValueChips extends StatelessWidget {
  const _WaterValueChips({required this.rows});

  final List<Map<String, dynamic>> rows;

  @override
  Widget build(BuildContext context) =>
      Wrap(spacing: 8, runSpacing: 8, children: [
        for (final row in rows)
          Chip(
            avatar: const Icon(Icons.science_outlined, size: 16),
            label: Text(
              '${_displayParameter(row['parameter']?.toString(), fallback: row['display_name']?.toString())} = ${row['value']}${_displayUnitSuffix(row['unit'])}',
            ),
          ),
      ]);
}

class _DesignReadinessBanner extends StatelessWidget {
  const _DesignReadinessBanner({required this.readiness});

  final ({String label, String reason}) readiness;

  @override
  Widget build(BuildContext context) => Container(
        width: double.infinity,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: NbsColors.warningAmber.withValues(alpha: 0.08),
          borderRadius: BorderRadius.circular(8),
          border:
              Border.all(color: NbsColors.warningAmber.withValues(alpha: 0.28)),
        ),
        child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Icon(Icons.engineering_outlined, color: NbsColors.warningAmber),
          const SizedBox(width: 10),
          Expanded(
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                Text('Design readiness: ${readiness.label}',
                    style: const TextStyle(fontWeight: FontWeight.w800)),
                const SizedBox(height: 4),
                Text(readiness.reason),
              ])),
        ]),
      );
}

class _ImplementationWorkspace extends StatelessWidget {
  const _ImplementationWorkspace(
      {required this.response,
      required this.train,
      required this.sourceLocationGuidance});

  final RecommendationResponse response;
  final TrainRecommendation? train;
  final List<String> sourceLocationGuidance;

  @override
  Widget build(BuildContext context) {
    final selectedTrain = train;
    if (selectedTrain == null) {
      return const Text(
          'No treatment train is available for implementation planning.');
    }
    final highOrder = response.inputSummary.context['intervention_position'] ==
            'in_channel' ||
        ((response.inputSummary.context['stream_order'] as num?)?.toDouble() ??
                0) >=
            5;
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      _DetailSection(
          title: 'What to do first',
          child: _ReadableBulletList(
              values: sourceLocationGuidance,
              emptyText: _implementationSteps(response, selectedTrain).first)),
      const SizedBox(height: 14),
      _DetailSection(
          title: 'What not to do',
          child: _ReadableBulletList(
              values: _whatNotToDo(response, selectedTrain))),
      const SizedBox(height: 14),
      _DetailSection(
          title: 'Implementation pathway',
          child:
              _ImplementationPathway(response: response, train: selectedTrain)),
      const SizedBox(height: 14),
      _DetailSection(
          title: 'Recommended treatment sequence',
          child: _TreatmentSequenceVisual(
              response: response, train: selectedTrain)),
      const SizedBox(height: 14),
      if (highOrder) ...[
        const _DetailSection(
            title: 'Mainstem safety schematic',
            child: NbsDiagramCard(kind: NbsDiagramKind.mainstemOffChannel)),
        const SizedBox(height: 14),
      ],
      _DetailSection(
          title: 'Monitoring points',
          child: _ReadableBulletList(values: _monitoringPoints(selectedTrain))),
    ]);
  }
}

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
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('Primary treatment train: ${train?.name ?? 'Not available'}',
            style: const TextStyle(fontWeight: FontWeight.w900)),
        const SizedBox(height: 8),
        _ReadableBulletList(
          values: [
            for (final item in supporting)
              '${item.name} - ${_titleFromSnake(item.role)}'
          ],
          emptyText: 'No supporting component screen is available.',
        ),
        if (limited.isNotEmpty) ...[
          const SizedBox(height: 8),
          Text(
              'Not suitable alone: ${limited.map((item) => item.name).join(', ')}.',
              style: Theme.of(context)
                  .textTheme
                  .bodySmall
                  ?.copyWith(color: NbsColors.mutedGrey)),
        ],
      ]),
    );
  }
}

class _NbsComponentsWorkspace extends StatelessWidget {
  const _NbsComponentsWorkspace(
      {required this.train,
      required this.components,
      required this.filteredComponents,
      required this.citationsById});

  final TrainRecommendation? train;
  final List<IndividualNbsRecommendation> components;
  final List<Map<String, dynamic>> filteredComponents;
  final Map<int, Citation> citationsById;

  @override
  Widget build(BuildContext context) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      _DetailSection(
        title: 'How to read this section',
        child: Text(
            'The primary recommendation is the treatment train ${train?.name ?? ''}. Individual NbS options below are supporting components and do not replace that train.'),
      ),
      const SizedBox(height: 14),
      if (components.isEmpty)
        const Text('No individual NbS component passed the current screening.')
      else
        for (final component in components.take(10))
          Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: _IndividualNbsCard(
                  component: component, citationsById: citationsById)),
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
            child: _LearningPlaceholder(train: train!)),
      ],
    ]);
  }
}

class _IndividualNbsCard extends StatelessWidget {
  const _IndividualNbsCard(
      {required this.component, required this.citationsById});

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
        title: Text(component.name,
            style: const TextStyle(fontWeight: FontWeight.w900)),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 8),
          child: Wrap(spacing: 8, runSpacing: 8, children: [
            _MetricChip(
                label: 'Role',
                value: _titleFromSnake(component.role),
                color: NbsColors.riverTeal),
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
                color: NbsColors.warningAmber),
          ]),
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
                  _displayParameter(value)
              ],
              emptyText: 'No pollutant-specific removal record is available.'),
          const SizedBox(height: 12),
          _TextBlockList(
              title: 'Where suitable',
              values: component.whereSuitable,
              emptyText: 'Site suitability requires local validation.'),
          const SizedBox(height: 12),
          _TextBlockList(
              title: 'Where not suitable',
              values: component.whereNotSuitable,
              emptyText: 'No additional context exclusion was returned.'),
          const SizedBox(height: 12),
          _TextBlockList(
              title: 'Key constraints',
              values: component.keyConstraints,
              emptyText: 'No component-specific constraint was returned.'),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Plant links',
            values: [
              for (final plant in component.plants)
                plant['plant_species']?.toString() ?? 'Catalogue plant'
            ],
            emptyText: component.plantingGuidance,
          ),
          const SizedBox(height: 12),
          _EvidenceDisclosure(
              sourceIds: component.sourceIds, citationsById: citationsById),
        ],
      ),
    );
  }
}

class _DataGapsWorkspace extends StatelessWidget {
  const _DataGapsWorkspace({required this.response, required this.groupedData});

  final RecommendationResponse response;
  final Map<String, List<String>> groupedData;

  @override
  Widget build(BuildContext context) =>
      Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        if (response.inputSummary.isContextOnly) ...[
          const _AlertBanner.compact(
              icon: Icons.info_outline,
              color: NbsColors.warningAmber,
              title: 'Water-quality input',
              message:
                  'Water-quality input not supplied. Screening uses canonical site/source context; recent measured values are recommended before design.'),
          const SizedBox(height: 14),
        ],
        _DetailSection(
            title: 'Required before design',
            child: _ReadableBulletList(
                values: groupedData['required'] ?? const [],
                emptyText:
                    'No mandatory design input was identified from this payload.')),
        const SizedBox(height: 14),
        _DetailSection(
            title: 'Useful for better ranking',
            child: _ReadableBulletList(
                values: groupedData['ranking'] ?? const [],
                emptyText: 'No additional ranking input was identified.')),
        const SizedBox(height: 14),
        _DetailSection(
            title: 'Site / design checks',
            child: _ReadableBulletList(
                values: groupedData['site'] ?? const [],
                emptyText:
                    'Complete normal site survey and preliminary design checks.')),
        if (response.exceedances.isNotEmpty) ...[
          const SizedBox(height: 14),
          _DetailSection(
              title: 'Detected standard exceedances',
              child: _ReadableBulletList(values: [
                for (final exceedance in response.exceedances)
                  exceedance.summary
              ])),
        ],
      ]);
}

class _EvidenceWorkspace extends StatelessWidget {
  const _EvidenceWorkspace(
      {required this.response, required this.bundle, required this.train});

  final RecommendationResponse response;
  final RecommendationAssemblyBundle? bundle;
  final TrainRecommendation? train;

  @override
  Widget build(BuildContext context) =>
      Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        _DetailSection(
            title: 'Method',
            child: _ReadableBulletList(values: [
              'A0 applicability screening checks placement and safety constraints before ranking.',
              'Criteria-weighted TOPSIS compares eligible treatment trains.',
              'Confidence uses ${_confidenceMethodLabel(response, bundle).toLowerCase()} and is reported separately from rank.',
              'Research-stage comparison weights require expert calibration.',
            ])),
        const SizedBox(height: 14),
        _DetailSection(
            title: 'Scientific criteria values',
            child: _TextBlockList(
                title: 'Top-train criteria',
                values: [
                  for (final item in train?.criteriaBreakdown ??
                      const <Map<String, dynamic>>[])
                    '${item['criterion_code']} ${_titleFromSnake(item['criterion_name']?.toString() ?? '')}: ${item['data_status'] == 'known' ? ((item['normalized_value'] as num?)?.toDouble() ?? 0).toStringAsFixed(3) : 'Evidence gap'}'
                ],
                emptyText: 'No criteria values are available.')),
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
            child: _ReadableBulletList(values: [
              'This tool supports decision-making and option screening.',
              'It does not replace expert engineering design, site survey, regulatory approval, or monitoring plans.',
              'Health-risk classification requires separate expert data and validation.',
            ])),
      ]);
}

class _ReportExportPanel extends StatelessWidget {
  const _ReportExportPanel({required this.response});

  final RecommendationResponse response;

  Future<void> _copy(BuildContext context, String text, String message) async {
    await Clipboard.setData(ClipboardData(text: text));
    if (context.mounted) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(message)));
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
          context, content, '$label prepared and copied to the clipboard.');
    } else if (context.mounted) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('$label downloaded.')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final report = RecommendationReport.fromResponse(response);
    return _DetailSection(
      title: 'Report and export',
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Review, copy, or download this planning-level result.'),
        const SizedBox(height: 10),
        Wrap(spacing: 8, runSpacing: 8, children: [
          OutlinedButton.icon(
            onPressed: () => _showReportPreview(context, response, report),
            icon: const Icon(Icons.preview_outlined),
            label: const Text('Report preview'),
          ),
          OutlinedButton.icon(
            onPressed: () => _copy(
                context, report.summary, 'Recommendation summary copied.'),
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
        ]),
      ]),
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
        child: Column(children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 12, 10),
            child: Row(children: [
              Expanded(
                child: Text('Planning-level report preview',
                    style: Theme.of(dialogContext)
                        .textTheme
                        .titleLarge
                        ?.copyWith(fontWeight: FontWeight.w900)),
              ),
              IconButton(
                tooltip: 'Close report preview',
                onPressed: () => Navigator.of(dialogContext).pop(),
                icon: const Icon(Icons.close),
              ),
            ]),
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
                      final opened = printReportPage();
                      ScaffoldMessenger.of(dialogContext).showSnackBar(SnackBar(
                        content: Text(opened
                            ? 'Use the browser print dialog to save as PDF.'
                            : 'Browser print is available in the web app.'),
                      ));
                    },
                    icon: const Icon(Icons.print_outlined),
                    label: const Text('Print / save as PDF'),
                  ),
                  FilledButton(
                      onPressed: () => Navigator.of(dialogContext).pop(),
                      child: const Text('Done')),
                ]),
          ),
        ]),
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
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text('Narmada NbS recommendation',
          style: Theme.of(context)
              .textTheme
              .headlineSmall
              ?.copyWith(fontWeight: FontWeight.w900)),
      const SizedBox(height: 4),
      const Text(
          'Method: criteria-weighted TOPSIS after applicability screening'),
      const SizedBox(height: 16),
      _TextBlockList(
        title: 'Project and input summary',
        values: [
          'Workflow: ${_titleFromSnake(response.inputSummary.workflowMode ?? 'available inputs')}',
          'Use case: ${_titleFromSnake(response.useCase ?? 'not specified')}',
          '${values.length} water-quality values used.',
        ],
        emptyText: 'No project input summary is available.',
      ),
      const SizedBox(height: 14),
      _TextBlockList(
        title: 'Recommended treatment train',
        values: train == null
            ? const ['No ranked treatment train is available.']
            : [
                train.name,
                'Technical match: ${train.matchPercent}',
                'Result confidence: ${_trainConfidenceDisplay(train)}',
                if (train.implementationRole != null)
                  'Role: ${train.implementationRole}',
              ],
        emptyText: 'No ranked treatment train is available.',
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
          for (final row
              in train?.pollutantGapBreakdown ?? const <Map<String, dynamic>>[])
            '${_displayParameter(row['parameter']?.toString())}: ${_gapStatusLabel(row['gap_status']?.toString())}',
        ],
        emptyText: 'No pollutant-gap comparison is available.',
      ),
      const SizedBox(height: 14),
      _TextBlockList(
        title: 'Individual NbS components',
        values: [
          for (final item in response.componentRecommendations)
            '${item.name} - ${_titleFromSnake(item.role)}'
        ],
        emptyText: 'No supporting component passed the current screen.',
      ),
      const SizedBox(height: 14),
      _TextBlockList(
        title: 'Use-case suitability',
        values: [
          for (final entry in train?.useCaseVerdicts.entries ??
              const <MapEntry<String, String>>[])
            '${_titleFromSnake(entry.key)}: ${_titleFromSnake(entry.value)}'
        ],
        emptyText: 'Use-case suitability could not be concluded.',
      ),
      const SizedBox(height: 14),
      _TextBlockList(
          title: 'Important limitations',
          values: train?.caveats ?? const [],
          emptyText: 'No additional train-specific limitation is recorded.'),
      const SizedBox(height: 14),
      _TextBlockList(
          title: 'Data gaps',
          values: _uniqueStrings([...response.globalGaps, ...?train?.dataGaps]),
          emptyText: 'No data gaps were reported.'),
      const SizedBox(height: 14),
      _TextBlockList(
          title: 'Evidence records',
          values: [
            for (final citation in response.citations)
              '${citation.id}: ${citation.display}'
          ],
          emptyText: 'No resolved evidence record is available.'),
      const SizedBox(height: 16),
      Text(report.payload['disclaimer'].toString(),
          style: Theme.of(context)
              .textTheme
              .bodySmall
              ?.copyWith(fontWeight: FontWeight.w700)),
    ]);
  }
}

class TrainRecommendationCard extends StatelessWidget {
  const TrainRecommendationCard({
    super.key,
    required this.train,
    required this.contextOnly,
    required this.hasMeasuredData,
    required this.citationsById,
  });

  final TrainRecommendation train;
  final bool contextOnly;
  final bool hasMeasuredData;
  final Map<int, Citation> citationsById;

  @override
  Widget build(BuildContext context) {
    final verdictColors = {
      'pass': NbsColors.wetlandGreen,
      'marginal': NbsColors.warningAmber,
      'fail': Colors.red.shade700,
      'unknown': NbsColors.mutedGrey,
    };
    return AppCard(
      padding: EdgeInsets.zero,
      borderColor: train.applicabilityStatus == 'conditional'
          ? NbsColors.warningAmber.withValues(alpha: 0.45)
          : NbsColors.researchBlue.withValues(alpha: 0.16),
      child: ExpansionTile(
        tilePadding: const EdgeInsets.all(14),
        childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        leading: _RankBlock(rank: train.rank),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(train.name,
                style: const TextStyle(fontWeight: FontWeight.w900)),
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
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Wrap(spacing: 8, runSpacing: 8, children: [
              _MetricChip(
                  label: 'Technical match',
                  value: train.matchPercent,
                  color: NbsColors.researchBlue),
              _MetricChip(
                  label: 'Result confidence',
                  value: _trainConfidenceDisplay(train),
                  color: NbsColors.wetlandGreen),
              if (train.allUseCasesUnknown)
                const _MetricChip(
                    label: 'Data gap',
                    value: 'Needs data for use-case assessment',
                    color: NbsColors.warningAmber),
              for (final entry in train.useCaseVerdicts.entries)
                Tooltip(
                  message: entry.value == 'unknown'
                      ? 'This use case cannot be concluded without current water-quality input or sufficient evidence.'
                      : '${_titleFromSnake(entry.key)} suitability from available canonical evidence.',
                  child: _MetricChip(
                    label: '${_titleFromSnake(entry.key)} suitability',
                    value: _suitabilityLabel(entry.value,
                        contextOnly: contextOnly,
                        hasMeasuredData: hasMeasuredData),
                    color: verdictColors[entry.value] ?? NbsColors.mutedGrey,
                  ),
                ),
            ]),
            const SizedBox(height: 8),
            Text(_trainStrength(train),
                maxLines: 2, overflow: TextOverflow.ellipsis),
          ]),
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
              emptyText: 'No explanation returned.'),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Key pretreatment / conditions',
            values: _uniqueStrings(
                [...train.pretreatmentRequirements, ...train.caveats.take(2)]),
            emptyText: 'No additional train-specific condition is recorded.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Treatment sequence',
            values: [
              for (final step in train.treatmentSequence)
                '${step['step_order']}. ${step['step_label']} (${step['role'] ?? 'step'})'
            ],
            emptyText: 'No treatment sequence returned.',
          ),
          const SizedBox(height: 12),
          _PollutantGapPanel(train: train),
          const SizedBox(height: 12),
          _TextBlockList(
            title: 'Why this confidence level',
            values: train.confidenceExplanation,
            emptyText: 'No confidence explanation was returned.',
          ),
          const SizedBox(height: 12),
          _EvidenceDisclosure(
              sourceIds: train.sourceIds, citationsById: citationsById),
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
        ? 'Data-limited confidence: canonical source/site context is available; a recent user-supplied sample would strengthen design-level confirmation.'
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
        border:
            Border.all(color: NbsColors.wetlandGreen.withValues(alpha: 0.18)),
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
                  style: Theme.of(context)
                      .textTheme
                      .bodySmall
                      ?.copyWith(height: 1.4),
                ),
                if ((train?.confidenceExplanation.length ?? 0) > 1) ...[
                  const SizedBox(height: 6),
                  Text(
                    train!.confidenceExplanation.skip(1).join(' '),
                    style: Theme.of(context)
                        .textTheme
                        .bodySmall
                        ?.copyWith(height: 1.4, color: NbsColors.mutedGrey),
                  ),
                ],
                const SizedBox(height: 8),
                const Text(
                  'Technical match = how well the train fits the supplied problem and context.\nResult confidence = how reliable this result is based on data completeness, evidence coverage, and context quality.',
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
    return LayoutBuilder(builder: (context, constraints) {
      final width = constraints.maxWidth >= 1050
          ? (constraints.maxWidth - 20) / 3
          : constraints.maxWidth >= 680
              ? (constraints.maxWidth - 10) / 2
              : constraints.maxWidth;
      return Wrap(spacing: 10, runSpacing: 10, children: [
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
                      : NbsColors.cardBorder),
            ),
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('#${train.rank}  ${train.name}',
                  style: const TextStyle(fontWeight: FontWeight.w900)),
              const SizedBox(height: 8),
              Wrap(spacing: 7, runSpacing: 7, children: [
                _MetricChip(
                    label: 'Technical match',
                    value: train.matchPercent,
                    color: NbsColors.researchBlue),
                _MetricChip(
                    label: 'Result confidence',
                    value: _trainConfidenceDisplay(train),
                    color: NbsColors.wetlandGreen),
              ]),
              const SizedBox(height: 8),
              Text('Role',
                  style: Theme.of(context)
                      .textTheme
                      .labelMedium
                      ?.copyWith(fontWeight: FontWeight.w800)),
              Text(train.implementationRole ?? 'Role requires review'),
              const SizedBox(height: 8),
              Text('Main strength',
                  style: Theme.of(context)
                      .textTheme
                      .labelMedium
                      ?.copyWith(fontWeight: FontWeight.w800)),
              Text(_trainStrength(train)),
              const SizedBox(height: 8),
              Text('Main limitation',
                  style: Theme.of(context)
                      .textTheme
                      .labelMedium
                      ?.copyWith(fontWeight: FontWeight.w800)),
              Text(_trainLimitation(train)),
              if (train.allUseCasesUnknown) ...[
                const SizedBox(height: 8),
                const Text('Needs data for use-case assessment',
                    style: TextStyle(
                        color: NbsColors.warningAmber,
                        fontWeight: FontWeight.w800)),
              ],
            ]),
          ),
      ]);
    });
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
                  child: Text('${index + 1}',
                      style: const TextStyle(fontWeight: FontWeight.w800)),
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
                size: 16),
            label: Text(labels[index]),
          ),
          if (index != labels.length - 1)
            const Icon(Icons.arrow_forward,
                size: 18, color: NbsColors.mutedGrey),
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
            'Planting guidance requires local validation.',
      );
    }
    final grouped = _groupPlantMappings(train.suitablePlants);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (final group in grouped.entries) ...[
          Text(group.key,
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w900, color: NbsColors.riverTeal)),
          const SizedBox(height: 8),
          Wrap(spacing: 10, runSpacing: 10, children: [
            for (final plant in group.value)
              Container(
                width: 290,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: NbsColors.wetlandGreen.withValues(alpha: 0.05),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                      color: NbsColors.wetlandGreen.withValues(alpha: 0.18)),
                ),
                child: Builder(builder: (context) {
                  final names = _plantNames(plant['plant_species']?.toString());
                  return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(names.commonName,
                            style:
                                const TextStyle(fontWeight: FontWeight.w900)),
                        if (names.scientificName != null)
                          Text(names.scientificName!,
                              style:
                                  const TextStyle(fontStyle: FontStyle.italic)),
                        const SizedBox(height: 6),
                        if (plant['native_status'] != null)
                          Text(
                              'Status: ${_titleFromSnake(plant['native_status'].toString())} / non-invasive mapping'),
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
                                ?.copyWith(color: NbsColors.mutedGrey)),
                      ]);
                }),
              ),
          ]),
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
  const _LearningPlaceholder({required this.train});

  final TrainRecommendation train;

  @override
  Widget build(BuildContext context) {
    const items = [
      (
        Icons.account_tree_outlined,
        'Treatment sequence',
        'Open the train-specific treatment flow.',
        'sequence'
      ),
      (
        Icons.layers_outlined,
        'Schematic / cross-section',
        'Open a built-in conceptual treatment cross-section.',
        'schematic'
      ),
      (
        Icons.info_outline,
        'Component explanation',
        'Review component function, placement, and maintenance.',
        'components'
      ),
      (
        Icons.grass_outlined,
        'Planting zones',
        'Review grouped, deduplicated non-invasive plant mappings.',
        'plants'
      ),
      (
        Icons.menu_book_outlined,
        'Curated references',
        'Review the source-review structure for future links.',
        'references'
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
                    color: NbsColors.researchBlue.withValues(alpha: 0.14)),
              ),
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(children: [
                      Icon(item.$1, size: 20, color: NbsColors.researchBlue),
                      const Spacer(),
                      const Icon(Icons.open_in_new, size: 16)
                    ]),
                    const SizedBox(height: 8),
                    Text(item.$2,
                        style: const TextStyle(fontWeight: FontWeight.w800)),
                    const SizedBox(height: 5),
                    Text(item.$3,
                        style: Theme.of(context)
                            .textTheme
                            .bodySmall
                            ?.copyWith(color: NbsColors.mutedGrey)),
                  ]),
            ),
          ),
      ],
    );
  }

  Future<void> _openLearningPanel(
      BuildContext context, String title, String topic) {
    return showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 880),
          child: SingleChildScrollView(
              child: _LearningDetail(topic: topic, train: train)),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Close'))
        ],
      ),
    );
  }
}

class _LearningDetail extends StatelessWidget {
  const _LearningDetail({required this.topic, required this.train});

  final String topic;
  final TrainRecommendation train;

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
      _ => const _CuratedReferencesPlaceholder(),
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
      'Monitoring'
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
                    size: 16),
                label: Text(labels[index])),
            if (index != labels.length - 1)
              const Icon(Icons.arrow_forward,
                  size: 18, color: NbsColors.mutedGrey),
          ],
        ]);
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
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      const Text(
          'Conceptual cross-section only. Dimensions, media, hydraulics, and planting require site-specific design.'),
      const SizedBox(height: 14),
      SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(children: [
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
                  border: Border.all(color: NbsColors.cardBorder)),
              child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(stages[index].$1, color: NbsColors.deepNavy),
                    const SizedBox(height: 7),
                    Text(stages[index].$2,
                        textAlign: TextAlign.center,
                        style: const TextStyle(fontWeight: FontWeight.w800)),
                    const SizedBox(height: 3),
                    Text(stages[index].$3,
                        textAlign: TextAlign.center,
                        style: Theme.of(context).textTheme.bodySmall)
                  ]),
            ),
            if (index != stages.length - 1)
              const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 6),
                  child: Icon(Icons.arrow_forward, color: NbsColors.mutedGrey)),
          ],
        ]),
      ),
    ]);
  }
}

class _ComponentExplanationList extends StatelessWidget {
  const _ComponentExplanationList({required this.train});

  final TrainRecommendation train;

  @override
  Widget build(BuildContext context) {
    if (train.nbsComponents.isEmpty) {
      return const Text(
          'No linked NbS components are available for explanation.');
    }
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      for (final component in train.nbsComponents) ...[
        Text(component['name']?.toString() ?? 'NbS component',
            style: Theme.of(context)
                .textTheme
                .titleSmall
                ?.copyWith(fontWeight: FontWeight.w900)),
        const SizedBox(height: 5),
        Text(_componentExplanation(component, train)),
        const Divider(height: 22),
      ],
    ]);
  }
}

class _CuratedReferencesPlaceholder extends StatelessWidget {
  const _CuratedReferencesPlaceholder();

  @override
  Widget build(BuildContext context) {
    const sections = [
      'Implementation photos',
      'Technical guidance',
      'Case examples',
      'Videos / learning links'
    ];
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      const Text('Curated links will be added after source review.'),
      const SizedBox(height: 12),
      for (final section in sections)
        ListTile(
            contentPadding: EdgeInsets.zero,
            leading: const Icon(Icons.pending_actions_outlined),
            title: Text(section),
            subtitle: const Text('Source review pending')),
    ]);
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
                label: 'Technical match',
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
                      'Technical match uses TOPSIS; result confidence is calculated separately.',
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
                                  label: 'Technical match',
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
                        label: 'Technical match',
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
      for (final citation in citations) citation.id: citation
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
                        label: 'Technical match', value: item.matchPercent),
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
                    'Technical match is TOPSIS closeness for the supplied problem and context.',
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
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('Canonical learning workspace',
            style: Theme.of(context)
                .textTheme
                .headlineSmall
                ?.copyWith(fontWeight: FontWeight.w900)),
        const SizedBox(height: 6),
        Text(
            'Explore stored treatment sequences, component evidence, planting mappings, monitoring, and O&M notes.',
            style: Theme.of(context)
                .textTheme
                .bodyMedium
                ?.copyWith(color: NbsColors.mutedGrey)),
        const SizedBox(height: 14),
        Wrap(spacing: 8, runSpacing: 8, children: [
          ChoiceChip(
              label: const Text('Treatment Trains'),
              avatar: const Icon(Icons.account_tree_outlined, size: 17),
              selected: _section == 0,
              onSelected: (_) => setState(() => _section = 0)),
          ChoiceChip(
              label: const Text('NbS Components'),
              avatar: const Icon(Icons.water_outlined, size: 17),
              selected: _section == 1,
              onSelected: (_) => setState(() => _section = 1)),
          ChoiceChip(
              label: const Text('Plants'),
              avatar: const Icon(Icons.grass_outlined, size: 17),
              selected: _section == 2,
              onSelected: (_) => setState(() => _section = 2)),
        ]),
        const SizedBox(height: 12),
        TextField(
          decoration: const InputDecoration(
              prefixIcon: Icon(Icons.search), labelText: 'Search catalogue'),
          onChanged: (value) => setState(() => _query = value),
        ),
        const SizedBox(height: 14),
        if (_error != null)
          _AlertBanner.compact(
              icon: Icons.error_outline,
              color: Colors.red,
              title: 'Catalogue unavailable',
              message: _error!)
        else if (_catalogue == null)
          const Center(
              child: Padding(
                  padding: EdgeInsets.all(28),
                  child: CircularProgressIndicator()))
        else if (rows.isEmpty)
          const _DetailSection(
              title: 'No catalogue matches',
              child: Text('Try a broader search term.'))
        else if (_section == 0)
          for (final row in rows)
            Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child:
                    _TrainCatalogueCard(row: row, citationsById: evidenceById))
        else if (_section == 1)
          for (final row in rows)
            Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: _NbsCatalogueCard(row: row, citationsById: evidenceById))
        else
          _PlantCatalogueGroups(rows: rows, citationsById: evidenceById),
      ]),
    );
  }
}

class _PlantCatalogueGroups extends StatelessWidget {
  const _PlantCatalogueGroups(
      {required this.rows, required this.citationsById});

  final List<Map<String, dynamic>> rows;
  final Map<int, Citation> citationsById;

  @override
  Widget build(BuildContext context) {
    final recommended = rows
        .where((row) => row['recommendation_status'] == 'recommended')
        .toList();
    final conditional = rows
        .where((row) =>
            row['recommendation_status'] != 'recommended' &&
            row['recommendation_status'] != 'do_not_recommend_invasive')
        .toList();
    final blocked = rows
        .where((row) =>
            row['recommendation_status'] == 'do_not_recommend_invasive')
        .toList();
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      if (recommended.isNotEmpty) ...[
        const SectionTitle(
            title: 'Recommended / suitable plants',
            subtitle:
                'Use only where the mapped component and site conditions apply.'),
        const SizedBox(height: 8),
        for (final row in recommended)
          Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child:
                  _PlantCatalogueCard(row: row, citationsById: citationsById)),
      ],
      if (conditional.isNotEmpty) ...[
        const SectionTitle(
            title: 'Conditional / local validation required',
            subtitle: 'Possible use, but confirm locally before planting.'),
        const SizedBox(height: 8),
        for (final row in conditional)
          Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child:
                  _PlantCatalogueCard(row: row, citationsById: citationsById)),
      ],
      if (blocked.isNotEmpty) ...[
        const SizedBox(height: 8),
        const SectionTitle(
            title: 'Not recommended / invasive',
            subtitle: 'These records are shown for safety awareness only.'),
        const SizedBox(height: 8),
        for (final row in blocked)
          Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child:
                  _PlantCatalogueCard(row: row, citationsById: citationsById)),
      ],
    ]);
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
        title: Text(row['name']?.toString() ?? 'Treatment train',
            style: const TextStyle(fontWeight: FontWeight.w900)),
        subtitle: Text(row['intended_role']?.toString() ?? 'Role not recorded'),
        children: [
          _TextBlockList(
              title: 'What it is',
              values: _uniqueStrings([
                row['intended_role']?.toString() ?? '',
                ..._catalogueStrings(row['strengths'])
              ]),
              emptyText: 'No train description is recorded.'),
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
                '${_titleFromSnake(item['use_case']?.toString() ?? 'use case')}: pass ${item['pass_count'] ?? 0}, conditional ${item['marginal_count'] ?? 0}, fail ${item['fail_count'] ?? 0}, unknown ${item['unknown_count'] ?? 0}'
            ]),
            emptyText: 'No use-case matrix record is available.',
          ),
          const SizedBox(height: 12),
          _TextBlockList(
              title: 'When not to use',
              values: _catalogueStrings(row['limitations']),
              emptyText:
                  'Confirm site constraints before selecting this train.'),
          const SizedBox(height: 12),
          Text('Typical sequence',
              style: Theme.of(context)
                  .textTheme
                  .titleSmall
                  ?.copyWith(fontWeight: FontWeight.w800)),
          const SizedBox(height: 8),
          _CatalogueFlow(steps: [
            for (final step in steps) step['step_label']?.toString() ?? 'Stage'
          ]),
          const SizedBox(height: 12),
          _TextBlockList(
              title: 'Key design checks',
              values: _catalogueStrings(row['pretreatment_needs']),
              emptyText:
                  'No additional canonical pretreatment field is recorded.'),
          const SizedBox(height: 12),
          _TextBlockList(
              title: 'O&M and monitoring checklist',
              values: _catalogueStrings(row['om_notes']),
              emptyText: 'No train-specific O&M record is available.'),
          const SizedBox(height: 12),
          _TextBlockList(
              title: 'Components',
              values: [
                for (final item in components)
                  '${item['name'] ?? 'Component'} - ${item['role'] ?? 'role not recorded'}'
              ],
              emptyText: 'No linked component is recorded.'),
          const SizedBox(height: 12),
          _TextBlockList(
              title: 'Plants / zones',
              values: [
                for (final plant in plants)
                  '${plant['plant_species'] ?? 'Plant'} - ${plant['nbs'] ?? 'mapped component'}'
              ],
              emptyText:
                  'No safe planting recommendation is available in this toolkit.'),
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
        title: Text(row['solution']?.toString() ?? 'NbS component',
            style: const TextStyle(fontWeight: FontWeight.w900)),
        subtitle: Text(
            '${row['family'] ?? 'Family not recorded'} | ${row['catalogue_role'] ?? 'Role not recorded'}'),
        children: [
          _TextBlockList(
              title: 'Role',
              values: [
                row['catalogue_role']?.toString() ??
                    'Role requires local confirmation.'
              ],
              emptyText: 'Role requires local confirmation.'),
          if (diagram != null) ...[
            const SizedBox(height: 12),
            NbsDiagramCard(kind: diagram),
          ],
          const SizedBox(height: 12),
          _TextBlockList(
              title: 'Can it be used alone?',
              values: [
                'Use only after site-safety screening confirms it is suitable.'
              ],
              emptyText: 'Use only after site-safety screening.'),
          const SizedBox(height: 12),
          _TextBlockList(
              title: 'Where suitable',
              values: _catalogueStrings(row['where_suitable']),
              emptyText: 'Site suitability requires local validation.'),
          const SizedBox(height: 12),
          _TextBlockList(
              title: 'Where not suitable',
              values: _catalogueStrings(row['where_not_suitable']),
              emptyText:
                  'Use only after site-safety screening confirms it is suitable.'),
          const SizedBox(height: 12),
          _TextBlockList(
              title: 'Pollutants addressed',
              values: [
                for (final value
                    in _catalogueStrings(row['pollutants_treated']))
                  _displayParameter(value)
              ],
              emptyText: 'No numeric pollutant-removal record is available.'),
          const SizedBox(height: 12),
          _TextBlockList(
              title: 'Cross-section / design notes',
              values: _catalogueStrings(row['design_notes']),
              emptyText:
                  'No canonical design cross-section note is available.'),
          const SizedBox(height: 12),
          _TextBlockList(
              title: 'O&M notes',
              values: _catalogueStrings(row['maintenance_notes']),
              emptyText: 'No canonical maintenance note is available.'),
          const SizedBox(height: 12),
          _TextBlockList(
              title: 'Plant links',
              values: [
                for (final plant in plants)
                  plant['plant_species']?.toString() ?? 'Mapped plant'
              ],
              emptyText: 'Planting guidance requires local validation.'),
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
        leading: Icon(invasive ? Icons.block_outlined : Icons.grass_outlined,
            color: invasive ? Colors.red : NbsColors.wetlandGreen),
        title: Text(row['plant_species']?.toString() ?? 'Plant species',
            style: const TextStyle(fontWeight: FontWeight.w900)),
        subtitle: Text(invasive
            ? 'Not recommended. This species is invasive and should not be used for planting.'
            : 'Possible use, but confirm locally before planting.'),
        children: [
          _TextBlockList(
              title: 'Mapped NbS components',
              values: [
                for (final item in mappings)
                  '${item['name'] ?? 'Component'} - ${item['basis'] ?? 'mapping basis not recorded'}'
              ],
              emptyText:
                  'No safe planting recommendation is available in this toolkit.'),
          const SizedBox(height: 12),
          _TextBlockList(
              title: 'Planting zone and conditions',
              values: _uniqueStrings([
                row['plant_type']?.toString() ?? '',
                row['locational_availability']?.toString() ?? '',
                row['climate_preference']?.toString() ?? '',
                row['soil_type']?.toString() ?? '',
                row['water_needs']?.toString() ?? ''
              ]),
              emptyText: 'Planting conditions require local validation.'),
          const SizedBox(height: 12),
          _TextBlockList(
              title: 'Ecological / treatment role',
              values: _uniqueStrings([
                row['ecological_role']?.toString() ?? '',
                row['metals_pollutants']?.toString() ?? '',
                row['evidence_note']?.toString() ?? ''
              ]),
              emptyText: 'No ecological role is recorded.'),
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
                'TOPSIS compares candidate options against ideal best and worst cases. The displayed technical match is the TOPSIS closeness value.',
          ),
          SizedBox(height: 12),
          _MethodCard(
            title: 'Confidence',
            body:
                'Confidence is calculated separately from ranking. It reflects data quality, evidence completeness, criteria coverage, and active caution flags.',
          ),
          SizedBox(height: 12),
          _MethodCard(
            title: 'Current limitations',
            body:
                'Current criteria weights support research-stage comparison and remain subject to expert calibration. Health-risk classification requires separate expert data.',
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

    canvas.drawCircle(
        Offset(size.width * 0.82, size.height * 0.08), 120, glowPaint);

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
              Rect.fromLTWH(
                  size.width - 70 + index * 14, size.height - h, 7, h),
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
                    label: 'Criteria-weighted',
                    color: NbsColors.warningAmber,
                  ),
                  _HeroChip(
                    label: 'Narmada intelligence',
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
                          ? 'No ranked recommendations were returned for this run.'
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
                label: 'Technical match',
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
          value: 'A0 → TOPSIS',
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
              StatusPill(label: 'Dataset', value: 'Narmada canonical'),
              StatusPill(label: 'Method', value: 'Criteria-weighted TOPSIS'),
              StatusPill(
                label: 'Evidence',
                value: 'Source linked',
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
            label: Text(citationsById[sourceId]?.display ??
                'Evidence record $sourceId'),
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
      title: const Text('View evidence',
          style: TextStyle(fontWeight: FontWeight.w800)),
      subtitle: const Text(
        'Evidence records show the sources used by the toolkit. They support screening and comparison, not final engineering design.',
      ),
      children: [
        if (populatedGroups.isEmpty)
          Align(
            alignment: Alignment.centerLeft,
            child: _SourceIdWrap(
                sourceIds: sourceIds, citationsById: citationsById),
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
                      Text(entry.key,
                          style: Theme.of(context)
                              .textTheme
                              .titleSmall
                              ?.copyWith(fontWeight: FontWeight.w800)),
                      const SizedBox(height: 7),
                      _SourceIdWrap(
                          sourceIds: entry.value, citationsById: citationsById),
                    ]),
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
          _ReadableBulletList(values: notes.map(_readableText).toList())
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
    _ => hasCurrentSample ? 'Mixed data basis' : 'Canonical context data',
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
      'Water-quality input not supplied. Screening uses canonical site/source context; recent measured values are recommended before design.',
    );
  }
  if (train?.allUseCasesUnknown == true) {
    values.add(
        'Use-case assessment needs recent water-quality values or additional canonical performance evidence.');
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
      'This recommendation uses canonical Narmada station/context data where available. No user-supplied current water-quality input was provided, so design-level pass/fail should be field-verified before implementation.',
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
      label: 'Concept screening only',
      reason:
          'Screening uses canonical Narmada station/source context. A recent user-supplied sample is recommended before preliminary design review.',
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
    return 'This is a canonical context screening recommendation. Confirm recent water quality, flow, land, and site constraints before design.';
  }
  return train.caveats.isNotEmpty
      ? train.caveats.first
      : 'Site survey, hydraulic design, regulatory review, and monitoring remain required.';
}

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
        'Confirm recent measured water quality before design-level treatment pass/fail assessment.');
  }
  final source =
      response.inputSummary.context['pollution_source_type']?.toString() ?? '';
  if (source.contains('industrial')) {
    required.add(
        'Confirm ETP/CETP availability, industrial chemistry, and pH-neutralization requirements.');
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
    required
        .add('Validate pretreatment: ${train!.pretreatmentRequirements.first}');
  }
  site.add(
      'Confirm land availability, slope, access, seasonal flow, and maintenance arrangements through site survey.');
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
      'Do not send acidic wastewater to biological or NbS units before neutralization.'
    ];
  }
  if (source.contains('agriculture')) {
    return const [
      'Do not present the ranked train as a complete farm-level design.',
      'Do not bypass field and edge-of-field source controls.'
    ];
  }
  if (context['intervention_position'] == 'in_channel' ||
      ((context['stream_order'] as num?)?.toDouble() ?? 0) >= 5) {
    return const [
      'Do not place treatment cells inside a mainstem or high-order river channel.',
      'Do not obstruct river conveyance or substitute in-channel cells for upstream pollution control.'
    ];
  }
  return train.caveats.isNotEmpty
      ? train.caveats.take(2).toList()
      : const [
          'Do not proceed to construction without site survey, hydraulic checks, and regulatory review.'
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
      'Suitability strength: available canonical evidence supports ${supportedUses.join(', ')} assessment.',
    if (train.pretreatmentRequirements.isNotEmpty)
      'Pretreatment: ${train.pretreatmentRequirements.first}',
    if (train.caveats.isNotEmpty) 'Key limitation: ${train.caveats.first}',
    if (train.caveats.isEmpty && train.dataGaps.isNotEmpty)
      'Key limitation: ${train.dataGaps.first}',
  ];
  final unique = _uniqueStrings(reasons);
  if (unique.length < 4) {
    unique.add(
      _practicalRecommendation(response, train),
    );
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
          'COD is absent from the current input; measure it to clarify organic load and pretreatment demand.');
    }
    if (!selected.any((value) => value == 'ammonia_n' || value == 'nh4_n') ||
        !selected.any((value) => value == 'phosphate_p' || value == 'tp')) {
      items.add(
          'NH4-N and PO4-P/TP are incomplete in the current input; collect them for nutrient-treatment design.');
    }
    if (response.useCase == 'drinking' &&
        !selected.contains('faecal_coliform')) {
      items.add(
          'Faecal coliform is absent from the current input; measure it for drinking or reuse risk assessment.');
    }
  }
  if (source.contains('industrial')) {
    items.add(
        'Confirm ETP/CETP availability, industrial chemistry, and upstream pH-neutralization requirements.');
  }
  if (source.contains('agriculture')) {
    items.add(
        'Confirm runoff collection points, seasonal drainage, nutrient sources, erosion pathways, and edge-of-field control locations.');
  }
  if (response.inputSummary.workflowMode == 'site_context_only') {
    items.add(
        'Confirm seasonal flow/discharge, drain or tributary entry points, land availability, and site slope before layout design.');
  }
  for (final gap in currentGaps.take(2)) {
    items.add('Resolve reported gap: $gap');
  }
  if (train != null && train.suitablePlants.isEmpty) {
    items.add(
        'Validate locally suitable non-invasive planting and maintenance requirements for the selected components.');
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
    if (train.pretreatmentRequirements
        .any((value) => value.toLowerCase().contains('neutral'))) {
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
    'temporary_not_expert_validated' => 'Criteria-weighted',
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
    return 'Not assessed';
  }
  if (!hasMeasuredData) {
    return 'Needs water-quality data';
  }
  return 'Evidence gap';
}

String _gapStatusLabel(String? status) {
  return switch (status) {
    'below_target' => 'Below / within target',
    'near_target' => 'Near target',
    'exceeds_target' => 'Exceeds target',
    _ => 'Not assessed',
  };
}

String _targetThresholdLabel(dynamic value) {
  if (value is! Map) return 'Not available';
  final low = value['limit_low'];
  final high = value['limit_high'];
  final unit = _displayUnit(value['unit']);
  if (low != null && high != null) return '$low-$high $unit'.trim();
  if (high != null) return '<= $high $unit'.trim();
  if (low != null) return '>= $low $unit'.trim();
  return 'Not available';
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

String _titleFromSnake(String value) {
  return value
      .split('_')
      .where((part) => part.isNotEmpty)
      .map((part) => '${part[0].toUpperCase()}${part.substring(1)}')
      .join(' ');
}

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
    'us_cm' || 'us/cm' => 'µS/cm',
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
          'rank_confidence_plants_v1', 'rank, confidence, and plant assembly')
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
