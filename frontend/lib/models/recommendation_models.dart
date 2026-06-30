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
    required this.componentRecommendations,
    required this.filteredComponents,
    required this.componentRecommendationMethod,
    required this.inputSummary,
    required this.locationContext,
    required this.designReadiness,
    required this.sizingEstimates,
    required this.scenarioComparison,
    required this.parameterCoverage,
    required this.validationNotes,
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
  final List<IndividualNbsRecommendation> componentRecommendations;
  final List<Map<String, dynamic>> filteredComponents;
  final String? componentRecommendationMethod;
  final RecommendationInputSummary inputSummary;
  final LocationContext locationContext;
  final DesignReadiness designReadiness;
  final List<SizingEstimate> sizingEstimates;
  final ScenarioComparison scenarioComparison;
  final List<Map<String, dynamic>> parameterCoverage;
  final Map<String, dynamic> validationNotes;

  /// Resolved citations indexed by source ID for quick lookup in the UI.
  Map<int, Citation> get citationsById {
    return {for (final citation in citations) citation.id: citation};
  }

  factory RecommendationResponse.fromJson(Map<String, dynamic> json) {
    final bundleJson = json['recommendation_assembly_bundle'];
    final exceedanceRows = json['exceedances'];
    final citationRows = json['citations'];
    final trainRows = json['ranked_trains'];
    final componentRows = json['component_recommendations'];
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
      componentRecommendations: componentRows is List
          ? componentRows
              .whereType<Map<String, dynamic>>()
              .map(IndividualNbsRecommendation.fromJson)
              .toList()
          : <IndividualNbsRecommendation>[],
      filteredComponents: (json['filtered_components'] as List?)
              ?.whereType<Map<String, dynamic>>()
              .toList() ??
          <Map<String, dynamic>>[],
      componentRecommendationMethod: _nullableString(
        json['component_recommendation_method'],
      ),
      inputSummary: RecommendationInputSummary.fromJson(
        json['input_summary'] is Map<String, dynamic>
            ? json['input_summary'] as Map<String, dynamic>
            : const <String, dynamic>{},
      ),
      locationContext: LocationContext.fromJson(
        json['location_context'] is Map<String, dynamic>
            ? json['location_context'] as Map<String, dynamic>
            : const <String, dynamic>{},
      ),
      designReadiness: DesignReadiness.fromJson(
        json['design_readiness'] is Map<String, dynamic>
            ? json['design_readiness'] as Map<String, dynamic>
            : const <String, dynamic>{},
      ),
      sizingEstimates: (json['sizing_estimates'] as List?)
              ?.whereType<Map<String, dynamic>>()
              .map(SizingEstimate.fromJson)
              .toList() ??
          <SizingEstimate>[],
      scenarioComparison: ScenarioComparison.fromJson(
        json['scenario_comparison'] is Map<String, dynamic>
            ? json['scenario_comparison'] as Map<String, dynamic>
            : const <String, dynamic>{},
      ),
      parameterCoverage: (json['parameter_coverage'] as List?)
              ?.whereType<Map<String, dynamic>>()
              .toList() ??
          <Map<String, dynamic>>[],
      validationNotes: json['validation_notes'] is Map<String, dynamic>
          ? json['validation_notes'] as Map<String, dynamic>
          : <String, dynamic>{},
    );
  }
}

class LocationContext {
  LocationContext({
    required this.regionId,
    required this.station,
    required this.river,
    required this.district,
    required this.basin,
    required this.subBasin,
    required this.streamOrder,
    required this.streamContext,
    required this.interventionPosition,
    required this.pollutionSourceType,
    required this.pollutionSourceRecordCount,
    required this.riverDischargeCms,
    required this.drainageAreaKm2,
    required this.slopeMean,
    required this.soilType,
    required this.infiltrationClass,
    required this.coordinatesAvailable,
    required this.latitude,
    required this.longitude,
    required this.contextFlags,
    required this.missingSiteInformation,
    required this.contextNotes,
  });

  final int? regionId;
  final String? station;
  final String? river;
  final String? district;
  final String? basin;
  final String? subBasin;
  final double? streamOrder;
  final String? streamContext;
  final String? interventionPosition;
  final String? pollutionSourceType;
  final int? pollutionSourceRecordCount;
  final double? riverDischargeCms;
  final double? drainageAreaKm2;
  final double? slopeMean;
  final String? soilType;
  final String? infiltrationClass;
  final bool coordinatesAvailable;
  final double? latitude;
  final double? longitude;
  final Map<String, bool> contextFlags;
  final List<String> missingSiteInformation;
  final List<String> contextNotes;

  bool get isEmpty =>
      regionId == null && station == null && contextFlags.isEmpty;

  factory LocationContext.fromJson(Map<String, dynamic> json) {
    final flags = json['context_flags'];
    return LocationContext(
      regionId: _nullableInt(json['region_id']),
      station: _nullableString(json['station']),
      river: _nullableString(json['river']),
      district: _nullableString(json['district']),
      basin: _nullableString(json['basin']),
      subBasin: _nullableString(json['sub_basin']),
      streamOrder: _nullableDouble(json['stream_order']),
      streamContext: _nullableString(json['stream_context']),
      interventionPosition: _nullableString(json['intervention_position']),
      pollutionSourceType: _nullableString(json['pollution_source_type']),
      pollutionSourceRecordCount: _nullableInt(
        json['pollution_source_record_count'],
      ),
      riverDischargeCms: _nullableDouble(json['river_discharge_cms']),
      drainageAreaKm2: _nullableDouble(json['drainage_area_km2']),
      slopeMean: _nullableDouble(json['slope_mean']),
      soilType: _nullableString(json['soil_type']),
      infiltrationClass: _nullableString(json['infiltration_class']),
      coordinatesAvailable: json['coordinates_available'] == true,
      latitude: _nullableDouble(json['latitude']),
      longitude: _nullableDouble(json['longitude']),
      contextFlags: flags is Map<String, dynamic>
          ? flags.map((key, value) => MapEntry(key, value == true))
          : <String, bool>{},
      missingSiteInformation: _stringList(json['missing_site_information']),
      contextNotes: _stringList(json['context_notes']),
    );
  }
}

class DesignReadiness {
  DesignReadiness({
    required this.level,
    required this.shortLabel,
    required this.explanation,
    required this.reasons,
    required this.missingInputs,
    required this.requiredNextSteps,
    required this.expertReviewRequired,
    required this.inputChecklist,
  });

  final String level;
  final String shortLabel;
  final String explanation;
  final List<String> reasons;
  final List<String> missingInputs;
  final List<String> requiredNextSteps;
  final bool expertReviewRequired;
  final List<ReadinessInput> inputChecklist;

  factory DesignReadiness.fromJson(Map<String, dynamic> json) {
    final checklist = json['input_checklist'];
    return DesignReadiness(
      level: _stringValue(json['level'], fallback: 'early_screening_only'),
      shortLabel: _stringValue(
        json['short_label'],
        fallback: 'Needs field data',
      ),
      explanation: _stringValue(
        json['explanation'],
        fallback: 'More field and water-quality data are needed.',
      ),
      reasons: _stringList(json['reasons']),
      missingInputs: _stringList(json['missing_inputs']),
      requiredNextSteps: _stringList(json['required_next_steps']),
      expertReviewRequired: json['expert_review_required'] == true,
      inputChecklist: checklist is List
          ? checklist
              .whereType<Map<String, dynamic>>()
              .map(ReadinessInput.fromJson)
              .toList()
          : <ReadinessInput>[],
    );
  }
}

class ReadinessInput {
  ReadinessInput({
    required this.key,
    required this.label,
    required this.status,
  });

  final String key;
  final String label;
  final String status;

  factory ReadinessInput.fromJson(Map<String, dynamic> json) => ReadinessInput(
        key: _stringValue(json['key']),
        label: _stringValue(json['label'], fallback: 'Design input'),
        status: _stringValue(json['status'], fallback: 'missing'),
      );
}

class SizingEstimate {
  SizingEstimate({
    required this.trainId,
    required this.trainName,
    required this.basis,
    required this.flowStatus,
    required this.populationStatus,
    required this.sizingConfidence,
    required this.estimateLabel,
    required this.estimatedAreaLowM2,
    required this.estimatedAreaHighM2,
    required this.areaPerPersonBand,
    required this.landFit,
    required this.fullComponentCoverage,
    required this.inputsUsed,
    required this.missingInputs,
    required this.keyAssumptions,
    required this.designCaution,
    required this.sourceIds,
  });

  final int trainId;
  final String trainName;
  final String basis;
  final String flowStatus;
  final String populationStatus;
  final String sizingConfidence;
  final String estimateLabel;
  final double? estimatedAreaLowM2;
  final double? estimatedAreaHighM2;
  final String? areaPerPersonBand;
  final String landFit;
  final bool fullComponentCoverage;
  final List<String> inputsUsed;
  final List<String> missingInputs;
  final List<String> keyAssumptions;
  final String designCaution;
  final List<int> sourceIds;

  factory SizingEstimate.fromJson(Map<String, dynamic> json) => SizingEstimate(
        trainId: _intValue(json['train_id']),
        trainName:
            _stringValue(json['train_name'], fallback: 'Treatment train'),
        basis: _stringValue(json['basis'], fallback: 'insufficient_data'),
        flowStatus: _stringValue(json['flow_status'], fallback: 'missing'),
        populationStatus: _stringValue(
          json['population_status'],
          fallback: 'not_supplied',
        ),
        sizingConfidence: _stringValue(
          json['sizing_confidence'],
          fallback: 'insufficient_data',
        ),
        estimateLabel: _stringValue(
          json['estimate_label'],
          fallback: 'Not enough information for a bounded estimate',
        ),
        estimatedAreaLowM2: _nullableDouble(json['estimated_area_low_m2']),
        estimatedAreaHighM2: _nullableDouble(json['estimated_area_high_m2']),
        areaPerPersonBand: _nullableString(json['area_per_person_band']),
        landFit: _stringValue(json['land_fit'], fallback: 'insufficient_data'),
        fullComponentCoverage: json['full_component_coverage'] == true,
        inputsUsed: _stringList(json['inputs_used']),
        missingInputs: _stringList(json['missing_inputs']),
        keyAssumptions: _stringList(json['key_assumptions']),
        designCaution: _stringValue(json['design_caution']),
        sourceIds: _intList(json['source_ids']),
      );
}

class ScenarioComparison {
  ScenarioComparison({
    required this.scope,
    required this.currentScenario,
    required this.options,
    required this.componentOptions,
    required this.takeaways,
    required this.limitations,
  });

  final String scope;
  final Map<String, dynamic> currentScenario;
  final List<ComparisonOption> options;
  final List<ComparisonComponent> componentOptions;
  final List<ComparisonTakeaway> takeaways;
  final List<String> limitations;

  factory ScenarioComparison.fromJson(Map<String, dynamic> json) =>
      ScenarioComparison(
        scope: _stringValue(
          json['comparison_scope'],
          fallback: 'current_ranked_alternatives',
        ),
        currentScenario: json['current_scenario'] is Map<String, dynamic>
            ? json['current_scenario'] as Map<String, dynamic>
            : <String, dynamic>{},
        options: (json['options'] as List?)
                ?.whereType<Map<String, dynamic>>()
                .map(ComparisonOption.fromJson)
                .toList() ??
            <ComparisonOption>[],
        componentOptions: (json['component_options'] as List?)
                ?.whereType<Map<String, dynamic>>()
                .map(ComparisonComponent.fromJson)
                .toList() ??
            <ComparisonComponent>[],
        takeaways: (json['takeaways'] as List?)
                ?.whereType<Map<String, dynamic>>()
                .map(ComparisonTakeaway.fromJson)
                .toList() ??
            <ComparisonTakeaway>[],
        limitations: _stringList(json['limitations']),
      );
}

class ComparisonComponent {
  ComparisonComponent({
    required this.nbsId,
    required this.name,
    required this.role,
    required this.suitabilityScore,
    required this.standaloneSuitability,
    required this.applicabilityStatus,
    required this.keyConstraints,
  });

  final int nbsId;
  final String name;
  final String role;
  final double? suitabilityScore;
  final String? standaloneSuitability;
  final String? applicabilityStatus;
  final List<String> keyConstraints;

  factory ComparisonComponent.fromJson(Map<String, dynamic> json) =>
      ComparisonComponent(
        nbsId: _intValue(json['nbs_id']),
        name: _stringValue(json['name'], fallback: 'NbS component'),
        role: _stringValue(json['role'], fallback: 'supporting'),
        suitabilityScore: _nullableDouble(json['suitability_score']),
        standaloneSuitability: _nullableString(json['standalone_suitability']),
        applicabilityStatus: _nullableString(json['applicability_status']),
        keyConstraints: _stringList(json['key_constraints']),
      );
}

class ComparisonOption {
  ComparisonOption({
    required this.trainId,
    required this.name,
    required this.rank,
    required this.technicalMatch,
    required this.resultConfidence,
    required this.confidenceLabel,
    required this.designReadiness,
    required this.landDemand,
    required this.landFit,
    required this.omIntensity,
    required this.applicabilityStatus,
    required this.selectedUseCaseVerdict,
    required this.warnings,
    required this.keyStrength,
    required this.keyLimitation,
    required this.whenToChoose,
  });

  final int trainId;
  final String name;
  final int rank;
  final double? technicalMatch;
  final double? resultConfidence;
  final String? confidenceLabel;
  final String? designReadiness;
  final String? landDemand;
  final String landFit;
  final String omIntensity;
  final String? applicabilityStatus;
  final String selectedUseCaseVerdict;
  final List<String> warnings;
  final String? keyStrength;
  final String? keyLimitation;
  final String whenToChoose;

  factory ComparisonOption.fromJson(
    Map<String, dynamic> json,
  ) =>
      ComparisonOption(
        trainId: _intValue(json['train_id']),
        name: _stringValue(json['name'], fallback: 'Treatment train'),
        rank: _intValue(json['rank']),
        technicalMatch: _nullableDouble(json['technical_match']),
        resultConfidence: _nullableDouble(json['result_confidence']),
        confidenceLabel: _nullableString(json['confidence_label']),
        designReadiness: _nullableString(json['design_readiness']),
        landDemand: _nullableString(json['land_demand']),
        landFit: _stringValue(json['land_fit'], fallback: 'insufficient_data'),
        omIntensity:
            _stringValue(json['om_intensity'], fallback: 'Not recorded'),
        applicabilityStatus: _nullableString(json['applicability_status']),
        selectedUseCaseVerdict: _stringValue(
          json['selected_use_case_verdict'],
          fallback: 'unknown',
        ),
        warnings: _stringList(json['warnings']),
        keyStrength: _nullableString(json['key_strength']),
        keyLimitation: _nullableString(json['key_limitation']),
        whenToChoose: _stringValue(
          json['when_to_choose'],
          fallback:
              'Choose after confirming flow, land, site conditions, and pretreatment requirements.',
        ),
      );
}

class ComparisonTakeaway {
  ComparisonTakeaway({
    required this.label,
    required this.trainId,
    required this.trainName,
    required this.explanation,
  });

  final String label;
  final int? trainId;
  final String? trainName;
  final String explanation;

  factory ComparisonTakeaway.fromJson(Map<String, dynamic> json) =>
      ComparisonTakeaway(
        label: _stringValue(json['label'], fallback: 'Comparison note'),
        trainId: _nullableInt(json['train_id']),
        trainName: _nullableString(json['train_name']),
        explanation: _stringValue(json['explanation']),
      );
}

class IndividualNbsRecommendation {
  IndividualNbsRecommendation({
    required this.nbsId,
    required this.name,
    required this.family,
    required this.componentRank,
    required this.suitabilityScore,
    required this.suitabilityBasis,
    required this.role,
    required this.pollutantsAddressed,
    required this.whereSuitable,
    required this.whereNotSuitable,
    required this.standaloneSuitability,
    required this.standaloneGuidance,
    required this.keyConstraints,
    required this.implementationGuidance,
    required this.plants,
    required this.plantingGuidance,
    required this.sourceIds,
    required this.evidenceStatus,
    required this.applicabilityStatus,
  });

  final int nbsId;
  final String name;
  final String? family;
  final int? componentRank;
  final double? suitabilityScore;
  final String suitabilityBasis;
  final String role;
  final List<String> pollutantsAddressed;
  final List<String> whereSuitable;
  final List<String> whereNotSuitable;
  final String standaloneSuitability;
  final String standaloneGuidance;
  final List<String> keyConstraints;
  final List<String> implementationGuidance;
  final List<Map<String, dynamic>> plants;
  final String plantingGuidance;
  final List<int> sourceIds;
  final String evidenceStatus;
  final String applicabilityStatus;

  factory IndividualNbsRecommendation.fromJson(Map<String, dynamic> json) {
    return IndividualNbsRecommendation(
      nbsId: _intValue(json['nbs_id']),
      name: _stringValue(json['name'], fallback: 'NbS component'),
      family: _nullableString(json['family']),
      componentRank: _nullableInt(json['component_rank']),
      suitabilityScore: _nullableDouble(json['suitability_score']),
      suitabilityBasis: _stringValue(json['suitability_basis']),
      role: _stringValue(json['role']),
      pollutantsAddressed: _stringList(json['pollutants_addressed']),
      whereSuitable: _stringList(json['where_suitable']),
      whereNotSuitable: _stringList(json['where_not_suitable']),
      standaloneSuitability: _stringValue(json['standalone_suitability']),
      standaloneGuidance: _stringValue(json['standalone_guidance']),
      keyConstraints: _stringList(json['key_constraints']),
      implementationGuidance: _stringList(json['implementation_guidance']),
      plants: (json['plants'] as List?)
              ?.whereType<Map<String, dynamic>>()
              .toList() ??
          <Map<String, dynamic>>[],
      plantingGuidance: _stringValue(json['planting_guidance']),
      sourceIds: _intList(json['source_ids']),
      evidenceStatus: _stringValue(json['evidence_status']),
      applicabilityStatus: _stringValue(json['applicability_status']),
    );
  }

  String get suitabilityPercent => _percent(suitabilityScore);
}

class RecommendationInputSummary {
  RecommendationInputSummary({
    required this.selectedSourceType,
    required this.sourceLabel,
    required this.observationCount,
    required this.selectedParameters,
    required this.dataUsed,
    required this.dataQualityNotes,
    required this.context,
  });

  final String? selectedSourceType;
  final String? sourceLabel;
  final int observationCount;
  final List<String> selectedParameters;
  final List<Map<String, dynamic>> dataUsed;
  final List<String> dataQualityNotes;
  final Map<String, dynamic> context;

  String? get workflowMode => _nullableString(context['workflow_mode']);

  bool get isContextOnly =>
      workflowMode == 'site_context_only' ||
      workflowMode == 'pollution_source_screening';

  factory RecommendationInputSummary.fromJson(Map<String, dynamic> json) {
    return RecommendationInputSummary(
      selectedSourceType: _nullableString(json['selected_source_type']),
      sourceLabel: _nullableString(json['source_label']),
      observationCount: _intValue(json['observation_count']),
      selectedParameters: _stringList(json['selected_parameters']),
      dataUsed: (json['data_used'] as List?)
              ?.whereType<Map<String, dynamic>>()
              .toList() ??
          <Map<String, dynamic>>[],
      dataQualityNotes: _stringList(json['data_quality_notes']),
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
    required this.criteriaExplanation,
    required this.applicabilityStatus,
    required this.whyRecommended,
    required this.caveats,
    required this.treatmentSequence,
    required this.trainPathway,
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
    required this.costBenefit,
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
  final List<CriteriaExplanation> criteriaExplanation;
  final String applicabilityStatus;
  final List<String> whyRecommended;
  final List<String> caveats;
  final List<Map<String, dynamic>> treatmentSequence;
  final List<TrainPathwayStep> trainPathway;
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
  final CostBenefitAnalysis? costBenefit;

  factory TrainRecommendation.fromJson(Map<String, dynamic> json) {
    final verdictRows = json['all_use_case_verdicts'];
    final criteriaRows = (json['criteria_explanation'] as List?) ??
        (json['criteria_breakdown'] as List?) ??
        const [];
    final pathwayRows = (json['train_pathway'] as List?) ??
        (json['treatment_sequence'] as List?) ??
        const [];
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
      criteriaExplanation: criteriaRows
          .whereType<Map<String, dynamic>>()
          .map(CriteriaExplanation.fromJson)
          .where((item) => item.code != 'C5')
          .toList(),
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
      trainPathway: pathwayRows
          .whereType<Map<String, dynamic>>()
          .map(TrainPathwayStep.fromJson)
          .toList(),
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
      costBenefit: json['cost_benefit'] is Map
          ? CostBenefitAnalysis.fromJson(_dynamicMap(json['cost_benefit']))
          : null,
    );
  }

  String get matchPercent => _percent(matchScore);
  String get confidencePercent => _percent(confidenceScore);
}

class CostBenefitAnalysis {
  CostBenefitAnalysis({
    required this.screeningCbr,
    required this.displayCbr,
    required this.label,
    required this.benefitScore,
    required this.costBurdenScore,
    required this.benefitComponents,
    required this.costComponents,
    required this.benefitDrivers,
    required this.costDrivers,
    required this.caveats,
    required this.isMonetary,
    required this.method,
    required this.methodName,
    required this.methodDisclaimer,
    required this.denominatorFloorUsed,
    required this.officialRankingUnchanged,
  });

  final double? screeningCbr;
  final String displayCbr;
  final String label;
  final double? benefitScore;
  final double? costBurdenScore;
  final List<CostBenefitComponent> benefitComponents;
  final List<CostBenefitComponent> costComponents;
  final List<String> benefitDrivers;
  final List<String> costDrivers;
  final List<String> caveats;
  final bool isMonetary;
  final String method;
  final String methodName;
  final String methodDisclaimer;
  final bool denominatorFloorUsed;
  final bool officialRankingUnchanged;

  factory CostBenefitAnalysis.fromJson(Map<String, dynamic> json) {
    return CostBenefitAnalysis(
      screeningCbr: _nullableDouble(json['screening_cbr']),
      displayCbr: _stringValue(json['display_cbr'], fallback: 'Not available'),
      label: _stringValue(json['label'], fallback: 'Indicative only'),
      benefitScore: _nullableDouble(json['benefit_score']),
      costBurdenScore: _nullableDouble(json['cost_burden_score']),
      benefitComponents: (json['benefit_components'] as List?)
              ?.whereType<Map>()
              .map((row) => CostBenefitComponent.fromJson(_dynamicMap(row)))
              .toList() ??
          <CostBenefitComponent>[],
      costComponents: (json['cost_components'] as List?)
              ?.whereType<Map>()
              .map((row) => CostBenefitComponent.fromJson(_dynamicMap(row)))
              .toList() ??
          <CostBenefitComponent>[],
      benefitDrivers: _stringList(json['benefit_drivers']),
      costDrivers: _stringList(json['cost_drivers']),
      caveats: _stringList(json['caveats']),
      isMonetary: json['is_monetary'] == true,
      method: _stringValue(
        json['method'],
        fallback: 'screening_non_monetary_v1',
      ),
      methodName: _stringValue(
        json['method_name'],
        fallback: 'Cost-Benefit Ratio Analysis - Screening Level',
      ),
      methodDisclaimer: _stringValue(
        json['method_disclaimer'],
        fallback:
            'Screening-level non-monetary ratio. Does not estimate rupee CAPEX/OPEX.',
      ),
      denominatorFloorUsed: json['denominator_floor_used'] == true,
      officialRankingUnchanged: json['official_ranking_unchanged'] != false,
    );
  }

  String get benefitScoreLabel => _decimal2Label(benefitScore);
  String get costBurdenScoreLabel => _decimal2Label(costBurdenScore);
}

class CostBenefitComponent {
  CostBenefitComponent({
    required this.key,
    required this.label,
    required this.value,
    required this.weight,
    required this.direction,
    required this.status,
    required this.explanation,
  });

  final String key;
  final String label;
  final double? value;
  final double? weight;
  final String direction;
  final String status;
  final String explanation;

  factory CostBenefitComponent.fromJson(Map<String, dynamic> json) {
    return CostBenefitComponent(
      key: _stringValue(json['key']),
      label: _stringValue(json['label'], fallback: 'Component'),
      value: _nullableDouble(json['value']),
      weight: _nullableDouble(json['weight']),
      direction: _stringValue(json['direction']),
      status: _stringValue(json['status'], fallback: 'missing'),
      explanation: _stringValue(json['explanation']),
    );
  }
}

class CriteriaExplanation {
  CriteriaExplanation({
    required this.code,
    required this.name,
    required this.score,
    required this.weight,
    required this.weightedContribution,
    required this.benefitOrCost,
    required this.status,
    required this.note,
  });

  final String code;
  final String name;
  final double? score;
  final double? weight;
  final double? weightedContribution;
  final String? benefitOrCost;
  final String? status;
  final String? note;

  factory CriteriaExplanation.fromJson(Map<String, dynamic> json) {
    return CriteriaExplanation(
      code: _stringValue(
        json['criterion_code'],
        fallback: _stringValue(json['code']),
      ),
      name: _stringValue(
        json['criterion_name'],
        fallback: _stringValue(json['name'], fallback: 'criterion'),
      ),
      score: _nullableDouble(json['score']) ??
          _nullableDouble(json['normalized_value']),
      weight: _nullableDouble(json['weight']),
      weightedContribution: _nullableDouble(json['weighted_contribution']) ??
          _nullableDouble(json['weighted_value']),
      benefitOrCost: _nullableString(json['benefit_or_cost']),
      status: _nullableString(json['status']) ??
          _nullableString(json['data_status']),
      note: _nullableString(json['note']),
    );
  }

  String get label {
    final mapped = _criterionDisplayName(code, name);
    return mapped.isEmpty ? code : mapped;
  }

  String get scoreLabel => _decimalLabel(score);
  String get weightLabel => _decimalLabel(weight);
  String get weightedContributionLabel => _decimalLabel(weightedContribution);
}

class TrainPathwayStep {
  TrainPathwayStep({
    required this.stepOrder,
    required this.componentName,
    required this.componentRole,
    required this.implementationRole,
    required this.nbsId,
  });

  final int? stepOrder;
  final String componentName;
  final String? componentRole;
  final String? implementationRole;
  final int? nbsId;

  factory TrainPathwayStep.fromJson(Map<String, dynamic> json) {
    return TrainPathwayStep(
      stepOrder: _nullableInt(json['step_order']),
      componentName: _stringValue(
        json['component_name'],
        fallback: _stringValue(
          json['step_label'],
          fallback: _stringValue(json['nbs_name'], fallback: 'Treatment step'),
        ),
      ),
      componentRole: _nullableString(json['component_role']) ??
          _nullableString(json['role']),
      implementationRole: _nullableString(json['implementation_role']),
      nbsId: _nullableInt(json['nbs_id']),
    );
  }
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
  String get display => short ?? citation ?? 'Evidence record $id';
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
      criterionName: _stringValue(
        json['criterion_name'],
        fallback: 'criterion',
      ),
      normalizedValue: _nullableDouble(json['normalized_value']) ?? 0,
      weight: _nullableDouble(json['weight']) ?? 0,
      weightedValue: _nullableDouble(json['weighted_value']) ?? 0,
    );
  }

  String get label {
    return _criterionDisplayName('', criterionName);
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

Map<String, dynamic> _dynamicMap(Object? value) {
  if (value is! Map) {
    return <String, dynamic>{};
  }
  return value.map((key, mapValue) => MapEntry(key.toString(), mapValue));
}

String _decimalLabel(double? value) {
  if (value == null) {
    return 'Not available';
  }
  return value.toStringAsFixed(3);
}

String _decimal2Label(double? value) {
  if (value == null) {
    return 'Not available';
  }
  return value.toStringAsFixed(2);
}

String _criterionDisplayName(String code, String name) {
  final byCode = switch (code) {
    'C1' => 'Treatment fit',
    'C2' => 'Standard fit',
    'C3' => 'Site fit',
    'C4' => 'Source fit',
    'C6' => 'Hydrologic fit',
    'C7' => 'Footprint requirement',
    'C8' => 'O&M practicality',
    _ => '',
  };
  if (byCode.isNotEmpty) {
    return byCode;
  }
  final normalized = name.trim().toLowerCase();
  if (normalized == 'om' ||
      normalized == 'o_m' ||
      normalized == 'om_simplicity' ||
      normalized.contains('o&m') ||
      (normalized.contains('operation') &&
          normalized.contains('maintenance'))) {
    return 'O&M practicality';
  }
  final readable = name.replaceAll('_', ' ');
  return readable.isEmpty
      ? name
      : '${readable[0].toUpperCase()}${readable.substring(1)}';
}
