import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import imageio.v2 as imageio
import io

# working with data
df = pd.read_csv("daily_ice_edge.csv")
df["Date"]     = pd.to_datetime(df["Date"], format="%d-%b-%Y")
df             = df.sort_values("Date").reset_index(drop=True)
lat_cols       = [c for c in df.columns if c != "Date"]
angles_rad     = np.deg2rad(np.arange(len(lat_cols)))
lats           = df[lat_cols].values

df["mean_lat"] = np.nanmean(lats, axis=1)
df["year"]     = df["Date"].dt.year
df["month"]    = df["Date"].dt.month
df["doy"]      = df["Date"].dt.day_of_year
df["sin_doy"]  = np.sin(2 * np.pi * df["doy"] / 365)
df["cos_doy"]  = np.cos(2 * np.pi * df["doy"] / 365)
df["lag365"]   = df["mean_lat"].shift(365)
df = df.dropna().reset_index(drop=True)

def lat_to_r(x):
    return (90 + x) * 111.2

lim = np.nanmax(lat_to_r(lats)) * 1.05

# random forest
features = ["year", "sin_doy", "cos_doy", "lag365"]
X = df[features].values
y = df["mean_lat"].values

train = df["year"] <= 2004
X_tr, y_tr = X[train],  y[train]
X_te, y_te = X[~train], y[~train]

rf = RandomForestRegressor(n_estimators=300, max_depth=8, random_state=42, n_jobs=-1)
rf.fit(X_tr, y_tr)
y_pred_rf = rf.predict(X_te)

lr = LinearRegression().fit(X_tr, y_tr)
y_pred_lr = lr.predict(X_te)

r2_rf   = r2_score(y_te, y_pred_rf)
r2_lr   = r2_score(y_te, y_pred_lr)
rmse_rf = np.sqrt(mean_squared_error(y_te, y_pred_rf))
rmse_lr = np.sqrt(mean_squared_error(y_te, y_pred_lr))
print(f"Random Forest:    R2={r2_rf:.3f}  RMSE={rmse_rf:.3f}")
print(f"Linear Regression: R2={r2_lr:.3f}  RMSE={rmse_lr:.3f}")

# prediction for 2010-2020
future_dates = pd.date_range("2010-01-01", "2020-12-31", freq="30D")
last_known   = df[df["year"] == 2009]["mean_lat"].mean()
future_rows  = []
for d in future_dates:
    doy = d.day_of_year
    future_rows.append({
        "year":    d.year,
        "sin_doy": np.sin(2 * np.pi * doy / 365),
        "cos_doy": np.cos(2 * np.pi * doy / 365),
        "lag365":  last_known,
    })
X_future    = pd.DataFrame(future_rows)[features].values
y_future_rf = rf.predict(X_future)
y_future_lr = lr.predict(X_future)

# seasonality
clim = df.groupby("month")["mean_lat"].mean()
month_labels = ["Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"]

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(range(1, 13), clim.values, color="steelblue", lw=2, marker="o", ms=6)
ax.fill_between(range(1, 13), clim.values, clim.min() - 0.5,
                color="steelblue", alpha=0.15)
ax.set_xticks(range(1, 13))
ax.set_xticklabels(month_labels)
ax.set_ylabel("Mean ice edge latitude [degrees]")
ax.set_title("Seasonality of Antarctic sea ice extent (mean 1978–2009)")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("seasonality.png", dpi=150, bbox_inches="tight")
plt.close()

# comaprision: RF vs LR
fig, axes = plt.subplots(2, 1, figsize=(12, 8))
fig.suptitle("Antarctic sea ice extent prediction – Random Forest vs Linear Regression",
             fontsize=12, fontweight="bold")

ax = axes[0]
ax.plot(df["Date"][train],  y[train],  color="steelblue", lw=0.8, alpha=0.4, label="Training data")
ax.plot(df["Date"][~train], y_te,      color="steelblue", lw=1.5, label="Test data (2005–2009)")
ax.plot(df["Date"][~train], y_pred_rf, color="tomato",    lw=1.5, label=f"RF   R2={r2_rf:.3f}  RMSE={rmse_rf:.2f}")
ax.plot(df["Date"][~train], y_pred_lr, color="orange",    lw=1.5, ls="--", label=f"LR   R2={r2_lr:.3f}  RMSE={rmse_lr:.2f}")
ax.axvline(pd.Timestamp("2005-01-01"), color="gray", lw=1, ls=":", alpha=0.7)
ax.axvspan(pd.Timestamp("1987-12-03"), pd.Timestamp("1988-01-13"),
           color="red", alpha=0.15, label="Data gap (Dec 1987 – Jan 1988)")
ax.set_ylabel("Mean ice edge latitude [degrees]")
ax.set_title("Model fit on test set")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

ax = axes[1]
ax.plot(df["Date"], y, color="steelblue", lw=0.8, alpha=0.4, label="Historical data")
ax.plot(future_dates, y_future_rf, color="tomato", lw=2, label="RF forecast")
ax.plot(future_dates, y_future_lr, color="orange",  lw=2, ls="--", label="Linear forecast")
ax.axvline(pd.Timestamp("2010-01-01"), color="gray", lw=1, ls=":", alpha=0.7, label="End of data")
ax.set_ylabel("Mean ice edge latitude [degrees]")
ax.set_title("Forecast 2010–2020")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("prediction_rf.png", dpi=150, bbox_inches="tight")
plt.close()

# animation
step   = 30
frames = df.iloc[::step].reset_index(drop=True)
n      = len(frames)

images = []
for _, row in frames.iterrows():
    r_ice = lat_to_r(lats[row.name])

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"projection": "polar"})
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.fill_between(angles_rad, 0, r_ice, color="deepskyblue", alpha=0.4)
    ax.plot(angles_rad, r_ice, color="steelblue", lw=1.5)
    ax.set_ylim(0, lim)
    ax.set_yticklabels([])
    ax.set_xticks(np.deg2rad([0, 90, 180, 270]))
    ax.set_xticklabels(["0", "90E", "180", "90W"], fontsize=9)
    ax.set_title(row["Date"].strftime("%d %b %Y"), fontsize=12, pad=12)
    fig.suptitle("Antarctic sea ice extent", fontsize=11, y=1.01)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    images.append(imageio.imread(buf))
    plt.close(fig)

imageio.mimsave("antarctica.gif", images, fps=8, loop=0)

#mean radial profile per day-of-year from historical data (contour shape)
mean_profile_by_doy = {}
for doy_val, grp in df.groupby("doy"):
    idx = grp.index
    mean_profile_by_doy[doy_val] = np.nanmean(lats[idx], axis=0)

images_pred = []
for d, pred_lat in zip(future_dates, y_future_rf):
    doy_val = d.day_of_year
    base_profile = mean_profile_by_doy.get(doy_val, mean_profile_by_doy[1])
    hist_mean = np.nanmean(base_profile)
    shift = pred_lat - hist_mean
    r_ice = lat_to_r(base_profile + shift)

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"projection": "polar"})
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.fill_between(angles_rad, 0, r_ice, color="tomato", alpha=0.3)
    ax.plot(angles_rad, r_ice, color="tomato", lw=1.5)
    ax.set_ylim(0, lim)
    ax.set_yticklabels([])
    ax.set_xticks(np.deg2rad([0, 90, 180, 270]))
    ax.set_xticklabels(["0", "90E", "180", "90W"], fontsize=9)
    ax.set_title(d.strftime("%d %b %Y"), fontsize=12, pad=12)
    fig.suptitle("RF forecast – Antarctic sea ice extent", fontsize=11, y=1.01)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    images_pred.append(imageio.imread(buf))
    plt.close(fig)

imageio.mimsave("prediction_rf.gif", images_pred, fps=4, loop=0)