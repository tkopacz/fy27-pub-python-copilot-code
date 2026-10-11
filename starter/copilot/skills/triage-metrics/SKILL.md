---
name: triage-metrics
description: "Stosuj przy pomiarze macro-F1 kategorii i trafności priorytetów w trybie demo oraz podsumowaniu wyniku. Nigdy nie dostrajaj klasyfikatora."
---

# Pomiar jakości

1. Pracuj w katalogu głównym aplikacji. Przeczytaj jej
   `.github\copilot-instructions.md`.
2. Użyj wskazanego w zleceniu nowego katalogu przebiegu w
   `reports\automation`. Jeśli nie podano katalogu, uzgodnij go przed
   uruchomieniem. Pomiar wykonaj niezależnie od wyniku testów.
3. Uruchom dołączony [skrypt](scripts/run.ps1), używając rzeczywistej
   pełnej ścieżki tego skilla:

   ```powershell
   powershell -NoProfile `
       -File '<absolute path to this skill>\scripts\run.ps1' `
       -RunDirectory 'reports\automation\<run-id>'
   ```

   To jedno samodzielne polecenie. Nie dodawaj potoków ani innych poleceń.
   Skrypt używa `.venv` projektu, wymusza `demo` i wyłącza ładowanie `.env`.
4. Odczytaj `evaluation.json` i `metrics-exit.json`. Porównaj osobno
   `macro_f1` i `priority_accuracy` z progiem `0.90`, bez zaokrąglania.
   Kod wyjścia `0` procesu ewaluacji oznacza tylko ukończenie pomiaru;
   nie potwierdza osiągnięcia progów jakości. Przy błędzie procesu lub
   braku raportu zgłoś problem, nie twórz zastępczego wyniku.
5. Krótko podsumuj tryb, liczbę przypadków, obie metryki, wynik każdego
   porównania z progiem, kod wyjścia i ścieżki raportów.
   Podaj tylko identyfikatory rozbieżności, nie treść komentarzy.
   Nie zmieniaj etykiet, zbiorów danych, kodu ani promptów w celu
   poprawy wyniku. Nie nadpisuj wcześniejszych raportów.
   Te metryki nie mierzą potrzeby działania ani użyteczności;
   AC-10 wymaga także porównywalnego pomiaru początkowego.
   Nie korzystaj z punktu końcowego trybu `live`.
