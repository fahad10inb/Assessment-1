import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from plotly.subplots import make_subplots

# Optional imports with error handling
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Fix for orjson circular import issue
try:
    import plotly.io as pio
    pio.json.config.default_engine = "json"
except:
    pass

# Page configuration
st.set_page_config(
    page_title="Marketing Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 UNIFIED DESIGN SYSTEM - Professional Dark Theme
DESIGN_SYSTEM = {
    'background_primary': '#1e1e2f',
    'background_secondary': '#2a2a40',
    'surface_elevated': '#353551',
    'primary': '#4f92ff',
    'primary_light': '#7bb3ff',
    'primary_dark': '#1a73e8',
    'secondary': '#7c3aed',
    'success': '#3dd598',
    'warning': '#f0b30b',
    'error': '#ff5c5c',
    'text_primary': '#f8faff',
    'text_secondary': '#c9c9d8',
    'text_muted': '#a1a1aa',
    'border': '#404040',
    'accent': '#ffffff',
    'font_heading': "'Montserrat', -apple-system, BlinkMacSystemFont, sans-serif",
    'font_body': "'Open Sans', -apple-system, BlinkMacSystemFont, sans-serif",
    'font_mono': "'JetBrains Mono', 'Courier New', monospace",
}

# 🎨 COMPLETE CSS WITH ENHANCED DATE PICKER
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Open+Sans:wght@300;400;500;600;700&display=swap');
    
    .main, .stApp {{
        background: {DESIGN_SYSTEM['background_primary']};
        color: {DESIGN_SYSTEM['text_primary']};
        font-family: {DESIGN_SYSTEM['font_body']};
        line-height: 1.6;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}
    
    .dashboard-title {{
        font-family: {DESIGN_SYSTEM['font_heading']};
        font-size: 2.75rem;
        font-weight: 800;
        background: linear-gradient(135deg, {DESIGN_SYSTEM['primary']}, {DESIGN_SYSTEM['primary_light']});
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.02em;
    }}
    
    .dashboard-subtitle {{
        font-family: {DESIGN_SYSTEM['font_body']};
        font-size: 1.1rem;
        font-weight: 400;
        color: {DESIGN_SYSTEM['text_secondary']};
        text-align: center;
        margin: 0 0 2rem 0;
        letter-spacing: 0.01em;
    }}
    
    .section-header {{
        font-family: {DESIGN_SYSTEM['font_heading']};
        font-size: 1.5rem;
        font-weight: 700;
        color: {DESIGN_SYSTEM['text_primary']};
        margin: 2.5rem 0 1.5rem 0;
        position: relative;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid {DESIGN_SYSTEM['primary']};
    }}
    
    .section-header::after {{
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 60px;
        height: 2px;
        background: {DESIGN_SYSTEM['primary_light']};
        border-radius: 1px;
    }}
    
    .metric-card {{
        background: linear-gradient(145deg, {DESIGN_SYSTEM['background_secondary']}, {DESIGN_SYSTEM['surface_elevated']});
        border: 1px solid {DESIGN_SYSTEM['border']};
        border-radius: 16px;
        padding: 1.75rem;
        margin: 1rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        position: relative;
        overflow: hidden;
    }}
    
    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, {DESIGN_SYSTEM['primary']}, {DESIGN_SYSTEM['secondary']});
        opacity: 0;
        transition: opacity 0.3s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border-color: {DESIGN_SYSTEM['primary']};
    }}
    
    .metric-card:hover::before {{
        opacity: 1;
    }}
    
    .metric-label {{
        font-family: {DESIGN_SYSTEM['font_body']};
        font-size: 0.85rem;
        font-weight: 600;
        color: {DESIGN_SYSTEM['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    
    .metric-value {{
        font-family: {DESIGN_SYSTEM['font_heading']};
        font-size: 2.25rem;
        font-weight: 700;
        color: {DESIGN_SYSTEM['text_primary']};
        margin-bottom: 0.75rem;
        letter-spacing: -0.02em;
    }}
    
    .metric-delta {{
        font-family: {DESIGN_SYSTEM['font_body']};
        font-size: 0.875rem;
        font-weight: 500;
        padding: 0.375rem 0.75rem;
        border-radius: 20px;
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        transition: all 0.2s ease;
    }}
    
    .metric-delta.positive {{
        color: {DESIGN_SYSTEM['success']};
        background: rgba(61, 213, 152, 0.15);
        border: 1px solid rgba(61, 213, 152, 0.3);
    }}
    
    .metric-delta.negative {{
        color: {DESIGN_SYSTEM['error']};
        background: rgba(255, 92, 92, 0.15);
        border: 1px solid rgba(255, 92, 92, 0.3);
    }}
    
    .metric-delta.neutral {{
        color: {DESIGN_SYSTEM['warning']};
        background: rgba(240, 179, 11, 0.15);
        border: 1px solid rgba(240, 179, 11, 0.3);
    }}
    
    .clean-stat {{
        background: linear-gradient(135deg, {DESIGN_SYSTEM['surface_elevated']}, {DESIGN_SYSTEM['background_secondary']});
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        font-weight: 500;
        font-size: 0.9rem;
        color: {DESIGN_SYSTEM['text_primary']};
        border-left: 3px solid {DESIGN_SYSTEM['primary']};
        transition: all 0.2s ease;
    }}
    
    .clean-stat:hover {{
        transform: translateX(2px);
        border-left-color: {DESIGN_SYSTEM['primary_light']};
        box-shadow: 0 4px 8px rgba(79, 146, 255, 0.1);
    }}
    
    .stat-value {{
        font-weight: 700;
        font-size: 1.1rem;
        color: {DESIGN_SYSTEM['primary']};
    }}
    
    .dashboard-header {{
        background: linear-gradient(135deg, {DESIGN_SYSTEM['background_secondary']}, {DESIGN_SYSTEM['surface_elevated']});
        padding: 2rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid {DESIGN_SYSTEM['border']};
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}
    
    /* 🔧 ENHANCED WIDGET STYLING */
    
    /* Selectbox styling */
    .stSelectbox > div > div {{
        background-color: {DESIGN_SYSTEM['background_secondary']} !important;
        border: 1px solid {DESIGN_SYSTEM['border']} !important;
        border-radius: 8px !important;
        color: {DESIGN_SYSTEM['text_primary']} !important;
        font-family: {DESIGN_SYSTEM['font_body']} !important;
        font-weight: 500 !important;
    }}
    
    .stSelectbox > div > div:hover {{
        border-color: {DESIGN_SYSTEM['primary']} !important;
    }}
    
    /* Enhanced Multiselect Styling */
    .stMultiSelect > div > div {{
        background-color: {DESIGN_SYSTEM['background_secondary']} !important;
        border: 1px solid {DESIGN_SYSTEM['border']} !important;
        border-radius: 8px !important;
        min-height: auto !important;
        max-height: 120px !important;
        overflow-y: auto !important;
    }}
    
    /* Multiselect tags - Compact & Clean */
    span[data-baseweb="tag"] {{
        background-color: {DESIGN_SYSTEM['surface_elevated']} !important;
        color: {DESIGN_SYSTEM['text_primary']} !important;
        border: 1px solid {DESIGN_SYSTEM['primary']} !important;
        border-radius: 6px !important;
        padding: 4px 8px !important;
        margin: 2px 4px 2px 0 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        max-width: 120px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 4px !important;
    }}
    
    span[data-baseweb="tag"] span {{
        color: {DESIGN_SYSTEM['text_primary']} !important;
        background-color: transparent !important;
        max-width: 80px !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }}
    
    /* Tag close button */
    span[data-baseweb="tag"] svg {{
        fill: {DESIGN_SYSTEM['text_secondary']} !important;
        width: 12px !important;
        height: 12px !important;
        cursor: pointer !important;
    }}
    
    span[data-baseweb="tag"] svg:hover {{
        fill: {DESIGN_SYSTEM['error']} !important;
    }}
    
    /* Multiselect dropdown */
    div[data-baseweb="select"] > div {{
        background-color: {DESIGN_SYSTEM['background_secondary']} !important;
        border: 1px solid {DESIGN_SYSTEM['border']} !important;
        color: {DESIGN_SYSTEM['text_primary']} !important;
    }}
    
    div[data-baseweb="select"] > div:focus {{
        border-color: {DESIGN_SYSTEM['primary']} !important;
    }}
    
    /* Dropdown options */
    div[role="listbox"] {{
        background-color: {DESIGN_SYSTEM['background_secondary']} !important;
        border: 1px solid {DESIGN_SYSTEM['border']} !important;
        border-radius: 8px !important;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2) !important;
        max-height: 200px !important;
        overflow-y: auto !important;
    }}
    
    div[role="listbox"] li {{
        background-color: transparent !important;
        color: {DESIGN_SYSTEM['text_primary']} !important;
        padding: 8px 12px !important;
        font-size: 0.9rem !important;
    }}
    
    div[role="listbox"] li:hover {{
        background-color: {DESIGN_SYSTEM['surface_elevated']} !important;
    }}
    
    div[role="listbox"] li[aria-selected="true"] {{
        background-color: {DESIGN_SYSTEM['primary']} !important;
        color: white !important;
    }}
    
    /* 🔧 ENHANCED DATE PICKER FIXES - FINAL VERSION */
    div[data-testid="stDateInput"] {{
        width: 100% !important;
    }}
    
    div[data-testid="stDateInput"] > div {{
        width: 100% !important;
        min-width: 100% !important;
        background: transparent !important;
    }}
    
    div[data-testid="stDateInput"] > div > div {{
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        background: transparent !important;
    }}
    
    /* Remove any background from date input container */
    div[data-testid="stDateInput"] > div > div > div {{
        background: transparent !important;
        width: 100% !important;
    }}
    
    /* Style the actual input field */
    div[data-testid="stDateInput"] input {{
        background-color: {DESIGN_SYSTEM['background_secondary']} !important;
        color: {DESIGN_SYSTEM['text_primary']} !important;
        border: 1px solid {DESIGN_SYSTEM['border']} !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        width: 100% !important;
        min-width: 260px !important;
        box-sizing: border-box !important;
        transition: all 0.2s ease !important;
    }}
    
    div[data-testid="stDateInput"] input:focus {{
        border-color: {DESIGN_SYSTEM['primary']} !important;
        box-shadow: 0 0 0 3px rgba(79, 146, 255, 0.15) !important;
        outline: none !important;
    }}
    
    div[data-testid="stDateInput"] input:hover {{
        border-color: {DESIGN_SYSTEM['primary_light']} !important;
    }}
    
    /* Style the calendar button */
    div[data-testid="stDateInput"] button {{
        background: transparent !important;
        border: none !important;
        padding: 10px !important;
        margin-left: 8px !important;
        border-radius: 6px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.2s ease !important;
    }}
    
    div[data-testid="stDateInput"] button:hover {{
        background-color: rgba(79, 146, 255, 0.15) !important;
    }}
    
    /* Calendar icon styling */
    div[data-testid="stDateInput"] svg {{
        fill: {DESIGN_SYSTEM['text_secondary']} !important;
        width: 18px !important;
        height: 18px !important;
        transition: fill 0.2s ease !important;
    }}
    
    div[data-testid="stDateInput"] button:hover svg {{
        fill: {DESIGN_SYSTEM['primary']} !important;
    }}
    
    /* Ensure no extra containers have backgrounds */
    div[data-testid="stDateInput"] * {{
        box-sizing: border-box !important;
    }}
    
    /* Fix any remaining backgrounds */
    div[data-testid="stDateInput"] div[role="button"] {{
        background: transparent !important;
    }}
    
    /* Enhanced Calendar popup styling */
    div[data-baseweb="calendar"] {{
        background-color: {DESIGN_SYSTEM['background_secondary']} !important;
        border: 1px solid {DESIGN_SYSTEM['border']} !important;
        border-radius: 12px !important;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.4) !important;
        padding: 1.5rem !important;
        margin-top: 8px !important;
    }}
    
    div[data-baseweb="calendar"] button {{
        background: transparent !important;
        color: {DESIGN_SYSTEM['text_primary']} !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin: 3px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        min-width: 40px !important;
        min-height: 40px !important;
    }}
    
    div[data-baseweb="calendar"] button:hover {{
        background-color: {DESIGN_SYSTEM['primary']} !important;
        color: white !important;
        transform: translateY(-1px) !important;
    }}
    
    div[data-baseweb="calendar"] button[aria-selected="true"] {{
        background-color: {DESIGN_SYSTEM['primary']} !important;
        color: white !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 8px rgba(79, 146, 255, 0.3) !important;
    }}
    
    /* Calendar navigation buttons */
    div[data-baseweb="calendar"] button[aria-label*="previous"],
    div[data-baseweb="calendar"] button[aria-label*="next"] {{
        background: transparent !important;
        color: {DESIGN_SYSTEM['primary']} !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }}
    
    div[data-baseweb="calendar"] button[aria-label*="previous"]:hover,
    div[data-baseweb="calendar"] button[aria-label*="next"]:hover {{
        background-color: rgba(79, 146, 255, 0.15) !important;
        transform: scale(1.1) !important;
    }}
    
    /* Calendar month/year header */
    div[data-baseweb="calendar"] div[role="heading"] {{
        color: {DESIGN_SYSTEM['text_primary']} !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        margin-bottom: 1rem !important;
    }}
    
    /* Hide default Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    .stDeployButton {{display: none;}}
    footer {{visibility: hidden;}}
    .stApp > header {{visibility: hidden;}}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {DESIGN_SYSTEM['background_primary']};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(135deg, {DESIGN_SYSTEM['primary']}, {DESIGN_SYSTEM['secondary']});
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(135deg, {DESIGN_SYSTEM['primary_light']}, {DESIGN_SYSTEM['primary']});
    }}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the data"""
    try:
        df = pd.read_csv('unified_marketing_business_data.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        try:
            df = pd.read_csv('data/processed/unified_marketing_business_data.csv')
            df['date'] = pd.to_datetime(df['date'])
            return df
        except FileNotFoundError:
            st.error("Please ensure the unified data file exists")
            return None

def apply_chart_theme(fig):
    """Apply consistent theme to all charts"""
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor=DESIGN_SYSTEM['background_secondary'],
        font=dict(
            family=DESIGN_SYSTEM['font_body'], 
            color=DESIGN_SYSTEM['text_primary'],
            size=12
        ),
        title_font=dict(
            family=DESIGN_SYSTEM['font_heading'], 
            size=18, 
            color=DESIGN_SYSTEM['text_primary']
        ),
        legend=dict(
            bgcolor=DESIGN_SYSTEM['background_secondary'],
            bordercolor=DESIGN_SYSTEM['border'],
            borderwidth=1,
            font=dict(color=DESIGN_SYSTEM['text_primary'])
        ),
        xaxis=dict(
            gridcolor=DESIGN_SYSTEM['border'], 
            color=DESIGN_SYSTEM['text_secondary'],
            linecolor=DESIGN_SYSTEM['border'],
            tickfont=dict(color=DESIGN_SYSTEM['text_secondary'])
        ),
        yaxis=dict(
            gridcolor=DESIGN_SYSTEM['border'], 
            color=DESIGN_SYSTEM['text_secondary'],
            linecolor=DESIGN_SYSTEM['border'],
            tickfont=dict(color=DESIGN_SYSTEM['text_secondary'])
        ),
        margin=dict(t=60, l=0, r=0, b=0),
        showlegend=True
    )
    return fig

def safe_plotly_chart(fig, **kwargs):
    """Display charts with consistent theming"""
    try:
        fig = apply_chart_theme(fig)
        st.plotly_chart(fig, **kwargs)
    except Exception as e:
        st.error(f"Chart rendering error: {str(e)}")

def calculate_kpis(df):
    """Calculate KPIs based on actual dataset columns"""
    total_revenue = df['total revenue'].sum()
    total_orders = df['# of orders'].sum()
    total_new_customers = df['new customers'].sum()
    total_spend = df['spend'].sum()
    avg_roas = df['marketing_roas'].mean()
    avg_profit_margin = df['profit_margin'].mean()
    
    # Growth calculations
    df_sorted = df.sort_values('date')
    mid_point = len(df_sorted) // 2
    first_half = df_sorted.iloc[:mid_point]
    second_half = df_sorted.iloc[mid_point:]
    
    # Revenue growth
    first_half_revenue = first_half['total revenue'].sum()
    second_half_revenue = second_half['total revenue'].sum()
    revenue_growth = ((second_half_revenue - first_half_revenue) / first_half_revenue * 100) if first_half_revenue > 0 else 0
    
    # Customer acquisition growth
    first_half_customers = first_half['new customers'].sum()
    second_half_customers = second_half['new customers'].sum()
    customer_growth = ((second_half_customers - first_half_customers) / first_half_customers * 100) if first_half_customers > 0 else 0
    
    # Customer Acquisition Cost (CAC)
    cac = total_spend / total_new_customers if total_new_customers > 0 else 0
    
    # Average Order Value
    aov = total_revenue / total_orders if total_orders > 0 else 0
    
    return {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_new_customers': total_new_customers,
        'total_spend': total_spend,
        'avg_roas': avg_roas,
        'avg_profit_margin': avg_profit_margin,
        'revenue_growth': revenue_growth,
        'customer_growth': customer_growth,
        'cac': cac,
        'aov': aov
    }

def render_sidebar(df):
    """Enhanced sidebar with perfect date picker styling"""
    with st.sidebar:
        # Custom branding at the top
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0; margin-bottom: 1rem;'>
            <h1 style='color: #4f92ff; font-size: 1.4rem; margin: 0; font-weight: 700;'>
                📊 MARKETING HUB
            </h1>
            <p style='color: #a1a1aa; font-size: 0.8rem; margin: 0;'>
                Intelligence Dashboard
            </p>
        </div>
        <hr style='margin: 1rem 0; border: 1px solid #404040; opacity: 0.3;'>
        """, unsafe_allow_html=True)
        
        # Enhanced Date Range with perfect styling
        date_range = st.date_input(
            "📅 Select Period",
            value=(df['date'].min(), df['date'].max()),
            min_value=df['date'].min(),
            max_value=df['date'].max(),
            format="YYYY/MM/DD"
        )
        
        # Enhanced Platform Selection
        platforms = st.multiselect(
            "🎯 Platforms",
            options=['Facebook', 'Google', 'TikTok'],
            default=['Facebook', 'Google', 'TikTok'],
            help="Select marketing platforms to analyze"
        )
        
        st.markdown("---")
        
        # Clean metrics display
        if len(df) > 0:
            kpis = calculate_kpis(df)
            
            st.markdown(f"""
            <div class="clean-stat">
                Revenue: <span class="stat-value">${kpis['total_revenue']:,.0f}</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="clean-stat">
                ROAS: <span class="stat-value">{kpis['avg_roas']:.1f}x</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="clean-stat">
                New Customers: <span class="stat-value">{kpis['total_new_customers']:,}</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="clean-stat">
                CAC: <span class="stat-value">${kpis['cac']:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
        
        return date_range, platforms

def executive_summary(df):
    """Executive Summary with key business metrics"""
    st.markdown('<div class="section-header">📈 Executive Summary</div>', unsafe_allow_html=True)
    
    kpis = calculate_kpis(df)
    
    # Enhanced KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_class = "positive" if kpis['revenue_growth'] > 0 else "negative" if kpis['revenue_growth'] < 0 else "neutral"
        icon = "📈" if kpis['revenue_growth'] > 0 else "📉" if kpis['revenue_growth'] < 0 else "📊"
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">💰 Total Revenue</div>
            <div class="metric-value">${kpis['total_revenue']:,.0f}</div>
            <div class="metric-delta {delta_class}">{icon} {kpis['revenue_growth']:+.1f}%</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">👥 New Customers</div>
            <div class="metric-value">{kpis['total_new_customers']:,.0f}</div>
            <div class="metric-delta positive">🚀 {kpis['customer_growth']:+.1f}%</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">🎯 Marketing ROAS</div>
            <div class="metric-value">{kpis['avg_roas']:.2f}x</div>
            <div class="metric-delta positive">💎 Return on Ad Spend</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">💎 Avg Order Value</div>
            <div class="metric-value">${kpis['aov']:.2f}</div>
            <div class="metric-delta neutral">💰 Per Order</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Performance Trends
    st.markdown('<div class="section-header">📊 Performance Trends</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily Revenue Trend
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['total revenue'],
            mode='lines',
            name='Daily Revenue',
            line=dict(color=DESIGN_SYSTEM['primary'], width=3),
            fill='tonexty',
            fillcolor=f"rgba(79, 146, 255, 0.1)"
        ))
        
        fig.update_layout(
            title="📈 Daily Revenue Trend",
            hovermode='x unified'
        )
        safe_plotly_chart(fig, use_container_width=True)
    
    with col2:
        # New Customers vs Orders
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['new customers'],
            mode='lines',
            name='New Customers',
            line=dict(color=DESIGN_SYSTEM['success'], width=3)
        ))
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['# of new orders'],
            mode='lines',
            name='New Orders',
            line=dict(color=DESIGN_SYSTEM['secondary'], width=3)
        ))
        
        fig.update_layout(
            title="👥 Customer & Order Acquisition",
            hovermode='x unified'
        )
        safe_plotly_chart(fig, use_container_width=True)

def revenue_profitability(df, platforms):
    """Revenue and Profitability Analysis"""
    st.markdown('<div class="section-header">💰 Revenue & Profitability Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue vs Gross Profit
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['total revenue'],
            name='Total Revenue',
            marker_color=DESIGN_SYSTEM['primary'],
            opacity=0.7
        ))
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['gross profit'],
            name='Gross Profit',
            marker_color=DESIGN_SYSTEM['success']
        ))
        
        fig.update_layout(
            title="💰 Revenue vs Gross Profit", 
            barmode='group',
            hovermode='x unified'
        )
        safe_plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Profit Margin Trend
        fig = px.line(
            df, 
            x='date', 
            y='profit_margin',
            title="📊 Profit Margin Trend"
        )
        fig.update_traces(
            line=dict(color=DESIGN_SYSTEM['success'], width=3),
            fill='tonexty',
            fillcolor=f"rgba(61, 213, 152, 0.1)"
        )
        safe_plotly_chart(fig, use_container_width=True)

def customer_acquisition_analysis(df):
    """Customer Acquisition Analysis"""
    st.markdown('<div class="section-header">👥 Customer Acquisition Analysis</div>', unsafe_allow_html=True)
    
    # Calculate key customer metrics
    total_spend = df['spend'].sum()
    total_new_customers = df['new customers'].sum()
    cac = total_spend / total_new_customers if total_new_customers > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">💸 Customer Acquisition Cost</div>
            <div class="metric-value">${cac:.2f}</div>
            <div class="metric-delta neutral">Per Customer</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        avg_new_customers = df['new customers'].mean()
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">📈 Daily New Customers</div>
            <div class="metric-value">{avg_new_customers:.1f}</div>
            <div class="metric-delta positive">Daily Average</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        new_customer_rate = (df['new customers'].sum() / df['# of orders'].sum() * 100) if df['# of orders'].sum() > 0 else 0
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">🎯 New Customer Rate</div>
            <div class="metric-value">{new_customer_rate:.1f}%</div>
            <div class="metric-delta positive">Of Total Orders</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Customer acquisition trends
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.line(
            df,
            x='date',
            y='new customers',
            title='👥 Daily New Customer Acquisition'
        )
        fig.update_traces(line=dict(color=DESIGN_SYSTEM['primary'], width=3))
        safe_plotly_chart(fig, use_container_width=True)
    
    with col2:
        # CAC trend over time
        df_temp = df.copy()
        df_temp['daily_cac'] = df_temp['spend'] / df_temp['new customers']
        df_temp['daily_cac'] = df_temp['daily_cac'].replace([np.inf, -np.inf], 0)
        
        fig = px.line(
            df_temp,
            x='date',
            y='daily_cac',
            title='💸 Customer Acquisition Cost Trend'
        )
        fig.update_traces(line=dict(color=DESIGN_SYSTEM['warning'], width=3))
        safe_plotly_chart(fig, use_container_width=True)

def platform_performance(df):
    """Platform Performance Analysis"""
    st.markdown('<div class="section-header">📱 Platform Performance Analysis</div>', unsafe_allow_html=True)
    
    # Platform metrics calculation
    platforms = ['facebook', 'google', 'tiktok']
    platform_data = []
    
    for platform in platforms:
        spend = df[f'{platform}_spend'].sum()
        revenue = df[f'{platform}_attributed revenue'].sum()
        clicks = df[f'{platform}_clicks'].sum()
        impressions = df[f'{platform}_impression'].sum()
        
        roas = revenue / spend if spend > 0 else 0
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        cpc = spend / clicks if clicks > 0 else 0
        
        platform_data.append({
            'Platform': platform.title(),
            'Spend': spend,
            'Revenue': revenue,
            'ROAS': roas,
            'CTR': ctr,
            'CPC': cpc,
            'Clicks': clicks,
            'Impressions': impressions
        })
    
    # Platform comparison cards
    col1, col2, col3 = st.columns(3)
    
    for i, platform_info in enumerate(platform_data):
        col = [col1, col2, col3][i]
        
        with col:
            st.markdown(f'''
            <div class="metric-card">
                <div class="metric-label">📱 {platform_info['Platform']}</div>
                <div class="metric-value">{platform_info['ROAS']:.2f}x</div>
                <div class="metric-delta positive">
                    💰 ${platform_info['Spend']:,.0f} → ${platform_info['Revenue']:,.0f}<br>
                    👆 CTR: {platform_info['CTR']:.2f}% | CPC: ${platform_info['CPC']:.2f}
                </div>
            </div>
            ''', unsafe_allow_html=True)
    
    # Platform performance charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue attribution pie chart
        fig = px.pie(
            values=[p['Revenue'] for p in platform_data],
            names=[p['Platform'] for p in platform_data],
            title="💰 Revenue Attribution by Platform",
            color_discrete_sequence=[DESIGN_SYSTEM['primary'], DESIGN_SYSTEM['primary_light'], DESIGN_SYSTEM['success']]
        )
        safe_plotly_chart(fig, use_container_width=True)
    
    with col2:
        # ROAS comparison
        fig = px.bar(
            x=[p['Platform'] for p in platform_data],
            y=[p['ROAS'] for p in platform_data],
            title="🎯 ROAS by Platform",
            color=[p['ROAS'] for p in platform_data],
            color_continuous_scale=[DESIGN_SYSTEM['error'], DESIGN_SYSTEM['warning'], DESIGN_SYSTEM['success']]
        )
        fig.update_traces(texttemplate='%{y:.2f}x', textposition='outside')
        safe_plotly_chart(fig, use_container_width=True)

def marketing_efficiency(df):
    """Marketing Efficiency & ROAS Analysis"""
    st.markdown('<div class="section-header">🎯 Marketing Efficiency & ROAS</div>', unsafe_allow_html=True)
    
    # Overall efficiency metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_spend = df['spend'].sum()
    total_attributed = df['attributed revenue'].sum()
    avg_attribution_rate = df['attribution_rate'].mean()
    overall_roas = total_attributed / total_spend if total_spend > 0 else 0
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">💸 Total Marketing Spend</div>
            <div class="metric-value">${total_spend:,.0f}</div>
            <div class="metric-delta neutral">All Platforms</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">📊 Overall ROAS</div>
            <div class="metric-value">{overall_roas:.2f}x</div>
            <div class="metric-delta positive">Return Multiple</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">🔗 Attribution Rate</div>
            <div class="metric-value">{avg_attribution_rate:.1%}</div>
            <div class="metric-delta positive">Tracked Revenue</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        total_clicks = df['clicks'].sum()
        total_impressions = df['impression'].sum()
        overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">👆 Overall CTR</div>
            <div class="metric-value">{overall_ctr:.2f}%</div>
            <div class="metric-delta positive">Click-Through Rate</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # ROAS and Attribution trends
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.line(
            df,
            x='date',
            y='marketing_roas',
            title='🎯 Daily Marketing ROAS Trend'
        )
        fig.update_traces(line=dict(color=DESIGN_SYSTEM['primary'], width=3))
        safe_plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(
            df,
            x='date',
            y='attribution_rate',
            title='🔗 Attribution Rate Trend'
        )
        fig.update_traces(line=dict(color=DESIGN_SYSTEM['success'], width=3))
        safe_plotly_chart(fig, use_container_width=True)

def main():
    # Enhanced Header
    st.markdown(f"""
    <div class="dashboard-header">
        <div class="dashboard-title">📊 Marketing Intelligence Dashboard</div>
        <div class="dashboard-subtitle">Multi-Platform Marketing Analytics & Customer Intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    if df is None:
        st.stop()
    
    # Perfect Sidebar with enhanced date picker
    date_range, platforms = render_sidebar(df)
    
    # Filter data based on selections
    if len(date_range) == 2:
        filtered_df = df[
            (df['date'] >= pd.to_datetime(date_range[0])) & 
            (df['date'] <= pd.to_datetime(date_range[1]))
        ].copy()
    else:
        filtered_df = df.copy()
    
    # Navigation
    st.markdown("### 📋 Analytics Dashboard")
    
    selected_view = st.selectbox(
        "Choose analytics view:",
        options=[
            "📈 Executive Summary",
            "💰 Revenue & Profitability", 
            "👥 Customer Acquisition",
            "📱 Platform Performance",
            "🎯 Marketing Efficiency"
        ],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Render selected view
    if selected_view == "📈 Executive Summary":
        executive_summary(filtered_df)
    elif selected_view == "💰 Revenue & Profitability":
        revenue_profitability(filtered_df, platforms)
    elif selected_view == "👥 Customer Acquisition":
        customer_acquisition_analysis(filtered_df)
    elif selected_view == "📱 Platform Performance":
        platform_performance(filtered_df)
    elif selected_view == "🎯 Marketing Efficiency":
        marketing_efficiency(filtered_df)

if __name__ == "__main__":
    main()
