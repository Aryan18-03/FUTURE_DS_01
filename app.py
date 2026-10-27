
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Business Sales Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

# Light theme colors
BLUE = "#636EFA"
ORANGE = "#EF553B"
GREEN = "#00CC96"
PURPLE = "#AB63FA"

# --------------------------------------------------
# 2. LOAD DATASET
# --------------------------------------------------

@st.cache_data
def load_data():
    data = pd.read_csv("SampleSuperstore.csv")

    # Convert important numeric columns to numeric format
    numeric_columns = ["Sales", "Profit", "Quantity", "Discount"]

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # Keep rows with valid values for core analysis
    data = data.dropna(
        subset=[
            "Sales",
            "Profit",
            "Quantity",
            "Category",
            "Sub-Category",
            "Region",
            "Segment"
        ]
    )

    return data


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "SampleSuperstore.csv was not found. "
        "Place it in the same folder as app.py."
    )
    st.stop()

if df.empty:
    st.error("The dataset contains no usable records.")
    st.stop()

# --------------------------------------------------
# 3. DASHBOARD HEADER
# --------------------------------------------------

st.title("📊 Business Sales Performance Dashboard")

st.markdown(
    """
    Explore business sales, profitability, product categories,
    regional performance, and customer segments.
    """
)

st.caption(
    "Future Interns | Task 1: Business Sales Performance Analytics"
)

st.divider()

# --------------------------------------------------
# 4. SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.title("Dashboard Filters")
st.sidebar.caption("Select options to explore the data.")

region_options = sorted(df["Region"].dropna().unique())
category_options = sorted(df["Category"].dropna().unique())
segment_options = sorted(df["Segment"].dropna().unique())

selected_regions = st.sidebar.multiselect(
    "Select Region",
    options=region_options,
    default=region_options
)

selected_categories = st.sidebar.multiselect(
    "Select Category",
    options=category_options,
    default=category_options
)

selected_segments = st.sidebar.multiselect(
    "Select Customer Segment",
    options=segment_options,
    default=segment_options
)

# --------------------------------------------------
# 5. APPLY FILTERS
# --------------------------------------------------

filtered_df = df[
    df["Region"].isin(selected_regions)
    & df["Category"].isin(selected_categories)
    & df["Segment"].isin(selected_segments)
].copy()

if filtered_df.empty:
    st.warning(
        "No records match these filters. "
        "Please select different options."
    )
    st.stop()

# --------------------------------------------------
# 6. CALCULATE KPIs
# --------------------------------------------------

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_quantity = filtered_df["Quantity"].sum()

profit_margin = (
    (total_profit / total_sales) * 100
    if total_sales != 0
    else 0
)

# --------------------------------------------------
# 7. DISPLAY KPI CARDS
# --------------------------------------------------

st.subheader("Business Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Sales",
    f"${total_sales:,.2f}"
)

col2.metric(
    "Total Profit",
    f"${total_profit:,.2f}"
)

col3.metric(
    "Quantity Sold",
    f"{total_quantity:,.0f}"
)

col4.metric(
    "Profit Margin",
    f"{profit_margin:.2f}%"
)

st.caption(
    "All KPI values update when you change the filters."
)

st.divider()

# --------------------------------------------------
# 8. CHART 1: SALES BY CATEGORY
# --------------------------------------------------

st.subheader("1. Total Sales by Product Category")

category_sales = (
    filtered_df.groupby("Category", as_index=False)
    .agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum")
    )
    .sort_values("Total_Sales", ascending=False)
)

fig1 = px.bar(
    category_sales,
    x="Category",
    y="Total_Sales",
    color="Category",
    text="Total_Sales",
    hover_data=["Total_Profit"],
    title="Total Sales by Product Category",
    labels={
        "Category": "Product Category",
        "Total_Sales": "Total Sales ($)",
        "Total_Profit": "Total Profit ($)"
    },
    color_discrete_map={
        "Technology": BLUE,
        "Furniture": ORANGE,
        "Office Supplies": GREEN
    }
)

fig1.update_traces(
    texttemplate="$%{y:,.2s}",
    textposition="outside",
    cliponaxis=False
)

fig1.update_layout(
    template="plotly_white",
    showlegend=False,
    title_x=0.5,
    yaxis=dict(gridcolor="#E5E7EB"),
    margin=dict(t=70, b=40)
)

st.plotly_chart(fig1, use_container_width=True)

# --------------------------------------------------
# 9. CHART 2: PROFIT BY SUB-CATEGORY
# --------------------------------------------------

st.subheader("2. Profit and Loss by Sub-Category")

subcategory_profit = (
    filtered_df.groupby("Sub-Category", as_index=False)
    .agg(
        Total_Profit=("Profit", "sum"),
        Total_Sales=("Sales", "sum"),
        Total_Quantity=("Quantity", "sum")
    )
    .sort_values("Total_Profit", ascending=True)
)

fig2 = px.bar(
    subcategory_profit,
    x="Total_Profit",
    y="Sub-Category",
    orientation="h",
    color="Total_Profit",
    color_continuous_scale=[
        "#D62728",
        "#F4C7C3",
        "#FEE08B",
        "#A6D96A",
        "#16803C"
    ],
    hover_data=["Total_Sales", "Total_Quantity"],
    title="Profit and Loss by Sub-Category",
    labels={
        "Total_Profit": "Total Profit ($)",
        "Sub-Category": "Product Sub-Category",
        "Total_Sales": "Total Sales ($)",
        "Total_Quantity": "Quantity Sold"
    }
)

fig2.add_vline(
    x=0,
    line_dash="dash",
    line_color="#374151"
)

fig2.update_layout(
    template="plotly_white",
    title_x=0.5,
    height=650,
    coloraxis_colorbar_title="Profit ($)",
    xaxis=dict(gridcolor="#E5E7EB")
)

st.plotly_chart(fig2, use_container_width=True)

# --------------------------------------------------
# 10. CHART 3: SALES BY REGION
# --------------------------------------------------

st.subheader("3. Total Sales by Region")

region_summary = (
    filtered_df.groupby("Region", as_index=False)
    .agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum")
    )
    .sort_values("Total_Sales", ascending=False)
)

fig3 = px.bar(
    region_summary,
    x="Region",
    y="Total_Sales",
    color="Region",
    text="Total_Sales",
    hover_data=["Total_Profit"],
    title="Total Sales by Region",
    labels={
        "Region": "Region",
        "Total_Sales": "Total Sales ($)",
        "Total_Profit": "Total Profit ($)"
    },
    color_discrete_sequence=[
        BLUE, ORANGE, GREEN, PURPLE
    ]
)

fig3.update_traces(
    texttemplate="$%{y:,.2s}",
    textposition="outside",
    cliponaxis=False
)

fig3.update_layout(
    template="plotly_white",
    showlegend=False,
    title_x=0.5,
    yaxis=dict(gridcolor="#E5E7EB")
)

st.plotly_chart(fig3, use_container_width=True)

# --------------------------------------------------
# 11. CHART 4: PROFIT BY CATEGORY
# --------------------------------------------------

st.subheader("4. Total Profit by Product Category")

profit_category = (
    filtered_df.groupby("Category", as_index=False)
    .agg(
        Total_Profit=("Profit", "sum"),
        Total_Sales=("Sales", "sum")
    )
    .sort_values("Total_Profit", ascending=False)
)

fig4 = px.bar(
    profit_category,
    x="Category",
    y="Total_Profit",
    color="Category",
    text="Total_Profit",
    hover_data=["Total_Sales"],
    title="Total Profit by Product Category",
    labels={
        "Category": "Product Category",
        "Total_Profit": "Total Profit ($)",
        "Total_Sales": "Total Sales ($)"
    },
    color_discrete_map={
        "Technology": BLUE,
        "Furniture": GREEN,
        "Office Supplies": ORANGE
    }
)

fig4.update_traces(
    texttemplate="$%{y:,.2s}",
    textposition="outside",
    cliponaxis=False
)

fig4.update_layout(
    template="plotly_white",
    showlegend=False,
    title_x=0.5,
    yaxis=dict(gridcolor="#E5E7EB")
)

st.plotly_chart(fig4, use_container_width=True)

# --------------------------------------------------
# 12. CHART 5: SALES BY CUSTOMER SEGMENT
# --------------------------------------------------

st.subheader("5. Total Sales by Customer Segment")

segment_summary = (
    filtered_df.groupby("Segment", as_index=False)
    .agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Total_Quantity=("Quantity", "sum")
    )
    .sort_values("Total_Sales", ascending=False)
)

fig5 = px.bar(
    segment_summary,
    x="Segment",
    y="Total_Sales",
    color="Segment",
    text="Total_Sales",
    hover_data=["Total_Profit", "Total_Quantity"],
    title="Total Sales by Customer Segment",
    labels={
        "Segment": "Customer Segment",
        "Total_Sales": "Total Sales ($)",
        "Total_Profit": "Total Profit ($)",
        "Total_Quantity": "Quantity Sold"
    },
    color_discrete_sequence=[
        BLUE, ORANGE, GREEN
    ]
)

fig5.update_traces(
    texttemplate="$%{y:,.2s}",
    textposition="outside",
    cliponaxis=False
)

fig5.update_layout(
    template="plotly_white",
    showlegend=False,
    title_x=0.5,
    yaxis=dict(gridcolor="#E5E7EB")
)

st.plotly_chart(fig5, use_container_width=True)

# --------------------------------------------------
# 13. AUTOMATIC BUSINESS INSIGHTS
# --------------------------------------------------

st.divider()
st.header("💡 Business Insights and Recommendations")

# Highest sales category
if not category_sales.empty:
    best_sales_category = category_sales.loc[
        category_sales["Total_Sales"].idxmax()
    ]

    st.markdown(
        f"**Sales leader:** {best_sales_category['Category']} "
        f"generates the highest sales among the selected categories, "
        f"at ${best_sales_category['Total_Sales']:,.2f}."
    )

# Highest profit category
if not profit_category.empty:
    best_profit_category = profit_category.loc[
        profit_category["Total_Profit"].idxmax()
    ]

    st.markdown(
        f"**Profit leader:** {best_profit_category['Category']} "
        f"generates the highest total profit, "
        f"at ${best_profit_category['Total_Profit']:,.2f}."
    )

# Lowest profit sub-category
if not subcategory_profit.empty:
    lowest_profit = subcategory_profit.iloc[0]

    if lowest_profit["Total_Profit"] < 0:
        st.markdown(
            f"**Area needing attention:** "
            f"{lowest_profit['Sub-Category']} records a loss of "
            f"${abs(lowest_profit['Total_Profit']):,.2f}. "
            "Investigate discounts, pricing, and costs."
        )
    else:
        st.markdown(
            f"**Lowest-profit sub-category:** "
            f"{lowest_profit['Sub-Category']} generates the lowest "
            f"profit among the selected sub-categories."
        )

# Regional sales leader
if not region_summary.empty:
    best_region = region_summary.loc[
        region_summary["Total_Sales"].idxmax()
    ]

    st.markdown(
        f"**Regional leader:** {best_region['Region']} "
        f"has the highest sales among the selected regions, "
        f"at ${best_region['Total_Sales']:,.2f}."
    )

st.markdown("### Recommended actions")

st.markdown(
    """
    - Review loss-making sub-categories and investigate their costs,
      discounts, and pricing.
    - Compare profit alongside sales before deciding where to focus
      sales and marketing resources.
    - Study high-performing categories to identify opportunities
      for sustainable growth.
    - Compare regional performance and customer segments to identify
      areas that may benefit from further investigation.
    """
)

# --------------------------------------------------
# 14. DATA TABLES
# --------------------------------------------------

with st.expander("View category performance data"):
    st.dataframe(
        category_sales.round(2),
        use_container_width=True,
        hide_index=True
    )

with st.expander("View sub-category performance data"):
    st.dataframe(
        subcategory_profit.round(2),
        use_container_width=True,
        hide_index=True
    )

with st.expander("View regional performance data"):
    st.dataframe(
        region_summary.round(2),
        use_container_width=True,
        hide_index=True
    )

with st.expander("View filtered dataset"):
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# 15. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Future Interns | Task 1: Business Sales Performance Analytics"
)

st.caption(
    "Analysis uses recorded sales, profit, quantity, category, "
    "region, and segment fields. Added synthetic dates and "
    "unverified product names are not used for business conclusions."
)
