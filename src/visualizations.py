import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st

def create_kpi_cards(kpis):
    """
    Create KPI metric cards for display
    
    Args:
        kpis (dict): Dictionary of KPI values
    
    Returns:
        None (displays Streamlit components)
    """
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            f"${kpis['total_revenue']:,.0f}",
            delta=f"{kpis['revenue_growth']:+.1f}%",
            help="Total revenue generated during the selected period"
        )
    
    with col2:
        st.metric(
            "Marketing ROAS", 
            f"{kpis['avg_roas']:.2f}",
            delta=f"{kpis['roas_trend']:+.2f}",
            help="Return on Ad Spend - Revenue generated per dollar spent"
        )
    
    with col3:
        st.metric(
            "Total Orders",
            f"{kpis['total_orders']:,.0f}",
            delta=f"{kpis['order_growth']:+.1f}%",
            help="Total number of orders placed"
        )
    
    with col4:
        st.metric(
            "Avg Profit Margin",
            f"{kpis['avg_profit_margin']:.1%}",
            delta=f"{kpis['margin_trend']:+.2%}",
            help="Average profit margin across all orders"
        )

def create_revenue_trend_chart(df):
    """
    Create a revenue trend chart over time
    
    Args:
        df (pd.DataFrame): Input dataframe
    
    Returns:
        plotly.graph_objects.Figure: Revenue trend chart
    """
    
    revenue_col = 'total_revenue' if 'total_revenue' in df.columns else 'total revenue'
    
    fig = go.Figure()
    
    # Add revenue line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df[revenue_col],
        mode='lines+markers',
        name='Daily Revenue',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6)
    ))
    
    # Add 7-day moving average if available
    if 'revenue_7d_ma' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['revenue_7d_ma'],
            mode='lines',
            name='7-Day Average',
            line=dict(color='red', width=2, dash='dash'),
            opacity=0.7
        ))
    
    fig.update_layout(
        title="Revenue Trend Over Time",
        xaxis_title="Date",
        yaxis_title="Revenue ($)",
        hovermode='x unified',
        showlegend=True,
        height=400
    )
    
    return fig

def create_platform_comparison(platform_metrics):
    """
    Create platform performance comparison chart
    
    Args:
        platform_metrics (dict): Platform metrics dictionary
    
    Returns:
        plotly.graph_objects.Figure: Platform comparison chart
    """
    
    platforms = list(platform_metrics.keys())
    
    # Extract metrics for comparison
    spend_data = [platform_metrics[p]['total_spend'] for p in platforms]
    revenue_data = [platform_metrics[p]['total_revenue'] for p in platforms]
    roas_data = [platform_metrics[p]['roas'] for p in platforms]
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Spend by Platform', 'Revenue by Platform', 'ROAS by Platform', 'Efficiency Ratio'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Spend comparison
    fig.add_trace(go.Bar(
        x=platforms,
        y=spend_data,
        name='Spend',
        marker_color='lightcoral',
        text=[f'${x:,.0f}' for x in spend_data],
        textposition='auto',
    ), row=1, col=1)
    
    # Revenue comparison
    fig.add_trace(go.Bar(
        x=platforms,
        y=revenue_data,
        name='Revenue',
        marker_color='lightblue',
        text=[f'${x:,.0f}' for x in revenue_data],
        textposition='auto',
    ), row=1, col=2)
    
    # ROAS comparison
    fig.add_trace(go.Bar(
        x=platforms,
        y=roas_data,
        name='ROAS',
        marker_color='lightgreen',
        text=[f'{x:.2f}' for x in roas_data],
        textposition='auto',
    ), row=2, col=1)
    
    # Efficiency ratio
    efficiency_data = [platform_metrics[p]['efficiency_ratio'] for p in platforms]
    fig.add_trace(go.Bar(
        x=platforms,
        y=efficiency_data,
        name='Efficiency Ratio',
        marker_color='gold',
        text=[f'{x:.2f}' for x in efficiency_data],
        textposition='auto',
    ), row=2, col=2)
    
    fig.update_layout(
        height=600,
        showlegend=False,
        title_text="Platform Performance Comparison"
    )
    
    return fig

def create_attribution_waterfall(attribution_models):
    """
    Create waterfall chart showing different attribution models
    
    Args:
        attribution_models (dict): Attribution model results
    
    Returns:
        plotly.graph_objects.Figure: Waterfall chart
    """
    
    # Prepare data for waterfall chart
    models = ['Last Click', 'Spend Based', 'Linear']
    platforms = ['Facebook', 'Google', 'TikTok']
    
    fig = go.Figure()
    
    x_pos = 0
    colors = ['#ff7f0e', '#2ca02c', '#d62728']  # Different colors for each platform
    
    for i, model in enumerate(['last_click', 'spend_based', 'linear']):
        for j, platform in enumerate(['facebook', 'google', 'tiktok']):
            value = attribution_models[model][platform]
            
            fig.add_trace(go.Bar(
                x=[f'{models[i]}<br>{platform.title()}'],
                y=[value],
                name=f'{platform.title()}',
                marker_color=colors[j],
                text=f'${value:,.0f}',
                textposition='auto',
                showlegend=(i == 0)  # Only show legend for first model
            ))
    
    fig.update_layout(
        title="Revenue Attribution Across Different Models",
        xaxis_title="Attribution Model & Platform",
        yaxis_title="Attributed Revenue ($)",
        barmode='group',
        height=500
    )
    
    return fig

def create_roas_efficiency_scatter(df):
    """
    Create scatter plot showing ROAS vs spend efficiency
    
    Args:
        df (pd.DataFrame): Input dataframe
    
    Returns:
        plotly.graph_objects.Figure: Scatter plot
    """
    
    revenue_col = 'total_revenue' if 'total_revenue' in df.columns else 'total revenue'
    
    fig = px.scatter(
        df,
        x='spend',
        y='marketing_roas',
        size=revenue_col,
        color='profit_margin',
        hover_data=['date', 'orders'],
        title="Marketing ROAS vs Daily Spend",
        labels={
            'spend': 'Daily Marketing Spend ($)',
            'marketing_roas': 'Marketing ROAS',
            'profit_margin': 'Profit Margin'
        },
        color_continuous_scale='viridis'
    )
    
    fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
    
    fig.update_layout(height=500)
    
    return fig

def create_customer_acquisition_funnel(df):
    """
    Create funnel chart for customer acquisition
    
    Args:
        df (pd.DataFrame): Input dataframe
    
    Returns:
        plotly.graph_objects.Figure: Funnel chart
    """
    
    # Calculate funnel metrics
    total_impressions = df['impression'].sum()
    total_clicks = df['clicks'].sum()
    total_orders = df['orders'].sum() if 'orders' in df.columns else df['# of orders'].sum()
    total_customers = df['new customers'].sum()
    
    # Create funnel data
    funnel_data = [
        ('Impressions', total_impressions, '#ff7f0e'),
        ('Clicks', total_clicks, '#2ca02c'),
        ('Orders', total_orders, '#d62728'),
        ('New Customers', total_customers, '#9467bd')
    ]
    
    fig = go.Figure(go.Funnel(
        y=[stage[0] for stage in funnel_data],
        x=[stage[1] for stage in funnel_data],
        textinfo="value+percent initial",
        marker=dict(
            color=[stage[2] for stage in funnel_data],
            line=dict(width=2, color="white")
        )
    ))
    
    fig.update_layout(
        title="Customer Acquisition Funnel",
        height=500
    )
    
    return fig

def create_cohort_heatmap(cohort_data):
    """
    Create cohort retention heatmap
    
    Args:
        cohort_data (pd.DataFrame): Cohort analysis data
    
    Returns:
        plotly.graph_objects.Figure: Heatmap
    """
    
    if 'retention_rate' in cohort_data.columns:
        fig = px.line(
            cohort_data,
            x='week',
            y='retention_rate',
            title="Weekly Retention Rate Trend",
            labels={'retention_rate': 'Retention Rate', 'week': 'Week'}
        )
        
        fig.update_traces(mode='lines+markers', line=dict(width=3))
        fig.update_layout(height=400)
        
        return fig
    else:
        # Simple weekly performance if retention data not available
        fig = px.bar(
            cohort_data,
            x='week',
            y='total revenue',
            title="Weekly Revenue Performance",
            labels={'total revenue': 'Revenue ($)', 'week': 'Week'}
        )
        
        fig.update_layout(height=400)
        
        return fig

def create_seasonality_analysis(seasonality_metrics):
    """
    Create seasonality analysis charts
    
    Args:
        seasonality_metrics (dict): Seasonality metrics
    
    Returns:
        plotly.graph_objects.Figure: Seasonality chart
    """
    
    # Day of week analysis
    dow_data = seasonality_metrics['day_of_week_analysis']['total revenue']
    days = list(dow_data.keys())
    revenues = list(dow_data.values())
    
    # Reorder days to start with Monday
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    ordered_days = [day for day in day_order if day in days]
    ordered_revenues = [dow_data[day] for day in ordered_days]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=ordered_days,
        y=ordered_revenues,
        name='Avg Daily Revenue',
        marker_color='lightblue',
        text=[f'${x:,.0f}' for x in ordered_revenues],
        textposition='auto'
    ))
    
    # Add trend line
    fig.add_trace(go.Scatter(
        x=ordered_days,
        y=ordered_revenues,
        mode='lines+markers',
        name='Trend',
        line=dict(color='red', width=2),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Revenue Performance by Day of Week",
        xaxis_title="Day of Week",
        yaxis_title="Average Revenue ($)",
        height=400
    )
    
    return fig

def create_multi_touch_attribution_chart(df):
    """
    Create multi-touch attribution visualization
    
    Args:
        df (pd.DataFrame): Input dataframe
    
    Returns:
        plotly.graph_objects.Figure: Attribution chart
    """
    
    platforms = ['Facebook', 'Google', 'TikTok']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    fig = go.Figure()
    
    for i, platform in enumerate(platforms):
        platform_lower = platform.lower()
        revenue_col = f'{platform_lower}_attributed revenue'
        
        if revenue_col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df[revenue_col],
                mode='lines+markers',
                name=f'{platform} Attribution',
                line=dict(color=colors[i], width=2),
                marker=dict(size=4),
                stackgroup='one',
                fillcolor=colors[i]
            ))
    
    fig.update_layout(
        title="Multi-Touch Attribution Over Time",
        xaxis_title="Date",
        yaxis_title="Attributed Revenue ($)",
        hovermode='x unified',
        height=500
    )
    
    return fig

def create_performance_summary_table(platform_metrics):
    """
    Create performance summary table
    
    Args:
        platform_metrics (dict): Platform metrics
    
    Returns:
        pd.DataFrame: Summary table
    """
    
    summary_data = []
    
    for platform, metrics in platform_metrics.items():
        summary_data.append({
            'Platform': platform,
            'Spend': f"${metrics['total_spend']:,.0f}",
            'Revenue': f"${metrics['total_revenue']:,.0f}",
            'ROAS': f"{metrics['roas']:.2f}",
            'CTR': f"{metrics['ctr']:.2%}",
            'CPC': f"${metrics['cpc']:.2f}",
            'Revenue Share': f"{metrics['revenue_share']:.1f}%",
            'Efficiency': f"{metrics['efficiency_ratio']:.2f}"
        })
    
    return pd.DataFrame(summary_data)