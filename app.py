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
.block-container {padding-top: .25rem; padding-bottom: .1rem; max-width: 1900px;}
h1 {font-size: 1.3rem !important; padding-bottom: 0 !important; margin-bottom: 0 !important; line-height: 1.15 !important;}
h2, h3 {font-size: .9rem !important; margin-bottom: .15rem !important;}
p {margin-bottom: .12rem;}
div[data-testid="stMetric"] {padding: 3px 7px; border: 1px solid #e4e7eb; border-radius: 7px;}
div[data-testid="stMetricLabel"] {font-size: .78rem;}
div[data-testid="stMetricValue"] {font-size: 1.05rem;}
div[data-testid="stPlotlyChart"] {margin-top: -8px; margin-bottom: -35px;}
section[data-testid="stSidebar"] {min-width: 245px !important; max-width: 245px !important;}
hr {margin: .2rem 0 !important;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

BLUE, ORANGE, GREEN, PURPLE = "#4263EB", "#F76707", "#12B886", "#7950F2"
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

    selected_regions = st.multiselect("Region", regions, default=regions, key="region_filter")
    selected_categories = st.multiselect("Category", categories, default=categories, key="category_filter")
    selected_segments = st.multiselect("Customer segment", segments, default=segments, key="segment_filter")
    selected_subcategories = st.multiselect("Sub-category", subcategories, default=subcategories, key="subcategory_filter")

    sales_min, sales_max = float(df["Sales"].min()), float(df["Sales"].max())
    profit_min, profit_max = float(df["Profit"].min()), float(df["Profit"].max())
    discount_min, discount_max = float(df["Discount"].min()), float(df["Discount"].max())

    sales_range = st.slider("Order sales ($)", sales_min, sales_max, (sales_min, sales_max), key="sales_filter")
    profit_range = st.slider("Order profit ($)", profit_min, profit_max, (profit_min, profit_max), key="profit_filter")
    discount_range = st.slider("Discount", discount_min, discount_max, (discount_min, discount_max), key="discount_filter")

    status = st.selectbox("Order profitability", ["All orders", "Profitable only", "Loss-making only"], key="status_filter")
    if "Ship Mode" in df.columns:
        ship_options = sorted(df["Ship Mode"].dropna().unique().tolist())
        selected_ship = st.multiselect("Shipping mode", ship_options, default=ship_options, key="ship_filter")
    else:
        selected_ship = None

filtered = df[
    df["Region"].isin(selected_regions)
    & df["Category"].isin(selected_categories)
    & df["Segment"].isin(selected_segments)
    & df["Sub-Category"].isin(selected_subcategories)
    & df["Sales"].between(*sales_range)
    & df["Profit"].between(*profit_range)
    & df["Discount"].between(*discount_range)
].copy()
if selected_ship is not None:
    filtered = filtered[filtered["Ship Mode"].isin(selected_ship)]
if status == "Profitable only":
    filtered = filtered[filtered["Profit"] > 0]
elif status == "Loss-making only":
    filtered = filtered[filtered["Profit"] < 0]

st.title("📊 Business Sales Performance Dashboard")
st.caption("Future Interns • Task 1 | Interactive sales, profit, product and regional analysis")

if filtered.empty:
    st.warning("No records match these filters. Adjust the filters in the left sidebar.")
    st.stop()

total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
total_qty = filtered["Quantity"].sum()
margin = total_profit / total_sales * 100 if total_sales else 0

# KPI row
k1, k2, k3, k4 = st.columns(4)
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
    pie.update_traces(textposition="inside", textinfo="percent+label", textfont_size=11)
    pie.update_layout(template="plotly_white", height=190, margin=dict(t=32,b=2,l=2,r=2), showlegend=False)
    st.plotly_chart(pie, use_container_width=True, config={"displayModeBar": False})

with right:
    bar = px.bar(region, x="Region", y="Sales", color="Region", text="Sales",
                 color_discrete_sequence=PALETTE, title="Sales by Region")
    bar.update_traces(texttemplate="$%{y:,.2s}", textposition="outside", cliponaxis=False)
    bar.update_layout(template="plotly_white", height=255, showlegend=False,
                      margin=dict(t=42,b=5,l=5,r=5), yaxis=dict(gridcolor="#E9ECEF"))
    st.plotly_chart(bar, use_container_width=True, config={"displayModeBar": False})

left2, right2 = st.columns(2, gap="medium")
with left2:
    profit_chart = px.bar(
        subcategory, x="Profit", y="Sub-Category", orientation="h",
        color="Profit", color_continuous_scale=["#E03131", "#FFC078", "#2F9E44"],
        title="Profit / Loss by Sub-category", labels={"Profit": "Profit ($)"}
    )
    profit_chart.add_vline(x=0, line_dash="dash", line_color="#343A40")
    profit_chart.update_layout(template="plotly_white", height=215, margin=dict(t=32,b=2,l=2,r=2),
                               coloraxis_showscale=False, yaxis_title=None, xaxis=dict(gridcolor="#E9ECEF"))
    st.plotly_chart(profit_chart, use_container_width=True, config={"displayModeBar": False})

with right2:
    line = px.bar(segment, x="Segment", y="Sales", color="Segment", text="Sales",
                  color_discrete_sequence=PALETTE, title="Sales by Customer Segment")
    line.update_traces(texttemplate="$%{y:,.2s}", textposition="outside", cliponaxis=False)
    line.update_layout(template="plotly_white", height=300, showlegend=False,
                       margin=dict(t=42,b=5,l=5,r=5), yaxis=dict(gridcolor="#E9ECEF"))
    st.plotly_chart(line, use_container_width=True, config={"displayModeBar": False})

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
trend.update_traces(line=dict(color=BLUE, width=3), marker=dict(size=6))
trend.update_layout(
    template="plotly_white", height=190,
    margin=dict(t=32, b=2, l=5, r=5),
    xaxis=dict(tickformat=".0%", gridcolor="#E9ECEF"),
    yaxis=dict(gridcolor="#E9ECEF")
)
st.plotly_chart(trend, use_container_width=True, config={"displayModeBar": False})

# Short business insight strip rather than a long section.
best_cat = category.loc[category["Sales"].idxmax()]
best_region = region.loc[region["Sales"].idxmax()]
worst_subcat = subcategory.iloc[0]
ins1, ins2, ins3 = st.columns(3, gap="small")
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
