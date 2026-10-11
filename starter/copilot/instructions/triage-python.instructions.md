---
description: "Stosuj przy tworzeniu lub zmianie kodu aplikacji w Pythonie w pakiecie triage."
applyTo: "triage/**/*.py"
---

# Kod aplikacji triage w Pythonie

- Zachowaj publiczne kontrakty żądań i odpowiedzi, chyba że kryterium akceptacji wyraźnie je zmienia.
- Dodawaj precyzyjne adnotacje typów do nowych i zmienianych funkcji. Korzystaj z istniejących klas danych, typów `TypedDict`, wartości `Literal` i `Protocol`, zamiast zastępować je słownikami bez określonych typów lub zbyt ogólnymi typami.
- Każda funkcja powinna mieć jasno określoną odpowiedzialność. Oddziel reguły domenowe od obsługi dostawcy, środowiska, Flask i systemu plików. Nie dodawaj warstw ani abstrakcji bez konkretnego zastosowania w tej małej aplikacji.
- Waliduj niezaufane dane i odpowiedzi modelu na granicy systemu. Zgłaszaj konkretny wyjątek wskazujący przyczynę i możliwe działanie. Nie używaj ogólnego `except`, nie przełączaj się po cichu na rozwiązanie zastępcze ani nie zwracaj po błędzie danych sugerujących sukces.
- Preferuj bibliotekę standardową i istniejące zależności projektu. Nie dodawaj pakietu do obsługi zachowania już zaimplementowanego lokalnie.
