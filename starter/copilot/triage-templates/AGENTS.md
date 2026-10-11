# Instrukcje szablonów triage

To lokalne instrukcje dla katalogu szablonów zawierającego ten plik
i jego podkatalogów. Uzupełniają instrukcje repozytorium, nie zastępują ich.

- Etykiety, decyzje i wskazówki postępowania po błędzie pisz po polsku. Techniczny JSON pozostaw jako opcjonalne szczegóły, nie główny wynik.
- Zachowaj obsługę klawiatury, widoczny fokus, etykiety pól, `aria-live` i blokadę przycisku wysyłania podczas oczekiwania na odpowiedź.
- Wyświetlaj niezaufany tekst przez `textContent` lub szablon z odpowiednim kodowaniem znaków specjalnych, nigdy jako surowy HTML.
- Oddziel ostatni poprawny wynik od stanu bieżącego żądania. Po błędzie zachowaj dane wejściowe i udostępnij wyraźną możliwość ponowienia.
- Obsługę żądań i wyświetlanie wyników umieszczaj w małych, osobnych funkcjach. Przy zadaniu dotyczącym wyłącznie prezentacji nie dodawaj nowego środowiska do budowy interfejsu ani nie zmieniaj kontraktu API.
- Sprawdź obsługę klawiatury, sekwencję sukces → błąd → ponowienie oraz widok o szerokości 375 px. Same testy pytest części serwerowej nie dowodzą użyteczności interfejsu.
