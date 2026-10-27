import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Business Sales Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Compact, single-screen layout
st.markdown("""
<style>
.block-container {padding-top: 0.8rem; padding-bottom: 0.5rem; max-width: 1600px;}
h1 {font-size: 1.65rem !important; padding-bottom: 0 !important;}
h2, h3 {font-size: 1.05rem !important;}
div[data-testid="stMetric"] {padding: 8px 10px; border: 1px solid #e5e7eb; border-radius: 10px;}
div[data-testid="stMetricValue"] {font-size: 1.35rem;}
div[data-testid="stPlotlyChart"] {margin-bottom: -20px;}
div[data-testid="stTabs"] button {padding-top: 7px; padding-bottom: 7px;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

BLUE = "#636EFA"
ORANGE = "#EF553B"
GREEN = "#00CC96"
PURPLE = "#AB63FA"
PINK = "#E056A0"
COLORS = [BLUE, ORANGE, GREEN, PURPLE, PINK]

@st.cache_data
def load_data():
    data = pd.read_csv("SampleSuperstore.csv")
    required = [
        "Sales", "Profit", "Quantity", "Discount", "Category",
        "Sub-Category", "Region", "Segment"
    ]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))
    for col in ["Sales", "Profit", "Quantity", "Discount"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    data = data.dropna(subset=required).copy()
    data["Discount Band"] = pd.cut(
        data["Discount"],
        bins=[-0.001, 0, 0.10, 0.20, 0.30, 1.0],
        labels=["No discount", "0–10%", "10–20%", "20–30%", "30%+"],
        include_lowest=True
    )
    return data

try:
    df = load_data()
except FileNotFoundError:
    st.error("SampleSuperstore.csv was not found. Keep it beside app.py.")
    st.stop()
except ValueError as error:
    st.error(str(error))
    st.stop()

if df.empty:
    st.error("The dataset contains no usable records.")
    st.stop()

# Header and compact filter row
head, filter_col = st.columns([5, 1])
with head:
    st.title("📊 Business Sales Performance")
    st.caption("Future Interns | Task 1 • Interactive sales, profit and customer analysis")
with filter_col:
    st.write("")
    st.write("")
    if st.button("↩ Reset filters", use_container_width=True):
        st.session_state.clear()
        st.rerun()

with st.expander("🎛️ Filters — open to refine the dashboard", expanded=False):
    f1, f2, f3, f4 = st.columns(4)
    regions = sorted(df["Region"].dropna().unique().tolist())
    categories = sorted(df["Category"].dropna().unique().tolist())
    segments = sorted(df["Segment"].dropna().unique().tolist())
    subcategories = sorted(df["Sub-Category"].dropna().unique().tolist())

    with f1:
        chosen_regions = st.multiselect("Region", regions, default=regions, key="regions")
    with f2:
        chosen_categories = st.multiselect("Category", categories, default=categories, key="categories")
    with f3:
        chosen_segments = st.multiselect("Customer segment", segments, default=segments, key="segments")
    with f4:
        chosen_subcategories = st.multiselect("Sub-category", subcategories, default=subcategories, key="subcategories")

    f5, f6, f7 = st.columns(3)
    with f5:
        sales_range = st.slider(
            "Order sales ($)", float(df["Sales"].min()), float(df["Sales"].max()),
            (float(df["Sales"].min()), float(df["Sales"].max())), key="sales_range"
        )
    with f6:
        profit_range = st.slider(
            "Order profit ($)", float(df["Profit"].min()), float(df["Profit"].max()),
            (float(df["Profit"].min()), float(df["Profit"].max())), key="profit_range"
        )
    with f7:
        discount_range = st.slider(
            "Discount", float(df["Discount"].min()), float(df["Discount"].max()),
            (float(df["Discount"].min()), float(df["Discount"].max())), key="discount_range"
        )

    if "Ship Mode" in df.columns:
        ship_modes = sorted(df["Ship Mode"].dropna().unique().tolist())
        chosen_ship_modes = st.multiselect("Shipping mode", ship_modes, default=ship_modes, key="ship_modes")
    else:
        chosen_ship_modes = None

    profit_status = st.radio(
        "Profit status", ["All orders", "Profitable orders", "Loss-making orders"],
        horizontal=True, key="profit_status"
    )

filtered = df[
    df["Region"].isin(chosen_regions)
    & df["Category"].isin(chosen_categories)
    & df["Segment"].isin(chosen_segments)
    & df["Sub-Category"].isin(chosen_subcategories)
    & df["Sales"].between(sales_range[0], sales_range[1])
    & df["Profit"].between(profit_range[0], profit_range[1])
    & df["Discount"].between(discount_range[0], discount_range[1])
].copy()

if chosen_ship_modes is not None:
    filtered = filtered[filtered["Ship Mode"].isin(chosen_ship_modes)]
if profit_status == "Profitable orders":
    filtered = filtered[filtered["Profit"] > 0]
elif profit_status == "Loss-making orders":
    filtered = filtered[filtered["Profit"] < 0]

if filtered.empty:
    st.warning("No records match these filters. Open Filters and widen your selections.")
    st.stop()

sales = filtered["Sales"].sum()
profit = filtered["Profit"].sum()
quantity = filtered["Quantity"].sum()
margin = (profit / sales * 100) if sales else 0
record_count = len(filtered)

# Compact KPI strip
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Sales", f"${sales:,.0f}")
k2.metric("Total Profit", f"${profit:,.0f}")
k3.metric("Quantity Sold", f"{quantity:,.0f}")
k4.metric("Profit Margin", f"{margin:.2f}%")
k5.metric("Filtered Records", f"{record_count:,}")

# Summaries used by charts and insights
category = filtered.groupby("Category", as_index=False).agg(
    Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum"), Quantity=("Quantity", "sum")
)
category["Sales Share (%)"] = category["Total_Sales"] / sales * 100 if sales else 0
category["Profit Margin (%)"] = (
    category["Total_Profit"] / category["Total_Sales"].where(category["Total_Sales"] != 0) * 100
).fillna(0)

region = filtered.groupby("Region", as_index=False).agg(
    Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum")
).sort_values("Total_Sales", ascending=False)

subcategory = filtered.groupby("Sub-Category", as_index=False).agg(
    Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum"), Quantity=("Quantity", "sum")
).sort_values("Total_Profit", ascending=True)

segment = filtered.groupby("Segment", as_index=False).agg(
    Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum"), Quantity=("Quantity", "sum")
).sort_values("Total_Sales", ascending=False)

discount = filtered.dropna(subset=["Discount Band"]).groupby(
    "Discount Band", observed=False, as_index=False
).agg(Total_Profit=("Profit", "sum"), Total_Sales=("Sales", "sum"), Records=("Profit", "size"))

# Tabs keep the dashboard in one compact page without a long scroll.
tab_overview, tab_products, tab_customers, tab_insights, tab_data = st.tabs([
    "📌 Overview", "📦 Products", "👥 Customers & Regions", "💡 Insights", "📋 Data"
])

with tab_overview:
    c1, c2 = st.columns(2)
    with c1:
        pie = px.pie(
            category, names="Category", values="Total_Sales", hole=0.48,
            color="Category",
            color_discrete_map={"Technology": BLUE, "Furniture": ORANGE, "Office Supplies": GREEN},
            title="Sales Share by Category"
        )
        pie.update_traces(textposition="inside", textinfo="percent+label")
        pie.update_layout(template="plotly_white", height=300, margin=dict(t=45, b=5, l=5, r=5), showlegend=False)
        st.plotly_chart(pie, use_container_width=True, config={"displayModeBar": False})
    with c2:
        region_chart = px.bar(
            region, x="Region", y="Total_Sales", color="Region", text="Total_Sales",
            color_discrete_sequence=COLORS, title="Sales by Region",
            labels={"Total_Sales": "Sales ($)"}
        )
        region_chart.update_traces(texttemplate="$%{y:,.2s}", textposition="outside", cliponaxis=False)
        region_chart.update_layout(template="plotly_white", height=300, showlegend=False,
                                   margin=dict(t=45, b=5, l=5, r=5), yaxis=dict(gridcolor="#E5E7EB"))
        st.plotly_chart(region_chart, use_container_width=True, config={"displayModeBar": False})
    st.caption("Use the tabs above to switch between chart groups. Filters apply to every tab.")

with tab_products:
    p1, p2 = st.columns(2)
    with p1:
        product_profit = px.bar(
            subcategory, x="Total_Profit", y="Sub-Category", orientation="h",
            color="Total_Profit",
            color_continuous_scale=["#D62728", "#F4C7C3", "#FEE08B", "#A6D96A", "#16803C"],
            title="Profit and Loss by Sub-category",
            labels={"Total_Profit": "Profit ($)"}
        )
        product_profit.add_vline(x=0, line_dash="dash", line_color="#374151")
        product_profit.update_layout(template="plotly_white", height=430, margin=dict(t=45, b=5, l=5, r=5))
        st.plotly_chart(product_profit, use_container_width=True, config={"displayModeBar": False})
    with p2:
        cat_profit = px.bar(
            category.sort_values("Total_Profit", ascending=False), x="Category", y="Total_Profit",
            color="Category", text="Total_Profit", color_discrete_sequence=COLORS,
            title="Total Profit by Category", labels={"Total_Profit": "Profit ($)"}
        )
        cat_profit.update_traces(texttemplate="$%{y:,.2s}", textposition="outside", cliponaxis=False)
        cat_profit.update_layout(template="plotly_white", height=430, showlegend=False,
                                 margin=dict(t=45, b=5, l=5, r=5), yaxis=dict(gridcolor="#E5E7EB"))
        st.plotly_chart(cat_profit, use_container_width=True, config={"displayModeBar": False})
    st.caption("Losses appear below zero. Review pricing, discounts and costs before changing product strategy.")

with tab_customers:
    c1, c2 = st.columns(2)
    with c1:
        seg_chart = px.bar(
            segment, x="Segment", y="Total_Sales", color="Segment", text="Total_Sales",
            color_discrete_sequence=COLORS, title="Sales by Customer Segment",
            labels={"Total_Sales": "Sales ($)"}
        )
        seg_chart.update_traces(texttemplate="$%{y:,.2s}", textposition="outside", cliponaxis=False)
        seg_chart.update_layout(template="plotly_white", height=330, showlegend=False,
                                margin=dict(t=45, b=5, l=5, r=5), yaxis=dict(gridcolor="#E5E7EB"))
        st.plotly_chart(seg_chart, use_container_width=True, config={"displayModeBar": False})
    with c2:
        scatter = px.scatter(
            category, x="Total_Sales", y="Total_Profit", size="Quantity", color="Category",
            text="Category", color_discrete_sequence=COLORS, title="Sales vs Profit by Category",
            labels={"Total_Sales": "Sales ($)", "Total_Profit": "Profit ($)"}
        )
        scatter.add_hline(y=0, line_dash="dash", line_color="#D62728")
        scatter.update_traces(textposition="top center")
        scatter.update_layout(template="plotly_white", height=330, margin=dict(t=45, b=5, l=5, r=5))
        st.plotly_chart(scatter, use_container_width=True, config={"displayModeBar": False})

    st.markdown("**Discount and profit comparison**")
    discount["Discount Band"] = discount["Discount Band"].astype(str)
    discount_chart = px.line(
        discount, x="Discount Band", y="Total_Profit", markers=True,
        custom_data=["Total_Sales", "Records"], title="Total Profit by Discount Band",
        labels={"Discount Band": "Discount range", "Total_Profit": "Profit ($)"}
    )
    discount_chart.add_hline(y=0, line_dash="dash", line_color="#D62728")
    discount_chart.update_traces(
        line=dict(color=BLUE, width=3), marker=dict(size=8, color=ORANGE),
        hovertemplate="Band: %{x}<br>Profit: $%{y:,.2f}<br>Sales: $%{customdata[0]:,.2f}<br>Records: %{customdata[1]}<extra></extra>"
    )
    discount_chart.update_layout(template="plotly_white", height=280, margin=dict(t=45, b=5, l=5, r=5))
    st.plotly_chart(discount_chart, use_container_width=True, config={"displayModeBar": False})
    st.caption("Discount bands are not time periods. This comparison shows association, not proof of causation.")

with tab_insights:
    st.subheader("Business insights for the current filters")
    best_sales = category.loc[category["Total_Sales"].idxmax()]
    best_profit = category.loc[category["Total_Profit"].idxmax()]
    best_region = region.loc[region["Total_Sales"].idxmax()]
    st.markdown(
        f"**Sales leader:** {best_sales['Category']} — ${best_sales['Total_Sales']:,.2f} in sales."
    )
    st.markdown(
        f"**Profit leader:** {best_profit['Category']} — ${best_profit['Total_Profit']:,.2f} in profit."
    )
    st.markdown(
        f"**Regional leader:** {best_region['Region']} — ${best_region['Total_Sales']:,.2f} in sales."
    )
    losses = subcategory[subcategory["Total_Profit"] < 0]
    if not losses.empty:
        worst = losses.iloc[0]
        st.warning(
            f"**Needs review:** {worst['Sub-Category']} has a total loss of "
            f"${abs(worst['Total_Profit']):,.2f}. Check pricing, discount levels and costs."
        )
    else:
        st.success("No loss-making sub-categories appear in the current filtered selection.")
    st.markdown("**Recommended actions**")
    st.markdown(
        "- Compare sales and profit together before allocating resources.\n"
        "- Review loss-making sub-categories and their discount patterns.\n"
        "- Investigate why stronger regions perform well before copying their approach.\n"
        "- Treat these findings as signals to investigate, not proof of cause."
    )

with tab_data:
    st.download_button(
        "⬇️ Download filtered records (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="filtered_sales_data.csv",
        mime="text/csv"
    )
    data_view = st.selectbox(
        "Choose a summary table",
        ["Category", "Sub-category", "Region", "Customer segment", "Filtered records"]
    )
    tables = {
        "Category": category.round(2),
        "Sub-category": subcategory.round(2),
        "Region": region.round(2),
        "Customer segment": segment.round(2),
        "Filtered records": filtered
    }
    st.dataframe(tables[data_view], use_container_width=True, hide_index=True, height=350)

st.caption(
    "Future Interns • Task 1 | Recorded fields are used for conclusions. "
    "Synthetic dates and unverified product names are not used."
)
