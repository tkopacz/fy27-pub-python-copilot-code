---
name: triage-conductor
description: "Uruchamia lokalne sprawdzenia po zmianie z użyciem dwóch agentów specjalistycznych, skilli i krótkiego podsumowania. Stosuj do powtarzalnych testów i pomiaru metryk."
tools: ["read", "search", "execute", "agent"]
---

# Lokalne sprawdzenie jednym poleceniem

Przestrzegaj `.github/copilot-instructions.md` projektu i przeczytaj
`starter/quality-standards.md`. Nie czytaj `.env`.
Wyklucz `lab.md`, `lab.pdf`, `lab-speaker.md` i `lab-speaker.pdf`
z odczytów, wyszukiwania i kontekstu, także przez linki z issues.
Przekaż to ograniczenie obu agentom; nie dołączaj im treści lab.
Nie edytuj kodu aplikacji, testów, danych testowych ani dokumentacji.

1. Wybierz nowy katalog przebiegu `reports\automation\<unique-run-id>`.
   To tymczasowe wyjście narzędzia; nie proś użytkownika o przekazanie raportu.
2. Wywołaj OBU agentów niestandardowych: `triage-workshop:triage-test-worker`
   i `triage-workshop:triage-metrics-worker`, przekazując im ten sam katalog.
   Każdemu jawnie zleć wczytanie jego skilla i uruchomienie dołączonego skryptu.
   Zapisują rozłączne artefakty i mogą pracować równolegle.
   Poczekaj na zakończenie obu. Nie zastępuj ich wbudowanymi agentami,
   nie wykonuj ich poleceń samodzielnie ani nie zagnieżdżaj delegacji.
3. Jeżeli agent nie może wykonać zadania, zgłoś BLOCKED i nie wymyślaj
   wyników. Niezaliczony test jest oczekiwany w projekcie
   startowym i NIE może powodować pominięcia pomiaru.
4. Znajdź `scripts\summarize.ps1` względem katalogu głównego TEGO pluginu.
   Uruchom poniższe polecenie samodzielnie, bez potoków ani dodatkowych
   poleceń powłoki. Skrypt pośredniczący wywołuje lokalnego Pythona projektu
   i przekazuje jego kod wyjścia:

   ```powershell
   powershell -NoProfile -File '<actual plugin root>\scripts\summarize.ps1' -RunDirectory 'reports\automation\<unique-run-id>'
   ```

   Skrypt podsumowania zwraca 0 dla zaliczonych automatycznych sprawdzeń,
   1 dla niezaliczonych i 2 przy braku lub niepoprawnych dowodach.
   Nigdy nie ukrywaj ani nie zmieniaj znaczenia tych kodów.
5. Odczytaj `summary.json` i krótko podsumuj po polsku, czy testy
   i oba progi metryk przeszły. Wskaż ograniczenia: ten przebieg nie
   sprawdza interfejsu ani nie zastępuje testów poszczególnych funkcji.

Nie uruchamiaj doraźnych poleceń powłoki do sprawdzania ścieżek ani
parsowania XML. Artefakty JSON z kodami wyjścia i licznikami odczytuj
narzędziami do czytania plików.
Kod wyjścia CLI nie jest statusem odbioru; podaj oba osobno, jeżeli są znane.
Ta procedura nie wysyła rzeczywistych zgłoszeń, nie odczytuje poświadczeń
ani nie wywołuje modelu w trybie `live`.
