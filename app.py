import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import analysis functions
from src.analysis import (
    load_data,
    get_funnel_summary,
    get_channel_performance,
    get_campaign_performance,
    get_category_performance,
    get_brand_performance,
    get_daily_trends,
    generate_insights_and_recommendations
)

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="Growth Analytics: Funnel & Acquisition Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, premium look and style
st.markdown("""
<style>
    /* Metric Card Styling */
    .metric-box {
        background-color: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
    }
    .metric-box-title {
        color: #94A3B8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .metric-box-value {
        color: #F8FAFC;
        font-size: 2rem;
        font-weight: 700;
    }
    .metric-box-delta {
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 5px;
    }
    .delta-positive { color: #10B981; }
    .delta-negative { color: #EF4444; }
    
    /* Recommendation Card Styling */
    .rec-card {
        border-left: 5px solid #3B82F6;
        background-color: rgba(59, 130, 246, 0.05);
        padding: 18px;
        border-radius: 4px 12px 12px 4px;
        margin-bottom: 15px;
        border-top: 1px solid rgba(59, 130, 246, 0.1);
        border-right: 1px solid rgba(59, 130, 246, 0.1);
        border-bottom: 1px solid rgba(59, 130, 246, 0.1);
    }
    .rec-high { border-left-color: #EF4444; background-color: rgba(239, 68, 68, 0.04); }
    .rec-medium { border-left-color: #F59E0B; background-color: rgba(245, 158, 11, 0.04); }
    
    .rec-title {
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 6px;
    }
    .rec-priority {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    .pri-high { background-color: rgba(239, 68, 68, 0.2); color: #FCA5A5; }
    .pri-medium { background-color: rgba(245, 158, 11, 0.2); color: #FDE047; }
    .pri-low { background-color: rgba(59, 130, 246, 0.2); color: #93C5FD; }
</style>
""", unsafe_allow_html=True)

# ----------------- LOAD & FILTER DATA -----------------
@st.cache_data
def get_clean_data():
    try:
        return load_data()
    except Exception as e:
        st.error(f"Error loading CSV data: {e}")
        # Try generating sample data if missing
        from src.generate_data import generate_funnel_data
        return generate_funnel_data("data/ecommerce_events.csv")

df_raw = get_clean_data()

# Sidebar title
st.sidebar.image("https://img.icons8.com/nolan/96/combo-chart.png", width=70)
st.sidebar.title("Funnel Filters")
st.sidebar.markdown("---")

# 1. Date filter
min_date = df_raw["event_time"].min().date()
max_date = df_raw["event_time"].max().date()
start_date, end_date = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# 2. Channel filter
df_raw["channel"] = df_raw["utm_source"] + " / " + df_raw["utm_medium"]
available_channels = sorted(df_raw["channel"].unique())
selected_channels = st.sidebar.multiselect(
    "Acquisition Channels",
    options=available_channels,
    default=available_channels
)

# 3. Product category filter
df_raw["main_category"] = df_raw["category_code"].fillna("unassigned").apply(lambda x: x.split(".")[0])
available_categories = sorted(df_raw["main_category"].unique())
selected_categories = st.sidebar.multiselect(
    "Product Categories",
    options=available_categories,
    default=available_categories
)

# Apply filters
df_filtered = df_raw[
    (df_raw["event_time"].dt.date >= start_date) &
    (df_raw["event_time"].dt.date <= end_date) &
    (df_raw["channel"].isin(selected_channels)) &
    (df_raw["main_category"].isin(selected_categories))
]

# Ensure we have data remaining after filters
if df_filtered.empty:
    st.warning("⚠️ No data available for the selected filters. Please adjust your filters in the sidebar.")
    st.stop()

# ----------------- CALCULATE METRICS -----------------
funnel_summary, metrics = get_funnel_summary(df_filtered)
channel_perf = get_channel_performance(df_filtered)
campaign_perf = get_campaign_performance(df_filtered)
category_perf = get_category_performance(df_filtered)
brand_perf = get_brand_performance(df_filtered)
daily_trends = get_daily_trends(df_filtered)
insights, recommendations = generate_insights_and_recommendations(df_filtered)

# ----------------- MAIN PAGE HEADER -----------------
st.title("📈 E-Commerce Marketing & Lead Funnel Dashboard")
st.markdown("Analyze how users progress from initial page views to product additions and successful purchases.")
st.markdown("---")

# ----------------- KEY PERFORMANCE INDICATORS (KPIs) -----------------
kpi_cols = st.columns(5)

# Calculate some baseline benchmarks for deltas (relative to overall average or synthetic targets)
with kpi_cols[0]:
    st.markdown(
        f'<div class="metric-box">'
        f'<div class="metric-box-title">Total Sessions</div>'
        f'<div class="metric-box-value">{metrics["unique_sessions"]:,}</div>'
        f'<div class="metric-box-delta delta-positive">👤 {metrics["unique_buyers"]:,} Buyers</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with kpi_cols[1]:
    st.markdown(
        f'<div class="metric-box">'
        f'<div class="metric-box-title">Overall Conversion Rate</div>'
        f'<div class="metric-box-value">{round(metrics["overall_cr"] * 100, 2)}%</div>'
        f'<div class="metric-box-delta delta-positive">🎯 Benchmark: 1.5% - 2.5%</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with kpi_cols[2]:
    st.markdown(
        f'<div class="metric-box">'
        f'<div class="metric-box-title">Total Revenue</div>'
        f'<div class="metric-box-value">${round(metrics["total_revenue"], 2):,}</div>'
        f'<div class="metric-box-delta delta-positive">💰 Gross Merchandise Value</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with kpi_cols[3]:
    st.markdown(
        f'<div class="metric-box">'
        f'<div class="metric-box-title">Average Order Value (AOV)</div>'
        f'<div class="metric-box-value">${round(metrics["aov"], 2):,}</div>'
        f'<div class="metric-box-delta delta-positive">🛒 Basket Size</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with kpi_cols[4]:
    st.markdown(
        f'<div class="metric-box">'
        f'<div class="metric-box-title">Cart Abandonment Rate</div>'
        f'<div class="metric-box-value">{round(metrics["cart_abandonment_rate"] * 100, 2)}%</div>'
        f'<div class="metric-box-delta delta-negative">🚪 {round(metrics["cart_abandonment_rate"] * 100, 1)}% Drop-off</div>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ----------------- TABS SYSTEM -----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Core Funnel Analysis", 
    "📣 Marketing & Acquisition Channels", 
    "🏷️ Segment & Brand Analysis", 
    "💡 Strategic Growth Recommendations"
])

# ----------------- TAB 1: CORE FUNNEL ANALYSIS -----------------
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Core Funnel Journey")
        st.markdown("This chart visualizes user progression from viewing a product page to adding items to a cart, and finally completing a transaction.")
        
        # Plotly Funnel Chart
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_summary["Stage"],
            x=funnel_summary["Sessions"],
            textinfo="value+percent initial+percent previous",
            marker={"color": ["#1E3A8A", "#2563EB", "#10B981"]},
            connector={"fillcolor": "rgba(226, 232, 240, 0.2)"}
        ))
        
        fig_funnel.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=20),
            height=380
        )
        st.plotly_chart(fig_funnel, use_container_width=True)
        
    with col2:
        st.subheader("Stage-by-Stage Funnel Table")
        st.markdown("Detailed breakdown of unique session counts, conversion rates from base, and drop-off percentages.")
        
        # Format the table beautifully
        display_funnel = funnel_summary.copy()
        display_funnel["Sessions"] = display_funnel["Sessions"].map(lambda x: f"{x:,}")
        display_funnel["Drop_off_from_previous_stage_%"] = display_funnel["Drop_off_from_previous_stage_%"].map(lambda x: f"{x}%")
        display_funnel["Conversion_Rate_from_view_%"] = display_funnel["Conversion_Rate_from_view_%"].map(lambda x: f"{x}%")
        
        st.dataframe(
            display_funnel,
            hide_index=True,
            use_container_width=True
        )
        
        st.info(
            "💡 **Funnel Concept:** In marketing, a funnel represents the customer journey. "
            "A healthy funnel has a gentle slope. A steep drop-off indicates friction at that stage. "
            "For example, a low View-to-Cart rate suggests bad product details, pricing, or targeting; "
            "a low Cart-to-Purchase rate suggests checkout friction or hidden shipping fees."
        )

    st.markdown("---")
    st.subheader("Daily Conversion and Revenue Trends")
    st.markdown("Monitor how daily traffic volume relates to purchasing rates and revenue over the selected period.")
    
    # Dual-axis daily trend chart
    fig_daily = go.Figure()
    
    # Line 1: Sessions
    fig_daily.add_trace(go.Scatter(
        x=daily_trends["date"],
        y=daily_trends["Sessions"],
        name="Sessions",
        line=dict(color="#3B82F6", width=3),
        yaxis="y1"
    ))
    
    # Line 2: Revenue
    fig_daily.add_trace(go.Bar(
        x=daily_trends["date"],
        y=daily_trends["Revenue"],
        name="Revenue ($)",
        marker_color="rgba(16, 185, 129, 0.4)",
        yaxis="y2"
    ))
    
    fig_daily.update_layout(
        title="Daily Traffic and Revenue Trends",
        xaxis=dict(title="Date"),
        yaxis=dict(title=dict(text="Sessions", font=dict(color="#3B82F6")), tickfont=dict(color="#3B82F6")),
        yaxis2=dict(title=dict(text="Revenue ($)", font=dict(color="#10B981")), tickfont=dict(color="#10B981"), anchor="x", overlaying="y", side="right"),
        legend=dict(x=0.01, y=0.99),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=380
    )
    st.plotly_chart(fig_daily, use_container_width=True)

# ----------------- TAB 2: MARKETING & ACQUISITION CHANNELS -----------------
with tab2:
    st.subheader("Multi-Channel Performance Overview")
    st.markdown("Compare the volume of traffic brought by each channel against its actual conversion efficiency and generated revenue.")
    
    # 1. Performance matrix scatter/bubble chart
    # X: Sessions, Y: Conversion Rate, Bubble Size: Revenue
    fig_matrix = px.scatter(
        channel_perf,
        x="Sessions",
        y="Conversion_Rate_%",
        size="Revenue",
        color="channel",
        hover_name="channel",
        text="channel",
        size_max=50,
        title="Channel Performance Grid: Session Volume vs. Conversion Rate"
    )
    fig_matrix.update_traces(textposition='top center')
    fig_matrix.update_layout(
        xaxis_title="Sessions (Traffic Volume)",
        yaxis_title="Conversion Rate (%)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=450,
        showlegend=False
    )
    
    # Add vertical line for average conversion rate as a reference
    avg_cr = metrics["overall_cr"] * 100
    fig_matrix.add_shape(
        type="line", line=dict(dash="dash", color="rgba(255,255,255,0.4)"),
        x0=0, x1=channel_perf["Sessions"].max() * 1.1, y0=avg_cr, y1=avg_cr
    )
    
    st.plotly_chart(fig_matrix, use_container_width=True)
    
    # 2. Channels breakdown table
    st.subheader("Acquisition Channel Ledger")
    display_channels = channel_perf.copy()
    display_channels["Sessions"] = display_channels["Sessions"].map(lambda x: f"{x:,}")
    display_channels["Cart_Sessions"] = display_channels["Cart_Sessions"].map(lambda x: f"{x:,}")
    display_channels["Purchases"] = display_channels["Purchases"].map(lambda x: f"{x:,}")
    display_channels["Revenue"] = display_channels["Revenue"].map(lambda x: f"${x:,.2f}")
    display_channels["Conversion_Rate_%"] = display_channels["Conversion_Rate_%"].map(lambda x: f"{x}%")
    display_channels["Cart_Abandonment_Rate_%"] = display_channels["Cart_Abandonment_Rate_%"].map(lambda x: f"{x}%")
    display_channels["AOV"] = display_channels["AOV"].map(lambda x: f"${x:.2f}")
    display_channels["Revenue_Share_%"] = display_channels["Revenue_Share_%"].map(lambda x: f"{x}%")
    
    st.dataframe(
        display_channels,
        hide_index=True,
        use_container_width=True
    )
    
    # 3. UTM Campaigns Section
    if not campaign_perf.empty:
        st.markdown("---")
        st.subheader("UTM Marketing Campaign Analysis")
        st.markdown("Granular performance of specific marketing campaigns driving traffic.")
        
        # Campaign chart
        fig_campaign = px.bar(
            campaign_perf.head(10),
            x="utm_campaign",
            y="Revenue",
            color="Conversion_Rate_%",
            color_continuous_scale=px.colors.sequential.Viridis,
            title="Top 10 Marketing Campaigns by Revenue and Conversion Rate",
            labels={"Revenue": "Revenue ($)", "Conversion_Rate_%": "Conversion Rate (%)", "utm_campaign": "Campaign Name"}
        )
        fig_campaign.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400
        )
        st.plotly_chart(fig_campaign, use_container_width=True)

# ----------------- TAB 3: SEGMENT & BRAND ANALYSIS -----------------
with tab3:
    st.subheader("Product Category Funnels")
    st.markdown("See which product verticals attract users and which ones actually lead to checkout completions.")
    
    cat_cols = st.columns([1, 1])
    
    with cat_cols[0]:
        # Category Revenue
        fig_cat_rev = px.bar(
            category_perf,
            x="main_category",
            y="Revenue",
            color="Overall_CR_%",
            title="Revenue Generated by Product Category",
            labels={"Revenue": "Revenue ($)", "Overall_CR_%": "Conversion Rate (%)", "main_category": "Category"}
        )
        fig_cat_rev.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=380
        )
        st.plotly_chart(fig_cat_rev, use_container_width=True)
        
    with cat_cols[1]:
        # Category Funnel Conversion Rates
        fig_cat_cr = go.Figure()
        
        fig_cat_cr.add_trace(go.Bar(
            x=category_perf["main_category"],
            y=category_perf["Cart-to-Purchase_CR_%"],
            name="Cart-to-Purchase CR %",
            marker_color="#10B981"
        ))
        
        fig_cat_cr.add_trace(go.Bar(
            x=category_perf["main_category"],
            y=category_perf["Overall_CR_%"],
            name="Overall View-to-Purchase CR %",
            marker_color="#3B82F6"
        ))
        
        fig_cat_cr.update_layout(
            title="Category Conversion Rate Benchmarks",
            xaxis_title="Category",
            yaxis_title="Conversion Rate (%)",
            barmode="group",
            legend=dict(x=0.6, y=0.99),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=380
        )
        st.plotly_chart(fig_cat_cr, use_container_width=True)

    st.markdown("---")
    st.subheader("Brand Performance Matrix")
    st.markdown("Brands sorted by revenue generation, showcasing their conversion efficiency and cart abandonment issues (filtered to brands with >20 views).")
    
    # Brand Scatter
    fig_brand = px.scatter(
        brand_perf,
        x="Conversion_Rate_%",
        y="Cart_Abandonment_%",
        size="Revenue",
        color="brand",
        hover_name="brand",
        text="brand",
        size_max=40,
        title="Brand Analysis: Conversion Rate vs. Cart Abandonment Rate"
    )
    fig_brand.update_traces(textposition='top center')
    fig_brand.update_layout(
        xaxis_title="Conversion Rate (%)",
        yaxis_title="Cart Abandonment Rate (%)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=420,
        showlegend=False
    )
    st.plotly_chart(fig_brand, use_container_width=True)

# ----------------- TAB 4: STRATEGIC GROWTH RECOMMENDATIONS -----------------
with tab4:
    st.subheader("🔍 Funnel Drop-off Insights")
    st.markdown("The metrics engine scanned the dataset and flagged the following drop-off bottlenecks:")
    
    # 1. Insights list
    for ins in insights:
        status_icon = "🟢" if ins["status"] == "good" else "🟡" if ins["status"] == "warning" else "🔴"
        st.markdown(
            f"**{status_icon} {ins['area']}** — *Metric:* `{ins['metric']}`  \n"
            f"{ins['finding']}"
        )
        
    st.markdown("---")
    
    # 2. Recommendations list
    st.subheader("🚀 Actionable Recommendations for Growth")
    st.markdown("Execute the following strategies to optimize user journey flow, increase conversion rates, and boost revenue:")
    
    for idx, rec in enumerate(recommendations):
        pri_class = "rec-high" if rec["priority"] == "High" else "rec-medium"
        badge_class = "pri-high" if rec["priority"] == "High" else "pri-medium"
        
        st.markdown(
            f'<div class="rec-card {pri_class}">'
            f'<div class="rec-title">{idx+1}. {rec["area"]}</div>'
            f'<span class="rec-priority {badge_class}">{rec["priority"]} Priority</span>'
            f'<p><strong>Recommended Action:</strong> {rec["action"]}</p>'
            f'<p style="margin-bottom:0; color:#3B82F6;"><strong>Expected Impact:</strong> {rec["expected_impact"]}</p>'
            f'</div>',
            unsafe_allow_html=True
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.success(
        "📝 **Intern Note on Revenue Growth:** "
        "A 10% increase in cart-to-purchase conversion rate (e.g., from 20% to 22%) doesn't just increase sales by 2%—"
        "it means a **10% increase in total revenue** from the exact same ad spend! "
        "This is why Conversion Rate Optimization (CRO) is one of the highest ROI activities in growth marketing."
    )
