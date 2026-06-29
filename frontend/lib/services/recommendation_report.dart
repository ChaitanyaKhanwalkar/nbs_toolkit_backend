/// Builds practitioner-readable recommendation summaries and structured exports.
library;

import 'dart:convert';

import '../models/recommendation_models.dart';

const planningLevelDisclaimer =
    'This is a planning-level decision-support output. It is not a final engineering design. Confirm flow, pollutant loads, land availability, hydraulics, and site constraints before implementation.';
const _targetMethodNote =
    'Target-use-case selection determines standards and AHP-Fuzzy AHP weight set.';
const _methodLabel =
    'Final v1 AHP-Fuzzy AHP weighted TOPSIS after safety/applicability screening.';

class RecommendationReport {
  RecommendationReport._({
    required this.payload,
    required this.summary,
    required this.csv,
  });

  final Map<String, dynamic> payload;
  final String summary;
  final String csv;

  String get json => const JsonEncoder.withIndent('  ').convert(payload);

  String get baseFileName => 'narmada_nbs_recommendation_report';

  String get printHtml => _buildPrintHtml(payload, summary);

  factory RecommendationReport.fromResponse(RecommendationResponse response) {
    final train =
        response.rankedTrains.isEmpty ? null : response.rankedTrains.first;
    final input = response.inputSummary;
    final readinessGroups = _groupReadinessForReport(
      response.designReadiness.inputChecklist,
    );
    final evidence = [
      for (final citation in response.citations)
        {
          'id': citation.id,
          'label': citation.display,
          if (citation.citation != null) 'citation': citation.citation,
          if (citation.type != null) 'type': citation.type,
          if (citation.url != null) 'url': citation.url,
          if (citation.license != null) 'license': citation.license,
        },
    ];
    final pollutionSource = input.context['pollution_source_type']?.toString();
    final rankingDrivers = _rankingDrivers(train);
    final trainPayload = train == null
        ? null
        : {
            'name': _expandAbbreviations(train.name),
            'rank': train.rank,
            'technical_match': train.matchScore,
            'result_confidence': train.confidenceScore,
            'confidence_label': train.confidenceLabel,
            'implementation_role': train.implementationRole,
            'applicability_status': train.applicabilityStatus,
            'why_recommended': train.whyRecommended,
            'ranking_drivers': rankingDrivers,
            'criteria_explanation': [
              for (final item in train.criteriaExplanation)
                if (item.code != 'C5')
                  {
                    'criterion_code': item.code,
                    'criterion_name': item.label,
                    'score': item.score,
                    'weight': item.weight,
                    'weighted_contribution': item.weightedContribution,
                    'benefit_or_cost': item.benefitOrCost,
                    'status': item.status,
                  },
            ],
            'use_case_suitability': train.useCaseVerdicts,
            'pretreatment_requirements': train.pretreatmentRequirements,
            'treatment_sequence': train.treatmentSequence,
            'treatment_train_pathway': [
              for (final step in train.trainPathway)
                {
                  'step_order': step.stepOrder,
                  'component_name': _expandAbbreviations(step.componentName),
                  'component_role': step.componentRole,
                  'nbs_id': step.nbsId,
                },
            ],
            'pollutant_gaps': train.pollutantGapBreakdown,
            'important_limitations': train.caveats,
            'data_gaps': train.dataGaps,
            'implementation_guidance': train.implementationGuidance,
            'evidence_record_ids': train.sourceIds,
          };
    final payload = <String, dynamic>{
      'report_type': 'Narmada NbS planning-level recommendation',
      'method': _methodLabel,
      'method_note': _targetMethodNote,
      'selected_target_use_case': response.useCase,
      'pollution_source': pollutionSource,
      'project_input_summary': {
        'workflow_mode': input.workflowMode,
        'source_label': input.sourceLabel,
        'selected_target_use_case': response.useCase,
        'selected_target_use_case_label': _targetUseCaseLabel(response.useCase),
        'pollution_source': pollutionSource,
        'pollution_source_label': _pollutionSourceLabel(pollutionSource),
        'target_use_case_method_note': _targetMethodNote,
        'observation_count': input.observationCount,
        'selected_parameters': input.selectedParameters,
        'water_quality_values_used': input.dataUsed,
        'data_quality_notes': input.dataQualityNotes,
        'parameter_coverage': response.parameterCoverage,
        'site_and_source_context': input.context,
      },
      'location_context': {
        'map_status': _mapStatus(response.locationContext),
        'station': response.locationContext.station,
        'river': response.locationContext.river,
        'district': response.locationContext.district,
        'basin': response.locationContext.basin,
        'sub_basin': response.locationContext.subBasin,
        'stream_order': response.locationContext.streamOrder,
        'stream_context': response.locationContext.streamContext,
        'intervention_position': response.locationContext.interventionPosition,
        'pollution_source_type': response.locationContext.pollutionSourceType,
        'pollution_source_record_count':
            response.locationContext.pollutionSourceRecordCount,
        'river_discharge_context_m3_s':
            response.locationContext.riverDischargeCms,
        'coordinates_available': response.locationContext.coordinatesAvailable,
        'latitude': response.locationContext.latitude,
        'longitude': response.locationContext.longitude,
        'context_flags': response.locationContext.contextFlags,
        'missing_site_information':
            response.locationContext.missingSiteInformation,
      },
      'design_readiness': {
        'level': response.designReadiness.level,
        'short_label': response.designReadiness.shortLabel,
        'explanation': response.designReadiness.explanation,
        'reasons': response.designReadiness.reasons,
        'missing_inputs': response.designReadiness.missingInputs,
        'required_next_steps': response.designReadiness.requiredNextSteps,
        'expert_review_required': response.designReadiness.expertReviewRequired,
        'input_checklist': [
          for (final item in response.designReadiness.inputChecklist)
            {'key': item.key, 'label': item.label, 'status': item.status},
        ],
        'grouped_input_checklist': readinessGroups,
      },
      'validation_notes': response.validationNotes,
      'recommended_treatment_train': trainPayload,
      'sizing_and_land': [
        for (final estimate in response.sizingEstimates)
          {
            'train_id': estimate.trainId,
            'train_name': estimate.trainName,
            'basis': estimate.basis,
            'flow_status': estimate.flowStatus,
            'population_status': estimate.populationStatus,
            'sizing_confidence': estimate.sizingConfidence,
            'estimated_land_need': estimate.estimateLabel,
            'estimated_area_low_m2': estimate.estimatedAreaLowM2,
            'estimated_area_high_m2': estimate.estimatedAreaHighM2,
            'area_per_person_band': estimate.areaPerPersonBand,
            'land_fit': estimate.landFit,
            'full_component_coverage': estimate.fullComponentCoverage,
            'inputs_used': estimate.inputsUsed,
            'missing_inputs': estimate.missingInputs,
            'key_assumptions': estimate.keyAssumptions,
            'design_caution': estimate.designCaution,
            'evidence_record_ids': estimate.sourceIds,
          },
      ],
      'scenario_comparison': {
        'scope': response.scenarioComparison.scope,
        'current_scenario': response.scenarioComparison.currentScenario,
        'options': [
          for (final option in response.scenarioComparison.options)
            {
              'train_id': option.trainId,
              'name': _expandAbbreviations(option.name),
              'rank': option.rank,
              'technical_match': option.technicalMatch,
              'result_confidence': option.resultConfidence,
              'confidence_label': option.confidenceLabel,
              'design_readiness': option.designReadiness,
              'land_demand': option.landDemand,
              'land_fit': option.landFit,
              'operation_and_maintenance': option.omIntensity,
              'applicability_status': option.applicabilityStatus,
              'selected_use_case_verdict': option.selectedUseCaseVerdict,
              'warnings': option.warnings,
              'key_strength': option.keyStrength,
              'key_limitation': option.keyLimitation,
              'when_to_choose': option.whenToChoose,
            },
        ],
        'component_options': [
          for (final component in response.scenarioComparison.componentOptions)
            {
              'nbs_id': component.nbsId,
              'name': _expandAbbreviations(component.name),
              'role': component.role,
              'suitability_score': component.suitabilityScore,
              'standalone_suitability': component.standaloneSuitability,
              'applicability_status': component.applicabilityStatus,
              'key_constraints': component.keyConstraints,
            },
        ],
        'takeaways': [
          for (final takeaway in response.scenarioComparison.takeaways)
            {
              'label': takeaway.label,
              'train_id': takeaway.trainId,
              'train_name': takeaway.trainName,
              'explanation': takeaway.explanation,
            },
        ],
        'limitations': response.scenarioComparison.limitations,
      },
      'cost_benefit_and_practicality': [
        for (final option in response.scenarioComparison.options.take(3))
          {
            'train_name': _expandAbbreviations(option.name),
            'practical_cost_burden': _practicalCostBurden(option),
            'main_cost_drivers': _practicalCostDrivers(option),
            'main_benefits': _practicalBenefits(option),
            'key_tradeoff': _practicalTradeoff(option),
            'monetary_cost_status':
                'Not estimated; no rupee CAPEX/OPEX values are invented.',
          },
      ],
      'individual_nbs_components': [
        for (final component in response.componentRecommendations)
          {
            'name': _expandAbbreviations(component.name),
            'role': component.role,
            'suitability_score': component.suitabilityScore,
            'standalone_suitability': component.standaloneSuitability,
            'pollutants_addressed': component.pollutantsAddressed,
            'key_constraints': component.keyConstraints,
            'implementation_guidance': component.implementationGuidance,
            'evidence_record_ids': component.sourceIds,
          },
      ],
      'global_data_gaps': response.globalGaps,
      'evidence_records': evidence,
      'disclaimer': planningLevelDisclaimer,
    };
    final summary = _buildSummary(response, train);
    return RecommendationReport._(
      payload: payload,
      summary: summary,
      csv: _buildCsv(payload),
    );
  }
}

String _buildSummary(
  RecommendationResponse response,
  TrainRecommendation? train,
) {
  final rankingDrivers = _rankingDrivers(train);
  final lines = <String>[
    'NARMADA NBS PLANNING-LEVEL RECOMMENDATION',
    'Method: $_methodLabel',
    _targetMethodNote,
    '',
    'Input basis: ${_workflowLabel(response.inputSummary.workflowMode)}',
    'Selected target use case: ${_targetUseCaseLabel(response.useCase)}',
    'Pollution source: ${_pollutionSourceLabel(response.inputSummary.context['pollution_source_type']?.toString())}',
    response.inputSummary.dataUsed.isEmpty
        ? 'No recent water-quality values were supplied.'
        : '${response.inputSummary.dataUsed.length} recent water-quality values informed this result.',
    if (response.parameterCoverage.isNotEmpty)
      'Parameter coverage: ${_coverageSummary(response.parameterCoverage)}',
    'Site context: ${response.locationContext.station ?? response.locationContext.district ?? 'Not selected'}',
    'Location display: ${_mapStatus(response.locationContext)}',
    if (response.locationContext.riverDischargeCms != null)
      'River discharge context: ${response.locationContext.riverDischargeCms} m³/s (not treatment design flow)',
    'Design readiness: ${response.designReadiness.shortLabel}',
    response.designReadiness.explanation,
    ..._validationSummaryMessages(response),
  ];
  if (train == null) {
    lines.add('Recommended treatment train: No ranked option available');
  } else {
    lines.addAll([
      '',
      'Recommended treatment train: ${_expandAbbreviations(train.name)}',
      'Screening match: ${train.matchPercent}',
      'Result confidence: ${_confidenceLabel(train)}',
      if (train.implementationRole != null) 'Role: ${train.implementationRole}',
      if (train.whyRecommended.isNotEmpty) 'Why: ${train.whyRecommended.first}',
      if (rankingDrivers.isNotEmpty)
        'Ranking drivers: ${rankingDrivers.join('; ')}',
      if (train.trainPathway.isNotEmpty)
        'Treatment train pathway: ${_pathwaySummary(train)}',
      if (train.pretreatmentRequirements.isNotEmpty)
        'Pretreatment: ${train.pretreatmentRequirements.join('; ')}',
      if (train.useCaseVerdicts.isNotEmpty)
        'Use-case suitability: ${train.useCaseVerdicts.entries.map((item) => '${_title(item.key)}: ${_title(item.value)}').join('; ')}',
      if (train.dataGaps.isNotEmpty) 'Data gaps: ${train.dataGaps.join('; ')}',
    ]);
  }
  if (response.sizingEstimates.isNotEmpty) {
    final sizing = response.sizingEstimates.first;
    lines.addAll([
      '',
      'Sizing and land: ${sizing.estimateLabel}',
      'Likely land fit: ${_title(sizing.landFit)}',
      'Sizing caution: ${sizing.designCaution}',
    ]);
  }
  if (response.scenarioComparison.takeaways.isNotEmpty) {
    lines.addAll([
      '',
      'Comparison takeaways:',
      for (final takeaway in response.scenarioComparison.takeaways)
        '${takeaway.label}: ${takeaway.explanation}',
    ]);
  }
  lines.addAll(['', planningLevelDisclaimer]);
  return lines.join('\n');
}

String _coverageSummary(List<Map<String, dynamic>> rows) {
  final counts = <String, int>{};
  for (final row in rows) {
    final category =
        row['coverage_category']?.toString() ?? 'read_not_assessed';
    counts[category] = (counts[category] ?? 0) + 1;
  }
  const labels = {
    'used_in_scoring': 'used in scoring',
    'supporting_context': 'used as supporting context',
    'read_not_assessed': 'used as supporting context',
    'skipped': 'not recognized or skipped',
  };
  return counts.entries
      .map((entry) => '${entry.value} ${labels[entry.key] ?? entry.key}')
      .join(', ');
}

String _buildCsv(Map<String, dynamic> payload) {
  final rows = <List<Object?>>[
    ['section', 'item', 'field', 'value'],
  ];
  void addValue(String section, String item, String field, Object? value) {
    if (value is Iterable) {
      for (final entry in value) {
        rows.add([section, item, field, _flatValue(entry)]);
      }
    } else if (value is Map) {
      for (final entry in value.entries) {
        rows.add([
          section,
          item,
          '$field.${entry.key}',
          _flatValue(entry.value),
        ]);
      }
    } else {
      rows.add([section, item, field, _flatValue(value)]);
    }
  }

  final input = payload['project_input_summary'] as Map<String, dynamic>;
  for (final entry in input.entries) {
    addValue('project_input_summary', 'input', entry.key, entry.value);
  }
  final location = payload['location_context'] as Map<String, dynamic>;
  for (final entry in location.entries) {
    addValue('location_context', 'site', entry.key, entry.value);
  }
  final readiness = payload['design_readiness'] as Map<String, dynamic>;
  for (final entry in readiness.entries) {
    addValue('design_readiness', 'readiness', entry.key, entry.value);
  }
  final validation = payload['validation_notes'] as Map<String, dynamic>;
  for (final entry in validation.entries) {
    addValue('validation_notes', 'safety_and_coverage', entry.key, entry.value);
  }
  final train = payload['recommended_treatment_train'];
  if (train is Map<String, dynamic>) {
    for (final entry in train.entries) {
      addValue('recommended_treatment_train', 'rank_1', entry.key, entry.value);
    }
  }
  final sizing = payload['sizing_and_land'] as List<dynamic>;
  for (var index = 0; index < sizing.length; index++) {
    final estimate = sizing[index] as Map<String, dynamic>;
    for (final entry in estimate.entries) {
      addValue(
        'sizing_and_land',
        'estimate_${index + 1}',
        entry.key,
        entry.value,
      );
    }
  }
  final comparison = payload['scenario_comparison'] as Map<String, dynamic>;
  for (final entry in comparison.entries) {
    addValue('scenario_comparison', 'current_run', entry.key, entry.value);
  }
  final practicality =
      payload['cost_benefit_and_practicality'] as List<dynamic>;
  for (var index = 0; index < practicality.length; index++) {
    final row = practicality[index] as Map<String, dynamic>;
    for (final entry in row.entries) {
      addValue(
        'cost_benefit_and_practicality',
        'option_${index + 1}',
        entry.key,
        entry.value,
      );
    }
  }
  final components = payload['individual_nbs_components'] as List<dynamic>;
  for (var index = 0; index < components.length; index++) {
    final component = components[index] as Map<String, dynamic>;
    for (final entry in component.entries) {
      addValue(
        'individual_nbs_components',
        'component_${index + 1}',
        entry.key,
        entry.value,
      );
    }
  }
  for (final gap in payload['global_data_gaps'] as List<dynamic>) {
    addValue('data_gaps', 'global', 'gap', gap);
  }
  for (final record in payload['evidence_records'] as List<dynamic>) {
    final evidence = record as Map<String, dynamic>;
    for (final entry in evidence.entries) {
      addValue(
        'evidence_records',
        'evidence_${evidence['id']}',
        entry.key,
        entry.value,
      );
    }
  }
  addValue('disclaimer', 'planning_level', 'text', payload['disclaimer']);
  return '\uFEFF${rows.map((row) => row.map(_csvCell).join(',')).join('\r\n')}';
}

String _flatValue(Object? value) {
  if (value == null) return '';
  if (value is Map || value is List) return jsonEncode(value);
  return value.toString();
}

String _csvCell(Object? value) {
  final text = value?.toString() ?? '';
  return '"${text.replaceAll('"', '""')}"';
}

String _buildPrintHtml(Map<String, dynamic> payload, String summary) {
  final escapedSummary = const HtmlEscape().convert(summary).replaceAll(
        '\n',
        '<br>',
      );
  final references = (payload['evidence_records'] as List<dynamic>? ?? const [])
      .cast<Map<String, dynamic>>()
      .map(
        (record) =>
            '<li>${const HtmlEscape().convert(record['label']?.toString() ?? 'Source ${record['id']}')}</li>',
      )
      .join();
  return '''
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Narmada NbS recommendation report</title>
  <style>
    @page { size: A4; margin: 18mm; }
    body { font-family: Arial, sans-serif; color: #102a43; line-height: 1.45; }
    h1 { font-size: 22px; margin: 0 0 8px; }
    h2 { font-size: 15px; margin-top: 18px; border-bottom: 1px solid #d8e2dc; padding-bottom: 4px; }
    p, li { font-size: 11.5px; }
    .method { font-weight: 700; margin-bottom: 16px; }
    .summary { white-space: normal; }
  </style>
</head>
<body>
  <h1>Narmada NbS recommendation report</h1>
  <p class="method">Method: $_methodLabel<br>${const HtmlEscape().convert(_targetMethodNote)}</p>
  <h2>Recommendation summary</h2>
  <p class="summary">$escapedSummary</p>
  <h2>References</h2>
  <ul>${references.isEmpty ? '<li>No resolved evidence record is available.</li>' : references}</ul>
  <h2>Limitations</h2>
  <p>${const HtmlEscape().convert(planningLevelDisclaimer)}</p>
</body>
</html>
''';
}

String _workflowLabel(String? value) => switch (value) {
      'uploaded_water_quality' => 'Uploaded water-quality data',
      'manual_measured_water_quality' => 'Measured water-quality values',
      'site_context_only' => 'Station and site context',
      'pollution_source_screening' => 'Pollution-source and site context',
      _ => 'Available project inputs',
    };

String _expandAbbreviations(String value) {
  var text = value;
  if (text == 'DEWATS modular train') {
    return 'DEWATS modular train — Decentralized Wastewater Treatment System';
  }
  if (text == 'DEWATS Train') {
    return 'DEWATS Train — Decentralized Wastewater Treatment System';
  }
  if (!text.contains('Decentralized Wastewater Treatment System')) {
    text = text.replaceAll(
      'DEWATS modular train',
      'DEWATS modular train — Decentralized Wastewater Treatment System',
    );
    text = text.replaceAll(
      'DEWATS Train',
      'DEWATS Train — Decentralized Wastewater Treatment System',
    );
  }
  if (text == 'French VF (no primary)') {
    return 'French Vertical Flow (VF) (no primary)';
  }
  const replacements = <(String, String)>[
    ('HSSF', 'Horizontal Subsurface Flow (HSSF)'),
    ('WSP', 'Waste Stabilization Pond (WSP)'),
    ('UASB', 'Upflow Anaerobic Sludge Blanket (UASB)'),
    ('STP', 'Sewage Treatment Plant (STP)'),
    ('ABR', 'Anaerobic Baffled Reactor (ABR)'),
    ('ETP', 'Effluent Treatment Plant (ETP)'),
    ('CETP', 'Common Effluent Treatment Plant (CETP)'),
    ('O&M', 'Operation and Maintenance (O&M)'),
    ('BOD', 'Biochemical Oxygen Demand (BOD)'),
    ('COD', 'Chemical Oxygen Demand (COD)'),
    ('TSS', 'Total Suspended Solids (TSS)'),
    ('TDS', 'Total Dissolved Solids (TDS)'),
    ('EC', 'Electrical Conductivity (EC)'),
    ('SAR', 'Sodium Adsorption Ratio (SAR)'),
    ('TP', 'Total Phosphorus (TP)'),
    ('NH4-N', 'Ammonium nitrogen / ammoniacal nitrogen (NH4-N)'),
    ('DO', 'Dissolved Oxygen (DO)'),
  ];
  if (!text.contains('Vertical Flow (VF)')) {
    text = text.replaceAll(RegExp(r'\bVF\b'), 'Vertical Flow (VF)');
  }
  for (final (abbr, full) in replacements) {
    if (!text.contains(full)) {
      text = abbr == 'O&M'
          ? text.replaceAll(abbr, full)
          : text.replaceAll(RegExp('\\b${RegExp.escape(abbr)}\\b'), full);
    }
  }
  return text;
}

String _targetUseCaseLabel(String? value) => switch (value) {
      'discharge_inland' => 'Discharge to inland surface water',
      'irrigation' => 'Irrigation reuse',
      'drinking' => 'Drinking / strict-use screening',
      null || '' => 'Not selected',
      _ => _title(value),
    };

String _pollutionSourceLabel(String? value) => switch (value) {
      'domestic_sewage' => 'Domestic sewage',
      'high_agriculture_only_no_water_data' => 'Agricultural runoff',
      'industrial_or_mixed_industrial' => 'Industrial / mixed industrial',
      null || '' => 'Not specified',
      _ => _title(value),
    };

String _confidenceLabel(TrainRecommendation train) {
  if ((train.confidenceScore ?? 0) <= 0) return 'Data-limited';
  return train.confidencePercent;
}

List<String> _rankingDrivers(TrainRecommendation? train) {
  if (train == null) return const [];
  final rows = [
    for (final item in train.criteriaExplanation)
      if (item.code != 'C5' && item.weightedContribution != null) item,
  ]..sort(
      (a, b) => b.weightedContribution!.compareTo(a.weightedContribution!),
    );
  return [
    for (final item in rows.take(3))
      '${item.code} ${item.label}: ${item.weightedContributionLabel}',
  ];
}

String _practicalCostBurden(ComparisonOption option) {
  final land = option.landFit.toLowerCase();
  final om = option.omIntensity.toLowerCase();
  if (land.contains('insufficient') || land.contains('unknown')) {
    return 'Data-limited';
  }
  if (land.contains('poor') ||
      land.contains('not') ||
      om.contains('high') ||
      om.contains('power')) {
    return 'High';
  }
  if (land.contains('borderline') ||
      land.contains('moderate') ||
      om.contains('moderate')) {
    return 'Moderate';
  }
  return 'Low';
}

List<String> _practicalCostDrivers(ComparisonOption option) {
  final values = <String>[];
  final land = option.landFit.toLowerCase();
  final om = option.omIntensity.toLowerCase();
  if (land.contains('insufficient') || land.contains('unknown')) {
    values.add('missing sizing data');
  } else if (!land.contains('good')) {
    values.add('land');
  }
  if (om.contains('high') || om.contains('moderate')) values.add('O&M');
  if (om.contains('power') || om.contains('energy')) values.add('energy');
  if (option.warnings.isNotEmpty) values.add('monitoring');
  return _uniqueStrings(values.isEmpty ? ['site verification'] : values);
}

List<String> _practicalBenefits(ComparisonOption option) {
  final values = <String>[];
  if ((option.technicalMatch ?? 0) >= 0.7) values.add('treatment coverage');
  if ((option.resultConfidence ?? 0) >= 0.5) values.add('confidence');
  if (option.omIntensity.toLowerCase().contains('low') ||
      option.omIntensity.toLowerCase().contains('gravity')) {
    values.add('low O&M');
  }
  if (option.applicabilityStatus != 'rejected') {
    values.add('off-channel suitability where site checks pass');
  }
  if (option.keyStrength != null) values.add('train completeness');
  return _uniqueStrings(values.isEmpty ? ['transparent screening'] : values);
}

String _practicalTradeoff(ComparisonOption option) {
  if (option.keyLimitation != null && option.keyLimitation!.isNotEmpty) {
    return _expandAbbreviations(option.keyLimitation!);
  }
  if (option.warnings.isNotEmpty) {
    return _expandAbbreviations(option.warnings.first);
  }
  return 'Still needs design-flow, land, and site verification before engineering design.';
}

String _pathwaySummary(TrainRecommendation train) {
  if (train.trainPathway.isEmpty) {
    return 'Treatment sequence details are not available for this train.';
  }
  return [
    'Influent/source',
    ...train.trainPathway
        .map((step) => _expandAbbreviations(step.componentName)),
    'Outlet / selected target screening',
  ].join(' -> ');
}

List<String> _validationSummaryMessages(RecommendationResponse response) {
  final notes = response.validationNotes;
  final strict = _validationMap(notes['strict_use']);
  final salinity = _validationMap(notes['salinity']);
  final standards = _validationMap(notes['standards_coverage']);
  final match = _validationMap(notes['match_vs_suitability']);
  return [
    if (strict['warning'] != null) strict['warning'].toString(),
    if (strict['advanced_treatment_warning'] != null)
      strict['advanced_treatment_warning'].toString(),
    if ((strict['blockers'] as List?)?.isNotEmpty ?? false)
      'Strict-use blockers detected: ${(strict['blockers'] as List).join(', ')}.',
    if (strict['pathogen_note'] != null) strict['pathogen_note'].toString(),
    if (salinity['warning'] != null) salinity['warning'].toString(),
    if (standards['note'] != null) standards['note'].toString(),
    if (match['explanation'] != null) match['explanation'].toString(),
    if (match['note'] != null) match['note'].toString(),
    ..._stringListFromDynamic(notes['soil_filter_cautions']),
  ];
}

Map<String, dynamic> _validationMap(Object? value) {
  return value is Map<String, dynamic> ? value : <String, dynamic>{};
}

List<String> _stringListFromDynamic(Object? value) {
  if (value is! List) return const [];
  return value.map((item) => item.toString()).toList();
}

List<String> _uniqueStrings(List<String> values) {
  final result = <String>[];
  for (final value in values) {
    if (value.trim().isNotEmpty && !result.contains(value)) {
      result.add(value);
    }
  }
  return result;
}

String _mapStatus(LocationContext location) {
  if (location.coordinatesAvailable) return 'Verified stored location';
  if (location.station != null ||
      location.river != null ||
      location.district != null ||
      location.basin != null) {
    return 'Schematic context only; not a surveyed map';
  }
  return 'No verified map location is available';
}

Map<String, List<Map<String, String>>> _groupReadinessForReport(
  List<ReadinessInput> items,
) {
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
  final result = <String, List<Map<String, String>>>{
    'needed_to_improve_result': [],
    'needed_before_engineering_design': [],
    'field_checks': [],
  };
  for (final item in items) {
    final key = improveKeys.contains(item.key)
        ? 'needed_to_improve_result'
        : fieldKeys.contains(item.key)
            ? 'field_checks'
            : 'needed_before_engineering_design';
    result[key]!.add({
      'key': item.key,
      'label': item.label,
      'status': item.status,
    });
  }
  return result;
}

String _title(String value) => value
    .split('_')
    .where((part) => part.isNotEmpty)
    .map((part) => '${part[0].toUpperCase()}${part.substring(1)}')
    .join(' ');
