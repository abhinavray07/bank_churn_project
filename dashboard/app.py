import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_style('whitegrid')

st.set_page_config(page_title="Customer Retention Analytics", layout="wide")

@st.cache_data
def load_data():
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(SCRIPT_DIR, '..', 'data', 'European_Bank.csv')
    df = pd.read_csv(DATA_PATH)
    df = df.drop(columns=['Year'])
    df['AgeBand'] = pd.cut(df['Age'], bins=[18, 30, 45, 60, 92], labels=['18-30', '31-45', '46-60', '61+'])
    df['HighBalance'] = (df['Balance'] > df['Balance'].median()).astype(int)

    def classify_engagement(row):
        if row['IsActiveMember'] == 1:
            return 'Active Engaged' if row['NumOfProducts'] >= 2 else 'Active Low-Product'
        else:
            return 'Inactive High-Balance' if row['HighBalance'] == 1 else 'Inactive Disengaged'

    df['EngagementProfile'] = df.apply(classify_engagement, axis=1)

    def product_score(n):
        if n == 2: return 1.0
        elif n == 1: return 0.5
        else: return 0.0

    df['ProductScore'] = df['NumOfProducts'].apply(product_score)
    df['TenureNorm'] = df['Tenure'] / df['Tenure'].max()
    df['RelationshipStrengthIndex'] = (
        0.4 * df['IsActiveMember'] +
        0.3 * df['ProductScore'] +
        0.1 * df['HasCrCard'] +
        0.2 * df['TenureNorm']
    )
    return df

df = load_data()

st.title("Customer Engagement & Retention Analytics")
st.caption(f"{len(df):,} customers | Overall churn rate: {df['Exited'].mean()*100:.1f}%")

# ---- Sidebar filters ----
st.sidebar.header("Filters")

engagement_options = st.sidebar.multiselect(
    "Engagement Profile",
    options=df['EngagementProfile'].unique(),
    default=df['EngagementProfile'].unique()
)

product_range = st.sidebar.slider(
    "Number of Products",
    min_value=int(df['NumOfProducts'].min()),
    max_value=int(df['NumOfProducts'].max()),
    value=(int(df['NumOfProducts'].min()), int(df['NumOfProducts'].max()))
)

balance_range = st.sidebar.slider(
    "Balance Range (€)",
    min_value=float(df['Balance'].min()),
    max_value=float(df['Balance'].max()),
    value=(float(df['Balance'].min()), float(df['Balance'].max()))
)

salary_range = st.sidebar.slider(
    "Salary Range (€)",
    min_value=float(df['EstimatedSalary'].min()),
    max_value=float(df['EstimatedSalary'].max()),
    value=(float(df['EstimatedSalary'].min()), float(df['EstimatedSalary'].max()))
)

# Apply filters to create the working dataframe every module below will use
filtered_df = df[
    (df['EngagementProfile'].isin(engagement_options)) &
    (df['NumOfProducts'].between(*product_range)) &
    (df['Balance'].between(*balance_range)) &
    (df['EstimatedSalary'].between(*salary_range))
]

st.sidebar.markdown(f"**{len(filtered_df):,}** customers match current filters")

# ============================================================
# 1. ENGAGEMENT VS CHURN OVERVIEW
# ============================================================

st.divider()
st.header("1. Engagement vs Churn Overview")

col1, col2 = st.columns([1, 1])

with col1:
    if len(filtered_df) > 0:
        churn_by_profile = filtered_df.groupby('EngagementProfile')['Exited'].mean().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(6, 4))
        churn_by_profile.plot(kind='bar', ax=ax, color='#d62728')
        ax.axhline(df['Exited'].mean(), color='black', linestyle='--', label='Overall baseline')
        ax.set_ylabel('Churn Rate')
        ax.set_title('Churn Rate by Engagement Profile')
        ax.legend()
        plt.xticks(rotation=20, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.warning("No customers match the current filters.")

with col2:
    if len(filtered_df) > 0:
        summary = filtered_df.groupby('EngagementProfile').agg(
            Customers=('Exited', 'count'),
            ChurnRate=('Exited', 'mean')
        ).sort_values('ChurnRate', ascending=False)
        summary['ChurnRate'] = (summary['ChurnRate'] * 100).round(1).astype(str) + '%'
        st.dataframe(summary, width='stretch')
    else:
        st.warning("No customers match the current filters.")

# ============================================================
# 2. PRODUCT UTILIZATION IMPACT
# ============================================================

st.divider()
st.header("2. Product Utilization Impact")

col1, col2 = st.columns([1, 1])

with col1:
    if len(filtered_df) > 0:
        churn_by_products = filtered_df.groupby('NumOfProducts')['Exited'].mean().sort_index()

        fig, ax = plt.subplots(figsize=(6, 4))
        churn_by_products.plot(kind='bar', ax=ax, color='#1f77b4')
        ax.axhline(df['Exited'].mean(), color='black', linestyle='--', label='Overall baseline')
        ax.set_ylabel('Churn Rate')
        ax.set_xlabel('Number of Products')
        ax.set_title('Churn Rate by Product Count')
        ax.legend()
        plt.xticks(rotation=0)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.warning("No customers match the current filters.")

with col2:
    if len(filtered_df) > 0:
        product_summary = filtered_df.groupby('NumOfProducts').agg(
            Customers=('Exited', 'count'),
            ChurnRate=('Exited', 'mean')
        )
        product_summary['ChurnRate'] = (product_summary['ChurnRate'] * 100).round(1).astype(str) + '%'
        st.dataframe(product_summary, width='stretch')

        if 3 in filtered_df['NumOfProducts'].values or 4 in filtered_df['NumOfProducts'].values:
            st.caption("⚠️ 3-4 product customers show a sharp, unexplained churn spike — see research paper Section 4.3.")
    else:
        st.warning("No customers match the current filters.")

# ============================================================
# 3. HIGH-VALUE DISENGAGED CUSTOMER DETECTOR
# ============================================================

st.divider()
st.header("3. High-Value Disengaged Customer Detector")

st.markdown("Customers who are **inactive**, in the **top quartile** for balance and salary, and have **not yet churned** — the bank's clearest live intervention targets.")

balance_p75 = df['Balance'].quantile(0.75)
salary_p75 = df['EstimatedSalary'].quantile(0.75)

at_risk = filtered_df[
    (filtered_df['IsActiveMember'] == 0) &
    (filtered_df['Balance'] > balance_p75) &
    (filtered_df['EstimatedSalary'] > salary_p75) &
    (filtered_df['Exited'] == 0)
]

col1, col2, col3 = st.columns(3)
col1.metric("At-Risk Customers", f"{len(at_risk):,}")
col2.metric("Avg Balance", f"€{at_risk['Balance'].mean():,.0f}" if len(at_risk) > 0 else "—")
col3.metric("Avg Salary", f"€{at_risk['EstimatedSalary'].mean():,.0f}" if len(at_risk) > 0 else "—")

if len(at_risk) > 0:
    display_cols = ['CustomerId', 'Surname', 'Geography', 'Age', 'Balance', 'EstimatedSalary', 'NumOfProducts', 'Tenure']
    st.dataframe(
        at_risk[display_cols].sort_values('Balance', ascending=False),
        width='stretch',
        hide_index=True
    )
else:
    st.info("No customers match the at-risk criteria under current filters.")

# ============================================================
# 4. RETENTION STRENGTH SCORING PANEL
# ============================================================

st.divider()
st.header("4. Retention Strength Scoring Panel")

if len(filtered_df) > 0:
    # Compute the 5 KPIs on the filtered data
    churn_active = filtered_df[filtered_df['IsActiveMember']==1]['Exited'].mean()
    churn_inactive = filtered_df[filtered_df['IsActiveMember']==0]['Exited'].mean()
    engagement_retention_ratio = churn_inactive / churn_active if churn_active > 0 else float('nan')

    product_stats = filtered_df.groupby('NumOfProducts').agg(Count=('Exited','count'), ChurnRate=('Exited','mean'))
    product_stats['RetentionScore'] = 1 - product_stats['ChurnRate']
    product_depth_index = (product_stats['RetentionScore'] * product_stats['Count']).sum() / product_stats['Count'].sum()

    high_bal = filtered_df[filtered_df['HighBalance'] == 1]
    high_balance_disengagement_rate = (high_bal['IsActiveMember'] == 0).mean() if len(high_bal) > 0 else float('nan')

    churn_no_card = filtered_df[filtered_df['HasCrCard']==0]['Exited'].mean()
    churn_card = filtered_df[filtered_df['HasCrCard']==1]['Exited'].mean()
    credit_card_stickiness_score = churn_no_card - churn_card

    avg_relationship_strength = filtered_df['RelationshipStrengthIndex'].mean()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Engagement Retention Ratio", f"{engagement_retention_ratio:.2f}")
    k2.metric("Product Depth Index", f"{product_depth_index:.2f}")
    k3.metric("High-Balance Disengagement", f"{high_balance_disengagement_rate*100:.1f}%")
    k4.metric("Credit Card Stickiness", f"{credit_card_stickiness_score:.3f}")
    k5.metric("Avg Relationship Strength", f"{avg_relationship_strength:.2f}")

    st.subheader("KPIs by Geography")
    geo_kpi = filtered_df.groupby('Geography').apply(lambda g: pd.Series({
        'Customers': len(g),
        'ChurnRate': g['Exited'].mean(),
        'AvgRelationshipStrength': g['RelationshipStrengthIndex'].mean(),
        'HighBalanceDisengagement': (g[g['HighBalance']==1]['IsActiveMember']==0).mean() if len(g[g['HighBalance']==1]) > 0 else float('nan')
    }), include_groups=False).round(3)
    st.dataframe(geo_kpi, width='stretch')
else:
    st.warning("No customers match the current filters.")