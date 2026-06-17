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

enum AppView {
  splash,
  home,
  entry,
  loading,
  results,
  detail,
  about,
}

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
  RecommendationItem? _selectedItem;
  String? _errorMessage;

  void _show(AppView view) {
    setState(() {
      _previousView = _view;
      _view = view;
    });
  }

  Future<void> _runRecommendation(
    double bod,
    double tss,
    double nitrateN,
    double ph,
  ) async {
    setState(() {
      _errorMessage = null;
      _view = AppView.loading;
    });

    try {
      final response = await _api.runRecommendation(
        bod: bod,
        tss: tss,
        nitrateN: nitrateN,
        ph: ph,
      );
      if (!mounted) {
        return;
      }
      setState(() {
        _response = response;
        _selectedItem = null;
        _view = AppView.results;
      });
    } catch (error) {
      if (!mounted) {
        return;
      }
      setState(() {
        _errorMessage = error.toString();
        _view = AppView.entry;
      });
    }
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
          onStartRecommendation: () => _show(AppView.entry),
          onAbout: _openAbout,
        ),
      AppView.entry => WaterQualityEntryScreen(
          onRun: _runRecommendation,
          onBack: () => _show(AppView.home),
          errorMessage: _errorMessage,
        ),
      AppView.loading => const LoadingScreen(),
      AppView.results => ResultsScreen(
          response: _response!,
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
    };
  }
}
