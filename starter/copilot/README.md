# Mapa materiałów Copilota

Ten katalog jest biblioteką nieaktywnych wzorców. Paczka uczestnika nie
dostarcza gotowych aktywnych instrukcji; uczestnik tworzy je w swojej kopii.
Repozytorium autorów ma osobne instrukcje synchronizacji materiałów
i składu PDF, wyłączane z paczki uczestnika; nie są rozwiązaniem modułu C1.
Najpierw wykonaj własną próbę, dopiero potem porównaj ją z rozwiązaniem.
Wyjątek oszczędzający czas w C3: skille testów i metryk możesz od razu
przeczytać i wykorzystać jako wzorce zamiast pisać je od zera.
Nie nadpisuj istniejącej konfiguracji firmowej.

Na początku wzorca instrukcji repozytorium jest reguła wyłączenia
`lab.md`, `lab.pdf`, `lab-speaker.md` i `lab-speaker.pdf` z kontekstu
agentów, również z wyszukiwania, notatek do przekazania zadania i zleceń
subagentów oraz odczytów przez linki w lokalnych zadaniach.
Uczestnik zapisuje tę regułę na początku własnych aktywnych
instrukcji przed pierwszym zleceniem, a pozostałe zasady opracowuje w C1.
Linki do lab w tej bibliotece służą człowiekowi, nie polecają agentowi
odczytu tych plików. To nie blokada techniczna ani powód usuwania materiałów.

Wzorzec instrukcji repozytorium zawiera konwencję `#iss<id>`:
odczyt lokalnego `issues\iss<id>.md`, np. `#iss002`.
Uczestnik dodaje ją do własnych aktywnych zasad w C1.
To nie integracja z Azure DevOps; [opis i próba](../../lab.md#lokalne-issues-zamiast-azure-devops)
są w instrukcji uczestnika.

| Materiał | Docelowe miejsce | Czego uczy |
|---|---|---|
| [Instrukcje repozytorium](copilot-instructions.md) | `.github\copilot-instructions.md` | Niezmienne zasady projektu, bez katalogu standardów Pythona |
| [Instrukcje kodu aplikacji](instructions/triage-python.instructions.md) | `.github\instructions\triage-python.instructions.md` | Standardy implementacji, `applyTo: "triage/**/*.py"` |
| [Instrukcje testów](instructions/triage-tests.instructions.md) | `.github\instructions\triage-tests.instructions.md` | Konwencje asercji, `applyTo: "tests/**/*.py"` |
| [Lokalne zasady UI](triage-templates/AGENTS.md) | `triage\templates\AGENTS.md` | Zakres podfolderu, nie druga kopia reguł repozytorium |
| [Kontrola jakości CSV](skills/csv-quality/SKILL.md) | `.github\skills\csv-quality` | Procedura z kontraktem, szablonem, przykładami i skryptem poza domeną zgłoszeń |
| [Przekazanie kontekstu](skills/triage-handoff/SKILL.md) | `.github\skills\triage-handoff` | Krótkie przekazanie faktów; skill nie zawsze potrzebuje skryptu |
| [Testy regresji](skills/triage-tests/SKILL.md) | `.github\skills\triage-tests` | pytest, JUnit XML i rzeczywisty kod wyjścia; kopiuj także `scripts\run.ps1` |
| [Pomiar metryk](skills/triage-metrics/SKILL.md) | `.github\skills\triage-metrics` | Pomiar `demo`, JSON i osobna ocena dwóch progów; kopiuj także `scripts\run.ps1` |
| [Plugin sprawdzeń](triage-workshop/plugin.json) | `.copilot-plugins\triage-workshop` | Dwie rozłączne delegacje, skrypty wykonawcze i lokalne podsumowanie |

Wzorce do C3 są w `skills\triage-tests` i `skills\triage-metrics`.
Przeczytaj ich `SKILL.md` i skrypty, zaplanuj przygotowanie, a potem
skopiuj **całe katalogi** do `.github\skills`, bez nadpisywania własnej
pracy. Możesz też napisać własne wersje. W obu wariantach wykonaj próby
w nowej sesji i sprawdź rzeczywiste raporty oraz kody wyjścia.
Skrypty są takie same jak w przykładzie pluginu, ale lokalne procedury
nie wymagają koordynatora ani instalowania pluginu.

W zespole zwykle jedna osoba przygotowuje wspólne skille i pakuje je
w plugin, a pozostali czytają i wykorzystują gotowe procedury.
W finale (etap 8) przenosisz działające skille do pluginu;
`triage-workshop\skills` pokazuje ich docelowy wariant w pakiecie.
Nie pozostawiaj dwóch aktywnych wersji o tej samej nazwie.
`csv-quality` jest oddzielnym ćwiczeniem i nie należy do sprawdzeń aplikacji.

## Co jest rozwiązaniem, a co tylko opisem?

- Instrukcje i definicje skilli/agentów są wzorcami do adaptacji, nie dowodem
  ich automatycznego odkrycia w dowolnym hoście.
- Walidator CSV i logika podsumowania pluginu mają lokalne testy.
  Polecenia oraz oczekiwane wyniki są w [instrukcji uczestnika](../../lab.md).
- Nie ma pełnej referencyjnej implementacji aplikacji po wszystkich etapach:
  `actionability`, poprawionego UI ani konsolowego TUI z oceną JSON.
  Nie traktuj opisu oczekiwanego wyniku jak istniejącego rozwiązania.
- Przewodnik prowadzącego zawiera podpowiedź do celowego błędu i wskazówki
  odbioru, nie kompletne rozwiązanie wszystkich rozszerzeń. Nie dodawaj go
  do kontekstu uczestnika.

Każdy przykład ma osobny cel: instrukcja = zasady, skill = procedura,
zasób = szczegół ładowany w odpowiednim kroku, skrypt = wykonanie,
agent = rola, plugin = pakiet. Liczba plików nie jest miarą jakości.
