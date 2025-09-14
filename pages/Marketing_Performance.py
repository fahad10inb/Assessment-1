import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# Import shared styling
from shared_style import apply_shared_styles, DESIGN_SYSTEM, safe_plotly_chart

# Fix for orjson circular import issue
try:
    import plotly.io as pio
    pio.json.config.default_engine = "json"
except:
    pass

st.set_page_config(
    page_title="Marketing Performance",
    page_icon="📢",
    layout="wide"
)

# Apply consistent styling
apply_shared_styles()

# Add custom CSS for this page only
st.markdown('''
<style>
.metric-delta.positive {
    background-color: rgba(61, 221, 152, 0.15);
    color: #3edd98;
    border: 1px solid rgba(61, 221, 152, 0.3);
    display: block;
    text-align: left;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: 500;
    font-size: 0.8rem;
    transition: all 0.2s ease;
    line-height: 1.3;
}
</style>
''', unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the data"""
    try:
        df = pd.read_csv('data/processed/unified_marketing_business_data.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        try:
            df = pd.read_csv('unified_marketing_business_data.csv')
            df['date'] = pd.to_datetime(df['date'])
            return df
        except FileNotFoundError:
            st.error("Data file not found.")
            return None

def calculate_platform_metrics(df, platforms):
    """Calculate detailed platform metrics using exact column names"""
    platform_metrics = {}
    for platform in platforms:
        platform_lower = platform.lower()
        
        # Use exact column names from your data
        spend = df[f'{platform_lower}_spend'].sum()
        revenue = df[f'{platform_lower}_attributed revenue'].sum()
        clicks = df[f'{platform_lower}_clicks'].sum() if f'{platform_lower}_clicks' in df.columns else 0
        impressions = df[f'{platform_lower}_impression'].sum() if f'{platform_lower}_impression' in df.columns else 0
        
        # Calculated metrics
        roas = revenue / spend if spend > 0 else 0
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        cpc = spend / clicks if clicks > 0 else 0
        cpm = (spend / impressions * 1000) if impressions > 0 else 0
        
        # Efficiency metrics
        revenue_per_click = revenue / clicks if clicks > 0 else 0
        
        platform_metrics[platform_lower] = {
            'spend': spend,
            'revenue': revenue,
            'clicks': clicks,
            'impressions': impressions,
            'roas': roas,
            'ctr': ctr,
            'cpc': cpc,
            'cpm': cpm,
            'revenue_per_click': revenue_per_click
        }
    
    return platform_metrics

def create_spend_vs_revenue_chart(df):
    """Create spend vs revenue comparison chart"""
    platforms = ['facebook', 'google', 'tiktok']
    spend_data = []
    revenue_data = []
    
    for platform in platforms:
        spend = df[f'{platform}_spend'].sum()
        revenue = df[f'{platform}_attributed revenue'].sum()
        spend_data.append({'Platform': platform.title(), 'Amount': spend, 'Type': 'Spend'})
        revenue_data.append({'Platform': platform.title(), 'Amount': revenue, 'Type': 'Revenue'})
    
    combined_data = spend_data + revenue_data
    chart_df = pd.DataFrame(combined_data)
    
    fig = px.bar(
        chart_df,
        x='Platform',
        y='Amount',
        color='Type',
        barmode='group',
        title="Spend vs Revenue by Platform",
        color_discrete_map={
            'Spend': DESIGN_SYSTEM['warning'], 
            'Revenue': DESIGN_SYSTEM['primary']
        }
    )
    
    return fig

def create_roas_comparison_chart(df):
    """Create ROAS comparison chart"""
    platforms = ['facebook', 'google', 'tiktok']
    roas_data = []
    
    for platform in platforms:
        spend = df[f'{platform}_spend'].sum()
        revenue = df[f'{platform}_attributed revenue'].sum()
        roas = revenue / spend if spend > 0 else 0
        roas_data.append({
            'Platform': platform.title(),
            'ROAS': roas
        })
    
    roas_df = pd.DataFrame(roas_data)
    
    fig = px.bar(
        roas_df,
        x='Platform',
        y='ROAS',
        title="ROAS by Platform",
        color='ROAS',
        color_continuous_scale=[DESIGN_SYSTEM['error'], DESIGN_SYSTEM['warning'], DESIGN_SYSTEM['success']],
        text='ROAS'
    )
    
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    
    return fig

def main():
    # Header
    st.markdown('<div class="dashboard-title">📢 Marketing Performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Platform performance metrics and analysis</div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Platform metrics
    platforms = ['Facebook', 'Google', 'TikTok']
    platform_metrics = calculate_platform_metrics(df, platforms)
    
    # Display platform performance
    st.markdown('<div class="section-header">📊 Platform Performance Overview</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    for i, platform in enumerate(['facebook', 'google', 'tiktok']):
        if platform in platform_metrics:
            metrics = platform_metrics[platform]
            col = [col1, col2, col3][i]
            
            with col:
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">🎯 {platform.title()}</div>
                    <div class="metric-value">{metrics['roas']:.2f}x</div>
                    <div class="metric-delta positive">
                        <strong>Spend:</strong> ${metrics['spend']:,.0f}<br>
                        <strong>Revenue:</strong> ${metrics['revenue']:,.0f}<br>
                        <strong>ROAS:</strong> {metrics['roas']:.2f}<br>
                        <strong>CTR:</strong> {metrics['ctr']:.2f}%<br>
                        <strong>CPC:</strong> ${metrics['cpc']:.2f}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
    
    # Charts
    st.markdown('<div class="section-header">📈 Performance Charts</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        spend_revenue_chart = create_spend_vs_revenue_chart(df)
        safe_plotly_chart(spend_revenue_chart, use_container_width=True)
    
    with col2:
        roas_chart = create_roas_comparison_chart(df)
        safe_plotly_chart(roas_chart, use_container_width=True)

if __name__ == "__main__":
    main()