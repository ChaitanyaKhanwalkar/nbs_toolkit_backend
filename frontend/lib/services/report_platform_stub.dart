/// Provides report-action fallbacks for non-web Flutter targets and tests.
library;

bool downloadReportText(String fileName, String content, String mimeType) =>
    false;

bool printReportPage(String htmlContent) => false;

bool openExternalUrl(String url) => false;
