# NbS Toolkit Frontend

The dashboard supports measured entry, canonical Narmada station selection,
pollution-source screening, and CSV upload (`parameter,value,unit`). Results
show treatment trains with separate match/confidence scores, drinking,
irrigation, and inland-discharge verdicts, applicability caveats, criteria,
sequence, and evidence IDs. Ranking remains provisional pending expert AHP
calibration.

Flutter prototype for the NbS Toolkit decision-support dashboard.

The app posts measured water-quality values to:

`https://maintenance-fantasy-jon-street.trycloudflare.com/api/v1/recommend`

It is intentionally scoped to the current Step L recommendation response and
uses temporary, non-expert-validated weights while AHP expert validation remains
pending.

## Local Commands

```cmd
flutter pub get
flutter analyze
```
