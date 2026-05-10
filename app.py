import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import os

st.set_page_config(
    page_title="Team Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1F4E79 0%, #2E75B6 100%);
        border-radius: 12px; padding: 18px 22px; color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-bottom: 10px;
    }
    .metric-card h3 { margin: 0; font-size: 14px; opacity: 0.85; }
    .metric-card h1 { margin: 4px 0 0; font-size: 28px; font-weight: 700; }
    .metric-green { background: linear-gradient(135deg, #1a6b3c 0%, #27ae60 100%) !important; }
    .metric-orange { background: linear-gradient(135deg, #c0392b 0%, #e67e22 100%) !important; }
    .metric-teal   { background: linear-gradient(135deg, #0e6655 0%, #17a589 100%) !important; }
    .stDataFrame { border-radius: 8px; overflow: hidden; }
    section[data-testid="stSidebar"] { background: #1F4E79; }
    section[data-testid="stSidebar"] * { color: white !important; }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label { color: white !important; }
</style>
""", unsafe_allow_html=True)


# ── Data loading ─────────────────────────────────────────────────────────────
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
    if "Achivment %" in df.columns and df["Achivment %"].max() > 5:
        df["Achivment %"] = df["Achivment %"] / 100
    return df


def fmt(n):
    if pd.isna(n): return "—"
    if abs(n) >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if abs(n) >= 1_000:     return f"{n/1_000:.1f}K"
    return f"{n:,.0f}"


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/bar-chart.png", width=60)
    st.title("Team Dashboard")
    st.markdown("---")

    uploaded = st.file_uploader("📂 Upload Excel File", type=["xlsx", "xls"],
                                 help="Upload your Team Sheet Excel file")
    if not uploaded:
        default = os.path.join(os.path.dirname(__file__), "data", "team_sheet_sample.xlsx")
        if os.path.exists(default):
            with open(default, "rb") as f:
                uploaded = BytesIO(f.read())
            st.info("Using sample data. Upload your file above.")
        else:
            st.warning("Please upload an Excel file.")
            st.stop()

    df_full = load_data(uploaded)

    st.markdown("### 🔍 Filters")
    months    = ["All"] + sorted(df_full["Month"].dropna().unique().tolist())
    reps      = ["All"] + sorted(df_full["Rep Name"].dropna().unique().tolist())
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
kpis = [
    (c1, "🎯 Total Target",     df["Target Month"].sum(),       "metric-card"),
    (c2, "💰 Total Net Sales",  df["Net Sales"].sum(),          "metric-card metric-green"),
    (c3, "📈 Avg Achievement",  df["Achivment %"].mean(),       "metric-card metric-orange"),
    (c4, "💳 Total Collection", df["Total Collection"].sum(),   "metric-card metric-teal"),
    (c5, "📋 End Balance",      df["End Balance"].sum(),        "metric-card"),
]
for col, label, val, cls in kpis:
    display = f"{val*100:.1f}%" if "Achievement" in label else fmt(val)
    col.markdown(f'<div class="{cls}"><h3>{label}</h3><h1>{display}</h1></div>',
                 unsafe_allow_html=True)

st.markdown("---")

# ── Row 1: charts ────────────────────────────────────────────────────────────
row1l, row1r = st.columns([3, 2])

with row1l:
    st.subheader("📅 Net Sales vs Target by Month")
    monthly = df_full.groupby("Month")[["Target Month", "Net Sales"]].sum().reset_index()
    fig = go.Figure()
    fig.add_bar(x=monthly["Month"], y=monthly["Target Month"], name="Target",
                marker_color="#ADB5BD")
    fig.add_bar(x=monthly["Month"], y=monthly["Net Sales"],   name="Net Sales",
                marker_color="#2E75B6")
    fig.update_layout(barmode="group", height=340,
                      plot_bgcolor="white", paper_bgcolor="white",
                      legend=dict(orientation="h", y=1.1),
                      margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

with row1r:
    st.subheader("🏆 Achievement % by Rep")
    rep_ach = df_full.groupby("Rep Name")["Achivment %"].mean().reset_index()
    rep_ach["Achivment %"] *= 100
    rep_ach = rep_ach.sort_values("Achivment %", ascending=True)
    fig2 = px.bar(rep_ach, x="Achivment %", y="Rep Name", orientation="h",
                  color="Achivment %", color_continuous_scale="RdYlGn",
                  range_color=[60, 120], height=340,
                  labels={"Achivment %": "Achievement %"})
    fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=10, r=10, t=30, b=10),
                       coloraxis_showscale=False)
    fig2.add_vline(x=100, line_dash="dash", line_color="gray",
                   annotation_text="100%", annotation_position="top right")
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2 ────────────────────────────────────────────────────────────────────
row2l, row2r = st.columns(2)

with row2l:
    st.subheader("💰 Collection Breakdown by Rep")
    rep_coll = df_full.groupby("Rep Name")[
        ["Madfoaat", "Tasweyat Madinah", "Tasweyat Dainah"]
    ].sum().reset_index()
    fig3 = go.Figure()
    for col_name, color in [("Madfoaat", "#2E75B6"),
                             ("Tasweyat Madinah", "#27AE60"),
                             ("Tasweyat Dainah", "#E67E22")]:
        fig3.add_bar(x=rep_coll["Rep Name"], y=rep_coll[col_name],
                     name=col_name, marker_color=color)
    fig3.update_layout(barmode="stack", height=320,
                       plot_bgcolor="white", paper_bgcolor="white",
                       legend=dict(orientation="h", y=1.12),
                       margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig3, use_container_width=True)

with row2r:
    st.subheader("📉 Returns vs Sales")
    rep_ret = df_full.groupby("Rep Name")[["Sales Value", "Returns Value"]].sum().reset_index()
    rep_ret["Return Rate %"] = (rep_ret["Returns Value"] / rep_ret["Sales Value"] * 100).round(1)
    fig4 = px.scatter(rep_ret, x="Sales Value", y="Returns Value",
                      size="Return Rate %", color="Rep Name",
                      hover_data=["Return Rate %"], height=320,
                      labels={"Sales Value": "Sales Value", "Returns Value": "Returns Value"})
    fig4.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig4, use_container_width=True)

# ── Balance trend ────────────────────────────────────────────────────────────
st.subheader("📊 Balance Trend (Opening → End)")
balance_trend = df_full.groupby("Month")[["Opening Balance", "End Balance",
                                          "Motalbet El Fatrah"]].sum().reset_index()
fig5 = go.Figure()
fig5.add_scatter(x=balance_trend["Month"], y=balance_trend["Opening Balance"],
                 mode="lines+markers", name="Opening Balance", line=dict(color="#1F4E79", width=2))
fig5.add_scatter(x=balance_trend["Month"], y=balance_trend["End Balance"],
                 mode="lines+markers", name="End Balance", line=dict(color="#27AE60", width=2))
fig5.add_scatter(x=balance_trend["Month"], y=balance_trend["Motalbet El Fatrah"],
                 mode="lines+markers", name="Motalbet El Fatrah",
                 line=dict(color="#E74C3C", width=2, dash="dot"))
fig5.update_layout(height=300, plot_bgcolor="white", paper_bgcolor="white",
                   legend=dict(orientation="h", y=1.1),
                   margin=dict(l=10, r=10, t=30, b=10))
st.plotly_chart(fig5, use_container_width=True)

# ── Data table ───────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📋 Detailed Data Table")

display_df = df.copy()
if "Achivment %" in display_df.columns:
    display_df["Achivment %"] = display_df["Achivment %"].apply(
        lambda x: f"{x*100:.1f}%" if pd.notna(x) else "—"
    )
num_display = ["Target Month", "Net Sales", "Opening Balance", "Sales Value",
               "Returns Value", "Tasweyat Madinah", "Total Collection",
               "Madfoaat", "Tasweyat Dainah", "End Balance", "Motalbet El Fatrah"]
for c in num_display:
    if c in display_df.columns:
        display_df[c] = display_df[c].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "—")

st.dataframe(display_df.drop(columns=["Month"], errors="ignore"),
             use_container_width=True, height=380)

# ── Download ─────────────────────────────────────────────────────────────────
buf = BytesIO()
df.to_excel(buf, index=False, sheet_name="Filtered Data")
st.download_button("⬇️ Download Filtered Data (.xlsx)", buf.getvalue(),
                   file_name="filtered_team_data.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown("---")
st.caption("Team Sales Dashboard · Built with Streamlit & Plotly")
