/// Implements browser text downloads and print/save-as-PDF for report export.
library;

import 'dart:async';

// ignore: avoid_web_libraries_in_flutter, deprecated_member_use
import 'dart:html' as html;

bool downloadReportText(String fileName, String content, String mimeType) {
  final blob = html.Blob([content], mimeType);
  final url = html.Url.createObjectUrlFromBlob(blob);
  html.AnchorElement(href: url)
    ..setAttribute('download', fileName)
    ..click();
  html.Url.revokeObjectUrl(url);
  return true;
}

bool printReportPage(String htmlContent) {
  final printable = htmlContent.replaceFirst(
    '</body>',
    '<script>window.addEventListener("load",function(){window.print();});</script></body>',
  );
  final blob = html.Blob([printable], 'text/html;charset=utf-8');
  final url = html.Url.createObjectUrlFromBlob(blob);
  html.window.open(url, '_blank', 'noopener,noreferrer');
  unawaited(
    Future<void>.delayed(
      const Duration(seconds: 30),
      () => html.Url.revokeObjectUrl(url),
    ),
  );
  return true;
}

bool openExternalUrl(String url) {
  html.window.open(url, '_blank', 'noopener,noreferrer');
  return true;
}
