---
name: triage-tests
description: "Stosuj przy uruchamianiu testów regresji ćwiczenia w Pythonie przez pytest i podsumowaniu ich wyniku. Nigdy nie poprawiaj kodu źródłowego."
---

# Uruchamianie testów regresji

Testy Pythona są uruchamiane przez pytest. Opcja `--junitxml` zapisuje
wyniki do `tests.xml` w formacie JUnit XML; narzędzia Javy nie są potrzebne.
Skrypt wykonawczy to dołączony skrypt PowerShell, nie inne środowisko testowe.

1. Pracuj w katalogu głównym aplikacji. Przeczytaj jej `.github/copilot-instructions.md`.
2. Użyj nowego katalogu przebiegu koordynatora w `reports\automation`.
   Wyniki są plikami tymczasowymi tego uruchomienia, nie raportem do oddania.
3. Uruchom dołączony [skrypt](./scripts/run.ps1), używając jego ustalonej
   rzeczywistej ścieżki, nie odgadniętej ścieżki instalacji pluginu:

   ```powershell
   powershell -NoProfile -File '<absolute path to this skill>\scripts\run.ps1' -RunDirectory 'reports\automation\<run-id>'
   ```

   Wykonaj je jako jedno samodzielne polecenie, bez potoków, dodatkowych
   poleceń powłoki ani zmiany na wywołanie przez `&`.
4. Odczytaj kod wyjścia i `totals` z `tests-exit.json` w tym katalogu.
   Skrypt pobiera liczniki z `tests.xml`; nie uruchamiaj dodatkowych
   poleceń powłoki do parsowania XML ani nie zwracaj treści niepowodzeń.
   Kod wyjścia 1 oznacza rzeczywiście niezaliczony test, nie powód
   do przerwania zbierania innych dowodów. Kod 2 lub wyższy oznacza
   problem wykonania lub zebrania wyników.
5. Krótko podsumuj liczbę testów i kod wyjścia. Nie zwracaj treści
   niepowodzeń zawierających komentarze klientów. Zielone regresje nie
   sprawdzają każdego zachowania aplikacji. Nie edytuj źródeł, testów
   ani danych testowych.
