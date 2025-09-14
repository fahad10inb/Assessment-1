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
    page_title="Attribution Analysis",
    page_icon="🎯",
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

def smart_column_finder(df):
    """Intelligently find the correct column names"""
    column_mapping = {}
    
    # Find total revenue column
    for col in df.columns:
        if 'total' in col.lower() and 'revenue' in col.lower():
            column_mapping['total_revenue'] = col
            break
        elif col.lower() == 'revenue':
            column_mapping['total_revenue'] = col
            break
    
    # Find platform attribution columns
    platforms = ['facebook', 'google', 'tiktok']
    for platform in platforms:
        # Look for attribution revenue columns
        for col in df.columns:
            if platform.lower() in col.lower() and 'revenue' in col.lower():
                column_mapping[f'{platform}_attributed_revenue'] = col
                break
        
        # Look for spend columns
        for col in df.columns:
            if platform.lower() in col.lower() and 'spend' in col.lower():
                column_mapping[f'{platform}_spend'] = col
                break
    
    # Look for attribution rate
    for col in df.columns:
        if 'attribution' in col.lower() and 'rate' in col.lower():
            column_mapping['attribution_rate'] = col
            break
    
    return column_mapping

def calculate_attribution_models_smart(df, column_mapping):
    """Calculate attribution models with smart column detection"""
    if 'total_revenue' not in column_mapping:
        st.error("Could not find total revenue column")
        return None
    
    total_revenue = df[column_mapping['total_revenue']].sum()
    
    # Attribution models
    last_click = {}
    spend_based = {}
    time_decay = {}
    total_spend = 0
    
    platforms = ['facebook', 'google', 'tiktok']
    
    for platform in platforms:
        platform_title = platform.title()
        
        # Get attributed revenue
        attr_col = column_mapping.get(f'{platform}_attributed_revenue')
        if attr_col and attr_col in df.columns:
            attributed = df[attr_col].sum()
            last_click[platform_title] = attributed
            
            # Time decay calculation
            df_sorted = df.sort_values('date')
            weights = np.exp(np.linspace(-2, 0, len(df_sorted)))
            weighted_revenue = (df_sorted[attr_col] * weights).sum()
            time_decay[platform_title] = weighted_revenue
        else:
            last_click[platform_title] = 0
            time_decay[platform_title] = 0
        
        # Get spend
        spend_col = column_mapping.get(f'{platform}_spend')
        if spend_col and spend_col in df.columns:
            spend = df[spend_col].sum()
            total_spend += spend
    
    # Calculate spend-based attribution
    for platform in platforms:
        platform_title = platform.title()
        spend_col = column_mapping.get(f'{platform}_spend')
        if spend_col and spend_col in df.columns and total_spend > 0:
            spend = df[spend_col].sum()
            spend_based[platform_title] = (spend / total_spend) * total_revenue
        else:
            spend_based[platform_title] = 0
    
    # Linear attribution
    linear = {
        'Facebook': total_revenue / 3,
        'Google': total_revenue / 3,
        'TikTok': total_revenue / 3
    }
    
    return {
        'last_click': last_click,
        'spend_based': spend_based,
        'time_decay': time_decay,
        'linear': linear
    }

def create_attribution_comparison_chart(attribution_models):
    """Create attribution model comparison chart"""
    if not attribution_models:
        return px.bar(x=['No Data'], y=[0], title="No Attribution Data Available")
    
    models_data = []
    for model_name, model_data in attribution_models.items():
        for platform, value in model_data.items():
            models_data.append({
                'Model': model_name.replace('_', ' ').title(),
                'Platform': platform,
                'Attribution': value
            })
    
    models_df = pd.DataFrame(models_data)
    
    fig = px.bar(
        models_df,
        x='Platform',
        y='Attribution',
        color='Model',
        barmode='group',
        title="Attribution Models Comparison",
        labels={'Attribution': 'Attributed Revenue ($)'},
        color_discrete_sequence=[
            DESIGN_SYSTEM['primary'], 
            DESIGN_SYSTEM['primary_light'], 
            DESIGN_SYSTEM['success'], 
            DESIGN_SYSTEM['warning']
        ]
    )
    
    return fig

def main():
    # Header
    st.markdown('<div class="dashboard-title">🎯 Attribution Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Multi-touch attribution modeling and analysis</div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Find columns
    column_mapping = smart_column_finder(df)
    
    # Calculate attribution models
    attribution_models = calculate_attribution_models_smart(df, column_mapping)
    
    if attribution_models:
        # Display attribution models
        st.markdown('<div class="section-header">📊 Attribution Models</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Last-click attribution
        with col1:
            st.markdown("**Last-Click Attribution**")
            model_data = attribution_models['last_click']
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-label">Facebook</div>
                <div class="metric-value">${model_data.get('Facebook', 0):,.0f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Google</div>
                <div class="metric-value">${model_data.get('Google', 0):,.0f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">TikTok</div>
                <div class="metric-value">${model_data.get('TikTok', 0):,.0f}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Spend-based attribution
        with col2:
            st.markdown("**Spend-Based Attribution**")
            model_data = attribution_models['spend_based']
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-label">Facebook</div>
                <div class="metric-value">${model_data.get('Facebook', 0):,.0f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Google</div>
                <div class="metric-value">${model_data.get('Google', 0):,.0f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">TikTok</div>
                <div class="metric-value">${model_data.get('TikTok', 0):,.0f}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Time decay attribution
        with col3:
            st.markdown("**Time Decay Attribution**")
            model_data = attribution_models['time_decay']
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-label">Facebook</div>
                <div class="metric-value">${model_data.get('Facebook', 0):,.0f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Google</div>
                <div class="metric-value">${model_data.get('Google', 0):,.0f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">TikTok</div>
                <div class="metric-value">${model_data.get('TikTok', 0):,.0f}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Linear attribution
        with col4:
            st.markdown("**Linear Attribution**")
            model_data = attribution_models['linear']
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-label">Facebook</div>
                <div class="metric-value">${model_data.get('Facebook', 0):,.0f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Google</div>
                <div class="metric-value">${model_data.get('Google', 0):,.0f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">TikTok</div>
                <div class="metric-value">${model_data.get('TikTok', 0):,.0f}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Comparison chart
        st.markdown('<div class="section-header">📈 Model Comparison</div>', unsafe_allow_html=True)
        
        comparison_chart = create_attribution_comparison_chart(attribution_models)
        safe_plotly_chart(comparison_chart, use_container_width=True)

if __name__ == "__main__":
    main()
