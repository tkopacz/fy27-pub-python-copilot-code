---
name: triage-tests
description: "Stosuj przy uruchamianiu testów regresji ćwiczenia w Pythonie przez pytest i podsumowaniu ich wyniku. Nigdy nie poprawiaj kodu źródłowego."
---

# Uruchamianie testów regresji

Testy Pythona są uruchamiane przez pytest. Opcja `--junitxml` zapisuje
wyniki do `tests.xml` w formacie JUnit XML; narzędzia Javy nie są potrzebne.
Skrypt wykonawczy to dołączony skrypt PowerShell, nie inne środowisko testowe.

1. Pracuj w katalogu głównym aplikacji. Przeczytaj jej
   `.github\copilot-instructions.md`.
2. Użyj wskazanego w zleceniu nowego katalogu przebiegu w
   `reports\automation`. Jeśli nie podano katalogu, uzgodnij go przed
   uruchomieniem. Wyniki są lokalnymi plikami tego uruchomienia.
3. Uruchom dołączony [skrypt](scripts/run.ps1), używając rzeczywistej
   pełnej ścieżki tego skilla:

   ```powershell
   powershell -NoProfile `
       -File '<absolute path to this skill>\scripts\run.ps1' `
       -RunDirectory 'reports\automation\<run-id>'
   ```

   To jedno samodzielne polecenie. Nie dodawaj potoków ani innych poleceń.
   Skrypt korzysta z interpretera `.venv` projektu.
4. Odczytaj kod wyjścia i `totals` z `tests-exit.json` w tym katalogu.
   Skrypt pobiera liczniki z `tests.xml`; nie twórz raportów ręcznie.
   Kod wyjścia `1` oznacza niezaliczony test i nie może blokować
   osobnego pomiaru metryk. Kod `2` lub wyższy oznacza problem wykonania
   lub zebrania wyników. Przy błędzie zgłoś go, nie zastępuj wyniku sukcesem.
5. Krótko podsumuj liczbę testów, kod wyjścia i ścieżki raportów.
   Nie zwracaj treści niepowodzeń zawierających komentarze klientów.
   Zielone regresje nie sprawdzają każdego zachowania aplikacji.
   Nie edytuj źródeł, testów ani danych testowych i nie nadpisuj
   wcześniejszych raportów.
