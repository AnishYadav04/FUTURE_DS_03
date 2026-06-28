import pandas as pd
import numpy as np

def load_data(filepath="data/ecommerce_events.csv"):
    """Loads the eCommerce events CSV and parses timestamps."""
    df = pd.read_csv(filepath)
    df["event_time"] = pd.to_datetime(df["event_time"])
    return df

def get_funnel_summary(df):
    """
    Computes unique sessions and conversion rates for the core funnel stages:
    view -> cart -> purchase.
    """
    # Count unique sessions per event type
    summary = df.groupby("event_type")["user_session"].nunique().to_dict()
    
    stages = ["view", "cart", "purchase"]
    counts = [summary.get(stage, 0) for stage in stages]
    
    # Calculate conversion rates
    view_count = counts[0]
    cart_count = counts[1]
    purchase_count = counts[2]
    
    view_to_cart_cr = cart_count / view_count if view_count > 0 else 0
    cart_to_purchase_cr = purchase_count / cart_count if cart_count > 0 else 0
    overall_cr = purchase_count / view_count if view_count > 0 else 0
    cart_abandonment = 1 - cart_to_purchase_cr if cart_count > 0 else 0
    
    funnel_df = pd.DataFrame({
        "Stage": ["1. View (Browsing)", "2. Cart (Intent)", "3. Purchase (Conversion)"],
        "Sessions": counts,
        "Drop_off_from_previous_stage_%": [
            0.0, 
            round((1 - view_to_cart_cr) * 100, 2), 
            round((1 - cart_to_purchase_cr) * 100, 2)
        ],
        "Conversion_Rate_from_view_%": [
            100.0, 
            round(view_to_cart_cr * 100, 2), 
            round(overall_cr * 100, 2)
        ]
    })
    
    metrics = {
        "total_views": df[df["event_type"] == "view"].shape[0],
        "total_carts": df[df["event_type"] == "cart"].shape[0],
        "total_purchases": df[df["event_type"] == "purchase"].shape[0],
        "unique_sessions": df["user_session"].nunique(),
        "unique_buyers": df[df["event_type"] == "purchase"]["user_id"].nunique(),
        "total_revenue": df[df["event_type"] == "purchase"]["price"].sum(),
        "view_to_cart_cr": view_to_cart_cr,
        "cart_to_purchase_cr": cart_to_purchase_cr,
        "overall_cr": overall_cr,
        "cart_abandonment_rate": cart_abandonment,
        "aov": df[df["event_type"] == "purchase"]["price"].mean() if purchase_count > 0 else 0
    }
    
    return funnel_df, metrics

def get_channel_performance(df):
    """
    Analyzes funnel conversion and financial metrics segmented by marketing channel (source/medium).
    """
    # Create channel column
    df_copy = df.copy()
    df_copy["channel"] = df_copy["utm_source"] + " / " + df_copy["utm_medium"]
    
    # Calculate sessions per channel
    sessions = df_copy.groupby("channel")["user_session"].nunique().rename("Sessions")
    
    # Calculate cart sessions per channel
    cart_sessions = df_copy[df_copy["event_type"] == "cart"].groupby("channel")["user_session"].nunique().rename("Cart_Sessions")
    
    # Calculate purchase sessions and revenue per channel
    purchases_df = df_copy[df_copy["event_type"] == "purchase"]
    purchase_sessions = purchases_df.groupby("channel")["user_session"].nunique().rename("Purchases")
    revenue = purchases_df.groupby("channel")["price"].sum().rename("Revenue")
    
    # Combine metrics
    channel_perf = pd.concat([sessions, cart_sessions, purchase_sessions, revenue], axis=1).fillna(0)
    channel_perf["Cart_Sessions"] = channel_perf["Cart_Sessions"].astype(int)
    channel_perf["Purchases"] = channel_perf["Purchases"].astype(int)
    
    # Calculate conversion metrics
    channel_perf["Conversion_Rate_%"] = round((channel_perf["Purchases"] / channel_perf["Sessions"]) * 100, 2)
    channel_perf["Cart_Abandonment_Rate_%"] = round((1 - (channel_perf["Purchases"] / channel_perf["Cart_Sessions"].replace(0, 1))) * 100, 2)
    channel_perf.loc[channel_perf["Cart_Sessions"] == 0, "Cart_Abandonment_Rate_%"] = 0
    
    channel_perf["AOV"] = round(channel_perf["Revenue"] / channel_perf["Purchases"].replace(0, 1), 2)
    channel_perf.loc[channel_perf["Purchases"] == 0, "AOV"] = 0
    
    channel_perf["Revenue_Share_%"] = round((channel_perf["Revenue"] / channel_perf["Revenue"].sum()) * 100, 2)
    
    return channel_perf.sort_values(by="Revenue", ascending=False).reset_index()

def get_campaign_performance(df):
    """
    Analyzes performance by UTM campaign.
    """
    df_copy = df.copy()
    
    # Exclude sessions with no campaign ('none' or NaN)
    df_campaigns = df_copy[~df_copy["utm_campaign"].isin(["none", "null", None]) & df_copy["utm_campaign"].notna()]
    
    if df_campaigns.empty:
        return pd.DataFrame()
        
    sessions = df_campaigns.groupby("utm_campaign")["user_session"].nunique().rename("Sessions")
    cart_sessions = df_campaigns[df_campaigns["event_type"] == "cart"].groupby("utm_campaign")["user_session"].nunique().rename("Cart_Sessions")
    
    purchases_df = df_campaigns[df_campaigns["event_type"] == "purchase"]
    purchase_sessions = purchases_df.groupby("utm_campaign")["user_session"].nunique().rename("Purchases")
    revenue = purchases_df.groupby("utm_campaign")["price"].sum().rename("Revenue")
    
    campaign_perf = pd.concat([sessions, cart_sessions, purchase_sessions, revenue], axis=1).fillna(0)
    campaign_perf["Cart_Sessions"] = campaign_perf["Cart_Sessions"].astype(int)
    campaign_perf["Purchases"] = campaign_perf["Purchases"].astype(int)
    
    campaign_perf["Conversion_Rate_%"] = round((campaign_perf["Purchases"] / campaign_perf["Sessions"]) * 100, 2)
    campaign_perf["AOV"] = round(campaign_perf["Revenue"] / campaign_perf["Purchases"].replace(0, 1), 2)
    campaign_perf.loc[campaign_perf["Purchases"] == 0, "AOV"] = 0
    
    return campaign_perf.sort_values(by="Revenue", ascending=False).reset_index()

def get_category_performance(df):
    """
    Analyzes products at the category level (split by the first hierarchy node).
    """
    df_copy = df.copy()
    # Extract main category (e.g. electronics from electronics.smartphone)
    df_copy["main_category"] = df_copy["category_code"].fillna("unassigned").apply(lambda x: x.split(".")[0])
    
    views = df_copy[df_copy["event_type"] == "view"].groupby("main_category")["user_session"].nunique().rename("Views (Sessions)")
    carts = df_copy[df_copy["event_type"] == "cart"].groupby("main_category")["user_session"].nunique().rename("Carts (Sessions)")
    
    purchases_df = df_copy[df_copy["event_type"] == "purchase"]
    purchases = purchases_df.groupby("main_category")["user_session"].nunique().rename("Purchases")
    revenue = purchases_df.groupby("main_category")["price"].sum().rename("Revenue")
    
    category_perf = pd.concat([views, carts, purchases, revenue], axis=1).fillna(0).astype({
        "Views (Sessions)": int, "Carts (Sessions)": int, "Purchases": int
    })
    
    category_perf["Cart-to-Purchase_CR_%"] = round((category_perf["Purchases"] / category_perf["Carts (Sessions)"].replace(0, 1)) * 100, 2)
    category_perf["Overall_CR_%"] = round((category_perf["Purchases"] / category_perf["Views (Sessions)"].replace(0, 1)) * 100, 2)
    
    return category_perf.sort_values(by="Revenue", ascending=False).reset_index()

def get_brand_performance(df):
    """
    Analyzes brands by revenue, conversion, and cart abandonments.
    """
    df_copy = df[df["brand"].notna()].copy()
    
    views = df_copy[df_copy["event_type"] == "view"].groupby("brand")["user_session"].nunique().rename("Views")
    carts = df_copy[df_copy["event_type"] == "cart"].groupby("brand")["user_session"].nunique().rename("Carts")
    
    purchases_df = df_copy[df_copy["event_type"] == "purchase"]
    purchases = purchases_df.groupby("brand")["user_session"].nunique().rename("Purchases")
    revenue = purchases_df.groupby("brand")["price"].sum().rename("Revenue")
    
    brand_perf = pd.concat([views, carts, purchases, revenue], axis=1).fillna(0).astype({
        "Views": int, "Carts": int, "Purchases": int
    })
    
    brand_perf["Conversion_Rate_%"] = round((brand_perf["Purchases"] / brand_perf["Views"].replace(0, 1)) * 100, 2)
    brand_perf["Cart_Abandonment_%"] = round((1 - (brand_perf["Purchases"] / brand_perf["Carts"].replace(0, 1))) * 100, 2)
    brand_perf.loc[brand_perf["Carts"] == 0, "Cart_Abandonment_%"] = 0
    
    # Filter to brands with at least 50 views to avoid tiny sample sizes
    brand_perf = brand_perf[brand_perf["Views"] >= 20]
    
    return brand_perf.sort_values(by="Revenue", ascending=False).reset_index()

def get_daily_trends(df):
    """
    Computes daily traffic, conversions, and revenue trends.
    """
    df_copy = df.copy()
    # Extract date
    df_copy["date"] = df_copy["event_time"].dt.date
    
    daily_sessions = df_copy.groupby("date")["user_session"].nunique().rename("Sessions")
    
    purchases_df = df_copy[df_copy["event_type"] == "purchase"]
    daily_purchases = purchases_df.groupby("date")["user_session"].nunique().rename("Purchases")
    daily_revenue = purchases_df.groupby("date")["price"].sum().rename("Revenue")
    
    daily_trends = pd.concat([daily_sessions, daily_purchases, daily_revenue], axis=1).fillna(0)
    daily_trends["Purchases"] = daily_trends["Purchases"].astype(int)
    daily_trends["Conversion_Rate_%"] = round((daily_trends["Purchases"] / daily_trends["Sessions"]) * 100, 2)
    
    return daily_trends.reset_index()

def generate_insights_and_recommendations(df):
    """
    Algorithmic insights engine that scans data and generates specific recommendations.
    """
    _, metrics = get_funnel_summary(df)
    channel_perf = get_channel_performance(df)
    category_perf = get_category_performance(df)
    
    insights = []
    recommendations = []
    
    # 1. Cart Abandonment Insight
    cart_abandonment = metrics["cart_abandonment_rate"]
    insights.append({
        "area": "Cart Abandonment",
        "metric": f"{round(cart_abandonment * 100, 1)}%",
        "status": "warning" if cart_abandonment > 0.70 else "good",
        "finding": f"The cart abandonment rate is {round(cart_abandonment * 100, 1)}%. Out of every 10 users who add items to their cart, only {round((1-cart_abandonment)*10, 1)} complete the purchase."
    })
    
    if cart_abandonment > 0.75:
        recommendations.append({
            "area": "Checkout Flow Optimization",
            "priority": "High",
            "action": "Implement a 1-click checkout option and resolve friction in checkout. Streamline form fields, add trust badges, and display clear shipping fees before the final step.",
            "expected_impact": "Reducing abandonment by 10% would increase overall conversion rate and reclaim significant lost revenue."
        })
        recommendations.append({
            "area": "Abandoned Cart Recovery Email/SMS",
            "priority": "High",
            "action": "Set up automated retargeting emails at 1 hour, 24 hours, and 48 hours post-abandonment, offering a 10% discount or free shipping in the final reminder.",
            "expected_impact": "Typically recovers 8% - 15% of abandoned carts."
        })

    # 2. Channel Performance Analysis
    # Find channels with high traffic but low conversion rate
    for _, row in channel_perf.iterrows():
        channel = row["channel"]
        sessions = row["Sessions"]
        cr = row["Conversion_Rate_%"]
        
        # High traffic (>10% of total sessions) but low CR (<1.5%)
        if sessions > (metrics["unique_sessions"] * 0.10) and cr < 1.5:
            insights.append({
                "area": f"Channel Efficiency: {channel}",
                "metric": f"{cr}% CR",
                "status": "danger",
                "finding": f"The '{channel}' channel brings high traffic volume ({sessions} sessions) but has a very low conversion rate of {cr}%. This indicates low traffic quality or landing page mismatch."
            })
            recommendations.append({
                "area": f"Paid Acquisition Audit: {channel}",
                "priority": "Medium",
                "action": f"Review targeting settings, keywords, and creative assets for '{channel}'. Exclude low-intent keywords, adjust audience demographics, and align landing page content with ad copy.",
                "expected_impact": "Saves wasted marketing spend (ad-spend efficiency) or increases conversion rates."
            })
            
    # Find highest performing channel
    best_channel = channel_perf.iloc[0] # Sorted by Revenue
    insights.append({
        "area": f"Top Revenue Channel",
        "metric": f"${round(best_channel['Revenue'], 2):,}",
        "status": "success",
        "finding": f"'{best_channel['channel']}' is the top revenue-generating channel, bringing in ${best_channel['Revenue']:,} ({best_channel['Revenue_Share_%']}% of total revenue) with a conversion rate of {best_channel['Conversion_Rate_%']}%."
    })
    
    recommendations.append({
        "area": f"Scale Acquisition on {best_channel['channel']}",
        "priority": "Medium-High",
        "action": f"Allocate more budget to '{best_channel['channel']}' and run a lookalike campaign based on the highest LTV customers acquired through this channel.",
        "expected_impact": "Directly scales revenue by targeting high-converting audiences."
    })

    # 3. Product Category Bottleneck
    # Identify category with lowest cart-to-purchase conversion
    lowest_cat_row = category_perf.sort_values(by="Cart-to-Purchase_CR_%").iloc[0]
    insights.append({
        "area": f"Category Bottleneck: {lowest_cat_row['main_category']}",
        "metric": f"{lowest_cat_row['Cart-to-Purchase_CR_%']}% Cart CR",
        "status": "warning",
        "finding": f"The '{lowest_cat_row['main_category']}' category has the lowest cart-to-purchase conversion rate ({lowest_cat_row['Cart-to-Purchase_CR_%']}%). Users add items to cart but struggle to finish checkout."
    })
    
    recommendations.append({
        "area": f"Category Pricing & Shipping Review",
        "priority": "Medium",
        "action": f"Analyze price competitiveness and shipping fees for products under '{lowest_cat_row['main_category']}'. High price tags or unexpected shipping costs for heavy kitchen appliances/electronics are common purchase barriers.",
        "expected_impact": "Increases cart-to-purchase conversions for this key category."
    })
    
    return insights, recommendations
