import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_kpis(df):
    """
    Calculate key performance indicators from the dataset
    
    Args:
        df (pd.DataFrame): Input dataframe with marketing and business data
    
    Returns:
        dict: Dictionary containing calculated KPIs
    """
    
    # Ensure we have the right column names
    revenue_col = 'total_revenue' if 'total_revenue' in df.columns else 'total revenue'
    orders_col = 'orders' if 'orders' in df.columns else '# of orders'
    
    # Basic business metrics
    total_revenue = df[revenue_col].sum()
    total_orders = df[orders_col].sum()
    total_spend = df['spend'].sum()
    
    # Calculate growth rates (comparing first and second half of the period)
    df_sorted = df.sort_values('date')
    mid_point = len(df_sorted) // 2
    
    first_half = df_sorted.iloc[:mid_point]
    second_half = df_sorted.iloc[mid_point:]
    
    first_half_revenue = first_half[revenue_col].sum()
    second_half_revenue = second_half[revenue_col].sum()
    revenue_growth = ((second_half_revenue - first_half_revenue) / first_half_revenue * 100) if first_half_revenue > 0 else 0
    
    first_half_orders = first_half[orders_col].sum()
    second_half_orders = second_half[orders_col].sum()
    order_growth = ((second_half_orders - first_half_orders) / first_half_orders * 100) if first_half_orders > 0 else 0
    
    # ROAS metrics
    avg_roas = df['marketing_roas'].mean()
    first_half_roas = first_half['marketing_roas'].mean()
    second_half_roas = second_half['marketing_roas'].mean()
    roas_trend = second_half_roas - first_half_roas
    
    # Profit margin metrics
    avg_profit_margin = df['profit_margin'].mean()
    first_half_margin = first_half['profit_margin'].mean()
    second_half_margin = second_half['profit_margin'].mean()
    margin_trend = second_half_margin - first_half_margin
    
    # Customer metrics
    total_new_customers = df['new customers'].sum()
    avg_aov = total_revenue / total_orders if total_orders > 0 else 0
    
    # Attribution metrics
    total_attributed_revenue = df['attributed revenue'].sum()
    attribution_rate = df['attribution_rate'].mean()
    
    kpis = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_spend': total_spend,
        'total_new_customers': total_new_customers,
        'avg_aov': avg_aov,
        'avg_roas': avg_roas,
        'avg_profit_margin': avg_profit_margin,
        'attribution_rate': attribution_rate,
        'total_attributed_revenue': total_attributed_revenue,
        'revenue_growth': revenue_growth,
        'order_growth': order_growth,
        'roas_trend': roas_trend,
        'margin_trend': margin_trend,
        'cac': total_spend / total_new_customers if total_new_customers > 0 else 0,
        'ltv_cac_ratio': (avg_aov * 3) / (total_spend / total_new_customers) if total_new_customers > 0 else 0  # Assuming 3 purchases per customer
    }
    
    return kpis

def calculate_platform_metrics(df, platforms):
    """
    Calculate platform-specific metrics
    
    Args:
        df (pd.DataFrame): Input dataframe
        platforms (list): List of platforms to analyze
    
    Returns:
        dict: Platform-specific metrics
    """
    
    platform_metrics = {}
    
    for platform in platforms:
        platform_lower = platform.lower()
        
        # Column names for the platform
        spend_col = f'{platform_lower}_spend'
        revenue_col = f'{platform_lower}_attributed revenue'
        clicks_col = f'{platform_lower}_clicks'
        impressions_col = f'{platform_lower}_impression'
        
        # Basic metrics
        total_spend = df[spend_col].sum() if spend_col in df.columns else 0
        total_revenue = df[revenue_col].sum() if revenue_col in df.columns else 0
        total_clicks = df[clicks_col].sum() if clicks_col in df.columns else 0
        total_impressions = df[impressions_col].sum() if impressions_col in df.columns else 0
        
        # Calculated metrics
        roas = total_revenue / total_spend if total_spend > 0 else 0
        ctr = total_clicks / total_impressions if total_impressions > 0 else 0
        cpc = total_spend / total_clicks if total_clicks > 0 else 0
        cpm = (total_spend / total_impressions) * 1000 if total_impressions > 0 else 0
        
        # Revenue share
        total_attributed = (df['facebook_attributed revenue'].sum() + 
                          df['google_attributed revenue'].sum() + 
                          df['tiktok_attributed revenue'].sum())
        revenue_share = (total_revenue / total_attributed) * 100 if total_attributed > 0 else 0
        
        # Spend efficiency
        spend_share = (total_spend / df['spend'].sum()) * 100 if df['spend'].sum() > 0 else 0
        efficiency_ratio = revenue_share / spend_share if spend_share > 0 else 0
        
        platform_metrics[platform] = {
            'total_spend': total_spend,
            'total_revenue': total_revenue,
            'total_clicks': total_clicks,
            'total_impressions': total_impressions,
            'roas': roas,
            'ctr': ctr,
            'cpc': cpc,
            'cpm': cpm,
            'revenue_share': revenue_share,
            'spend_share': spend_share,
            'efficiency_ratio': efficiency_ratio
        }
    
    return platform_metrics

def calculate_cohort_metrics(df):
    """
    Calculate cohort-based metrics for customer analysis
    
    Args:
        df (pd.DataFrame): Input dataframe
    
    Returns:
        pd.DataFrame: Cohort analysis data
    """
    
    # Ensure we have the right column names
    revenue_col = 'total_revenue' if 'total_revenue' in df.columns else 'total revenue'
    orders_col = 'orders' if 'orders' in df.columns else '# of orders'
    
    # Group by week for cohort analysis
    df['week'] = df['date'].dt.to_period('W')
    
    weekly_metrics = df.groupby('week').agg({
        'new customers': 'sum',
        orders_col: 'sum',
        revenue_col: 'sum',
        'spend': 'sum'
    }).reset_index()
    
    weekly_metrics['week'] = weekly_metrics['week'].dt.start_time
    
    # Calculate cumulative metrics
    weekly_metrics['cumulative_customers'] = weekly_metrics['new customers'].cumsum()
    weekly_metrics['cumulative_revenue'] = weekly_metrics[revenue_col].cumsum()
    weekly_metrics['cumulative_spend'] = weekly_metrics['spend'].cumsum()
    
    # Calculate weekly retention (simplified)
    weekly_metrics['retention_rate'] = weekly_metrics[orders_col] / weekly_metrics['new customers'].shift(1).fillna(1)
    weekly_metrics['retention_rate'] = weekly_metrics['retention_rate'].clip(0, 1)
    
    return weekly_metrics

def calculate_attribution_model(df):
    """
    Calculate different attribution models
    
    Args:
        df (pd.DataFrame): Input dataframe
    
    Returns:
        dict: Attribution model results
    """
    
    # Ensure we have the right column names
    revenue_col = 'total_revenue' if 'total_revenue' in df.columns else 'total revenue'
    
    # Last-click attribution (current model)
    last_click_facebook = df['facebook_attributed revenue'].sum()
    last_click_google = df['google_attributed revenue'].sum()
    last_click_tiktok = df['tiktok_attributed revenue'].sum()
    
    total_attributed = last_click_facebook + last_click_google + last_click_tiktok
    
    # Spend-based attribution (proportional to spend)
    total_facebook_spend = df['facebook_spend'].sum()
    total_google_spend = df['google_spend'].sum()
    total_tiktok_spend = df['tiktok_spend'].sum()
    total_spend = total_facebook_spend + total_google_spend + total_tiktok_spend
    
    total_revenue = df[revenue_col].sum()
    
    spend_based_facebook = (total_facebook_spend / total_spend) * total_revenue if total_spend > 0 else 0
    spend_based_google = (total_google_spend / total_spend) * total_revenue if total_spend > 0 else 0
    spend_based_tiktok = (total_tiktok_spend / total_spend) * total_revenue if total_spend > 0 else 0
    
    # Linear attribution (equal weight)
    linear_facebook = total_revenue / 3
    linear_google = total_revenue / 3
    linear_tiktok = total_revenue / 3
    
    attribution_models = {
        'last_click': {
            'facebook': last_click_facebook,
            'google': last_click_google,
            'tiktok': last_click_tiktok
        },
        'spend_based': {
            'facebook': spend_based_facebook,
            'google': spend_based_google,
            'tiktok': spend_based_tiktok
        },
        'linear': {
            'facebook': linear_facebook,
            'google': linear_google,
            'tiktok': linear_tiktok
        }
    }
    
    return attribution_models

def calculate_seasonality_metrics(df):
    """
    Calculate seasonality and trend metrics
    
    Args:
        df (pd.DataFrame): Input dataframe
    
    Returns:
        dict: Seasonality metrics
    """
    
    # Ensure we have the right column names
    revenue_col = 'total_revenue' if 'total_revenue' in df.columns else 'total revenue'
    orders_col = 'orders' if 'orders' in df.columns else '# of orders'
    
    df['day_of_week'] = df['date'].dt.day_name()
    df['week_of_year'] = df['date'].dt.isocalendar().week
    
    # Day of week analysis
    dow_metrics = df.groupby('day_of_week').agg({
        revenue_col: 'mean',
        orders_col: 'mean',
        'spend': 'mean',
        'marketing_roas': 'mean'
    }).round(2)
    
    # Weekly trends
    weekly_metrics = df.groupby('week_of_year').agg({
        revenue_col: 'sum',
        orders_col: 'sum',
        'spend': 'sum',
        'marketing_roas': 'mean'
    }).round(2)
    
    # Identify best and worst performing days/weeks
    best_day = dow_metrics[revenue_col].idxmax()
    worst_day = dow_metrics[revenue_col].idxmin()
    
    best_week = weekly_metrics[revenue_col].idxmax()
    worst_week = weekly_metrics[revenue_col].idxmin()
    
    seasonality_metrics = {
        'day_of_week_analysis': dow_metrics.to_dict(),
        'weekly_analysis': weekly_metrics.to_dict(),
        'best_performing_day': best_day,
        'worst_performing_day': worst_day,
        'best_performing_week': best_week,
        'worst_performing_week': worst_week,
        'revenue_volatility': df[revenue_col].std() / df[revenue_col].mean()
    }
    
    return seasonality_metrics

def calculate_efficiency_metrics(df):
    """
    Calculate marketing efficiency metrics
    
    Args:
        df (pd.DataFrame): Input dataframe
    
    Returns:
        dict: Efficiency metrics
    """
    
    # Ensure we have the right column names
    orders_col = 'orders' if 'orders' in df.columns else '# of orders'
    
    # Revenue per dollar spent
    revenue_per_dollar = df['attributed revenue'].sum() / df['spend'].sum() if df['spend'].sum() > 0 else 0
    
    # Orders per dollar spent
    orders_per_dollar = df[orders_col].sum() / df['spend'].sum() if df['spend'].sum() > 0 else 0
    
    # Customers per dollar spent
    customers_per_dollar = df['new customers'].sum() / df['spend'].sum() if df['spend'].sum() > 0 else 0
    
    # Click efficiency
    revenue_per_click = df['attributed revenue'].sum() / df['clicks'].sum() if df['clicks'].sum() > 0 else 0
    orders_per_click = df[orders_col].sum() / df['clicks'].sum() if df['clicks'].sum() > 0 else 0
    
    # Impression efficiency
    revenue_per_impression = df['attributed revenue'].sum() / df['impression'].sum() if df['impression'].sum() > 0 else 0
    
    efficiency_metrics = {
        'revenue_per_dollar': revenue_per_dollar,
        'orders_per_dollar': orders_per_dollar,
        'customers_per_dollar': customers_per_dollar,
        'revenue_per_click': revenue_per_click,
        'orders_per_click': orders_per_click,
        'revenue_per_impression': revenue_per_impression,
        'overall_efficiency_score': (revenue_per_dollar + orders_per_dollar + customers_per_dollar) / 3
    }
    
    return efficiency_metrics

def calculate_daily_performance_metrics(df):
    """
    Calculate daily performance metrics and trends
    
    Args:
        df (pd.DataFrame): Input dataframe
    
    Returns:
        pd.DataFrame: DataFrame with additional daily metrics
    """
    
    df_copy = df.copy()
    
    # Ensure we have the right column names
    revenue_col = 'total_revenue' if 'total_revenue' in df.columns else 'total revenue'
    orders_col = 'orders' if 'orders' in df.columns else '# of orders'
    
    # Daily efficiency metrics
    df_copy['daily_roas'] = df_copy['attributed revenue'] / df_copy['spend']
    df_copy['daily_roas'] = df_copy['daily_roas'].replace([np.inf, -np.inf], 0)
    
    # Daily AOV
    df_copy['daily_aov'] = df_copy[revenue_col] / df_copy[orders_col]
    df_copy['daily_aov'] = df_copy['daily_aov'].replace([np.inf, -np.inf], 0)
    
    # Daily CAC
    df_copy['daily_cac'] = df_copy['spend'] / df_copy['new customers']
    df_copy['daily_cac'] = df_copy['daily_cac'].replace([np.inf, -np.inf], 0)
    
    # Daily conversion rate
    df_copy['daily_conversion_rate'] = df_copy[orders_col] / df_copy['clicks']
    df_copy['daily_conversion_rate'] = df_copy['daily_conversion_rate'].replace([np.inf, -np.inf], 0)
    
    # Daily CTR
    df_copy['daily_ctr'] = df_copy['clicks'] / df_copy['impression']
    df_copy['daily_ctr'] = df_copy['daily_ctr'].replace([np.inf, -np.inf], 0)
    
    # Moving averages
    df_copy = df_copy.sort_values('date')
    df_copy['revenue_7d_ma'] = df_copy[revenue_col].rolling(window=7, min_periods=1).mean()
    df_copy['roas_7d_ma'] = df_copy['marketing_roas'].rolling(window=7, min_periods=1).mean()
    df_copy['spend_7d_ma'] = df_copy['spend'].rolling(window=7, min_periods=1).mean()
    
    return df_copy