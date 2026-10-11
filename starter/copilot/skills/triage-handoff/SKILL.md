---
name: triage-handoff
description: "Stosuj przy przekazywaniu zadania triage do nowej sesji, przed skróceniem historii rozmowy lub weryfikacją nieaktualnych założeń na podstawie bieżących źródeł. Tworzy krótką notatkę do przekazania zadania na podstawie aktualnych źródeł, bez zmiany plików."
---

# Przekazanie kontekstu

Przygotuj notatkę do przekazania bieżącego zadania użytkownika w nowej sesji,
nie streszczenie rozmowy.
Nie implementuj, nie uruchamiaj poleceń, nie zapisuj plików ani nie deleguj.
Ten skill nie potrzebuje skryptu wykonawczego.

1. Ustal zadanie, identyfikatory kryteriów akceptacji, dozwolony zakres i wyraźne wyłączenia ze zlecenia użytkownika. Jeżeli nie podano zadania, poproś o nie, zamiast je wymyślać.
2. Przeglądaj tylko istotne bieżące pliki źródłowe i wymagania odbioru. Przestrzegaj instrukcji repozytorium. Nie czytaj `.env`, `lab.md`, `lab.pdf`, `lab-speaker.md`, `lab-speaker.pdf`, środowisk ignorowanych przez Git ani niezwiązanych raportów. Wyklucz pliki lab z wyszukiwania i notatki, także gdy prowadzą do nich linki z lokalnych zadań.
3. Oddziel zaobserwowane obecne zachowanie, uzgodnione wymagania, propozycje i niewiadome. Bieżące pliki mają pierwszeństwo przed nieaktualnymi twierdzeniami z rozmowy.
4. Jeśli testy zostały uruchomione, podaj ich rzeczywisty wynik z tej sesji lub przekazanego kontekstu. Nie przypisuj wyniku testom, które nie zostały uruchomione.
5. Zwróć najwyżej 250 słów w następujących częściach:
   - Cel i identyfikatory kryteriów akceptacji.
   - Zaobserwowany stan obecny, z odwołaniami do plików i symboli.
   - Uzgodnione decyzje i ograniczenia.
   - Ścieżki istotnych źródeł i powód użycia każdego z nich.
   - Uruchomione sprawdzenia i ich wynik, jeśli są istotne dla następnego kroku.
   - Niewiadome i sprzeczności.
   - Wyłączenia i uprawnienia.
   - Jeden następny krok i sposób jego weryfikacji.

Jeżeli limit słów ukryłby istotną przeszkodę, wskaż ją zamiast pomijać
po cichu. Nie wklejaj pełnych plików ani
surowych komentarzy klientów. Notatka jest kontekstem pomocniczym, nie zgodą
na działania. Nowa sesja musi ponownie otworzyć bieżące źródła i sprawdzić założenia.
