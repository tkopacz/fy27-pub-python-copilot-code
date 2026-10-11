---
description: "Stosuj przy tworzeniu lub zmianie testów pytest dotyczących kontraktów triage, prywatności, dostawców lub zachowania API."
applyTo: "tests/**/*.py"
---

# Dowody z testów triage

- Powiąż każdy dodany lub zmieniony test z odpowiednim kryterium akceptacji i obserwowalnym kontraktem, nie z wewnętrznymi szczegółami implementacji.
- Przy naprawie lub nowym zachowaniu pokaż przed zmianą implementacji asercję nieprzechodzącą z właściwej przyczyny. Błąd importu lub przygotowania środowiska nie jest takim dowodem.
- Przed refaktoryzacją utrwal obecne zachowanie testami charakteryzującymi i porównaj istotne wyniki przed zmianą i po niej. Oddziel to od zmian zachowania.
- Nie usuwaj testów, nie osłabiaj asercji ani nie dodawaj `skip` lub `xfail`, aby uzyskać zielony wynik. Jeżeli nowe wymaganie zmienia oczekiwanie kontraktu, wyjaśnij tę konkretną zmianę.
- Korzystaj z istniejących danych i mechanizmów przygotowania testów pytest (fixtures) oraz parametryzacji. Używaj kontrolowanych klasyfikatorów i atrap odpowiedzi oraz awarii dostawcy. Nigdy nie wywołuj rzeczywistego modelu w testach jednostkowych.
- Sprawdzaj pola i wartości odpowiedzi, obecność lub brak szkicu oraz obsługę błędów, nie tylko status HTTP. W testach prywatności sprawdzaj wejście klasyfikatora i eksportowany szkic; uwzględniaj też przypadki, które muszą pozostać niezmienione.
- Najpierw uruchamiaj testy dotyczące zmiany, potem właściwe regresje, np. `.\scripts\test.ps1 -PytestArgs @("tests\test_privacy.py", "-q")`. Odczytaj podsumowanie testów i sprawdź, czy obejmuje kontrakt istotny dla zmiany.
