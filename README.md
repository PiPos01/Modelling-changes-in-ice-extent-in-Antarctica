# 🧊 Analiza zasięgu lodu morskiego Antarktyki

Projekt analizuje dzienny zasięg lodu morskiego wokół Antarktyki w latach **1978–2009** na podstawie danych NSIDC. Zawiera wizualizacje, analizę sezonowości i trendu oraz predykcję z użyciem **Random Forest**.

---

## 📁 Struktura projektu

```
.
├── antarktyda.py     # główny skrypt – uruchom ten plik
├── daily_ice_edge.csv     # dane wejściowe 
├── README.md
└── outputs/
    ├── antarktyda.gif     # animacja zasięgu lodu
    ├── sezonosc.png       # klimatologiczny cykl sezonowy
    └── predykcja_rf.png   # predykcja Random Forest vs regresja liniowa
```

---

## 📊 Dane

- **Źródło:** NSIDC (National Snow and Ice Data Center)
- **Zakres:** 26 października 1978 – 16 maja 2009
- **Format:** 9530 wierszy × 362 kolumny
  - kolumna `Date` – data obserwacji
  - kolumny `longitude_0E` … `longitude_360E` – szerokość geograficzna krawędzi lodu dla każdego kąta (0°–360°)

> ⚠️ **Brak danych:** w okresie **3 grudnia 1987 – 13 stycznia 1988** brak obserwacji satelitarnych. Dni z tego przedziału zostały usunięte z analizy.

---

## 🚀 Uruchomienie

### Wymagania

```bash
pip install pandas numpy matplotlib scikit-learn imageio
```

### Uruchomienie skryptu

```bash
python antarktyda.py
```

Skrypt generuje wszystkie wykresy i animację automatycznie.

---

## Co robi skrypt

### 1. Sezonowość
Średnia szerokość geograficzna krawędzi lodu dla każdego miesiąca (klimatologia 1978–2009). Pokazuje, że lód osiąga maksimum we wrześniu (zima australska) i minimum w lutym (lato australskie).

### 2. Predykcja – Random Forest vs regresja liniowa
Model uczy się na danych z lat 1979–2004, a testowany jest na latach 2005–2009.

**Cechy modelu:**
| Cecha | Opis |
|---|---|
| `year` | rok – wychwytuje długoterminowy trend |
| `sin_doy`, `cos_doy` | dzień roku zakodowany cyklicznie – sezonowość |
| `lag365` | wartość sprzed 365 dni – "pamięć" roczna |

**Wyniki:**
| Model | R² | RMSE |
|---|---|---|
| Random Forest | 0.984 | 0.371° |
| Regresja liniowa | 0.960 | 0.582° |

Prognoza rozciąga się na lata 2010–2020.

### 3. Animacja GIF
Polarna mapa zasięgu lodu odtwarzana co 30 dni. Widok z bieguna południowego, biegun w centrum, krawędź lodu animuje się zgodnie z sezonem i latami.

---

## Kluczowe obserwacje z projektu

- Trend długoterminowy: **−0.018°/rok** – krawędź lodu powoli przesuwa się ku biegunowi
- Maksimum zasięgu: wrzesień 2006 (~33.76 mln km²)
- Minimum zasięgu: luty 1997 (~16.72 mln km²)
- Random Forest znacznie lepiej odwzorowuje sezonowość niż prosta regresja liniowa

---

## Technologie użyte w projekcie

- `pandas` – wczytywanie i przetwarzanie danych
- `numpy` – obliczenia numeryczne
- `matplotlib` – wykresy i animacja
- `scikit-learn` – Random Forest, regresja liniowa, metryki
- `imageio` – zapis animacji GIF
