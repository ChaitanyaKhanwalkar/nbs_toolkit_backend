/// Implements browser text downloads and print/save-as-PDF for report export.
library;

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

bool printReportPage() {
  html.window.print();
  return true;
}
