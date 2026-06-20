/// Selects browser report actions on web and safe no-op fallbacks elsewhere.
library;

export 'report_platform_stub.dart'
    if (dart.library.html) 'report_platform_web.dart';
