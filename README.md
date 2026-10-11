# Od komentarza do działania

Rdzeń zdalnego hackathonu dla osób pracujących z Pythonem
i generatywną AI, po wcześniejszym przygotowaniu środowiska.
Instrukcje, skille, kontekst, agenci i plugin są rdzeniem; Spec Kit
i końcowe TUI są rozszerzeniami na dodatkową sesję lub pracę domową.
Każda osoba samodzielnie rozwija własną kopię prototypu do wstępnej kwalifikacji
zgłoszeń. To materiał szkoleniowy, a nie integracja z rzeczywistymi systemami
przedsiębiorstwa.

- [Osiem etapów — kolejność, zadania i sprawdzenia](lab.md#mapa-ośmiu-etapów)
- [Szczegółowa instrukcja uczestnika](lab.md)
- [Lokalne zadania — jak w Azure DevOps / Jira, bez usługi](lab.md#lokalne-issues-zamiast-azure-devops)
- [Przewodnik prowadzącego — zawiera rozwiązanie celowego błędu](lab-speaker.md)
- [Kontrakt i reguły biznesowe](starter/brief.md)
- [Standardy kodu, użyteczność i macierz kryteriów akceptacji](starter/quality-standards.md)
- [Dane syntetyczne](starter/data/evaluation.json)
- [Mapa wzorców instrukcji, skilli i pluginu Copilot CLI](starter/copilot/README.md)

## Folder uczestnika — najpierw kopiowanie

Z repozytorium autorów przygotuj **nowy folder poza repozytorium**:

```powershell
.\scripts\export-participant.ps1 -Destination ..\triage-participant
Set-Location ..\triage-participant
code .
```

Dalej pracuj w tej kopii według `lab.md`: utwórz lokalny punkt Git
`lab-start`, przygotuj środowisko i rozpocznij C1. Jeśli otrzymałeś już
paczkę, wystarczy skopiować ją do własnego folderu — nie eksportuj ponownie.

Skrypt kopiuje bieżące źródła według jawnej listy
`scripts\participant-files.txt`, także `issues\iss001.md`–`issues\iss010.md`
symulujące Azure DevOps / Jira oraz nieaktywne wzorce Copilota.
Nie kopiuje `.git`, `.env`, `.venv`, raportów, aktywnej konfiguracji autorów,
materiałów prowadzącego ani pokazu Azure. Nie nadpisuje istniejącego celu,
nie instaluje pakietów i nie tworzy commitów. Autorski `README.md` nie jest
częścią paczki; jej punktem wejścia jest `lab.md`.
Opcjonalne `-IncludePdf` dodaje `lab.pdf`, który wcześniej należy
przebudować przez `gen-pdf.cmd`; zadania `issues` pozostają Markdown.

## Szybki start — PowerShell, w kopii uczestnika

Wymagany jest Python 3.11+ oraz dostęp do zatwierdzonego firmowego źródła pakietów.
Skrypty używają wyłącznie `python`, `venv` i `pip`, bez `uv`.

```powershell
.\scripts\setup.ps1
.\scripts\test.ps1
.\scripts\run.ps1
```

Otwórz http://127.0.0.1:5000. W drugim terminalu:

```powershell
.\scripts\smoke.ps1
.\scripts\evaluate.ps1 -Output reports\baseline.json
```

**Projekt startowy celowo ma dokładnie jeden niezaliczony test**, bez `skip`
i `xfail`. Kod wyjścia testów wynosi 1. Naprawienie błędu aplikacji jest
zadaniem uczestników. Testy nie wymagają dostępu do sieci ani kluczy i nie
wymagają instalacji klienta dużego modelu językowego (LLM).

**Działający projekt startowy nie jest wzorcem jakości.** Celowo pozostawiono
w nim naruszenia opisanych standardów kodu i problemy z użytecznością:
powiązane ze sobą odpowiedzialności, wynik w postaci JSON oraz techniczne
komunikaty o błędach. Uczestnicy mają je poprawić z pomocą agenta: najpierw
ustalić kryteria akceptacji i dodać testy. **Pomyślne uruchomienie testów pytest nie potwierdza
użyteczności interfejsu.**

Domyślny tryb `demo` korzysta z klasyfikatora regułowego, a nie z modelu AI.
Tryb `live` wykorzystuje LangChain i punkt końcowy zgodny z OpenAI Chat Completions.
Konfigurację i ograniczenia opisano w
[instrukcji uczestnika](lab.md#opcjonalny-tryb-live).
Żadne dane nie są wysyłane do zewnętrznego systemu obsługi zgłoszeń ani
zapisywane jako prawdziwe zgłoszenie.

## Automatyzacja pracy z Copilotem

Repozytorium autorów ma [instrukcje utrzymania materiałów](.github/copilot-instructions.md):
przy zmianie ćwiczeń, kodu lub przykładów sprawdzamy i aktualizujemy
instrukcję uczestnika (wraz z mapą etapów) oraz przewodnik prowadzącego razem.
Ta konfiguracja i reguły składu Markdown nie są rozwiązaniem modułu C1;
nie dołączamy ich do paczki uczestników. Wzorce uczestnika pozostają
nieaktywne do czasu utworzenia własnej konfiguracji.

Moduł C1 rozpoczyna ćwiczenie od utworzenia instrukcji repozytorium oraz osobnych,
oszczędzających kontekst reguł dla `triage/**/*.py` i `tests/**/*.py`.
Uczestnik dodaje też regułę odczytu `issues\iss<id>.md` przy odwołaniu
`#iss<id>`, np. `#iss002`. Pliki z zadaniami są częścią paczki uczestnika,
nie integracją z Azure DevOps; nie generujemy dla nich PDF-ów.
Lokalny [wzorzec zasad UI](starter/copilot/triage-templates/AGENTS.md),
przenoszony przez uczestnika do `triage\templates\AGENTS.md`, pokazuje
hierarchię: instrukcje repozytorium plus zasady tylko dla podfolderu.
Finał rdzenia pakuje skille testów i metryk wraz z agentami do
lokalnego pluginu: jedno polecenie uruchamia powtarzalne sprawdzenia
i pokazuje ich podsumowanie, bez samowolnej naprawy aplikacji.
[Pakiet wzorcowy](starter/copilot/triage-workshop)
nie jest aktywną konfiguracją repozytorium; uczestnik tworzy własną lub
ładuje wzorzec przez `--plugin-dir`. Nie wymaga nowych pakietów ani usług
GitHub. Przebieg i granice automatyzacji opisuje [instrukcja uczestnika](lab.md).

Moduł C2 [zarządzanie kontekstem](lab.md#0c-context-management--wybierz-sprawdź-przekaż)
uczy doboru źródeł, weryfikacji instrukcji ograniczonych do testów,
kompakcji i przekazania pracy do nowej sesji. Wzorce
[instrukcji testowych](starter/copilot/instructions/triage-tests.instructions.md)
i [skilla triage-handoff](starter/copilot/skills/triage-handoff/SKILL.md)
pozostają nieaktywne, dopóki uczestnik nie doda ich do własnej konfiguracji.

Moduł C3: [dwie procedury sprawdzania zmian](lab.md#0b-dodaj-dwie-procedury-jako-skille)
uczy przygotowania skilli ze skryptami uruchamiającymi testy i pomiar metryk
oraz iteracji promptu: start własny albo skopiowany, porównanie planu z wymaganiami,
własne doprecyzowanie i porównanie odpowiedzi.
To część rdzenia. Aby oszczędzić czas, można przeczytać i skopiować
kompletne wzorce [testów](starter/copilot/skills/triage-tests/SKILL.md)
i [metryk](starter/copilot/skills/triage-metrics/SKILL.md) wraz ze skryptami,
zamiast pisać je od zera. Wzorce są nieaktywne do skopiowania do
`.github\skills`; pakowanie wspólnych procedur w plugin następuje później.

Moduł C4: [Autopilot, Fleet i subagenci](lab.md#0d-goal-fleet-i-subagenci--cel-budżet-równoległe-pomysły)
pokazują cel z limitem kredytów AI, równoległe propozycje UI i śledzenie
delegacji przez `/tasks`. Pomoc CLI 1.0.95 podaje `/autopilot`
z opcjonalnym `--max-ai-credits`; nie podaje `/goal` ani `--max-tokens`.
Prośba o budżet tokenów w treści zlecenia nie jest limitem egzekwowanym
przez CLI. Składnię i dostępność sprawdzaj w pomocy używanej wersji.

Moduł C5: [Rubber Duck i lokalny przegląd kodu](lab.md#0e-rubber-duck-i-lokalny-code-review--druga-opinia-bez-pr-a)
uzupełniają pracę o krytykę planu, CLI `/review` i przegląd zmian w VS Code.
Bez PR-a i repozytorium zdalnego; lokalny przegląd nadal korzysta z usługi
Copilot, a uwagi trzeba zweryfikować z kodem i testami. Zakres obejmuje
zmiany od `lab-start`, także commitowane, oraz nowe pliki.

Aby nie ćwiczyć wszystkich mechanizmów wyłącznie na aplikacji do kwalifikacji
zgłoszeń, dodano niezależny
[skill csv-quality](starter/copilot/skills/csv-quality/SKILL.md).
Ma podfoldery `references`, `assets`, `examples` i `scripts`, kontrakt,
szablon odpowiedzi, dwa wejścia syntetyczne oraz przetestowany walidator
bez nowych zależności. [Moduł C6](lab.md#0b1-skill-z-podfolderami--kontrola-csv-nie-kolejny-triage)
uczy napisania własnego `SKILL.md`, wykorzystania zasobów, rozróżnienia
FAIL/BLOCKED i zachowania danych bez automatycznej naprawy.

Na koniec jest [opcjonalny etap Spec Kit](lab.md#etap-rozszerzony--spec-kit-od-istniejącego-kodu-do-nowej-funkcji):
Uczestnik instaluje narzędzie przez `pip` w istniejącym `.venv` aplikacji,
inicjalizuje je we własnej kopii i dodaje Brownfield. Odtwarza specyfikację
z kodu: wariant A obejmuje znany przepływ, a wariant B rozpoznaje całą
nieznaną aplikację, zapisuje mapę rozwiązania i specyfikacje odkrytych
funkcji. Warianty są alternatywami; B symuluje przejęcie brownfield
bez podpowiadania agentowi, co robi kod. Po przeglądzie uczestnik kopiuje
wybraną specyfikację do katalogu bazowego i ustawia aktywną funkcję,
zachowując pozostałe wyniki pełnej analizy.
Następnie tworzy odrębną specyfikację, plan i zadania
[końcowego TUI](lab.md#zadanie-koncowe-tui): wpisywanie komentarza
w konsoli oraz JSON oceny zgodny z WWW.
To rozszerzenie podstawowego ćwiczenia; wymaga zatwierdzonego narzędzia
`specify` i rozszerzenia społecznościowego, nie nowych zależności aplikacji.

## Uwierzytelnianie Entra bez klucza API

Opcjonalnie ustaw `OPENAI_AUTH_MODE=azure-cli` w lokalnym pliku `.env`.
Po uruchomieniu `.\scripts\setup.ps1 -WithLLM` wykonaj `.\scripts\login.ps1`,
a następnie `.\scripts\run.ps1 -Mode live`.
Sesja `az login` udostępnia odnawiane tokeny; w tym trybie
`OPENAI_API_KEY` nie jest wymagany ani używany. Uczestnicy nadal mogą
korzystać z domyślnego trybu `api-key`.

Wymagany jest punkt końcowy obsługujący Entra, właściwa dzierżawa i uprawnienia
do wywoływania modelu. Uczestnik dostaje
[krótkie zasady trybu live](lab.md#opcjonalny-tryb-live), a diagnostyka
organizatora pozostaje w prywatnym przewodniku prowadzącego.

## Skład do PDF

[Skrypt Pandoc](gen-pdf.cmd) tworzy osobno `lab.pdf` i `lab-speaker.pdf`
przy użyciu XeLaTeX oraz `mermaid-filter.cmd`, z wyłączonym automatycznym
instalowaniem pakietów MiKTeX. Przewodnika prowadzącego
ani jego PDF nie dołączaj do paczki uczestników. Mapa etapów na początku
instrukcji uczestnika używa linków wewnętrznych do szczegółowych kroków w tym samym PDF.
W prozie i cytowanych zleceniach zapisuj
ścieżki, wzorce ścieżek i polecenia jako kod w odwrotnych apostrofach; wielowierszowe polecenia
i drzewa katalogów umieszczaj w blokach kodu. Odnośnik do pliku ma krótką
etykietę, a ścieżkę względną w celu linku.

## Osobny pokaz GitHub i Azure

[Pokaz GitHub Agentic Workflows](demo.md) zawiera narrację prowadzącego,
interpretację dowodów w GitHub Actions i osobno zatwierdzane wdrożenie
syntetycznego projektu startowego do Azure. Nie jest częścią ćwiczenia ani rozwiązaniem
uczestnika; nie zmienia ośmiu etapów ani kryteriów odbioru.
Wymaga osobnej konfiguracji GitHub/Azure i zgody na koszty.