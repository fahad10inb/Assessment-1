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
    page_title="Executive Overview",
    page_icon="📊",
    layout="wide"
)

# Apply consistent styling
apply_shared_styles()

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

def calculate_kpis(df):
    """Calculate key performance indicators"""
    # Handle column name variations
    revenue_col = 'total revenue' if 'total revenue' in df.columns else 'total_revenue'
    orders_col = '# of orders' if '# of orders' in df.columns else 'orders'
    
    # Calculate growth rates (comparing first and second half)
    df_sorted = df.sort_values('date')
    mid_point = len(df_sorted) // 2
    first_half = df_sorted.iloc[:mid_point]
    second_half = df_sorted.iloc[mid_point:]
    
    # Revenue growth
    first_half_revenue = first_half[revenue_col].sum()
    second_half_revenue = second_half[revenue_col].sum()
    revenue_growth = ((second_half_revenue - first_half_revenue) / first_half_revenue * 100) if first_half_revenue > 0 else 0
    
    # Orders growth
    first_half_orders = first_half[orders_col].sum()
    second_half_orders = second_half[orders_col].sum()
    order_growth = ((second_half_orders - first_half_orders) / first_half_orders * 100) if first_half_orders > 0 else 0
    
    # ROAS trend
    first_half_roas = first_half['marketing_roas'].mean()
    second_half_roas = second_half['marketing_roas'].mean()
    roas_trend = second_half_roas - first_half_roas
    
    # Margin trend
    first_half_margin = first_half['profit_margin'].mean()
    second_half_margin = second_half['profit_margin'].mean()
    margin_trend = second_half_margin - first_half_margin
    
    return {
        'total_revenue': df[revenue_col].sum(),
        'total_orders': df[orders_col].sum(),
        'avg_roas': df['marketing_roas'].mean(),
        'avg_profit_margin': df['profit_margin'].mean(),
        'revenue_growth': revenue_growth,
        'order_growth': order_growth,
        'roas_trend': roas_trend,
        'margin_trend': margin_trend,
        'total_spend': df['spend'].sum(),
        'attribution_rate': df['attribution_rate'].mean()
    }

def create_revenue_trend_chart(df):
    """Create revenue trend chart"""
    revenue_col = 'total revenue' if 'total revenue' in df.columns else 'total_revenue'
    
    fig = px.line(
        df,
        x='date',
        y=revenue_col,
        title="Daily Revenue Trend",
        labels={revenue_col: 'Revenue ($)', 'date': 'Date'}
    )
    
    fig.update_traces(
        line_color=DESIGN_SYSTEM['primary'], 
        line_width=3
    )
    
    return fig

def create_platform_performance_chart(df):
    """Create platform performance comparison chart"""
    platforms = ['facebook', 'google', 'tiktok']
    platform_data = []
    
    for platform in platforms:
        spend = df[f'{platform}_spend'].sum()
        revenue = df[f'{platform}_attributed revenue'].sum()
        roas = revenue / spend if spend > 0 else 0
        
        platform_data.append({
            'Platform': platform.title(),
            'Spend': spend,
            'Revenue': revenue,
            'ROAS': roas
        })
    
    platform_df = pd.DataFrame(platform_data)
    
    # Create subplot
    fig = go.Figure()
    
    # Add spend bars
    fig.add_trace(go.Bar(
        name='Spend',
        x=platform_df['Platform'],
        y=platform_df['Spend'],
        yaxis='y',
        offsetgroup=1,
        marker_color=DESIGN_SYSTEM['warning']
    ))
    
    # Add revenue bars
    fig.add_trace(go.Bar(
        name='Revenue',
        x=platform_df['Platform'],
        y=platform_df['Revenue'],
        yaxis='y',
        offsetgroup=2,
        marker_color=DESIGN_SYSTEM['primary']
    ))
    
    # Add ROAS line
    fig.add_trace(go.Scatter(
        name='ROAS',
        x=platform_df['Platform'],
        y=platform_df['ROAS'],
        yaxis='y2',
        mode='lines+markers',
        marker_color=DESIGN_SYSTEM['success'],
        line=dict(width=3)
    ))
    
    fig.update_layout(
        title='Platform Performance Comparison',
        xaxis=dict(title='Platform'),
        yaxis=dict(title='Amount ($)', side='left'),
        yaxis2=dict(title='ROAS', side='right', overlaying='y'),
        legend=dict(x=0, y=1)
    )
    
    return fig

def main():
    # Header
    st.markdown('<div class="dashboard-title">📊 Executive Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Key performance indicators and business metrics</div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Calculate KPIs
    kpis = calculate_kpis(df)
    
    # KPI Cards
    st.markdown('<div class="section-header">📈 Key Performance Indicators</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_class = "positive" if kpis['revenue_growth'] > 0 else "negative" if kpis['revenue_growth'] < 0 else "neutral"
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">💰 Total Revenue</div>
            <div class="metric-value">${kpis['total_revenue']:,.0f}</div>
            <div class="metric-delta {delta_class}">{"📈" if kpis['revenue_growth'] > 0 else "📉"} {kpis['revenue_growth']:+.1f}%</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">🎯 Marketing ROAS</div>
            <div class="metric-value">{kpis['avg_roas']:.2f}x</div>
            <div class="metric-delta positive">🚀 Performance</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">🛒 Total Orders</div>
            <div class="metric-value">{kpis['total_orders']:,.0f}</div>
            <div class="metric-delta neutral">📦 Volume</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">💎 Profit Margin</div>
            <div class="metric-value">{kpis['avg_profit_margin']:.1%}</div>
            <div class="metric-delta positive">💰 Margin</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Charts
    st.markdown('<div class="section-header">📊 Performance Analytics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        revenue_chart = create_revenue_trend_chart(df)
        safe_plotly_chart(revenue_chart, use_container_width=True)
    
    with col2:
        platform_chart = create_platform_performance_chart(df)
        safe_plotly_chart(platform_chart, use_container_width=True)

if __name__ == "__main__":
    main()
