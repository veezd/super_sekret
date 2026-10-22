# Hack the Dorm – MS AGH
Samowystarczalność energetyczna Miasteczka Studenckiego AGH (hakaton).

Start: `uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt` → pliki źródłowe do `data/raw/` → `.venv/bin/python scripts/inspect_raw.py` → `.venv/bin/python scripts/01_build_processed.py` (czyste dane w `data/processed/`, log anomalii w `outputs/tables/anomaly_log.csv`).
Kontekst dla agentów AI: `CLAUDE.md`. Szczegóły: `docs/`.

## Dashboard (przeglądarka danych)
`.venv/bin/streamlit run app/dashboard.py` → http://localhost:8501
Dowolne pliki z `data/processed/` na jednym wykresie, obok siebie lub pod sobą; filtry czasu (zakres, miesiące, dni tygodnia,
godziny, dni robocze/święta, strefy B23, godziny opłaty mocowej), flagi jakości, agregacja (15 min…rok; energia / moc śr./maks./min.),
normalizacja, wygładzanie, wygaszanie/ukrywanie/wyróżnianie serii, porównanie lat, profil dobowy, mapa cieplna, krzywa uporządkowana,
statystyki, eksport CSV, log anomalii. Nowy plik parquet (np. ceny RDN, PVGIS) pojawia się automatycznie (format: ts + kolumny liczbowe).
