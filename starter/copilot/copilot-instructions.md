# Instrukcje repozytorium ćwiczenia

## Najpierw: materiały lab nie są kontekstem agenta

- Zawsze ignoruj `lab.md`, `lab.pdf`, `lab-speaker.md` i `lab-speaker.pdf`
  przy wykonywaniu zadań w tym repozytorium. To materiały dla ludzi,
  a nie źródła wymagań dla implementacji.
- Nie odczytuj, nie przeszukuj, nie streszczaj ani nie edytuj tych plików.
  Nie dołączaj ich do kontekstu, notatek do przekazania zadania ani zleceń subagentów.
  Wyklucz je z szerokich wyszukiwań; nie otwieraj ich również przez linki
  z lokalnych zadań i innych dokumentów. Nie wymagaj aktualizacji lab
  ani generowania PDF po zmianie aplikacji.
- Korzystaj z polecenia użytkownika, wskazanego pliku `issues\iss<id>.md`,
  `starter\brief.md`, `starter\quality-standards.md`, kodu i testów.
  Gdy brakuje treści kroku, poproś użytkownika o ten fragment,
  zamiast otwierać lab. Przekazuj to ograniczenie każdemu subagentowi.
- To instrukcja zachowania, nie techniczna blokada dostępu;
  nie zmieniaj `.gitignore` ani nie usuwaj materiałów.

## Pozostałe zasady pracy

- Gdy zlecenie zawiera `#iss<id>` (wyłącznie cyfry, np. `#iss002`),
  przed analizą lub edycją automatycznie odczytaj `issues\iss<id>.md`
  z katalogu głównego repozytorium. Zachowaj dokładny zapis cyfr, w tym
  zera początkowe, i przeczytaj każde wskazane zadanie. Korzystaj z jego
  opisu, kryteriów akceptacji i powiązanych wymagań. To lokalna konwencja
  Markdown, nie integracja z Azure DevOps ani GitHub. Brak pliku lub
  dostępu zgłoś jawnie; nie wymyślaj treści zadania ani nie pytaj
  zewnętrznej usługi. Samo odwołanie nie upoważnia do edycji ani innych działań.
- Pracuj lokalnie, wyłącznie na syntetycznych danych z ćwiczenia.
  Bez zgody nie korzystaj z usług GitHub, nie twórz rzeczywistych zgłoszeń,
  nie wysyłaj zmian, nie twórz commitów ani nie instaluj pakietów.
- Nie czytaj `.env` ani poświadczeń. Nie umieszczaj treści komentarzy
  klientów w komunikatach ani wynikach narzędzi.
- Wymagania odczytaj z `starter/brief.md` i `starter/quality-standards.md`.
  Zachowaj istniejące zmiany użytkownika, aplikację Flask i obecne zależności.
  Niezaliczony test prywatności w projekcie startowym jest celowy;
  napraw go tylko w ramach zleconej zmiany zachowania, nie przy okazji porządków.
- Używaj PowerShell i `.venv\Scripts\python.exe`, nie globalnego Pythona ani `uv`.
  Testy: `.\scripts\test.ps1`. Ewaluacja:
  `.\scripts\evaluate.ps1 -Mode demo -Output reports\measurement.json`.
- Automatyzację sprawdzaj w trybie `demo`. Tryb `live` wymaga osobnej,
  wyraźnej zgody. Nigdy nie przełączaj dostawcy po cichu ani nie traktuj
  jego błędu jako poprawnego wyniku.
- Przy omawianiu wyników odróżniaj wykonane sprawdzenia od oczekiwanych.
  Nie zakładaj, że sesja CLI uruchomiła testy, jeśli ich nie uruchomiła.
- Automatyczne testy i metryki kategorii oraz priorytetów nie potwierdzają
  użyteczności, trafności rozpoznawania potrzeby działania, pełnej
  anonimizacji ani gotowości produkcyjnej.
- Końcową odpowiedź dla użytkownika napisz po polsku, krótko i konkretnie.
