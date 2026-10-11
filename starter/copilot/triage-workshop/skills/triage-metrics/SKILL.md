---
name: triage-metrics
description: "Stosuj przy pomiarze macro-F1 kategorii i trafności priorytetów w trybie demo oraz podsumowaniu wyniku. Nigdy nie dostrajaj klasyfikatora."
---

# Pomiar jakości

1. Pracuj w katalogu głównym aplikacji. Przeczytaj jej `.github/copilot-instructions.md`.
2. Użyj nowego katalogu przebiegu koordynatora w `reports\automation`.
   Wyniki są plikami tymczasowymi tego uruchomienia, nie raportem do oddania.
3. Uruchom dołączony [skrypt](./scripts/run.ps1), używając jego ustalonej rzeczywistej ścieżki:

   ```powershell
   powershell -NoProfile -File '<absolute path to this skill>\scripts\run.ps1' -RunDirectory 'reports\automation\<run-id>'
   ```

   Wykonaj je jako jedno samodzielne polecenie, bez potoków, dodatkowych
   poleceń powłoki ani zmiany na wywołanie przez `&`.
4. Odczytaj `evaluation.json` i `metrics-exit.json`. Porównaj OBIE metryki,
   macro-F1 i trafność priorytetów, z progiem 0.90, bez zaokrąglania.
   Kod wyjścia 0 procesu ewaluacji oznacza tylko ukończenie pomiaru;
   nie potwierdza osiągnięcia progów jakości.
5. Krótko podsumuj tryb, liczbę przypadków, obie metryki i kod wyjścia.
   Podaj tylko identyfikatory rozbieżności, nie treść komentarzy.
   Nie zmieniaj etykiet, zbiorów danych,
   kodu źródłowego ani promptów w celu poprawy wyniku.
   Te metryki nie mierzą potrzeby działania ani użyteczności;
   AC-10 wymaga także porównywalnego pomiaru początkowego.
   Nie korzystaj z punktu końcowego trybu `live`.
