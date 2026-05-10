# Antarctic Sea Ice Extent – ML Forecasting

**Predicting Antarctic sea ice edge latitude using Random Forest and Linear Regression, based on daily satellite observations from 1978 to 2009.**

## Overview
This project analyzes the seasonal cycle of Antarctic sea ice and trains Machine Learning models to forecast its mean edge latitude. It features data processing, model evaluation, and the generation of dynamic polar visualizations (animated GIFs) for both historical data (1978–2009) and RF-based predictions for the future (2010–2020).

---

## Key Findings

* **Long-term Trend:** **−0.018°/year** – the ice edge is slowly shifting towards the pole.
* **Maximum Extent:** September 2006 (~33.76 million km²).
* **Minimum Extent:** February 1997 (~16.72 million km²).
* **Model Performance:** Random Forest substantially outperforms the simple linear regression baseline, capturing the non-linear seasonal dynamics much more accurately.

---

## Data & Features

* **Source:** `daily_ice_edge.csv` (NSIDC daily satellite observations).
* **Period:** 1978–2009 *(Note: Missing data between Dec 1987 – Jan 1988 is accounted for).*
* **Target Variable:** `mean_lat` — the mean latitude of the ice edge across all longitude sectors.

### Engineered Features
| Feature | Description |
| :--- | :--- |
| `year` | Calendar year – captures the long-term trend. |
| `sin_doy`, `cos_doy` | Cyclically encoded day-of-year – captures seasonality. |
| `lag365` | Ice edge latitude from 365 days prior – annual "memory". |

---

## Modeling & Forecasting

The models were trained on data from 1978–2004 and tested on the 2005–2009 period.

### Model Evaluation
| Model | Details | R² Score | RMSE |
| :--- | :--- | :--- | :--- |
| **Random Forest** | 300 trees, max depth 8 | **0.984** | **0.371°** |
| **Linear Regression** | Baseline | 0.960 | 0.582° |

### 🔮 Forecast (2010–2020)
Future predictions use `lag365 = mean(2009 ice edge)` as a fixed anchor. The RF model predicts the mean latitude every 30 days. To reconstruct a realistic polar map, the historical angular contour shape for each day-of-year is shifted by the difference between the predicted and historical mean.

---

## Repository Files & Outputs

| File | Description |
| :--- | :--- |
| `antarctica.py` | Main script handling data processing, model training, plots, and animations. |
| `seasonality.png` | **Monthly Climatology:** Shows mean ice edge latitude (1978–2009). Ice peaks in Sept–Oct (~−61°) and retreats in Feb (~−69°). |
| `prediction_rf.png` | **Prediction Chart:** RF and LR fits against test data + 2010–2020 forecast vs historical baseline. |
| `antarctica.gif` | **Historical Animation:** Polar map of historical ice extent (blue area). |
| `prediction_rf.gif` | **Forecast Animation:** Polar map using RF-predicted latitudes for 2010–2020 (red/pink area). |
| `daily_ice_edge.csv` | Input dataset *(Not included in repo due to size/source restrictions)*. |

*(Note: In the visualization, the coordinate system centers on the South Pole [0° at the top]. Latitude is converted to a radial distance via `r = (90 + lat) × 111.2 km` for accurate polar plotting).*

---

## Installation & Usage

### 1. Requirements
Ensure you have Python installed along with the required libraries:
```bash
pip install pandas numpy matplotlib scikit-learn imageio
```
### 2. Run the Script
Execute the main script to process the data, train the models, and generate all outputs directly into your working directory:

```bash
python anatarktyda.py
```

## Technologies

* **`pandas`** – Data loading and preprocessing.
* **`numpy`** – Numerical computations and spatial transformations.
* **`matplotlib`** – Static plotting and polar mapping.
* **`scikit-learn`** – Random Forest, Linear Regression, and evaluation metrics.
* **`imageio`** – Rendering high-quality GIF animations.

