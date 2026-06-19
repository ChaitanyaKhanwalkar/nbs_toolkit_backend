class RecommendationResponse {
  RecommendationResponse({
    required this.workflowStatus,
    required this.stepCompleted,
    required this.useCase,
    required this.dataQualityLevel,
    required this.exceedances,
    required this.globalGaps,
    required this.recommendationAssemblyBundle,
    required this.citations,
    required this.warnings,
    required this.errors,
    required this.missingDataMessages,
    required this.weightsStatus,
    required this.expertValidated,
    required this.provisionalNote,
    required this.recommendationCount,
    required this.rankedTrains,
    required this.rejectedOptions,
    required this.inputSummary,
  });

  final String workflowStatus;
  final String? stepCompleted;
  final String? useCase;
  final String? dataQualityLevel;
  final List<Exceedance> exceedances;
  final List<String> globalGaps;
  final RecommendationAssemblyBundle? recommendationAssemblyBundle;
  final List<Citation> citations;
  final List<String> warnings;
  final List<String> errors;
  final List<String> missingDataMessages;
  final String? weightsStatus;
  final bool expertValidated;
  final String? provisionalNote;
  final int recommendationCount;
  final List<TrainRecommendation> rankedTrains;
  final List<Map<String, dynamic>> rejectedOptions;
  final RecommendationInputSummary inputSummary;

  /// Resolved citations indexed by source ID for quick lookup in the UI.
  Map<int, Citation> get citationsById {
    return {for (final citation in citations) citation.id: citation};
  }

  factory RecommendationResponse.fromJson(Map<String, dynamic> json) {
    final bundleJson = json['recommendation_assembly_bundle'];
    final exceedanceRows = json['exceedances'];
    final citationRows = json['citations'];
    final trainRows = json['ranked_trains'];
    return RecommendationResponse(
      workflowStatus: _stringValue(json['workflow_status']),
      stepCompleted: _nullableString(json['step_completed']),
      useCase: _nullableString(json['use_case']),
      dataQualityLevel: _nullableString(json['data_quality_level']),
      exceedances: exceedanceRows is List
          ? exceedanceRows
              .whereType<Map<String, dynamic>>()
              .map(Exceedance.fromJson)
              .toList()
          : <Exceedance>[],
      globalGaps: _stringList(json['global_gaps']),
      recommendationAssemblyBundle: bundleJson is Map<String, dynamic>
          ? RecommendationAssemblyBundle.fromJson(bundleJson)
          : null,
      citations: citationRows is List
          ? citationRows
              .whereType<Map<String, dynamic>>()
              .map(Citation.fromJson)
              .toList()
          : <Citation>[],
      warnings: _stringList(json['warnings']),
      errors: _stringList(json['errors']),
      missingDataMessages: _stringList(json['missing_data_messages']),
      weightsStatus: _nullableString(json['weights_status']),
      expertValidated: json['expert_validated'] == true,
      provisionalNote: _nullableString(json['provisional_note']),
      recommendationCount: _nullableInt(json['recommendation_count']) ??
          (bundleJson is Map<String, dynamic>
              ? _intValue(bundleJson['recommendation_count'])
              : 0),
      rankedTrains: trainRows is List
          ? trainRows
              .whereType<Map<String, dynamic>>()
              .map(TrainRecommendation.fromJson)
              .toList()
          : <TrainRecommendation>[],
      rejectedOptions: (json['rejected_options'] as List?)
              ?.whereType<Map<String, dynamic>>()
              .toList() ??
          <Map<String, dynamic>>[],
      inputSummary: RecommendationInputSummary.fromJson(
        json['input_summary'] is Map<String, dynamic>
            ? json['input_summary'] as Map<String, dynamic>
            : const <String, dynamic>{},
      ),
    );
  }
}

class RecommendationInputSummary {
  RecommendationInputSummary({
    required this.observationCount,
    required this.selectedParameters,
    required this.dataUsed,
    required this.context,
  });

  final int observationCount;
  final List<String> selectedParameters;
  final List<Map<String, dynamic>> dataUsed;
  final Map<String, dynamic> context;

  String? get workflowMode => _nullableString(context['workflow_mode']);

  bool get isContextOnly =>
      workflowMode == 'site_context_only' ||
      workflowMode == 'pollution_source_screening';

  factory RecommendationInputSummary.fromJson(Map<String, dynamic> json) {
    return RecommendationInputSummary(
      observationCount: _intValue(json['observation_count']),
      selectedParameters: _stringList(json['selected_parameters']),
      dataUsed: (json['data_used'] as List?)
              ?.whereType<Map<String, dynamic>>()
              .toList() ??
          <Map<String, dynamic>>[],
      context: json['context'] is Map<String, dynamic>
          ? json['context'] as Map<String, dynamic>
          : <String, dynamic>{},
    );
  }
}

class TrainRecommendation {
  TrainRecommendation({
    required this.trainId,
    required this.name,
    required this.rank,
    required this.matchScore,
    required this.confidenceScore,
    required this.confidenceLabel,
    required this.confidenceCap,
    required this.confidenceFactors,
    required this.confidenceExplanation,
    required this.pollutantGapBreakdown,
    required this.useCaseVerdicts,
    required this.criteriaBreakdown,
    required this.applicabilityStatus,
    required this.whyRecommended,
    required this.caveats,
    required this.treatmentSequence,
    required this.nbsComponents,
    required this.suitablePlants,
    required this.sourceIds,
    required this.implementationRole,
    required this.pretreatmentRequirements,
    required this.dataGaps,
    required this.implementationGuidance,
    required this.sourceLocationGuidance,
    required this.plantingGuidance,
    required this.allUseCasesUnknown,
    required this.useCaseAssessmentStatus,
  });

  final int trainId;
  final String name;
  final int rank;
  final double? matchScore;
  final double? confidenceScore;
  final String? confidenceLabel;
  final double? confidenceCap;
  final Map<String, dynamic> confidenceFactors;
  final List<String> confidenceExplanation;
  final List<Map<String, dynamic>> pollutantGapBreakdown;
  final Map<String, String> useCaseVerdicts;
  final List<Map<String, dynamic>> criteriaBreakdown;
  final String applicabilityStatus;
  final List<String> whyRecommended;
  final List<String> caveats;
  final List<Map<String, dynamic>> treatmentSequence;
  final List<Map<String, dynamic>> nbsComponents;
  final List<Map<String, dynamic>> suitablePlants;
  final List<int> sourceIds;
  final String? implementationRole;
  final List<String> pretreatmentRequirements;
  final List<String> dataGaps;
  final List<String> implementationGuidance;
  final List<String> sourceLocationGuidance;
  final String? plantingGuidance;
  final bool allUseCasesUnknown;
  final String? useCaseAssessmentStatus;

  factory TrainRecommendation.fromJson(Map<String, dynamic> json) {
    final verdictRows = json['all_use_case_verdicts'];
    return TrainRecommendation(
      trainId: _intValue(json['train_id']),
      name: _stringValue(json['name'], fallback: 'Treatment train'),
      rank: _intValue(json['rank']),
      matchScore: _nullableDouble(json['match_score']),
      confidenceScore: _nullableDouble(json['confidence_score']),
      confidenceLabel: _nullableString(json['confidence_label']),
      confidenceCap: _nullableDouble(json['confidence_cap']),
      confidenceFactors: json['confidence_factors'] is Map<String, dynamic>
          ? json['confidence_factors'] as Map<String, dynamic>
          : <String, dynamic>{},
      confidenceExplanation: _stringList(json['confidence_explanation']),
      pollutantGapBreakdown: (json['pollutant_gap_breakdown'] as List?)
              ?.whereType<Map<String, dynamic>>()
              .toList() ??
          <Map<String, dynamic>>[],
      useCaseVerdicts: verdictRows is Map<String, dynamic>
          ? verdictRows.map(
              (key, value) => MapEntry(
                key,
                value is Map<String, dynamic>
                    ? _stringValue(value['verdict'], fallback: 'unknown')
                    : 'unknown',
              ),
            )
          : <String, String>{},
      criteriaBreakdown: (json['criteria_breakdown'] as List?)
              ?.whereType<Map<String, dynamic>>()
              .toList() ??
          <Map<String, dynamic>>[],
      applicabilityStatus: _stringValue(
        (json['applicability_result'] as Map<String, dynamic>?)?['status'],
        fallback: 'unknown',
      ),
      whyRecommended: _stringList(json['why_recommended']),
      caveats: _stringList(json['caveats']),
      treatmentSequence: (json['treatment_sequence'] as List?)
              ?.whereType<Map<String, dynamic>>()
              .toList() ??
          <Map<String, dynamic>>[],
      nbsComponents: (json['nbs_components'] as List?)
              ?.whereType<Map<String, dynamic>>()
              .toList() ??
          <Map<String, dynamic>>[],
      suitablePlants: (json['suitable_plants'] as List?)
              ?.whereType<Map<String, dynamic>>()
              .toList() ??
          <Map<String, dynamic>>[],
      sourceIds: _intList(json['evidence_source_ids']),
      implementationRole: _nullableString(json['implementation_role']),
      pretreatmentRequirements: _stringList(json['pretreatment_requirements']),
      dataGaps: _stringList(json['data_gaps']),
      implementationGuidance: _stringList(json['implementation_guidance']),
      sourceLocationGuidance: _stringList(json['source_location_guidance']),
      plantingGuidance: _nullableString(json['planting_guidance']),
      allUseCasesUnknown: json['all_use_cases_unknown'] == true,
      useCaseAssessmentStatus: _nullableString(
        json['use_case_assessment_status'],
      ),
    );
  }

  String get matchPercent => _percent(matchScore);
  String get confidencePercent => _percent(confidenceScore);
}

class Exceedance {
  Exceedance({
    required this.parameter,
    required this.observedValue,
    required this.observedUnit,
    required this.limitHigh,
    required this.status,
    required this.requiredRemovalPercent,
  });

  final String parameter;
  final double? observedValue;
  final String? observedUnit;
  final double? limitHigh;
  final String? status;
  final double? requiredRemovalPercent;

  factory Exceedance.fromJson(Map<String, dynamic> json) {
    return Exceedance(
      parameter: _stringValue(json['parameter'], fallback: 'parameter'),
      observedValue: _nullableDouble(json['observed_value']),
      observedUnit: _nullableString(json['observed_unit']),
      limitHigh: _nullableDouble(json['limit_high']),
      status: _nullableString(json['status']),
      requiredRemovalPercent: _nullableDouble(json['required_removal_percent']),
    );
  }

  String get summary {
    final observed =
        observedValue == null ? '?' : observedValue!.toStringAsFixed(2);
    final limit = limitHigh == null ? '?' : limitHigh!.toStringAsFixed(2);
    final unit = observedUnit == null ? '' : ' $observedUnit';
    return '$parameter: $observed$unit (limit $limit$unit)';
  }
}

class RecommendationAssemblyBundle {
  RecommendationAssemblyBundle({
    required this.useCase,
    required this.assemblyMethod,
    required this.recommendationCount,
    required this.recommendations,
    required this.weightsStatus,
    required this.expertValidated,
    required this.rankingMethod,
    required this.confidenceMethod,
    required this.plantMatchingMethod,
    required this.warnings,
    required this.notes,
  });

  final String? useCase;
  final String? assemblyMethod;
  final int recommendationCount;
  final List<RecommendationItem> recommendations;
  final String? weightsStatus;
  final bool expertValidated;
  final String? rankingMethod;
  final String? confidenceMethod;
  final String? plantMatchingMethod;
  final List<String> warnings;
  final List<String> notes;

  factory RecommendationAssemblyBundle.fromJson(Map<String, dynamic> json) {
    final rows = json['recommendations'];
    return RecommendationAssemblyBundle(
      useCase: _nullableString(json['use_case']),
      assemblyMethod: _nullableString(json['assembly_method']),
      recommendationCount: _intValue(json['recommendation_count']),
      recommendations: rows is List
          ? rows
              .whereType<Map<String, dynamic>>()
              .map(RecommendationItem.fromJson)
              .toList()
          : <RecommendationItem>[],
      weightsStatus: _nullableString(json['weights_status']),
      expertValidated: json['expert_validated'] == true,
      rankingMethod: _nullableString(json['ranking_method']),
      confidenceMethod: _nullableString(json['confidence_method']),
      plantMatchingMethod: _nullableString(json['plant_matching_method']),
      warnings: _stringList(json['warnings']),
      notes: _stringList(json['notes']),
    );
  }
}

class RecommendationItem {
  RecommendationItem({
    required this.nbsId,
    required this.nbsName,
    required this.rank,
    required this.matchScore,
    required this.topsisCloseness,
    required this.confidenceScore,
    required this.confidenceLabel,
    required this.weightsStatus,
    required this.expertValidated,
    required this.rankingMethod,
    required this.confidenceMethod,
    required this.plantMatches,
    required this.evidenceSummary,
    required this.criteriaBreakdown,
    required this.whyRecommended,
    required this.cautions,
    required this.dataGaps,
    required this.implementationSummary,
    required this.explanation,
    required this.warnings,
    required this.notes,
  });

  final int? nbsId;
  final String nbsName;
  final int? rank;
  final double? matchScore;
  final double? topsisCloseness;
  final double? confidenceScore;
  final String? confidenceLabel;
  final String? weightsStatus;
  final bool expertValidated;
  final String? rankingMethod;
  final String? confidenceMethod;
  final List<Map<String, dynamic>> plantMatches;
  final EvidenceSummary evidenceSummary;
  final List<CriterionBreakdown> criteriaBreakdown;
  final List<String> whyRecommended;
  final List<String> cautions;
  final List<String> dataGaps;
  final String? implementationSummary;
  final List<String> explanation;
  final List<String> warnings;
  final List<String> notes;

  factory RecommendationItem.fromJson(Map<String, dynamic> json) {
    final plantRows = json['plant_matches'];
    final evidenceJson = json['evidence_summary'];
    final breakdownRows = json['criteria_breakdown'];
    return RecommendationItem(
      nbsId: _nullableInt(json['nbs_id']),
      nbsName: _stringValue(json['nbs_name'], fallback: 'Unnamed NbS option'),
      rank: _nullableInt(json['rank']),
      matchScore: _nullableDouble(json['match_score']),
      topsisCloseness: _nullableDouble(json['topsis_closeness']),
      confidenceScore: _nullableDouble(json['confidence_score']),
      confidenceLabel: _nullableString(json['confidence_label']),
      weightsStatus: _nullableString(json['weights_status']),
      expertValidated: json['expert_validated'] == true,
      rankingMethod: _nullableString(json['ranking_method']),
      confidenceMethod: _nullableString(json['confidence_method']),
      plantMatches: plantRows is List
          ? plantRows.whereType<Map<String, dynamic>>().toList()
          : <Map<String, dynamic>>[],
      evidenceSummary: evidenceJson is Map<String, dynamic>
          ? EvidenceSummary.fromJson(evidenceJson)
          : EvidenceSummary.empty(),
      criteriaBreakdown: breakdownRows is List
          ? breakdownRows
              .whereType<Map<String, dynamic>>()
              .map(CriterionBreakdown.fromJson)
              .toList()
          : <CriterionBreakdown>[],
      whyRecommended: _stringList(json['why_recommended']),
      cautions: _stringList(json['cautions']),
      dataGaps: _stringList(json['data_gaps']),
      implementationSummary: _nullableString(json['implementation_summary']),
      explanation: _stringList(json['explanation']),
      warnings: _stringList(json['warnings']),
      notes: _stringList(json['notes']),
    );
  }

  String get matchPercent => _percent(matchScore);
  String get topsisPercent => _percent(topsisCloseness);
  String get confidencePercent => _percent(confidenceScore);
}

class EvidenceSummary {
  EvidenceSummary({
    required this.sourceIds,
    required this.cautionFlags,
    required this.warnings,
    required this.notes,
  });

  final List<int> sourceIds;
  final List<String> cautionFlags;
  final List<String> warnings;
  final List<String> notes;

  factory EvidenceSummary.fromJson(Map<String, dynamic> json) {
    return EvidenceSummary(
      sourceIds: _intList(json['source_ids']),
      cautionFlags: _stringList(json['caution_flags']),
      warnings: _stringList(json['warnings']),
      notes: _stringList(json['notes']),
    );
  }

  factory EvidenceSummary.empty() {
    return EvidenceSummary(
      sourceIds: const [],
      cautionFlags: const [],
      warnings: const [],
      notes: const [],
    );
  }
}

class Citation {
  Citation({
    required this.id,
    required this.short,
    required this.citation,
    required this.type,
    required this.url,
    required this.license,
  });

  final int id;
  final String? short;
  final String? citation;
  final String? type;
  final String? url;
  final String? license;

  factory Citation.fromJson(Map<String, dynamic> json) {
    return Citation(
      id: _intValue(json['id']),
      short: _nullableString(json['short']),
      citation: _nullableString(json['citation']),
      type: _nullableString(json['type']),
      url: _nullableString(json['url']),
      license: _nullableString(json['license']),
    );
  }

  /// Best human-readable label for the citation.
  String get display => citation ?? short ?? 'Source $id';
}

class CriterionBreakdown {
  CriterionBreakdown({
    required this.criterionName,
    required this.normalizedValue,
    required this.weight,
    required this.weightedValue,
  });

  final String criterionName;
  final double normalizedValue;
  final double weight;
  final double weightedValue;

  factory CriterionBreakdown.fromJson(Map<String, dynamic> json) {
    return CriterionBreakdown(
      criterionName:
          _stringValue(json['criterion_name'], fallback: 'criterion'),
      normalizedValue: _nullableDouble(json['normalized_value']) ?? 0,
      weight: _nullableDouble(json['weight']) ?? 0,
      weightedValue: _nullableDouble(json['weighted_value']) ?? 0,
    );
  }

  String get label {
    final readable = criterionName.replaceAll('_', ' ');
    return readable.isEmpty
        ? criterionName
        : '${readable[0].toUpperCase()}${readable.substring(1)}';
  }

  String get normalizedPercent => _percent(normalizedValue);
}

String _percent(double? value) {
  if (value == null) {
    return 'Not available';
  }
  return '${(value * 100).clamp(0, 100).toStringAsFixed(1)}%';
}

String _stringValue(Object? value, {String fallback = ''}) {
  if (value == null) {
    return fallback;
  }
  return value.toString();
}

String? _nullableString(Object? value) {
  if (value == null) {
    return null;
  }
  final text = value.toString();
  return text.isEmpty ? null : text;
}

int _intValue(Object? value) {
  return _nullableInt(value) ?? 0;
}

int? _nullableInt(Object? value) {
  if (value is int) {
    return value;
  }
  if (value is num) {
    return value.toInt();
  }
  return int.tryParse(value?.toString() ?? '');
}

double? _nullableDouble(Object? value) {
  if (value is double) {
    return value;
  }
  if (value is num) {
    return value.toDouble();
  }
  return double.tryParse(value?.toString() ?? '');
}

List<String> _stringList(Object? value) {
  if (value is! List) {
    return const [];
  }
  return value.map((item) => item.toString()).toList();
}

List<int> _intList(Object? value) {
  if (value is! List) {
    return const [];
  }
  return value.map(_nullableInt).whereType<int>().toList();
}
