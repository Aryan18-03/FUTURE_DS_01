import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Business Sales Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Compact dashboard styling to reduce scrolling.
st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp {
  background:
    radial-gradient(ellipse at 12% 0%, rgba(0, 229, 255, .10), transparent 34%),
    radial-gradient(ellipse at 90% 18%, rgba(139, 92, 246, .12), transparent 32%),
    linear-gradient(135deg, #050816 0%, #0a1020 52%, #080d1b 100%);
  color: #eaf2ff;
}
header[data-testid="stHeader"] { background: transparent !important; height: 2.5rem !important; }
/* Keep the dashboard clean for portfolio screenshots */
div[data-testid="stToolbar"], div[data-testid="stDecoration"], #MainMenu { visibility: hidden !important; height: 0 !important; }
.block-container { padding: 2.1rem 1.6rem 1.2rem 1.6rem !important; max-width: 1900px; }
h1 { line-height: 1.3 !important; overflow: visible !important; }
h1 {
  color: #f4f7ff !important; font-size: 1.9rem !important; font-weight: 750 !important;
  letter-spacing: -.025em; text-shadow: none !important;
  padding-bottom: .15rem !important; margin-bottom: .15rem !important;
}
h2, h3 { color: #d7e5ff !important; text-shadow: none !important; font-weight: 650 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
  color: #e4ecff !important; text-shadow: none !important; font-weight: 650 !important;
}
p, label, .stMarkdown { color: #b9c8e5; }
[data-testid="stCaptionContainer"] { color: #9eb2d6 !important; }
div[data-testid="stMetric"] {
  background: linear-gradient(145deg, rgba(18,29,54,.98), rgba(10,17,34,.98));
  padding: 14px 16px; border: 1px solid rgba(0,229,255,.26); border-radius: 16px;
  box-shadow: 0 0 0 1px rgba(0,229,255,.04), 0 0 18px rgba(0,229,255,.10), 0 10px 30px rgba(0,0,0,.30);
}
div[data-testid="stMetricLabel"] { color: #9db5d8 !important; font-size: .82rem; font-weight: 650; }
div[data-testid="stMetricValue"] { color: #f4fbff !important; font-size: 1.55rem; font-weight: 850; text-shadow: 0 0 12px rgba(0,229,255,.18); }
div[data-testid="stPlotlyChart"] {
  background: #0d172b !important;
  border: 1px solid rgba(110,160,220,.32); border-radius: 14px; padding: 8px 8px 4px 8px;
  box-shadow: 0 8px 22px rgba(0,0,0,.22);
  margin: 0 0 16px 0; overflow: visible !important;
}
div[data-testid="stPlotlyChart"] * { color: #eaf2ff; }
div[data-testid="stPlotlyChart"]:hover { box-shadow: 0 8px 22px rgba(0,0,0,.22); }
div[data-testid="stPlotlyChart"], div[data-testid="stPlotlyChart"] iframe { animation: none !important; transition: none !important; }
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0b1328 0%, #090f20 100%);
  border-right: 1px solid rgba(0,229,255,.25); min-width: 270px !important; max-width: 270px !important;
  box-shadow: 8px 0 28px rgba(0,0,0,.24);
}
section[data-testid="stSidebar"] * { color: #eaf2ff; }
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #9eb2d6 !important; }
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
  background: #111d35 !important; border: 1px solid rgba(0,229,255,.30) !important; border-radius: 10px !important;
  box-shadow: 0 0 10px rgba(0,229,255,.05);
}
section[data-testid="stSidebar"] div[data-baseweb="select"] span { color: #edf7ff !important; }
section[data-testid="stSidebar"] input { color: #edf7ff !important; }
section[data-testid="stSidebar"] button {
  background: linear-gradient(90deg, #12334b, #24214c) !important; border: 1px solid rgba(0,229,255,.35) !important;
  border-radius: 10px !important; box-shadow: 0 0 12px rgba(0,229,255,.10);
}
section[data-testid="stSidebar"] button p { color: #eafcff !important; }
div[data-testid="stAlert"] { background: #111d35; border-radius: 12px; border: 1px solid rgba(0,229,255,.2); }
div[data-testid="stExpander"] { background: #0e172c; border: 1px solid rgba(0,229,255,.2); border-radius: 12px; }
div[data-testid="stDataFrame"] { border: 1px solid rgba(0,229,255,.2); border-radius: 10px; }
hr { margin: .5rem 0 !important; border-color: rgba(0,229,255,.18); }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

BLUE, ORANGE, GREEN, PURPLE = "#00E5FF", "#FF9F43", "#35F2A0", "#A78BFA"
PALETTE = [BLUE, ORANGE, GREEN, PURPLE]

@st.cache_data
def load_data():
    data = pd.read_csv("SampleSuperstore.csv")
    required = ["Sales", "Profit", "Quantity", "Discount", "Category", "Sub-Category", "Region", "Segment"]
    missing = [col for col in required if col not in data.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    for col in ["Sales", "Profit", "Quantity", "Discount"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    return data.dropna(subset=required).copy()

try:
    df = load_data()
except (FileNotFoundError, ValueError) as err:
    st.error(f"Could not load the dataset: {err}")
    st.stop()

if df.empty:
    st.error("The dataset has no usable rows.")
    st.stop()

# All filters are vertical in the sidebar.
st.sidebar.title("🎛️ Filters")
st.sidebar.caption("Change a filter to update every chart.")
regions = sorted(df["Region"].unique().tolist())
categories = sorted(df["Category"].unique().tolist())
segments = sorted(df["Segment"].unique().tolist())
subcategories = sorted(df["Sub-Category"].unique().tolist())

with st.sidebar:
    if st.button("↩ Reset all filters", use_container_width=True):
        for key in ["region_filter", "category_filter", "segment_filter", "subcategory_filter",
                    "sales_filter", "profit_filter", "discount_filter", "status_filter", "ship_filter"]:
            st.session_state.pop(key, None)
        st.rerun()

    selected_region = st.selectbox("Region", ["All regions"] + regions, key="region_filter")
    selected_category = st.selectbox("Category", ["All categories"] + categories, key="category_filter")
    selected_segment = st.selectbox("Customer Segment", ["All segments"] + segments, key="segment_filter")
    selected_subcategory = st.selectbox("Sub-category", ["All sub-categories"] + subcategories, key="subcategory_filter")

    sales_min, sales_max = float(df["Sales"].min()), float(df["Sales"].max())
    profit_min, profit_max = float(df["Profit"].min()), float(df["Profit"].max())
    discount_min, discount_max = float(df["Discount"].min()), float(df["Discount"].max())

    sales_range = st.slider("Order sales ($)", sales_min, sales_max, (sales_min, sales_max), key="sales_filter")
    profit_range = st.slider("Order profit ($)", profit_min, profit_max, (profit_min, profit_max), key="profit_filter")
    discount_range = st.slider("Discount", discount_min, discount_max, (discount_min, discount_max), key="discount_filter")

    status = st.selectbox("Order profitability", ["All orders", "Profitable only", "Loss-making only"], key="status_filter")
    if "Ship Mode" in df.columns:
        ship_options = sorted(df["Ship Mode"].dropna().unique().tolist())
        selected_ship = st.selectbox("Shipping Mode", ["All shipping modes"] + ship_options, key="ship_filter")
    else:
        selected_ship = None

filtered = df[
    (df["Region"].isin(regions) if selected_region == "All regions" else df["Region"].eq(selected_region))
    & (df["Category"].isin(categories) if selected_category == "All categories" else df["Category"].eq(selected_category))
    & (df["Segment"].isin(segments) if selected_segment == "All segments" else df["Segment"].eq(selected_segment))
    & (df["Sub-Category"].isin(subcategories) if selected_subcategory == "All sub-categories" else df["Sub-Category"].eq(selected_subcategory))
    & df["Sales"].between(*sales_range)
    & df["Profit"].between(*profit_range)
    & df["Discount"].between(*discount_range)
].copy()
if selected_ship is not None and selected_ship != "All shipping modes":
    filtered = filtered[filtered["Ship Mode"].eq(selected_ship)]
if status == "Profitable only":
    filtered = filtered[filtered["Profit"] > 0]
elif status == "Loss-making only":
    filtered = filtered[filtered["Profit"] < 0]

st.title("📊 Business Sales Performance Analysis")
st.caption("FUTURE INTERNS · TASK 1  |  Sales, profitability and customer insights")

if filtered.empty:
    st.warning("No records match these filters. Adjust the filters in the left sidebar.")
    st.stop()

total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
total_qty = filtered["Quantity"].sum()
margin = total_profit / total_sales * 100 if total_sales else 0

# KPI row
k1, k2, k3, k4 = st.columns(4, gap="medium")
k1.metric("Total Sales", f"${total_sales:,.0f}")
k2.metric("Total Profit", f"${total_profit:,.0f}", delta=f"{margin:.1f}% margin")
k3.metric("Quantity Sold", f"{total_qty:,.0f}")
k4.metric("Orders / Records", f"{len(filtered):,}")

# Aggregate data once, then show four charts in a compact 2x2 grid.
category = filtered.groupby("Category", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
region = filtered.groupby("Region", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).sort_values("Sales", ascending=False)
subcategory = filtered.groupby("Sub-Category", as_index=False).agg(Profit=("Profit", "sum"), Sales=("Sales", "sum")).sort_values("Profit", ascending=True)
segment = filtered.groupby("Segment", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))

left, right = st.columns(2, gap="medium")
with left:
    pie = px.pie(category, names="Category", values="Sales", hole=.42,
                 color="Category", color_discrete_map={"Technology": BLUE, "Furniture": ORANGE, "Office Supplies": GREEN},
                 title="Sales Share by Category")
    pie.update_traces(textposition="inside", textinfo="percent+label", textfont=dict(color="#172033", size=12, family="Arial"))
    pie.update_layout(template="plotly_dark", height=290, margin=dict(t=58,b=20,l=18,r=18), showlegend=False,
                      title_font=dict(size=17, color="#F1F5FF"), font=dict(color="#EAF2FF"),
                      paper_bgcolor="#0D172B", plot_bgcolor="#0D172B")
    st.plotly_chart(pie, use_container_width=True, config={"displayModeBar": False})

with right:
    bar = px.bar(region, x="Region", y="Sales", color="Region", text="Sales",
                 color_discrete_sequence=PALETTE, title="Sales by Region")
    bar.update_traces(texttemplate="$%{y:,.2s}", textposition="outside", cliponaxis=False)
    bar.update_layout(template="plotly_dark", height=290, showlegend=False,
                      margin=dict(t=52,b=30,l=16,r=24), title_font=dict(size=17, color="#F1F5FF"),
                      yaxis=dict(gridcolor="rgba(151,180,220,0.16)", zeroline=False, tickfont=dict(color="#EAF2FF")),
                      xaxis=dict(tickfont=dict(color="#EAF2FF")),
                      plot_bgcolor="#0D172B", paper_bgcolor="#0D172B", font=dict(family="Arial", color="#EAF2FF"))
    st.plotly_chart(bar, use_container_width=True, config={"displayModeBar": False})

left2, right2 = st.columns(2, gap="medium")
with left2:
    profit_chart = px.bar(
        subcategory, x="Profit", y="Sub-Category", orientation="h",
        color="Profit", color_continuous_scale=["#FF5C7A", "#FFCA7A", "#35F2A0"],
        title="Profit / Loss by Sub-category", labels={"Profit": "Profit ($)"}
    )
    profit_chart.add_vline(x=0, line_dash="dash", line_color="#B6C7E8")
    profit_chart.update_layout(template="plotly_dark", height=340, margin=dict(t=58,b=24,l=12,r=18),
                               title_font=dict(size=17, color="#F1F5FF"), font=dict(color="#EAF2FF"),
                               paper_bgcolor="#0D172B", plot_bgcolor="#0D172B",
                               coloraxis_showscale=False, yaxis_title=None,
                               yaxis=dict(tickfont=dict(color="#EAF2FF")),
                               xaxis=dict(gridcolor="rgba(151,180,220,0.16)", tickfont=dict(color="#EAF2FF")))
    st.plotly_chart(profit_chart, use_container_width=True, config={"displayModeBar": False})

with right2:
    segment_chart = px.bar(segment, x="Segment", y="Sales", color="Segment", text="Sales",
                  color_discrete_map={"Consumer": BLUE, "Corporate": PURPLE, "Home Office": ORANGE},
                  title="Sales by Customer Segment")
    segment_chart.update_traces(texttemplate="$%{y:,.2s}", textposition="outside", cliponaxis=False,
                                marker_line_width=0)
    segment_chart.update_layout(template="plotly_dark", height=340, showlegend=False,
                       margin=dict(t=58,b=30,l=16,r=18), title_font=dict(size=17, color="#F1F5FF"),
                       yaxis=dict(gridcolor="rgba(151,180,220,0.16)", zeroline=False, tickfont=dict(color="#EAF2FF")),
                       xaxis=dict(tickfont=dict(color="#EAF2FF")),
                       plot_bgcolor="#0D172B", paper_bgcolor="#0D172B",
                       font=dict(family="Arial", color="#EAF2FF"))
    st.plotly_chart(segment_chart, use_container_width=True, config={"displayModeBar": False})

# Compact line chart: sales trend across discount levels (dataset has no reliable date field).
discount_trend = (
    filtered.groupby("Discount", as_index=False)
    .agg(Sales=("Sales", "sum"))
    .sort_values("Discount")
)
trend = px.line(
    discount_trend, x="Discount", y="Sales", markers=True,
    title="Sales by Discount Level",
    labels={"Discount": "Discount", "Sales": "Sales ($)"}
)
trend.update_traces(line=dict(color=BLUE, width=3), marker=dict(size=8, color=ORANGE),
                    fill="tozeroy", fillcolor="rgba(0,229,255,0.12)")
trend.update_layout(
    template="plotly_dark", height=230,
    margin=dict(t=48, b=24, l=16, r=18),
    title_font=dict(size=17, color="#F1F5FF"), paper_bgcolor="#0D172B", plot_bgcolor="#0D172B",
    font=dict(color="#EAF2FF"),
    xaxis=dict(tickformat=".0%", gridcolor="rgba(151,180,220,0.16)"),
    yaxis=dict(gridcolor="rgba(151,180,220,0.16)")
)
st.plotly_chart(trend, use_container_width=True, config={"displayModeBar": False})

# Short business insight strip rather than a long section.
best_cat = category.loc[category["Sales"].idxmax()]
best_region = region.loc[region["Sales"].idxmax()]
worst_subcat = subcategory.iloc[0]
ins1, ins2, ins3 = st.columns(3, gap="medium")
ins1.info(f"**Top category:** {best_cat['Category']} · ${best_cat['Sales']:,.0f} sales")
ins2.info(f"**Top region:** {best_region['Region']} · ${best_region['Sales']:,.0f} sales")
if worst_subcat["Profit"] < 0:
    ins3.warning(f"**Loss to review:** {worst_subcat['Sub-Category']} · ${abs(worst_subcat['Profit']):,.0f} loss")
else:
    ins3.success(f"**Lowest profit:** {worst_subcat['Sub-Category']} · ${worst_subcat['Profit']:,.0f}")

with st.expander("View data and download filtered records"):
    st.download_button(
        "Download filtered CSV", filtered.to_csv(index=False).encode("utf-8"),
        "filtered_sales_data.csv", "text/csv"
    )
    st.dataframe(filtered, use_container_width=True, hide_index=True, height=240)

st.caption("Source: Sample Superstore dataset. Synthetic dates and unverified product names are excluded from conclusions.")
