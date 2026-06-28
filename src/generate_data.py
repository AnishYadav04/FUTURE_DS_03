import os
import random
import uuid
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_funnel_data(output_path, num_sessions=12000, start_date="2026-06-01", end_date="2026-06-28"):
    print(f"Generating synthetic funnel data to {output_path}...")
    
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    delta_days = (end_dt - start_dt).days + 1
    
    # 1. Setup Product Database
    brands = {
        "electronics.smartphone": ["apple", "samsung", "xiaomi", "huawei", "oppo"],
        "electronics.audio": ["sony", "bose", "jbl", "apple", "sennheiser"],
        "computers.notebook": ["apple", "hp", "lenovo", "dell", "asus"],
        "appliances.kitchen.refrigerator": ["samsung", "lg", "whirlpool", "bosch", "haier"],
        "apparel.shoes": ["nike", "adidas", "puma", "under_armour", "reebok"],
        "apparel.tshirt": ["nike", "adidas", "levis", "zara", "h&m"],
        "auto.accessories": ["garmin", "pioneer", "bosch", "michelin", "meguiars"]
    }
    
    category_ids = {cat: random.randint(1000000, 9999999) for cat in brands.keys()}
    
    # Pre-generate a list of products
    products = []
    product_counter = 10001
    for category, cat_brands in brands.items():
        cat_id = category_ids[category]
        for brand in cat_brands:
            # Create 3-5 products per brand in this category
            num_products = random.randint(3, 6)
            for _ in range(num_products):
                # Set price range based on category
                if "smartphone" in category:
                    price = round(random.uniform(150, 1200), 2)
                elif "notebook" in category:
                    price = round(random.uniform(400, 2200), 2)
                elif "refrigerator" in category:
                    price = round(random.uniform(300, 1800), 2)
                elif "audio" in category:
                    price = round(random.uniform(20, 400), 2)
                elif "shoes" in category:
                    price = round(random.uniform(40, 180), 2)
                elif "tshirt" in category:
                    price = round(random.uniform(15, 60), 2)
                else: # auto
                    price = round(random.uniform(10, 250), 2)
                
                products.append({
                    "product_id": product_counter,
                    "category_id": cat_id,
                    "category_code": category,
                    "brand": brand,
                    "price": price
                })
                product_counter += 1
                
    # 2. Marketing Channels Setup
    # Different channels have different traffic share, add-to-cart probability, and purchase probability
    channels = {
        "organic_search": {
            "source": "google", "medium": "organic", "campaign": "none", 
            "traffic_weight": 0.30, "view_to_cart_prob": 0.08, "cart_to_purchase_prob": 0.18
        },
        "direct": {
            "source": "direct", "medium": "none", "campaign": "none", 
            "traffic_weight": 0.15, "view_to_cart_prob": 0.12, "cart_to_purchase_prob": 0.25
        },
        "paid_search_brand": {
            "source": "google", "medium": "cpc", "campaign": "brand_search", 
            "traffic_weight": 0.10, "view_to_cart_prob": 0.15, "cart_to_purchase_prob": 0.30
        },
        "paid_search_generic": {
            "source": "google", "medium": "cpc", "campaign": "generic_categories", 
            "traffic_weight": 0.12, "view_to_cart_prob": 0.06, "cart_to_purchase_prob": 0.12
        },
        "paid_social_facebook": {
            "source": "facebook", "medium": "social", "campaign": "lookalike_audience", 
            "traffic_weight": 0.12, "view_to_cart_prob": 0.05, "cart_to_purchase_prob": 0.10
        },
        "paid_social_instagram": {
            "source": "instagram", "medium": "social", "campaign": "lifestyle_influencers", 
            "traffic_weight": 0.08, "view_to_cart_prob": 0.07, "cart_to_purchase_prob": 0.08
        },
        "retargeting_facebook": {
            "source": "facebook", "medium": "social", "campaign": "retargeting_abandoned_cart", 
            "traffic_weight": 0.04, "view_to_cart_prob": 0.22, "cart_to_purchase_prob": 0.55
        },
        "newsletter": {
            "source": "email", "medium": "newsletter", "campaign": "weekly_digest", 
            "traffic_weight": 0.06, "view_to_cart_prob": 0.14, "cart_to_purchase_prob": 0.22
        },
        "partner_referral": {
            "source": "partner_blog", "medium": "referral", "campaign": "affiliate_launch", 
            "traffic_weight": 0.03, "view_to_cart_prob": 0.18, "cart_to_purchase_prob": 0.28
        }
    }
    
    channel_names = list(channels.keys())
    channel_weights = [channels[ch]["traffic_weight"] for ch in channel_names]
    
    # 3. Generate Events
    events = []
    
    # Create ~3000 unique users
    num_users = int(num_sessions * 0.6)
    user_ids = [random.randint(500000000, 599999999) for _ in range(num_users)]
    
    # Distribute sessions across dates
    # We will simulate a mid-June sale campaign that spikes traffic and purchases
    date_weights = np.ones(delta_days)
    # Mid-June sale: June 12 to June 15
    for i in range(11, 15):
        if i < delta_days:
            date_weights[i] = 2.2  # 2.2x traffic during the campaign sale
    
    date_weights = date_weights / date_weights.sum()
    session_dates = np.random.choice(delta_days, size=num_sessions, p=date_weights)
    
    print("Generating sessions and event sequences...")
    for session_idx in range(num_sessions):
        # Determine date and time
        day_offset = int(session_dates[session_idx])
        session_date = start_dt + timedelta(days=day_offset)
        
        # Hourly distribution: peak at 10 AM to 2 PM, and 7 PM to 10 PM
        hour_probs = np.zeros(24)
        hour_probs[0:7] = 0.02
        hour_probs[7:10] = 0.05
        hour_probs[10:14] = 0.08
        hour_probs[14:18] = 0.06
        hour_probs[18:22] = 0.10
        hour_probs[22:24] = 0.04
        hour_probs = hour_probs / hour_probs.sum()
        hour = np.random.choice(24, p=hour_probs)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        session_time = session_date.replace(hour=hour, minute=minute, second=second)
        
        # Assign user and session properties
        user_id = random.choice(user_ids)
        session_id = str(uuid.uuid4())
        
        # Select marketing channel
        ch_name = np.random.choice(channel_names, p=channel_weights)
        ch_info = channels[ch_name]
        
        # User behavior modeling
        # Determine number of page views in this session (between 1 and 8)
        # Bounces (1 view only) are common
        if ch_name in ["paid_social_facebook", "paid_social_instagram"]:
            # Higher bounce rate for social
            views_in_session = random.choices([1, 2, 3, 4, 5, 6], weights=[0.55, 0.20, 0.12, 0.07, 0.04, 0.02])[0]
        else:
            views_in_session = random.choices([1, 2, 3, 4, 5, 6, 7, 8], weights=[0.30, 0.25, 0.18, 0.12, 0.07, 0.04, 0.03, 0.01])[0]
            
        current_time = session_time
        
        # Pre-select 2-3 products that this user is interested in for this session
        session_products = random.sample(products, k=min(3, len(products)))
        
        # Generate view events
        viewed_products = []
        for v in range(views_in_session):
            prod = random.choice(session_products)
            viewed_products.append(prod)
            
            events.append({
                "event_time": current_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "event_type": "view",
                "product_id": prod["product_id"],
                "category_id": prod["category_id"],
                "category_code": prod["category_code"],
                "brand": prod["brand"],
                "price": prod["price"],
                "user_id": user_id,
                "user_session": session_id,
                "utm_source": ch_info["source"],
                "utm_medium": ch_info["medium"],
                "utm_campaign": ch_info["campaign"]
            })
            # Wait 30s to 3 mins before next action
            current_time += timedelta(seconds=random.randint(30, 180))
            
        # Determine if the user adds to cart
        # Base probability from channel
        add_to_cart_prob = ch_info["view_to_cart_prob"]
        
        # Add modifier based on product price (higher price = slightly lower cart addition probability)
        # Let's say a baseline is calculated on the last viewed product
        last_prod = viewed_products[-1]
        if last_prod["price"] > 1000:
            add_to_cart_prob *= 0.6
        elif last_prod["price"] > 500:
            add_to_cart_prob *= 0.8
        elif last_prod["price"] < 50:
            add_to_cart_prob *= 1.3
            
        if random.random() < add_to_cart_prob:
            # User adds last product to cart
            events.append({
                "event_time": current_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "event_type": "cart",
                "product_id": last_prod["product_id"],
                "category_id": last_prod["category_id"],
                "category_code": last_prod["category_code"],
                "brand": last_prod["brand"],
                "price": last_prod["price"],
                "user_id": user_id,
                "user_session": session_id,
                "utm_source": ch_info["source"],
                "utm_medium": ch_info["medium"],
                "utm_campaign": ch_info["campaign"]
            })
            
            current_time += timedelta(seconds=random.randint(15, 60))
            
            # Check if user removes from cart (happens occasionally, say 10% of cart additions)
            if random.random() < 0.10:
                events.append({
                    "event_time": current_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "event_type": "remove_from_cart",
                    "product_id": last_prod["product_id"],
                    "category_id": last_prod["category_id"],
                    "category_code": last_prod["category_code"],
                    "brand": last_prod["brand"],
                    "price": last_prod["price"],
                    "user_id": user_id,
                    "user_session": session_id,
                    "utm_source": ch_info["source"],
                    "utm_medium": ch_info["medium"],
                    "utm_campaign": ch_info["campaign"]
                })
            else:
                # Determine if user purchases
                purchase_prob = ch_info["cart_to_purchase_prob"]
                
                # Brand loyalty modifiers (e.g. apple, samsung convert slightly better)
                if last_prod["brand"] in ["apple", "samsung", "nike"]:
                    purchase_prob *= 1.25
                elif last_prod["brand"] in ["oppo", "haier"]:
                    purchase_prob *= 0.85
                    
                # Price barrier modifier (expensive items get abandoned more)
                if last_prod["price"] > 800:
                    purchase_prob *= 0.7
                elif last_prod["price"] < 100:
                    purchase_prob *= 1.2
                    
                # Cap probability at 0.95
                purchase_prob = min(purchase_prob, 0.95)
                
                if random.random() < purchase_prob:
                    # Successful purchase!
                    events.append({
                        "event_time": current_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "event_type": "purchase",
                        "product_id": last_prod["product_id"],
                        "category_id": last_prod["category_id"],
                        "category_code": last_prod["category_code"],
                        "brand": last_prod["brand"],
                        "price": last_prod["price"],
                        "user_id": user_id,
                        "user_session": session_id,
                        "utm_source": ch_info["source"],
                        "utm_medium": ch_info["medium"],
                        "utm_campaign": ch_info["campaign"]
                    })

    # Convert to DataFrame, sort by event_time, and save
    df = pd.DataFrame(events)
    df["event_time"] = pd.to_datetime(df["event_time"])
    df = df.sort_values(by="event_time").reset_index(drop=True)
    
    # Format back to string UTC
    df["event_time"] = df["event_time"].dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Save directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Dataset generated. Shape: {df.shape}. Sessions generated: {num_sessions}")
    return df

if __name__ == "__main__":
    import sys
    # Allow overriding output path from command line
    out = "data/ecommerce_events.csv"
    if len(sys.argv) > 1:
        out = sys.argv[1]
    
    generate_funnel_data(out)
