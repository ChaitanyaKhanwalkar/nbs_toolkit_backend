/// Builds practitioner-readable recommendation summaries and structured exports.
library;

import 'dart:convert';

import '../models/recommendation_models.dart';

const planningLevelDisclaimer =
    'This is a planning-level decision-support output. It is not a final engineering design. Confirm flow, pollutant loads, land availability, hydraulics, and site constraints before implementation.';

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

  String get baseFileName => 'nbs_recommendation_report';

  factory RecommendationReport.fromResponse(RecommendationResponse response) {
    final train = response.rankedTrains.isEmpty
        ? null
        : response.rankedTrains.first;
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
    final trainPayload = train == null
        ? null
        : {
            'name': train.name,
            'rank': train.rank,
            'technical_match': train.matchScore,
            'result_confidence': train.confidenceScore,
            'confidence_label': train.confidenceLabel,
            'implementation_role': train.implementationRole,
            'applicability_status': train.applicabilityStatus,
            'why_recommended': train.whyRecommended,
            'use_case_suitability': train.useCaseVerdicts,
            'pretreatment_requirements': train.pretreatmentRequirements,
            'treatment_sequence': train.treatmentSequence,
            'pollutant_gaps': train.pollutantGapBreakdown,
            'important_limitations': train.caveats,
            'data_gaps': train.dataGaps,
            'implementation_guidance': train.implementationGuidance,
            'evidence_record_ids': train.sourceIds,
          };
    final payload = <String, dynamic>{
      'report_type': 'Narmada NbS planning-level recommendation',
      'method': 'criteria-weighted TOPSIS after applicability screening',
      'project_input_summary': {
        'workflow_mode': input.workflowMode,
        'use_case': response.useCase,
        'observation_count': input.observationCount,
        'selected_parameters': input.selectedParameters,
        'water_quality_values_used': input.dataUsed,
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
      'recommended_treatment_train': trainPayload,
      'sizing_and_land': [
        for (final estimate in response.sizingEstimates)
          {
            'train_id': estimate.trainId,
            'train_name': estimate.trainName,
            'basis': estimate.basis,
            'flow_status': estimate.flowStatus,
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
              'name': option.name,
              'rank': option.rank,
              'technical_match': option.technicalMatch,
              'result_confidence': option.resultConfidence,
              'confidence_label': option.confidenceLabel,
              'design_readiness': option.designReadiness,
              'land_demand': option.landDemand,
              'land_fit': option.landFit,
              'operation_and_maintenance': option.omIntensity,
              'applicability_status': option.applicabilityStatus,
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
              'name': component.name,
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
      'individual_nbs_components': [
        for (final component in response.componentRecommendations)
          {
            'name': component.name,
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
  final lines = <String>[
    'NARMADA NBS PLANNING-LEVEL RECOMMENDATION',
    'Method: criteria-weighted TOPSIS after applicability screening',
    '',
    'Input basis: ${_workflowLabel(response.inputSummary.workflowMode)}',
    response.inputSummary.dataUsed.isEmpty
        ? 'No recent water-quality values were supplied.'
        : '${response.inputSummary.dataUsed.length} recent water-quality values informed this result.',
    'Site context: ${response.locationContext.station ?? response.locationContext.district ?? 'Not selected'}',
    'Location display: ${_mapStatus(response.locationContext)}',
    'Design readiness: ${response.designReadiness.shortLabel}',
    response.designReadiness.explanation,
  ];
  if (train == null) {
    lines.add('Recommended treatment train: No ranked option available');
  } else {
    lines.addAll([
      '',
      'Recommended treatment train: ${train.name}',
      'Technical match: ${train.matchPercent}',
      'Result confidence: ${_confidenceLabel(train)}',
      if (train.implementationRole != null) 'Role: ${train.implementationRole}',
      if (train.whyRecommended.isNotEmpty) 'Why: ${train.whyRecommended.first}',
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
  return rows.map((row) => row.map(_csvCell).join(',')).join('\r\n');
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

String _workflowLabel(String? value) => switch (value) {
  'uploaded_water_quality' => 'Uploaded water-quality data',
  'manual_measured_water_quality' => 'Measured water-quality values',
  'site_context_only' => 'Station and site context',
  'pollution_source_screening' => 'Pollution-source and site context',
  _ => 'Available project inputs',
};

String _confidenceLabel(TrainRecommendation train) {
  if ((train.confidenceScore ?? 0) <= 0) return 'Data-limited';
  return train.confidencePercent;
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
