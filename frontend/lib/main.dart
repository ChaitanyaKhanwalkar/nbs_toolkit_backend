import 'package:flutter/material.dart';

import 'models/recommendation_models.dart';
import 'screens/nbs_screens.dart';
import 'services/recommendation_api.dart';
import 'theme/nbs_theme.dart';

void main() {
  runApp(const NbsToolkitApp());
}

class NbsToolkitApp extends StatelessWidget {
  const NbsToolkitApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NbS Toolkit',
      debugShowCheckedModeBanner: false,
      theme: NbsTheme.light(),
      home: const NbsToolkitShell(),
    );
  }
}

enum AppView { splash, home, entry, loading, results, detail, about, catalogue }

class NbsToolkitShell extends StatefulWidget {
  const NbsToolkitShell({super.key});

  @override
  State<NbsToolkitShell> createState() => _NbsToolkitShellState();
}

class _NbsToolkitShellState extends State<NbsToolkitShell> {
  final _api = RecommendationApi();
  AppView _view = AppView.splash;
  AppView _previousView = AppView.home;
  RecommendationResponse? _response;
  final List<RecommendationResponse> _previousResponses = [];
  RecommendationItem? _selectedItem;
  String? _errorMessage;
  String _entryMode = 'Measured Water Quality';

  void _show(AppView view) {
    setState(() {
      _previousView = _view;
      _view = view;
    });
  }

  Future<void> _runAnalysis(AnalysisInput input) async {
    setState(() {
      _errorMessage = null;
      _view = AppView.loading;
    });
    try {
      final response = await _api.runContextualRecommendation(
        observations: input.observations,
        regionId: input.regionId,
        station: input.station,
        context: input.context,
      );
      if (!mounted) return;
      setState(() {
        if (_response != null) {
          _previousResponses.insert(0, _response!);
          if (_previousResponses.length > 4) {
            _previousResponses.removeLast();
          }
        }
        _response = response;
        _selectedItem = null;
        _view = AppView.results;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _errorMessage = error.toString();
        _view = AppView.entry;
      });
    }
  }

  void _openEntry(String mode) {
    setState(() {
      _entryMode = mode;
      _errorMessage = null;
      _view = AppView.entry;
    });
  }

  void _openDetail(RecommendationItem item) {
    setState(() {
      _selectedItem = item;
      _previousView = AppView.results;
      _view = AppView.detail;
    });
  }

  void _openAbout() {
    setState(() {
      _previousView = _view;
      _view = AppView.about;
    });
  }

  void _backFromAbout() {
    setState(() {
      _view = _previousView == AppView.about ? AppView.home : _previousView;
    });
  }

  @override
  Widget build(BuildContext context) {
    return switch (_view) {
      AppView.splash => SplashScreen(onStart: () => _show(AppView.home)),
      AppView.home => HomeDashboard(
        onStartRecommendation: () => _openEntry('Measured Water Quality'),
        onSelectSite: () => _openEntry('Select Narmada Site / Station'),
        onPollutionScreening: () => _openEntry('Pollution Source Screening'),
        onUploadWater: () => _openEntry('Upload Water Data'),
        onCatalogue: () => _show(AppView.catalogue),
        onAbout: _openAbout,
      ),
      AppView.entry => AnalysisSetupScreen(
        api: _api,
        mode: _entryMode,
        onRun: _runAnalysis,
        onBack: () => _show(AppView.home),
        errorMessage: _errorMessage,
      ),
      AppView.loading => const LoadingScreen(),
      AppView.results => ResultsScreen(
        response: _response!,
        previousScenarios: _previousResponses,
        onViewDetail: _openDetail,
        onNewRun: () => _show(AppView.entry),
        onHome: () => _show(AppView.home),
        onAbout: _openAbout,
      ),
      AppView.detail => DetailScreen(
        item: _selectedItem!,
        citations: _response?.citations ?? const [],
        onBack: () => _show(AppView.results),
      ),
      AppView.about => MethodAboutScreen(onBack: _backFromAbout),
      AppView.catalogue => CatalogueScreen(
        api: _api,
        onBack: () => _show(AppView.home),
      ),
    };
  }
}
