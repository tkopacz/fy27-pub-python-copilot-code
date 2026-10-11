# Kontrakt: syntetyczne koszty warsztatu

- CSV w UTF-8, opcjonalnie z BOM; separatorem jest przecinek.
- Nagłówek w dokładnie tej kolejności: `item,quantity,unit_price`.
- Co najmniej jeden wiersz danych; każdy wiersz ma dokładnie trzy komórki.
- `item`: wartość niepusta po usunięciu białych znaków z początku i końca.
- `quantity`: liczba całkowita od 1 do 9999, bez znaku i zer początkowych.
- `unit_price`: nieujemna liczba dziesiętna, z kropką jako separatorem
  i najwyżej dwoma miejscami po przecinku. Bez symboli walut, zapisu
  wykładniczego, `NaN` ani nieskończoności.
- Białe znaki na początku i końcu komórek są pomijane tylko przy walidacji;
  plik źródłowy nigdy nie jest zapisywany ponownie.
- Wszystkie kwoty są w tej samej, nieokreślonej walucie. Nie sprawdzamy
  podatków, rabatów, kursów walut ani zgodności z fakturami.

JSON zawiera dokładnie `schema_version`, `status`, `rows`, `valid_rows`,
`invalid_rows`, `valid_total`, `issues`. Każdy problem zawiera `row`, `field`
i `message`. Numery wierszy oznaczają numery rekordów CSV, z nagłówkiem
jako rekordem 1, nie numery fizycznych linii wewnątrz komórek wielowierszowych.

Kwoty są obliczane przez `Decimal` i eksportowane jako tekst z dwoma
miejscami po przecinku. `valid_total` sumuje **wyłącznie poprawne wiersze**,
więc przy FAIL jest sumą częściową. Niepoprawny format CSV, błędny nagłówek,
brak danych lub brak możliwości odczytu pliku oznacza BLOCKED,
nie PASS dla zera wierszy. Istniejący raport nigdy nie jest nadpisywany.

## Oczekiwane wyniki przykładów

| Wejście | Kod wyjścia | Status | Wiersze | Poprawne | Błędne | Suma poprawnych |
|---|---|---|---|---|---|---|
| `examples/valid.csv` | 0 | PASS | 2 | 2 | 0 | `77.50` |
| `examples/invalid.csv` | 1 | FAIL | 4 | 2 | 2 | `31.00` |

Niepoprawne wejście ma błędy w rekordzie 3 (`quantity`) i rekordzie 4
(`unit_price`). Zmiana etykiet lub pomijanie tych rekordów nie jest naprawą.
