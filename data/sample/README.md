# Testdata og Kjent Fasit (data/sample)

Dette området inneholder syntetiske, oppdiktede regnskapsdata for å verifisere at internkontrollen og kjerneflyten i applikasjonen fungerer etter suksesskriteriene i `product-brief.md`.

Ingen av filene inneholder personopplysninger eller reelle selskapsdata.

---

## 1. Balanserte filer (Happy Path)

### `saldobalanse_balansert.csv`
* **Innhold:** Saldobalanse med 7 kontoer som dekker eiendeler, gjeld, egenkapital, inntekter og kostnader etter NS 4102.
* **Kjent fasit:**
  * Sum Debet: 530 000,00 NOK
  * Sum Kredit: 530 000,00 NOK
  * Differanse Debet vs. Kredit: 0,00 NOK (Godkjent)
  * Sum IB: 0,00 NOK
  * Sum UB: 0,00 NOK

### `hovedbok_balansert.csv`
* **Innhold:** Hovedbok med 7 bilag (14 transaksjonslinjer) som nøyaktig representerer periodens transaksjoner for kontoene i `saldobalanse_balansert.csv`.
* **Kjent fasit:**
  * Sum Debet i HB: 530 000,00 NOK
  * Sum Kredit i HB: 530 000,00 NOK
  * Differanse Debet vs. Kredit i HB: 0,00 NOK (Godkjent)
* **Kryssavstemming mot saldobalansen ($IB + \text{bevegelser i HB} = UB$):**
  * Konto 1920: IB 100 000 + (200 000 - 120 000) = 180 000 (0,00 i avvik)
  * Konto 1500: IB 50 000 + (150 000 - 110 000) = 90 000 (0,00 i avvik)
  * Konto 2050: IB -110 000 + 0 = -110 000 (0,00 i avvik)
  * Konto 2400: IB -40 000 + (90 000 - 100 000) = -50 000 (0,00 i avvik)
  * Konto 3000: IB 0 + (0 - 200 000) = -200 000 (0,00 i avvik)
  * Konto 4000: IB 0 + (60 000 - 0) = 60 000 (0,00 i avvik)
  * Konto 5000: IB 0 + (30 000 - 0) = 30 000 (0,00 i avvik)
  * **Resultat:** 100 % konsistent. Ingen avvik flagges.

---

## 2. Testfiler med bevisste feil (Negative Testing)

### `saldobalanse_med_ubalanse.csv`
* **Hensikt:** Teste Suksesskriterium 1 (Balansekontroll).
* **Konstruert feil:** Konto 3000 har kreditføring 190 000 istedenfor 200 000.
* **Kjent fasit:**
  * Sum Debet: 530 000,00 NOK
  * Sum Kredit: 520 000,00 NOK
  * **Forventet oppførsel:** Appen stopper analysen umiddelbart, gir rød feilmelding og viser at det er en ubalanse på nøyaktig **10 000,00 NOK**.

### `hovedbok_med_avvik.csv`
* **Hensikt:** Teste Suksesskriterium 2 (Kryssavstemming HB mot SB).
* **Konstruert feil:** Hovedboken balanserer internt ($\sum \text{Debet} = \sum \text{Kredit} = 530\ 000$), men i Bilag 1 er 30 000 kr feilført på konto 1920 i stedet for konto 1500.
* **Kjent fasit ved kryssavstemming mot `saldobalanse_balansert.csv`:**
  * Konto 1500 flagges: $IB (50\ 000) + \text{netto HB} (10\ 000) = 60\ 000 \neq UB (90\ 000)$. **Avvik: -30 000,00 NOK**.
  * Konto 1920 flagges: $IB (100\ 000) + \text{netto HB} (110\ 000) = 210\ 000 \neq UB (180\ 000)$. **Avvik: +30 000,00 NOK**.
  * **Forventet oppførsel:** Appen flagger de to kontoene med advarsel og spesifiserer nøyaktig avvik for hver konto.
