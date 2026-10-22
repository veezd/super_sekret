# Hack the Dorm – opis danych

Dane są surowe, wyeksportowane z systemów pomiarowych AGH i od operatora sieci. Nie były czyszczone. Część anomalii opisujemy poniżej, ale nie wszystkie – ich wykrycie i obsługa to część zadania (kryterium „Wykorzystanie danych”).

Wszystkie czasy są w czasie lokalnym (CET/CEST), więc w danych widać zmiany czasu w marcu i październiku.

---

## 1\. Przegląd plików

| Plik | Obiekt | Rozdzielczość | Okres | Jednostka |
| :---- | :---- | :---- | :---- | :---- |
| Nowa Hala Sportowa 2025.xls | Hala sportowa | 15 min | 2025 | kWh / 15 min |
| Profil mocy Hala Sportowa 2025.xls | Hala sportowa | 15 min | 2025 | kW (moc średnia) |
| Dane D-17 2025.xls | Budynek D-17 | 15 min | 2025 | stan licznika kWh \+ kW |
| Basen 2025.csv | Basen AGH | 1 h | 2025 | kWh / h |
| Profil poboru \- AGH MS.xls | DS18, Akropol (2 liczniki) | 15 min | od 04.07.2026 | kW |
| MS\_AGH\_energia\_ele\_i\_cieplna\_2023-2025.xlsx | Akademiki DS-1…DS-19, Alfa | miesięcznie | 2023–2025 | kWh, GJ |
| Dane D17 ciepło.xlsx | Budynek D-17 | miesięcznie | 2024 | GJ, MW, zł |

&nbsp;

Plik „Zużycie mediów 2023r.,2024r.,2025r..xlsx” jest identyczny z plikiem MS\_AGH\_energia\_ele\_i\_cieplna\_2023-2025.xlsx. Wystarczy używać jednego z nich.

---

## 2\. Hala sportowa

### Nowa Hala Sportowa 2025.xls

- Energia pobrana w kWh na kwadrans.  
- Dwa punkty poboru (PPE):  
  - …615820 – główne zasilanie hali,  
  - …615837 – stały, mały odbiór (ok. 0,17 kWh/15 min, czyli ok. 0,7 kW).  
- Kolumna „Suma zużycia” to suma obu PPE.

### Profil mocy Hala Sportowa 2025.xls

- **To ten sam pomiar co PPE …615820**, tylko wyrażony jako moc średnia w kW (moc \= energia z kwadransa × 4).  
- **Nie sumujcie tych dwóch plików** – podwoicie zużycie hali.  
- Braki danych 04.07.2025 między ok. 10:00 a 14:30 (lista w nagłówku pliku).

---

## 3\. Budynek D-17

### Dane D-17 2025.xls (prąd)

- Budynek ma **dwa zasilania: ZAS1 i ZAS2. Zużycie budynku \= suma obu.**  
- Kolumny „Energia Czynna Pobrana” to **stany licznika (narastająco), a nie zużycie.** Zużycie w kwadransie \= różnica dwóch kolejnych odczytów.  
- Kolumny „Moc Czynna Uśred.” to moc średnia w kW. Można ich używać jako kontroli (różnica stanów × 4 ≈ moc średnia).  
- Braki danych są wypisane w nagłówku pliku. Są w różnych miejscach dla energii i dla mocy. Zalecamy liczyć zużycie z różnic stanów licznika: przy luce różnica obejmuje cały brakujący okres, więc suma się nie gubi (trzeba ją tylko rozłożyć na brakujące kwadranse).  
- Pomiary pochodzą z rozdzielni niskiego napięcia („RG\_D17\_nn”), czyli są to podliczniki wewnątrz sieci AGH, a nie liczniki rozliczeniowe operatora.  
- Charakterystyka: ZAS2 ma stałe obciążenie ok. 85–90 kW przez całą dobę, ZAS1 ma wyraźny profil dzienny (ok. 22–30 kW w nocy, 70–90 kW w dni robocze).

---

## 4\. Basen – Basen 2025.csv

- Dane godzinowe z odczytu operatora, PPE …049120, energia pobrana w kWh na godzinę.  
- **Format:** kodowanie Windows-1250 (cp1250), separator średnik, przecinek dziesiętny.  
- **Znacznik czasu oznacza koniec godziny:** „01:00” to zużycie z godziny 00:00–01:00. Plik zaczyna się 01.01.2025 01:00 i kończy 01.01.2026 00:00.  
- **Kolumna „Strefa” to strefy taryfy trzystrefowej (B23):**  
  - szczyt przedpołudniowy: dni robocze 7–13,  
  - szczyt popołudniowy: dni robocze 16–21 (październik–marzec), 19–22 (kwiecień–wrzesień),  
  - reszta dnia: pozostałe godziny, weekendy i święta.  
- **Zmiana czasu:**  
  - 30.03.2025 brakuje godziny 03:00 (poprawnie),  
  - 26.10.2025 o 03:00 jest wartość 247,8 przy kompletności 200% – to dwie godziny w jednym wierszu, trzeba je rozdzielić.  
- **Anomalie:**  
  - 05.08.2025 00:00: wartość 0,  
  - 19–21.04.2025 (Wielkanoc): wyraźny spadek zużycia – realny, nie błąd.  
- Charakterystyka: stałe obciążenie nocne ok. 70–100 kW (filtracja, podgrzewanie wody).

---

## 5\. Akademiki – profile 15-minutowe (Profil poboru \- AGH MS.xls)

- Trzy arkusze: „AGH \- DS18”, „AGH \_ Akropol 50088752”, „AGH Akropol 50088740”. Akropol ma dwa liczniki – zużycie akademika to ich suma.  
- **Daty zapisane jako liczby Excela** (np. 46207,0104 \= 04.07.2026 00:15).  
- Dane zaczynają się 4 lipca 2026, czyli **w okresie wakacyjnym, przy niskim obłożeniu.** Kształt profilu w roku akademickim będzie inny – zestawcie go z danymi miesięcznymi akademików, gdzie widać różnicę między latem a zimą.  
- Moc ma rozdzielczość 2,4 kW (stała licznika). Skoki o tę wartość wynikają z pomiaru, a nie z zachowania mieszkańców.  
- Są też kolumny z mocą bierną (indukcyjną i pojemnościową).

---

## 6\. Akademiki – dane miesięczne (MS\_AGH\_energia\_ele\_i\_cieplna\_2023-2025.xlsx)

### Struktura

- Arkusze z prądem (kWh) i ciepłem (GJ) dla każdego roku 2023–2025.  
- Prąd: dla każdego DS dwa wiersze – **D (dzień) i N (noc)**, czyli dwie strefy liczników. Alfa podana w blokach bl.1–bl.5.  
- Ciepło: dla każdego DS osobno c.o., c.w. i czasem CT (opis skrótów w punkcie 8).  
- Kolejność kolumn podsumowania (c.o./c.w.) jest inna w 2023 roku niż w 2024 i 2025\.

---

## 8\. Słownik skrótów

- **c.o.** – centralne ogrzewanie  
- **c.w. / c.w.u.** – ciepła woda użytkowa  
- **CT** – ciepło technologiczne, czyli ciepło dla nagrzewnic central wentylacyjnych  
- **D / N** – strefa dzienna / nocna licznika energii elektrycznej  
- **PPE** – punkt poboru energii (licznik rozliczeniowy operatora)  
- **nn** – niskie napięcie  
- **GJ → MWh:** 1 GJ \= 0,2778 MWh