# 📊 Team Sales Dashboard

An interactive Streamlit dashboard for visualizing sales team performance from Excel Team Sheet data.

## 🖥️ Live Demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

---

## 📋 Columns Supported

| Column | Description |
|--------|-------------|
| Date | Transaction / reporting date |
| Rep Code | Unique sales rep identifier |
| Rep Name | Sales representative name |
| Target Month | Monthly sales target |
| Net Sales | Actual net sales achieved |
| Achivment % | Achievement percentage (Net Sales / Target) |
| Opening Balance | Balance at start of period |
| Sales Value | Gross sales value |
| Returns Value | Value of returned goods |
| Tasweyat Madinah | City settlement amount |
| Total Collection | Total amount collected |
| Madfoaat | Payments made |
| Tasweyat Dainah | Debt settlement |
| End Balance | Closing balance |
| Motalbet El Fatrah | Period claims/receivables |

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/team-sales-dashboard.git
cd team-sales-dashboard
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Locally

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

### 4. Upload Your Data

- Click **"Upload Excel File"** in the sidebar
- Select your Excel file with a **"Team Sheet"** worksheet
- The dashboard updates automatically

---

## 📁 Project Structure

```
team-sales-dashboard/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── data/
│   └── team_sheet_sample.xlsx  # Sample data (auto-loaded if no upload)
├── .streamlit/
│   └── config.toml             # Streamlit theme config
└── README.md
```

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"**
4. Select your repo, branch `main`, and file `app.py`
5. Click **"Deploy"**

Your dashboard is live in ~2 minutes! 🎉

---

## 📊 Dashboard Features

- **KPI Cards** — Target, Net Sales, Achievement %, Total Collection, End Balance
- **Sales vs Target** — Grouped bar chart by month
- **Achievement % by Rep** — Color-coded horizontal bar (red → green)
- **Collection Breakdown** — Stacked bar: Madfoaat / Tasweyat Madinah / Tasweyat Dainah
- **Returns vs Sales** — Scatter plot with return rate bubble size
- **Balance Trend** — Line chart: Opening → End Balance → Motalbet El Fatrah
- **Filterable Data Table** — Filter by Month and Rep, download filtered results

---

## 🔧 Excel File Requirements

- The workbook must contain a sheet named exactly **`Team Sheet`**
- Row 1 must be the header row with the column names listed above
- Dates should be in a recognizable date format (YYYY-MM-DD recommended)
- Numeric columns should contain numbers (no currency symbols in cells)

---

## 📄 License

MIT License — free to use and modify.
