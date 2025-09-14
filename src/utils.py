import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
import plotly.colors

def format_currency(value):
    """Format value as currency"""
    return f"${value:,.2f}"

def format_percentage(value):
    """Format value as percentage"""
    return f"{value:.2%}"

def format_number(value):
    """Format large numbers with appropriate suffixes"""
    if value >= 1e6:
        return f"{value/1e6:.1f}M"
    elif value >= 1e3:
        return f"{value/1e3:.1f}K"
    else:
        return f"{value:.0f}"

def get_color_palette(n_colors):
    """Get a color palette with n colors"""
    return plotly.colors.qualitative.Set3[:n_colors]

def calculate_growth_rate(current, previous):
    """Calculate growth rate between two values"""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100

def add_moving_average(df, column, window=7):
    """Add moving average column to dataframe"""
    df[f'{column}_ma_{window}'] = df[column].rolling(window=window, min_periods=1).mean()
    return df

def detect_outliers(series, threshold=3):
    """Detect outliers using z-score method"""
    z_scores = np.abs((series - series.mean()) / series.std())
    return z_scores > threshold

def clean_column_names(df):
    """Clean and standardize column names"""
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    return df

def validate_date_column(df, date_col='date'):
    """Validate and convert date column"""
    try:
        df[date_col] = pd.to_datetime(df[date_col])
        return True
    except:
        return False

def create_summary_metrics(df):
    """Create summary metrics for dashboard"""
    summary = {
        'total_revenue': df['total revenue'].sum() if 'total revenue' in df.columns else 0,
        'total_orders': df['# of orders'].sum() if '# of orders' in df.columns else 0,
        'total_spend': df['spend'].sum() if 'spend' in df.columns else 0,
        'avg_roas': df['marketing_roas'].mean() if 'marketing_roas' in df.columns else 0,
        'date_range': f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"
    }
    return summary

def export_insights_to_text(insights_dict):
    """Export key insights to a text summary"""
    summary = "Marketing Intelligence Dashboard - Key Insights\n"
    summary += "=" * 50 + "\n\n"
    
    for category, insights in insights_dict.items():
        summary += f"{category.upper()}:\n"
        summary += "-" * len(category) + "\n"
        for insight in insights:
            summary += f"• {insight}\n"
        summary += "\n"
    
    return summary

@st.cache_data
def load_and_cache_data(file_path):
    """Load and cache data for better performance"""
    return pd.read_csv(file_path)

def create_download_link(df, filename="marketing_data.csv"):
    """Create download link for dataframe"""
    csv = df.to_csv(index=False)
    return csv

def get_business_insights(df):
    """Generate business insights from the data"""
    insights = {
        'performance': [],
        'efficiency': [],
        'recommendations': []
    }
    
    # Performance insights
    total_revenue = df['total revenue'].sum()
    total_spend = df['spend'].sum()
    overall_roas = total_revenue / total_spend if total_spend > 0 else 0
    
    if overall_roas > 3:
        insights['performance'].append(f"Excellent overall ROAS of {overall_roas:.2f}")
    elif overall_roas > 2:
        insights['performance'].append(f"Good overall ROAS of {overall_roas:.2f}")
    else:
        insights['performance'].append(f"ROAS of {overall_roas:.2f} needs improvement")
    
    # Platform efficiency
    platforms = ['facebook', 'google', 'tiktok']
    platform_roas = {}
    
    for platform in platforms:
        spend = df[f'{platform}_spend'].sum()
        revenue = df[f'{platform}_attributed revenue'].sum()
        roas = revenue / spend if spend > 0 else 0
        platform_roas[platform] = roas
    
    best_platform = max(platform_roas.items(), key=lambda x: x[1])
    worst_platform = min(platform_roas.items(), key=lambda x: x[1])
    
    insights['efficiency'].append(f"Best performing platform: {best_platform[0].title()} (ROAS: {best_platform[1]:.2f})")
    insights['efficiency'].append(f"Lowest performing platform: {worst_platform[0].title()} (ROAS: {worst_platform[1]:.2f})")
    
    # Recommendations
    if best_platform[1] > worst_platform[1] * 1.5:
        insights['recommendations'].append(f"Consider reallocating budget from {worst_platform[0].title()} to {best_platform[0].title()}")
    
    avg_profit_margin = df['profit_margin'].mean()
    if avg_profit_margin < 0.3:
        insights['recommendations'].append("Consider reviewing COGS to improve profit margins")
    
    return insights

def create_data_quality_report(df):
    """Create a data quality report"""
    report = {
        'shape': df.shape,
        'missing_values': df.isnull().sum().to_dict(),
        'duplicate_rows': df.duplicated().sum(),
        'date_range': (df['date'].min(), df['date'].max()) if 'date' in df.columns else None,
        'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
        'warnings': []
    }
    
    # Check for anomalies
    if df['marketing_roas'].max() > 10:
        report['warnings'].append("Unusually high ROAS values detected")
    
    if (df['spend'] == 0).any():
        report['warnings'].append("Zero spend days detected")
    
    return report

def generate_executive_summary(df):
    """Generate executive summary text"""
    total_revenue = df['total revenue'].sum()
    total_spend = df['spend'].sum()
    total_orders = df['# of orders'].sum()
    avg_roas = df['marketing_roas'].mean()
    
    summary = f"""
    📊 EXECUTIVE SUMMARY
    
    📈 Revenue Performance:
    • Total Revenue: {format_currency(total_revenue)}
    • Total Orders: {format_number(total_orders)}
    • Average Order Value: {format_currency(total_revenue/total_orders if total_orders > 0 else 0)}
    
    💰 Marketing Performance:
    • Total Marketing Spend: {format_currency(total_spend)}
    • Average ROAS: {avg_roas:.2f}
    • Marketing Efficiency: {format_percentage((total_revenue - total_spend)/total_spend if total_spend > 0 else 0)} profit margin
    
    🎯 Key Insights:
    • Marketing is generating {avg_roas:.2f}x return on investment
    • {format_percentage(df['attribution_rate'].mean())} of revenue is attributed to marketing efforts
    • Average profit margin: {format_percentage(df['profit_margin'].mean())}
    """
    
    return summary