# Brief: od komentarza do działania

## Kontekst

Pracujesz nad prototypem wspierającym obsługę syntetycznych zgłoszeń dotyczących
sklepów. Nie masz dostępu do rzeczywistego systemu obsługi zamówień ani
zewnętrznego systemu zgłoszeniowego. System ma proponować
klasyfikację i szkic, a nie samodzielnie podejmować decyzje operacyjne.
Wszystkie dane w paczce są fikcyjne.

## Kontrakt początkowy

`POST /api/triage`, `Content-Type: application/json`:

```json
{
  "store_id": "store-001",
  "text": "Obsługa super, ale nie mogę zamówić towaru."
}
```

Odpowiedź 200:

```json
{
  "store_id": "store-001",
  "sanitized_text": "Obsługa super, ale nie mogę zamówić towaru.",
  "category": "order",
  "priority": "P1",
  "sentiment": "mixed",
  "rationale": "Wynik demonstracyjnej reguły słownikowej; wymaga weryfikacji przez człowieka.",
  "team": "commerce-support",
  "review_status": "draft_ready",
  "jira_draft": {
    "project": "DEMO",
    "issuetype": "Task",
    "summary": "[store-001] order",
    "description": "Obsługa super, ale nie mogę zamówić towaru.\n\nUzasadnienie: Wynik demonstracyjnej reguły słownikowej; wymaga oceny człowieka.",
    "priority": "P1",
    "team": "commerce-support"
  },
  "mode": "demo"
}
```

Nie należy porównywać za pomocą asercji swobodnego uzasadnienia zwracanego
przez model w trybie `live`.
Pozostałe pola mają zamknięty kontrakt.

### Kategorie i zespoły

| Kategoria | Znaczenie | Zespół |
|---|---|---|
| `order` | Składanie zamówienia, koszyk, aplikacja zamówień | `commerce-support` |
| `delivery` | Transport, termin dostawy, braki w dostawie | `logistics` |
| `store_service` | Obsługa, kolejki, organizacja pracy sklepu | `store-operations` |
| `product` | Dostępność, cena, jakość produktu | `quality` |
| `other` | Niewystarczające informacje / poza taksonomią | `manual-triage` |

### Priorytety

- `P1`: jawna niemożność złożenia zamówienia albo brak całej dostawy.
- `P2`: inny problem wymagający działania.
- `P3`: pochwała, informacja lub zbyt mało danych.
- W komentarzu mieszanym kategorię wyznacza problem, nie pochwała.
- Kilka problemów: najwyższy priorytet; remis: `order`, `delivery`, `product`,
  `store_service`, `other`.

To celowo uproszczona taksonomia szkoleniowa, a nie procedura operacyjna
konkretnej sieci handlowej. Nie obejmuje obsługi sytuacji kryzysowych.

### Sentyment, przegląd i szkic

- Sentyment: `positive`, `neutral`, `negative`, `mixed`.
- Początkowo `other` oznacza `manual_review`, bez szkicu.
- Inna poprawna kategoria oznacza `draft_ready`, ze szkicem.
- `draft_ready` **nie oznacza zatwierdzenia ani wysłania do systemu zgłoszeniowego**.
- Szkic ma format lokalny i nie jest pełnym żądaniem API systemu zgłoszeniowego.
- Początkowo sama pochwała też otrzymuje szkic. Zmiana tego zachowania to
  nowe wymaganie, nie drugi celowo uszkodzony test.

### Walidacja i błędy

| Sytuacja | Odpowiedź |
|---|---|
| Niepoprawny JSON, pola, typy, pusty tekst, tekst >4000 znaków | 400 + `error` |
| `store_id` inne niż `store-` i trzy cyfry | 400 + `error` |
| Treść >16 KiB | 413 + `error` |
| Inny Content-Type | 415 + `error` |
| Błąd punktu końcowego lub odpowiedź modelu niezgodna z kontraktem | 502 + `error`, bez szkicu |
| Nieznany tryb / brak konfiguracji live | Jawny błąd przy starcie |

Nie ma automatycznego przełączania z trybu `live` na `demo`.
`GET /health` sprawdza proces aplikacji, **nie połączenie z modelem**.
`GET /` udostępnia formularz.

### Dane osobowe — zakres ćwiczenia

Przed wywołaniem klasyfikatora i przed eksportem maskuj:

- adresy e-mail w prostych formatach z przykładów;
- polskie telefony: `500600700`, `+48500600700`, `500 600 700`,
  `+48 500 600 700`, `500-600-700`;
- 11-cyfrowe ciągi przypominające PESEL, bez sprawdzania sumy kontrolnej.

Projekt startowy nie obsługuje jeszcze wszystkich wymaganych formatów numeru telefonu.
To przyczyna jednego czerwonego testu. Nie przesyłaj rzeczywistych danych.
Maskowanie jest heurystyką; nie gwarantuje anonimizacji, nie obejmuje nazwisk,
adresów ani wszystkich wariantów PII i nie dowodzi zgodności z RODO.

## Nowe wymaganie: potrzeba działania

Dodaj pole `actionability` do kontraktu klasyfikatora i odpowiedzi API:

| Wartość | Znaczenie | `review_status` | Szkic |
|---|---|---|---|
| `actionable` | Konkretny problem operacyjny, znana kategoria | `draft_ready` | Tak |
| `informational` | Wyłącznie pochwała / informacja, znana kategoria | `no_action` | Nie |
| `unclear` | Nie wiadomo, czego dotyczy sprawa / brak podstaw | `manual_review` | Nie |

`category=other` zawsze wymusza ręczny przegląd. Sprzeczność
`other + actionable` albo `other + informational` traktuj zachowawczo:
normalizuj wynik do `actionability=unclear` i `manual_review`.
Nie poprawiaj po cichu kategorii spoza listy — nadal zwracaj 502.

Przykłady akceptacyjne:

1. „Miła obsługa, dziękuję.” → `store_service`, `P3`,
   `informational`, `no_action`, `jira_draft=null`.
2. „Miła obsługa, ale składanie zamówień nie działa.” → `order`, `P1`,
   `actionable`, `draft_ready`.
3. „Proszę o kontakt.” → `other`, `P3`, `unclear`, `manual_review`.
4. „Produkt ma uszkodzone opakowanie.” → `product`, `P2`,
   `actionable`, `draft_ready`.

Nie wyprowadzaj potrzeby działania wyłącznie z sentymentu.
Spokojnie opisany problem nadal wymaga działania.

## Co sprawdzić po zmianach

Porównaj wyniki testów, pomiary i działanie aplikacji z
[macierzą jakości](quality-standards.md). Sprawdź poniższe zachowania.

- Napraw pierwotny czerwony test bez zmiany jego oczekiwania.
- Zachowaj dotychczasowe kontrakty poza jawnym rozszerzeniem o nowe pole/status.
- Połącz nowe pole z poleceniem dla modelu, oboma dostawcami, walidacją,
  kierowaniem zgłoszeń, odpowiedzią API, interfejsem, testami i dokumentacją.
- Dodaj testy czterech przykładów i sprzecznego `other + actionable`.
- Sprawdź wymagane formaty telefonu oraz to, że maskowanie nie zmienia
  zwykłych ilości ani identyfikatorów sklepu.
- Porównaj pomiar początkowy i końcowy w tym samym trybie aplikacji i,
  dla `live`, na tym samym modelu klasyfikującym. Tryb `demo` używa reguł,
  nie modelu językowego; wybór modelu Copilota nie jest konfiguracją aplikacji.
- Sprawdź macro-F1 >=0,90 i trafność priorytetów >=0,90 na 25 przykładach.
  To cel ćwiczenia, nie obietnica wyniku dowolnego modelu.
- Po głównej implementacji uruchom osobny zbiór kontrolny.
- Rozdziel reguły domenowe od integracji trybu `live` oraz transport HTTP
  od prezentacji interfejsu, bez zbędnych warstw.
- Sprawdź osobno, że sama refaktoryzacja zachowuje wyniki przed/po.
- W interfejsie rozpoznaj decyzję i kolejny krok po polsku bez czytania JSON.
- Rzuć okiem na obsługę błędu i ponowienia, zachowanie poprzedniego wyniku,
  klawiaturę i wąski ekran.
- Przejrzyj lokalnie zmiany względem `lab-start`, jeśli utworzono ten punkt
  odniesienia; zwróć uwagę także na nowe pliki.

Zbiór 25 przypadków jest jawny i rozwojowy; nie dowodzi zdolności
klasyfikatora do uogólniania. Nie dopisuj reguł rozpoznających ID lub całe
teksty konkretnych przykładów.

## Opcjonalne rozszerzenie po rdzeniu: komentarz z konsoli

Po odtworzeniu specyfikacji istniejącego kodu w Spec Kit
([zadanie 010](../issues/iss010.md)) dodaj nową funkcję
([zadanie 009](../issues/iss009.md), AC-11).

`python -m triage.console` ma pobierać jeden identyfikator sklepu i jeden
komentarz, każdy w osobnym wierszu, a następnie wypisywać JSON oceny
zgodny z aktualną odpowiedzią `POST /api/triage`, jak na WWW.
Modułu nie ma w projekcie startowym. To prosty interfejs tekstowy,
nie monitor ewaluacji ani eksport samego szkicu.

- Współdziel usługę i walidację z WWW; bez nowych pakietów, powielania
  reguł ani wymagania działającego serwera HTTP.
- Zachowaj wszystkie pola wyniku po rdzeniu, w tym `actionability`,
  `review_status` i `jira_draft`. Poprawne `no_action` i `manual_review`
  również zwracają ocenę, ze szkicem `null`.
- Pytania kieruj do `stderr`; sukces to jeden obiekt JSON na `stdout`
  i kod `0`. Błąd walidacji, konfiguracji lub dostawcy to komunikat
  na `stderr`, pusty `stdout` i kod `1`, bez pozornego sukcesu.
- EOF lub przerwanie kończy proces bez JSON z kodem `2`.
  Nie klasyfikuj niedokończonego wejścia.
- Zachowaj wymagane maskowanie, tryby `demo`/`live` i brak automatycznego
  przełączenia na `demo`. Nie zapisuj historii komentarzy ani nie wysyłaj
  szkicu do systemu zgłoszeniowego.
- Kontrakt WWW i dotychczasowy raport ewaluacji pozostają bez zmian.
  Dla kontrolowanego klasyfikatora wynik konsoli i API ma być identyczny.

Rozszerzenie nie należy do rdzenia AC-01–AC-10. Najpierw zatwierdź
osobną specyfikację nowej funkcji, potem plan, zadania i implementację.
