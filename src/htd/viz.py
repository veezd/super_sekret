"""Standard charts. Save to outputs/figures/<name>.png (dpi 150). Polish labels on charts (presentation is PL)."""
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from .config import FIG


def save(fig, name: str):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def heatmap_day_time(s: pd.Series, title="", unit="kW"):
    """Calendar heatmap: rows = date, cols = time of day. s: tz-aware index."""
    d = s.to_frame("v")
    d["date"], d["time"] = d.index.date, d.index.strftime("%H:%M")
    piv = d.pivot_table(index="date", columns="time", values="v", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(12, 7))
    sns.heatmap(piv, ax=ax, cmap="viridis", cbar_kws={"label": unit})
    ax.set_title(title)
    return fig


def daily_profile(s: pd.Series, by: pd.Series | None = None, title="", unit="kW"):
    """Mean profile by time of day, optionally grouped (e.g. workday/weekend, month)."""
    d = s.to_frame("v")
    d["time"] = d.index.hour + d.index.minute / 60
    d["g"] = by.values if by is not None else "all"
    fig, ax = plt.subplots(figsize=(10, 4))
    for g, x in d.groupby("g"):
        x.groupby("time")["v"].mean().plot(ax=ax, label=str(g))
    ax.set(xlabel="godzina", ylabel=unit, title=title)
    ax.legend()
    return fig


def load_duration(s: pd.Series, title="", unit="kW"):
    v = s.dropna().sort_values(ascending=False).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(v.index / len(v) * 100, v.values)
    ax.set(xlabel="% czasu", ylabel=unit, title=title)
    return fig
