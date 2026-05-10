import streamlit as st
import pandas as pd
from io import BytesIO
import os

st.set_page_config(
    page_title="Team Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.metric-card {
    background: #1F4E79;
    border-radius: 10px;
    padding: 16px 20px;
    color: white;
    margin-bottom: 8px;
}
.metric-card h4 { margin: 0; font-size: 13px; opacity: 0.8; }
.metric-card h2 { margin: 4px 0 0; font-size: 26px; font-weight: 700; }
.green  { background: #1a6b3c !important; }
.orange { background: #b94000 !important; }
.teal   { background: #0e6655 !important; }
.gray   { background: #444 !important; }
section[data-testid="stSidebar"] > div { background-color: #1F4E79; }
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSelectbox label { color: white !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(file) -> pd.DataFrame:
    df = pd.read_excel(file, sheet_name="Team Sheet")
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    num_cols = [
        "Target Month", "Net Sales", "Achivment %",
        "Opening Balance", "Sales Value", "Returns Value",
        "Tasweyat Madinah", "Total Collection", "Madfoaat",
        "Tasweyat Dainah", "End Balance", "Motalbet El Fatrah",
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "Achivment %" in df.columns:
        if df["Achivment %"].dropna().max() > 5:
            df["Achivment %"] = df["Achivment %"] / 100
    return df


def fmt(n):
    if pd.isna(n): return "—"
    if abs(n) >= 1_000_000: return f"{n/1_000_000:.2f}M"
    if abs(n) >= 1_000:     return f"{n/1_000:.1f}K"
    return f"{n:,.0f}"


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Team Dashboard")
    st.markdown("---")
    uploaded = st.file_uploader("📂 Upload Excel File", type=["xlsx", "xls"])

    if not uploaded:
        default = os.path.join(os.path.dirname(__file__), "data", "team_sheet_sample.xlsx")
        if os.path.exists(default):
            with open(default, "rb") as f:
                uploaded = BytesIO(f.read())
            st.info("Using sample data.")
        else:
            st.warning("Please upload an Excel file.")
            st.stop()

    df_full = load_data(uploaded)

    st.markdown("### 🔍 Filters")
    months = ["All"] + sorted(df_full["Month"].dropna().unique().tolist())
    reps   = ["All"] + sorted(df_full["Rep Name"].dropna().unique().tolist())
    sel_month = st.selectbox("Month", months)
    sel_rep   = st.selectbox("Sales Rep", reps)

df = df_full.copy()
if sel_month != "All": df = df[df["Month"] == sel_month]
if sel_rep   != "All": df = df[df["Rep Name"] == sel_rep]

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("## 📊 Team Sales Performance Dashboard")
st.caption(f"Showing **{len(df)}** records · Month: **{sel_month}** · Rep: **{sel_rep}**")
st.markdown("---")

# ── KPI Cards ────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
cards = [
    (c1, "🎯 Total Target",     df["Target Month"].sum(),      "metric-card"),
    (c2, "💰 Net Sales",        df["Net Sales"].sum(),         "metric-card green"),
    (c3, "📈 Avg Achievement",  df["Achivment %"].mean(),      "metric-card orange"),
    (c4, "💳 Total Collection", df["Total Collection"].sum(),  "metric-card teal"),
    (c5, "📋 End Balance",      df["End Balance"].sum(),       "metric-card gray"),
]
for col, label, val, cls in cards:
    display = f"{val*100:.1f}%" if "Achievement" in label else fmt(val)
    col.markdown(f'<div class="{cls}"><h4>{label}</h4><h2>{display}</h2></div>',
                 unsafe_allow_html=True)

st.markdown("---")

# ── Charts Row 1 ─────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("📅 Net Sales vs Target by Month")
    monthly = df_full.groupby("Month")[["Target Month", "Net Sales"]].sum()
    monthly.columns = ["Target", "Net Sales"]
    st.bar_chart(monthly, height=300)

with col2:
    st.subheader("🏆 Achievement % by Rep")
    rep_ach = df_full.groupby("Rep Name")["Achivment %"].mean().reset_index()
    rep_ach["Achievement %"] = (rep_ach["Achivment %"] * 100).round(1)
    rep_ach = rep_ach.set_index("Rep Name")[["Achievement %"]]
    st.bar_chart(rep_ach, height=300)

# ── Charts Row 2 ─────────────────────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("💰 Collection Breakdown by Rep")
    coll = df_full.groupby("Rep Name")[
        ["Madfoaat", "Tasweyat Madinah", "Tasweyat Dainah"]
    ].sum()
    st.bar_chart(coll, height=280)

with col4:
    st.subheader("📊 Balance Trend by Month")
    bal = df_full.groupby("Month")[
        ["Opening Balance", "End Balance", "Motalbet El Fatrah"]
    ].sum()
    st.line_chart(bal, height=280)

# ── Returns Summary ───────────────────────────────────────────────────────────
st.subheader("📉 Returns vs Sales by Rep")
ret = df_full.groupby("Rep Name")[["Sales Value", "Returns Value"]].sum()
st.bar_chart(ret, height=250)

# ── Data Table ────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📋 Detailed Data Table")

display_df = df.copy()
if "Achivment %" in display_df.columns:
    display_df["Achivment %"] = display_df["Achivment %"].apply(
        lambda x: f"{x*100:.1f}%" if pd.notna(x) else "—"
    )
num_display = [
    "Target Month", "Net Sales", "Opening Balance", "Sales Value",
    "Returns Value", "Tasweyat Madinah", "Total Collection",
    "Madfoaat", "Tasweyat Dainah", "End Balance", "Motalbet El Fatrah"
]
for c in num_display:
    if c in display_df.columns:
        display_df[c] = display_df[c].apply(
            lambda x: f"{x:,.0f}" if pd.notna(x) else "—"
        )

st.dataframe(
    display_df.drop(columns=["Month"], errors="ignore"),
    use_container_width=True,
    height=400
)

# ── Rep Summary Table ─────────────────────────────────────────────────────────
st.subheader("👤 Rep Summary")
summary = df_full.groupby("Rep Name").agg(
    Target=("Target Month", "sum"),
    Net_Sales=("Net Sales", "sum"),
    Achievement=("Achivment %", "mean"),
    Total_Collection=("Total Collection", "sum"),
    End_Balance=("End Balance", "sum"),
    Returns=("Returns Value", "sum"),
).reset_index()
summary["Achievement"] = summary["Achievement"].apply(
    lambda x: f"{x*100:.1f}%" if pd.notna(x) else "—"
)
for c in ["Target", "Net_Sales", "Total_Collection", "End_Balance", "Returns"]:
    summary[c] = summary[c].apply(lambda x: f"{x:,.0f}")
summary.columns = [
    "Rep Name", "Target", "Net Sales", "Achievement %",
    "Total Collection", "End Balance", "Returns"
]
st.dataframe(summary, use_container_width=True, hide_index=True)

# ── Download ──────────────────────────────────────────────────────────────────
buf = BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Filtered Data")
    df_full.groupby("Rep Name").agg(
        Target=("Target Month","sum"),
        Net_Sales=("Net Sales","sum"),
        Total_Collection=("Total Collection","sum"),
        End_Balance=("End Balance","sum"),
    ).to_excel(writer, sheet_name="Rep Summary")

st.download_button(
    "⬇️ Download Filtered Data (.xlsx)",
    buf.getvalue(),
    file_name="team_filtered_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.markdown("---")
st.caption("Team Sales Dashboard · Built with Streamlit")
