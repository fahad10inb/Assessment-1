import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# Import shared styling
from shared_style import apply_shared_styles, safe_plotly_chart, DESIGN_SYSTEM

# Fix for orjson circular import issue
try:
    import plotly.io as pio
    pio.json.config.default_engine = "json"
except:
    pass

st.set_page_config(
    page_title="Revenue Analysis",
    page_icon="💰",
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

def create_revenue_composition_chart(df):
    """Create revenue composition over time"""
    revenue_columns = ['facebook_attributed revenue', 'google_attributed revenue', 'tiktok_attributed revenue']
    
    # Check which columns exist
    available_columns = [col for col in revenue_columns if col in df.columns]
    if not available_columns:
        st.warning("No attribution revenue columns found")
        return go.Figure()
    
    # Prepare data for stacked area chart
    revenue_data = df[['date'] + available_columns].copy()
    revenue_melted = revenue_data.melt(
        id_vars=['date'], 
        value_vars=available_columns,
        var_name='Platform', 
        value_name='Revenue'
    )
    
    # Clean platform names
    revenue_melted['Platform'] = revenue_melted['Platform'].str.replace('_attributed revenue', '').str.title()
    
    fig = px.area(
        revenue_melted,
        x='date',
        y='Revenue',
        color='Platform',
        title="📈 Revenue Composition Over Time",
        color_discrete_map={
            'Facebook': DESIGN_SYSTEM['primary'],
            'Google': DESIGN_SYSTEM['primary_light'], 
            'Tiktok': DESIGN_SYSTEM['success']
        }
    )
    
    return fig

def create_profit_analysis_chart(df):
    """Create profit margin analysis"""
    if 'profit_margin' not in df.columns:
        st.warning("Profit margin data not available")
        return go.Figure()
    
    fig = go.Figure()
    
    # Add profit margin line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['profit_margin'],
        mode='lines',
        name='Profit Margin',
        line=dict(color=DESIGN_SYSTEM['success'], width=3),
        fill='tozeroy',
        fillcolor=f"rgba(61, 221, 152, 0.1)",
        yaxis='y'
    ))
    
    # Add revenue bars
    revenue_col = 'total revenue' if 'total revenue' in df.columns else 'total_revenue'
    if revenue_col in df.columns:
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df[revenue_col],
            name='Revenue',
            marker_color=DESIGN_SYSTEM['primary'],
            opacity=0.3,
            yaxis='y2'
        ))
    
    fig.update_layout(
        title='📊 Revenue vs Profit Margin Trend',
        xaxis_title='Date',
        yaxis=dict(
            title='Profit Margin', 
            side='left', 
            tickformat='.1%',
            color=DESIGN_SYSTEM['success']
        ),
        yaxis2=dict(
            title='Revenue ($)', 
            side='right', 
            overlaying='y',
            color=DESIGN_SYSTEM['primary']
        ),
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def create_revenue_distribution(df):
    """Create revenue distribution by platform"""
    platforms = ['facebook', 'google', 'tiktok']
    platform_revenue = []
    
    for platform in platforms:
        revenue_col = f'{platform}_attributed revenue'
        if revenue_col in df.columns:
            revenue = df[revenue_col].sum()
            platform_revenue.append({
                'Platform': platform.title(),
                'Revenue': revenue
            })
    
    if not platform_revenue:
        st.warning("No platform revenue data available")
        return go.Figure()
    
    platform_df = pd.DataFrame(platform_revenue)
    
    fig = px.pie(
        platform_df,
        values='Revenue',
        names='Platform',
        title="🏆 Revenue Distribution by Platform",
        color_discrete_map={
            'Facebook': DESIGN_SYSTEM['primary'],
            'Google': DESIGN_SYSTEM['primary_light'], 
            'Tiktok': DESIGN_SYSTEM['success']
        }
    )
    
    return fig

def create_aov_trend_chart(df):
    """Create Average Order Value trend"""
    revenue_col = 'total revenue' if 'total revenue' in df.columns else 'total_revenue'
    orders_col = '# of orders' if '# of orders' in df.columns else 'orders'
    
    if revenue_col not in df.columns or orders_col not in df.columns:
        st.warning("Revenue or orders data not available for AOV calculation")
        return go.Figure()
    
    df_temp = df.copy()
    df_temp['aov'] = df_temp[revenue_col] / df_temp[orders_col]
    df_temp['aov'] = df_temp['aov'].replace([np.inf, -np.inf], 0)
    
    fig = px.line(
        df_temp,
        x='date',
        y='aov',
        title="💎 Average Order Value Trend",
        labels={'aov': 'AOV ($)', 'date': 'Date'}
    )
    
    fig.update_traces(
        line_color=DESIGN_SYSTEM['primary'], 
        line_width=3
    )
    
    return fig

def calculate_revenue_metrics(df):
    """Calculate key revenue metrics"""
    revenue_col = 'total revenue' if 'total revenue' in df.columns else 'total_revenue'
    
    if revenue_col not in df.columns:
        return {}
    
    total_revenue = df[revenue_col].sum()
    avg_daily_revenue = df[revenue_col].mean()
    
    # Growth calculation
    df_sorted = df.sort_values('date')
    mid_point = len(df_sorted) // 2
    first_half = df_sorted.iloc[:mid_point]
    second_half = df_sorted.iloc[mid_point:]
    
    first_half_revenue = first_half[revenue_col].sum()
    second_half_revenue = second_half[revenue_col].sum()
    growth_rate = ((second_half_revenue - first_half_revenue) / first_half_revenue * 100) if first_half_revenue > 0 else 0
    
    return {
        'total_revenue': total_revenue,
        'avg_daily_revenue': avg_daily_revenue,
        'growth_rate': growth_rate,
        'peak_revenue': df[revenue_col].max(),
        'peak_date': df.loc[df[revenue_col].idxmax(), 'date'].strftime('%Y-%m-%d')
    }

def main():
    # Header
    st.markdown('<div class="section-header">💰 Revenue Analysis</div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Calculate metrics
    metrics = calculate_revenue_metrics(df)
    
    # Display key metrics
    if metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-label">💰 Total Revenue</div>
                <div class="metric-value">${metrics['total_revenue']:,.0f}</div>
                <div class="metric-delta positive">Total Period</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-label">📊 Daily Average</div>
                <div class="metric-value">${metrics['avg_daily_revenue']:,.0f}</div>
                <div class="metric-delta neutral">Per Day</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col3:
            delta_class = "positive" if metrics['growth_rate'] > 0 else "negative" if metrics['growth_rate'] < 0 else "neutral"
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-label">📈 Growth Rate</div>
                <div class="metric-value">{metrics['growth_rate']:+.1f}%</div>
                <div class="metric-delta {delta_class}">Period Growth</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col4:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-label">🎯 Peak Revenue</div>
                <div class="metric-value">${metrics['peak_revenue']:,.0f}</div>
                <div class="metric-delta positive">{metrics['peak_date']}</div>
            </div>
            ''', unsafe_allow_html=True)
    
    # Charts Section
    st.markdown('<div class="section-header">📊 Revenue Analytics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        composition_chart = create_revenue_composition_chart(df)
        safe_plotly_chart(composition_chart, use_container_width=True)
    
    with col2:
        profit_chart = create_profit_analysis_chart(df)
        safe_plotly_chart(profit_chart, use_container_width=True)
    
    # Second row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        distribution_chart = create_revenue_distribution(df)
        safe_plotly_chart(distribution_chart, use_container_width=True)
    
    with col2:
        aov_chart = create_aov_trend_chart(df)
        safe_plotly_chart(aov_chart, use_container_width=True)

if __name__ == "__main__":
    main()
