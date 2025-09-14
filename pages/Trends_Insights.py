import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# Import shared styling
from shared_style import apply_shared_styles, safe_plotly_chart, DESIGN_SYSTEM

# Optional advanced imports
try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# Fix for orjson circular import issue
try:
    import plotly.io as pio
    pio.json.config.default_engine = "json"
except:
    pass

st.set_page_config(
    page_title="Trends & Insights",
    page_icon="📈",
    layout="wide"
)

# Apply consistent styling
apply_shared_styles()

# Simple CSS with top space
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem !important;
    }
    
    .section-header {
        margin-bottom: 1rem !important;
        margin-top: 1.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

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

def calculate_trend_direction(series):
    """Calculate trend direction using linear regression"""
    if len(series) < 2:
        return "stable", 0
    
    x = np.arange(len(series)).reshape(-1, 1)
    y = series.values
    
    try:
        if SKLEARN_AVAILABLE:
            model = LinearRegression()
            model.fit(x, y)
            slope = model.coef_[0]
            
            if abs(slope) < 0.01 * np.mean(y):
                return "stable", slope
            elif slope > 0:
                return "increasing", slope
            else:
                return "decreasing", slope
        else:
            slope = (y[-1] - y[0]) / len(y)
            if abs(slope) < 0.01 * np.mean(y):
                return "stable", slope
            elif slope > 0:
                return "increasing", slope
            else:
                return "decreasing", slope
    except:
        return "stable", 0

def generate_insights_and_recommendations(df):
    """Generate comprehensive business insights and recommendations"""
    insights = []
    recommendations = []
    
    revenue_col = 'total revenue' if 'total revenue' in df.columns else 'total_revenue'
    
    # Revenue trend analysis
    if revenue_col in df.columns:
        revenue_trend, _ = calculate_trend_direction(df[revenue_col])
        insights.append(f"Revenue trend is {revenue_trend}")
        
        if revenue_trend == "decreasing":
            recommendations.append("Consider increasing marketing spend or optimizing campaign performance")
            recommendations.append("Review underperforming campaigns and reallocate budget")
        elif revenue_trend == "increasing":
            recommendations.append("Scale successful campaigns while maintaining efficiency")
            recommendations.append("Invest more in top-performing platforms")
        else:
            recommendations.append("Focus on optimization to break through revenue plateau")
            recommendations.append("Test new creative formats and targeting strategies")
    
    # ROAS analysis
    if 'marketing_roas' in df.columns:
        avg_roas = df['marketing_roas'].mean()
        roas_trend, _ = calculate_trend_direction(df['marketing_roas'])
        insights.append(f"Average ROAS is {avg_roas:.2f} with {roas_trend} trend")
        
        if avg_roas < 2.0:
            recommendations.append("ROAS below 2.0 - Review targeting and creative performance immediately")
        elif avg_roas > 4.0:
            recommendations.append("Excellent ROAS - Consider scaling budget allocation")
        else:
            recommendations.append("Good ROAS performance - Focus on incremental improvements")
    
    # Platform performance analysis
    platforms = ['facebook', 'google', 'tiktok']
    platform_performance = {}
    
    for platform in platforms:
        spend_col = f'{platform}_spend'
        revenue_col_platform = f'{platform}_attributed revenue'
        
        if spend_col in df.columns and revenue_col_platform in df.columns:
            total_spend = df[spend_col].sum()
            total_revenue = df[revenue_col_platform].sum()
            roas = total_revenue / total_spend if total_spend > 0 else 0
            roas = float(roas) if np.isfinite(roas) else 0.0
            platform_performance[platform] = roas
    
    if platform_performance:
        best_platform = max(platform_performance.items(), key=lambda x: x[1])
        worst_platform = min(platform_performance.items(), key=lambda x: x[1])
        
        insights.append(f"Best performing platform: {best_platform[0].title()} (ROAS: {best_platform[1]:.2f})")
        insights.append(f"Lowest performing platform: {worst_platform[0].title()} (ROAS: {worst_platform[1]:.2f})")
        
        recommendations.append(f"Increase budget allocation to {best_platform[0].title()}")
        if worst_platform[1] < 1.5:
            recommendations.append(f"Consider optimizing {worst_platform[0].title()} campaigns")
    
    # Attribution analysis
    if 'attribution_rate' in df.columns:
        avg_attribution = df['attribution_rate'].mean()
        insights.append(f"Average attribution rate: {avg_attribution:.1%}")
        
        if avg_attribution < 0.4:
            recommendations.append("Low attribution rate - Implement better tracking systems")
        elif avg_attribution > 0.6:
            recommendations.append("High attribution rate - Leverage this data for optimization")
        else:
            recommendations.append("Good attribution tracking - Continue monitoring")
    
    # Ensure minimum content
    while len(insights) < 5:
        fallback_insights = [
            "Marketing performance shows consistent patterns across platforms",
            "Data tracking captures significant portion of customer journey",
            "Campaign performance varies across different time periods",
            "Attribution data indicates multi-channel customer behavior"
        ]
        for fallback in fallback_insights:
            if fallback not in insights:
                insights.append(fallback)
                if len(insights) >= 5:
                    break
    
    while len(recommendations) < 5:
        fallback_recommendations = [
            "Continue monitoring key performance indicators regularly",
            "Implement A/B testing for continuous improvement",
            "Review and optimize underperforming campaigns weekly",
            "Focus on customer lifetime value optimization"
        ]
        for fallback in fallback_recommendations:
            if fallback not in recommendations:
                recommendations.append(fallback)
                if len(recommendations) >= 5:
                    break
    
    return insights[:5], recommendations[:5]

def main():
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Generate insights and recommendations
    insights, recommendations = generate_insights_and_recommendations(df)
    
    # ✅ STACKED VERTICAL LAYOUT - INSIGHTS FIRST, THEN RECOMMENDATIONS BELOW
    st.markdown('<div class="section-header">💡 Trends & Insights</div>', unsafe_allow_html=True)
    
    # Display all insights first
    for insight in insights:
        st.markdown(f'''
        <div style="
            background: linear-gradient(135deg, #353551, #2a2a40);
            border-left: 4px solid #4f92ff;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.8rem;
            color: #f8faff;
            font-size: 0.9rem;
            min-height: 50px;
            display: flex;
            align-items: center;
        ">
            📊 {insight}
        </div>
        ''', unsafe_allow_html=True)
    
    # Then display recommendations BELOW insights
    st.markdown('<div class="section-header">🎯 Recommendations</div>', unsafe_allow_html=True)
    
    for i, recommendation in enumerate(recommendations, 1):
        st.markdown(f'''
        <div style="
            background: linear-gradient(135deg, #353551, #2a2a40);
            border-left: 4px solid #3dd598;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.8rem;
            color: #f8faff;
            font-size: 0.9rem;
            min-height: 50px;
            display: flex;
            align-items: center;
        ">
            <strong>{i}.</strong> 🟡 {recommendation}
        </div>
        ''', unsafe_allow_html=True)
    
    # Performance Analytics
    st.markdown('<div class="section-header">📊 Performance Analytics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'marketing_roas' in df.columns:
            fig = px.line(df, x='date', y='marketing_roas', title='📈 Marketing ROAS Trend')
            fig.update_traces(line=dict(color=DESIGN_SYSTEM['primary'], width=3))
            safe_plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'attribution_rate' in df.columns:
            fig = px.line(df, x='date', y='attribution_rate', title='🔗 Attribution Rate Trend')
            fig.update_traces(line=dict(color=DESIGN_SYSTEM['success'], width=3))
            safe_plotly_chart(fig, use_container_width=True)
    
    # Additional Analytics
    col3, col4 = st.columns(2)
    
    with col3:
        if 'profit_margin' in df.columns:
            fig = px.line(df, x='date', y='profit_margin', title='💰 Profit Margin Trend')
            fig.update_traces(line=dict(color=DESIGN_SYSTEM['warning'], width=3))
            safe_plotly_chart(fig, use_container_width=True)
    
    with col4:
        if 'total revenue' in df.columns:
            fig = px.line(df, x='date', y='total revenue', title='💸 Total Revenue Trend')
            fig.update_traces(line=dict(color=DESIGN_SYSTEM['secondary'], width=3))
            safe_plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
