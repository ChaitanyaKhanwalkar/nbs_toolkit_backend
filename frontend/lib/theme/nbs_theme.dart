import 'package:flutter/material.dart';

class NbsColors {
  static const deepNavy = Color(0xFF071A2E);
  static const riverBlue = Color(0xFF0F4C81);
  static const researchBlue = Color(0xFF1E64C8);
  static const wetlandGreen = Color(0xFF2EAD7A);
  static const riverTeal = Color(0xFF12A6A6);
  static const softBackground = Color(0xFFF5F8FA);
  static const warningAmber = Color(0xFFF59E0B);
  static const mutedGrey = Color(0xFF667085);
  static const cardBorder = Color(0xFFE4E7EC);
  static const textOnDark = Color(0xFFF8FAFC);
}

class NbsTheme {
  static ThemeData light() {
    const colorScheme = ColorScheme(
      brightness: Brightness.light,
      primary: NbsColors.researchBlue,
      onPrimary: Colors.white,
      secondary: NbsColors.riverTeal,
      onSecondary: Colors.white,
      error: Color(0xFFB42318),
      onError: Colors.white,
      surface: Colors.white,
      onSurface: NbsColors.deepNavy,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: NbsColors.softBackground,
      fontFamily: 'Inter',
      fontFamilyFallback: const ['Arial', 'sans-serif'],
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.white,
        foregroundColor: NbsColors.deepNavy,
        elevation: 0,
        centerTitle: false,
      ),
      cardTheme: CardThemeData(
        color: Colors.white,
        elevation: 1,
        shadowColor: Color(0x1A071A2E),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
          side: const BorderSide(color: NbsColors.cardBorder),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: NbsColors.cardBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: NbsColors.cardBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(
            color: NbsColors.researchBlue,
            width: 1.5,
          ),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: NbsColors.researchBlue,
          foregroundColor: Colors.white,
          minimumSize: const Size(48, 48),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          textStyle: const TextStyle(fontWeight: FontWeight.w700),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: NbsColors.researchBlue,
          side: const BorderSide(color: NbsColors.cardBorder),
          minimumSize: const Size(48, 48),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(foregroundColor: NbsColors.riverTeal),
      ),
    );
  }
}
