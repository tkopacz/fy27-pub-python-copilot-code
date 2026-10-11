# Standardy jakości i kryteria akceptacji ćwiczenia

> **Działająca aplikacja nie oznacza dobrego kodu ani użytecznego interfejsu.
> Zielone testy potwierdzają tylko to, co rzeczywiście sprawdzają.**

To jawny standard ćwiczenia przyjęty na jego potrzeby. Nie jest standardem
żadnej konkretnej firmy ani deklaracją pełnej zgodności z WCAG. Obowiązuje
uczestników i agenta. Nie dodawaj kolejnych zasad po zapoznaniu się
z rozwiązaniem.

## 1. Problemy projektu startowego

| Obszar | Dowód w kodzie / zachowaniu | Dlaczego to problem | Zadanie uczestnika i agenta |
|---|---|---|
| Błąd funkcjonalny | Telefon ze spacjami dociera do klasyfikatora bez maskowania | Niespełnione wymaganie przetwarzania wejścia | Najpierw czerwony test, potem poprawka i regresje |
| Standard kodu K1 | [providers.py](../triage/providers.py) zawiera algorytm trybu `demo`, polecenie dla modelu, adapter SDK i wybór dostawcy | Reguły domenowe i integracja z modelem zmieniają się z różnych powodów | Oddziel klasyfikator regułowy od integracji trybu `live`, nie zmieniając zachowania |
| Standard kodu K2 | Jeden odbiornik zdarzenia `submit` w [interfejsie](../triage/templates/index.html) odczytuje formularz, wykonuje żądanie HTTP, interpretuje odpowiedź i wyświetla komunikaty | Warstwa prezentacji i komunikacja są ze sobą powiązane, przez co trudno osobno sprawdzać różne stany interfejsu | Wydziel niewielkie funkcje do wysyłania żądań i wyświetlania stanów; zachowaj prostą aplikację |
| Użyteczność U1 | Głównym wynikiem jest surowy JSON z `commerce-support`, `manual_review` itp. | Osoba obsługująca zgłoszenie musi tłumaczyć kontrakt techniczny na decyzję | Pokaż podsumowanie po polsku; JSON pozostaw jako zwijane szczegóły |
| Użyteczność U2 | Komunikat `Błąd HTTP 502: ...` pokazuje techniczną treść odpowiedzi | Użytkownik nie dowiaduje się, co może teraz zrobić | Podaj zrozumiały powód, następny krok i możliwość ponowienia |
| Użyteczność U3 | Po wysłaniu kolejnego zgłoszenia poprzedni wynik zastępuje napis „Przetwarzanie...” | Użytkownik traci poprzedni wynik i kontekst | Oddziel stan bieżącej operacji od ostatniego wyniku i oznacz, którego zgłoszenia dotyczy |

**Nie twierdzimy, że cały projekt startowy jest wadliwy.** Już ma etykiety pól, `required`,
`aria-live`, blokadę przycisku podczas żądania, `textContent` zamiast wstawiania
niezaufanego HTML, walidację odpowiedzi modelu i jawne błędy. Zachowaj te zalety.
Nie zgłaszaj „braku etykiet” czy „braku obsługi błędów” bez dowodu.

K1 i K2 to świadomie przyjęte granice odpowiedzialności na potrzeby ćwiczenia.
Nie wymagamy dowolnej liczby warstw, plików ani klas ani rozbudowanej
architektury korporacyjnej. Przeniesienie klasy do osobnego modułu oraz
wydzielenie kilku funkcji interfejsu może wystarczyć.

## 2. Jak korzystać z kryteriów

1. **Najpierw kryterium**, potem test lub próba użytkownika.
2. Dla naprawy lub nowej funkcji uruchom test, który ujawnia problem,
   popraw implementację i uruchom go ponownie. Błąd importu nie oznacza,
   że test wykrył błąd biznesowy.
3. Dla refaktoryzacji najpierw zabezpiecz **obecne** zachowanie testami
   charakteryzującymi. Wyniki przed refaktoryzacją i po niej powinny być takie same.
   Nie mieszaj jej z poprawą jakości klasyfikatora ani zmianą kontraktu.
4. Nie usuwaj testów, nie dodawaj `skip/xfail` i nie osłabiaj asercji, żeby
   uzyskać zielony wynik. Nowe wymaganie może uzasadniać konkretną zmianę
   kontraktu testu.
5. Nie utrwalaj słabego zachowania jako wymagania docelowego: testy
   charakteryzujące służą etapowi refaktoryzacji; późniejszą zmianę zachowania
   uzasadnij nowym kryterium i aktualizacją odpowiedniej asercji.
6. Nie traktuj regexu, promptu ani samego testu „status HTTP == 200” jako
   gwarancji jakości całej aplikacji. Obejrzyj konkretne wartości odpowiedzi
   i zachowanie interfejsu.

Poniższa tabela wskazuje oczekiwane zachowania i sposób ich sprawdzenia.
Porównuj z nią wyniki testów i działanie aplikacji; nie wypełniaj jej.

## 3. Macierz akceptacji

`NOWE` oznacza wymaganie do pokrycia przez uczestników. Nie jest kolejnym
czerwonym testem w dostarczonym projekcie startowym. Nadal jest dokładnie jeden FAIL.
Po zakończeniu ćwiczenia wszystkie testy i wymagane sprawdzenia mają przejść.

**Zakres rdzenia to AC-01–AC-10.** AC-11 należy do opcjonalnego rozszerzenia
TUI i nie jest potrzebne do wykonania rdzenia. Własne instrukcje, kontekst,
skille i plugin są ćwiczeniami pracy z Copilotem, a nie dodatkowymi polami API.

| ID | Oczekiwane zachowanie | Co uruchomić lub obejrzeć |
|---|---|---|
| AC-01 | Dla komentarza z numerem telefonu zapisanym ze spacjami ani argument dostawcy, ani szkic nie zawiera numeru; treść biznesowa pozostaje | Uruchom `test_privacy.py` i obejrzyj argument dostawcy oraz szkic dla wymaganych formatów |
| AC-02 | Dla samej pochwały: `informational`, `no_action`, brak szkicu | Uruchom test serwisu/API i obejrzyj dokładne wartości pól |
| AC-03 | Dla pochwały połączonej z blokadą zamawiania: `order`, P1, `actionable` i szkic; dla spokojnego opisu uszkodzonego produktu: P2 i szkic | Uruchom przypadki testowe i obejrzyj wynik używanego klasyfikatora |
| AC-04 | Dla niejasnego zgłoszenia oraz sprzecznego `other + actionable`: `unclear`, `manual_review` i brak szkicu | Uruchom testy, w tym przypadek dostawcy zwracającego sprzeczne dane |
| AC-05 | Dla niepoprawnej kategorii modelu lub awarii punktu końcowego: 502, jawny błąd, brak szkicu i brak automatycznego przełączenia trybu | Uruchom regresje API i obejrzyj komunikat błędu |
| AC-06 | Po oddzieleniu odpowiedzialności K1/K2 dotychczasowe API i wyniki klasyfikatora się nie zmieniają; demo nie wymaga klienta LLM | Uruchom testy charakteryzujące, porównaj 25 wyników przed/po K1 i obejrzyj podział odpowiedzialności |
| AC-07 | Po uzyskaniu wyniku, bez otwierania JSON, widać decyzję, kategorię, priorytet, zespół, krótkie uzasadnienie i informację, że szkic nie został wysłany | Użyj formularza i spróbuj odczytać wynik z interfejsu |
| AC-08 | Po błędzie polski komunikat wskazuje dalsze postępowanie, tekst pozostaje w formularzu i można ponowić żądanie; jego stan jest oddzielony od wcześniejszego wyniku | Sprawdź sekwencję: powodzenie → kolejne żądanie → błąd → ponowienie |
| AC-09 | Formularz można wypełnić i wysłać klawiaturą, rozpoznać fokus i odczytać stan; przy szerokości 375 px nie występuje poziome przewijanie głównego widoku | Spróbuj obsługi klawiaturą i obejrzyj widok w wąskim oknie; sam zrzut ekranu nie wystarczy |
| AC-10 | Macro-F1 >=0,90 i trafność priorytetów >=0,90 na zbiorze rozwojowym, zmierzone w tym samym trybie aplikacji i, dla `live`, na tym samym modelu klasyfikującym | Uruchom pomiar początkowy i końcowy oraz porównaj oba progi; zbiór kontrolny uruchom osobno |
| AC-11 | Konsola pobiera sklep i komentarz, zwraca JSON jak WWW; współdzieli walidację i maskowanie, nie zmienia API ani raportu ewaluacji | Porównaj JSON konsoli i API; sprawdź kanały, kody wyjścia i przypadki opisane poniżej |

AC-11 jest opcjonalne. W jednym uruchomieniu `python -m triage.console`
użytkownik wpisuje `store_id` i komentarz, po jednym wierszu na pole.
Sukces: pytania na `stderr`, jeden JSON na `stdout`, kod `0`, również
dla `no_action` i `manual_review`. Błąd: komunikat na `stderr`, pusty
`stdout`, kod `1`. EOF/przerwanie: bez JSON, kod `2`, bez klasyfikacji
niedokończonego wejścia. Nie ma nowych pakietów, historii komentarzy,
automatycznego przełączenia `live` na `demo` ani wysłania szkicu.

Porównaj wszystkie pola i wartości z API przy identycznym wejściu
i kontrolowanej odpowiedzi dostawcy. Obejrzyj problem, pochwałę,
niejasną sprawę, pusty tekst, tekst >4000 znaków, błędny sklep,
maskowanie wymaganych formatów PII, błąd dostawcy i przerwanie.
Sprawdź, że przekierowany `stdout` zawiera tylko JSON po sukcesie
i jest pusty po błędzie. Przy niezależnych wywołaniach `live` nie
porównuj dosłownie swobodnego uzasadnienia modelu.

Test usługi z kontrolowaną odpowiedzią dostawcy potwierdza kierowanie zgłoszeń,
a nie jakość modelu. Dlatego AC-03 wymaga również sprawdzenia przykładów
na używanym klasyfikatorze. Zewnętrznego dużego modelu językowego (LLM) nie
uruchamiamy w testach jednostkowych.

Model klasyfikujący w AC-10 to model aplikacji w trybie `live`, nie model
wybrany w Copilocie. Tryb `demo` używa reguł, nie modelu językowego.

### Samodzielne sprawdzenie interfejsu

1. **Zadanie użytkownika:** „Ustal, czy trzeba działać, jaki jest priorytet
   i kto powinien zająć się sprawą. Czy zgłoszenie zostało już wysłane?”
2. Odczytaj z interfejsu decyzję, priorytet, zespół i stan wysłania,
   bez otwierania JSON.
3. Sprawdź trzy stany: szkic do zatwierdzenia, brak działania, ręczny przegląd.
   Nie używaj wyłącznie koloru do ich odróżniania.
4. Sprawdź sukces, kolejne oczekujące żądanie, błąd i udane ponowienie.
   Poprzedni wynik może pozostać, ale musi być jawnie opisany jako poprzedni
   i powiązany z poprzednim zgłoszeniem. Nie pokazuj go jako nowego sukcesu.
5. Sprawdź klawiaturę i 375 px. Zachowaj etykiety, widoczny fokus i czytelny
   status dostępny dla technologii asystujących. Nie ogłaszaj pełnej
   zgodności z WCAG na podstawie tych kilku sprawdzeń.

Wykonaj te próby w przeglądarce. Nie instaluj dodatkowego środowiska do budowy
interfejsu ani nowego narzędzia testowego tylko na potrzeby warsztatu.
Sam zrzut ekranu nie sprawdza klawiatury ani ponowienia żądania.

Po samej refaktoryzacji oczekuj **zachowania bez zmian**. Po dodaniu funkcji
lub poprawie użyteczności oczekuj **jawnie określonej zmiany**. Jeśli coś
nie działa, popraw to; nie trzeba przygotowywać ani przekazywać zestawienia
statusów kryteriów.
