# eCommerce Funnel & Marketing Acquisition Analytics Dashboard

This project is an end-to-end web analytics and growth marketing funnel dashboard built using **Python, Pandas, Plotly, and Streamlit**. It models customer behavior for a multi-category eCommerce store, segments customer journeys by marketing acquisition channel and campaign, calculates funnel conversion rates, identifies key drop-off bottlenecks, and generates data-driven recommendations.

---

## 📊 Business Context & Why This Matters

For any eCommerce startup, SaaS platform, or digital marketing agency, **improving conversion rates is the most cost-effective way to scale revenue**. 

* **The Problem:** Many businesses spend heavily on paid advertisements (Google Ads, Facebook Ads) but suffer from steep drops in their user funnel—either users land and immediately bounce, or they add items to their carts but abandon them at checkout.
* **The ROI of Funnel Optimization:** If a store receives 100,000 visitors at a 1% overall conversion rate with an Average Order Value (AOV) of $100, they make $100,000 in revenue. If you optimize the checkout funnel and increase the conversion rate to **2%** (a small 1% absolute increase), you **double the revenue to $200,000 from the exact same ad spend and traffic volume**.

This dashboard translates raw behavioral data into actionable growth strategies.

---

## ⚙️ Setup & Installation

### Prerequisites
Make sure you have **Python 3.8+** installed. You can check your version by running:
```bash
python --version
```

### Installation Steps

1. **Navigate to the Project Directory:**
   ```bash
   cd c:\ds3
   ```

2. **Install Dependencies:**
   All required packages (`pandas`, `numpy`, `plotly`, `streamlit`) are listed in `requirements.txt`. Install them using:
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate the Dataset (Optional):**
   A pre-configured, high-fidelity eCommerce event log dataset will be generated automatically when the app starts, or you can manually trigger it with:
   ```bash
   python src/generate_data.py
   ```
   This creates a file at `data/ecommerce_events.csv` (about 32,000 events across 12,000 sessions).

4. **Launch the Streamlit Dashboard:**
   Start the interactive dashboard server:
   ```bash
   streamlit run app.py
   ```

5. **Access the Dashboard:**
   Once running, Streamlit will open a tab in your default browser. If it doesn't open automatically, navigate to the local link:
   👉 **[http://localhost:8501](http://localhost:8501)**

---

## 📁 Repository Structure

```
c:\ds3\
├── requirements.txt         # Project library dependencies
├── README.md                # Project documentation and report (this file)
├── app.py                   # Main interactive Streamlit dashboard
├── data/
│   └── ecommerce_events.csv # Generated event dataset (Kaggle Schema + UTMs)
└── src/
    ├── __init__.py          # Module initializer
    ├── generate_data.py     # High-fidelity synthetic event sequence generator
    └── analysis.py          # Metrics, funnel, and recommendation engine
```

---

## 📋 Data Schema

The dataset matches the schema of the popular [Kaggle eCommerce Behavior Data from Multi-Category Store](https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store), enriched with standard web-analytics marketing acquisition attributes (UTM tags):

| Column | Data Type | Description |
| :--- | :--- | :--- |
| **event_time** | datetime / str | UTC Timestamp of the action. |
| **event_type** | category / str | The user action: `view`, `cart`, `remove_from_cart`, or `purchase`. |
| **product_id** | integer | Unique identifier for the specific product. |
| **category_id** | integer | Unique identifier for the product's category. |
| **category_code** | string | Hierarchical taxonomy code (e.g., `electronics.smartphone`). |
| **brand** | string | The brand of the product (e.g., `apple`, `samsung`, `nike`). |
| **price** | float | Price of the product in USD. |
| **user_id** | integer | Permanent, unique user identifier. |
| **user_session** | string | Temporary session identifier (resets after 30 mins of inactivity). |
| **utm_source** | string | Traffic source (e.g., `google`, `facebook`, `instagram`, `email`, `direct`). |
| **utm_medium** | string | Traffic medium (e.g., `cpc`, `social`, `newsletter`, `none`, `referral`). |
| **utm_campaign** | string | Specific ad campaign (e.g., `brand_search`, `lookalike_audience`, `retargeting_abandoned_cart`). |

---

## 📈 Marketing Funnel Insights Report

### 1. The Core Funnel Summary
A typical eCommerce user journey flows through three main phases:
$$\text{View (Product Page)} \longrightarrow \text{Cart (Add to Cart)} \longrightarrow \text{Purchase (Completed Transaction)}$$

* **View (Browsing / Awareness):** Users browsing product pages.
* **Cart (Intent / Consideration):** Adding an item to the shopping cart. Indicates purchase intent.
* **Purchase (Conversion / Action):** Checking out.

Based on the generated analysis, the overall funnel averages:
* **View-to-Cart Conversion Rate:** ~10% (Friction points: pricing, product images, page load speeds, lack of trust signals).
* **Cart-to-Purchase Conversion Rate:** ~22% (Friction points: complex forms, hidden shipping costs, lack of payment options, forcing account creation).
* **Overall E-Commerce Conversion Rate:** ~2.2% (Typical healthy eCommerce stores range from 1.5% to 3.0%).
* **Shopping Cart Abandonment Rate:** ~78% (Industry average ranges from 70% to 80%).

### 2. Marketing Channels Performance Analysis

* **High Volume, Low Quality (e.g. Paid Social):** Channels like `facebook / social` (Lookalike Audience campaign) bring a substantial amount of traffic but convert at lower rates (~0.45% - 0.75%). Users coming from social feeds are browsing and have low immediate intent.
* **High Intent, High Conversion (e.g. Paid & Organic Search):** Channels like `google / cpc` (specifically the `brand_search` campaign) convert at higher rates (~4.5% - 5.2%) and command a high Average Order Value (AOV). These users are actively searching for the brand.
* **Retargeting and Loyalty (e.g. Email & Retargeting Social):** The `email / newsletter` (Weekly Digest) and `facebook / social` (`retargeting_abandoned_cart`) campaigns exhibit the highest conversion rates (~8% - 15% and up to 35% on cart abandons). Retargeting cart abandoners has the absolute highest ROI since the customer has already expressed high intent.

### 3. Product & Segment Bottlenecks
* **Category Variations:** High-end categories like `electronics.smartphone` and `computers.notebook` generate the highest total revenue due to high prices, but show a higher cart abandonment rate because purchasing expensive items requires longer consideration.
* **Brand Strengths:** Tier-1 brands (`apple`, `samsung`, `nike`) convert at higher rates compared to budget brands (`oppo`, `haier`), showing the power of brand equity and customer confidence during checkout.

---

## 🚀 Growth Strategy & Recommendations

Based on the behavioral metrics, four high-impact marketing and UX experiments should be run:

### 1. Checkout Optimization (Immediate Impact)
* **Finding:** The cart abandonment rate is ~78%.
* **Strategy:** Optimize the checkout flow. Enable 1-click checkouts (Apple Pay, Google Pay, PayPal Express). Shorten checkout steps from 4 steps to 1 step. Disclose all shipping costs early on the product details page so there are no surprises at the end.
* **Expected Impact:** Reclaiming 5% of abandoned carts translates directly to a **+16% increase in overall revenue**.

### 2. Automated Email/SMS Abandoned Cart Retargeting
* **Finding:** Cart drop-off represents the highest concentration of high-intent, unconverted users.
* **Strategy:** Set up a 3-step automated email sequence:
  * **Email 1 (1 Hour Later):** "Did you forget something?" (Friendly reminder + product photo).
  * **Email 2 (24 Hours Later):** Add urgency ("Your cart items are selling out!").
  * **Email 3 (48 Hours Later):** Incentivize with a small benefit (e.g., "Free shipping" or "10% off your cart").
* **Expected Impact:** Typically recovers 10% - 15% of abandoned carts, resulting in automated, highly profitable sales.

### 3. Paid Media Budget Allocation (ROAS Optimization)
* **Finding:** Paid Search (`google / cpc / brand_search`) and Retargeting Campaigns convert at 4x - 6x the rate of cold paid social campaigns.
* **Strategy:** Shift 15% of the marketing budget away from broad lookalike campaigns on Facebook/Instagram towards:
  * Brand Search Ads on Google.
  * Dynamically generated catalog retargeting ads on Instagram/Facebook showcasing the exact products users viewed.
* **Expected Impact:** Decreases customer acquisition cost (CAC) and increases Return on Ad Spend (ROAS).

### 4. Shipping Threshold Promo on Apparel & Accessories
* **Finding:** Low-AOV categories (like `apparel.tshirt` and `auto.accessories`) have high conversion rates but small basket sizes.
* **Strategy:** Introduce a free shipping threshold (e.g., "Free shipping on orders over $50"). Promote this with a dynamic progress bar in the cart header ("Add $15 more to get free shipping!").
* **Expected Impact:** Increases Average Order Value (AOV) by encouraging users to add multiple items to their carts.
