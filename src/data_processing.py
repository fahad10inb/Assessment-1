import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_and_process_data(file_path='data/processed/unified_marketing_business_data.csv'):
    """
    Load and process the unified marketing and business data
    
    Args:
        file_path (str): Path to the CSV file
    
    Returns:
        pd.DataFrame: Processed dataframe
    """
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Data loaded successfully. Shape: {df.shape}")
        
        # Data type conversions
        df['date'] = pd.to_datetime(df['date'])
        
        # Rename columns to standardize naming
        column_mapping = {
            '# of orders': 'orders',
            '# of new orders': 'new_orders',
            'total revenue': 'total_revenue',
            'gross profit': 'gross_profit',
            'attributed revenue': 'attributed_revenue'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Data validation and cleaning
        df = validate_and_clean_data(df)
        
        # Calculate additional derived metrics
        df = calculate_derived_metrics(df)
        
        logger.info("Data processing completed successfully")
        return df
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise

def validate_and_clean_data(df):
    """
    Validate and clean the dataset
    
    Args:
        df (pd.DataFrame): Input dataframe
    
    Returns:
        pd.DataFrame: Cleaned dataframe
    """
    logger.info("Starting data validation and cleaning")
    
    # Check for missing values
    missing_data = df.isnull().sum()
    if missing_data.any():
        logger.warning(f"Missing values found:\n{missing_data[missing_data > 0]}")
    
    # Fill missing values with 0 for numeric columns
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(0)
    
    # Ensure no negative values for key metrics
    financial_columns = [
        'total_revenue', 'gross_profit', 'COGS', 'spend', 
        'facebook_spend', 'google_spend', 'tiktok_spend',
        'attributed_revenue', 'facebook_attributed revenue', 
        'google_attributed revenue', 'tiktok_attributed revenue'
    ]
    
    for col in financial_columns:
        if col in df.columns:
            df[col] = df[col].clip(lower=0)
    
    # Validate ROAS calculations
    df['calculated_marketing_roas'] = np.where(
        df['spend'] > 0, 
        df['attributed_revenue'] / df['spend'], 
        0
    )
    
    # Check if calculated ROAS matches existing ROAS (within tolerance)
    if 'marketing_roas' in df.columns:
        roas_diff = abs(df['marketing_roas'] - df['calculated_marketing_roas'])
        if roas_diff.max() > 0.1:  # tolerance of 0.1
            logger.warning("ROAS calculations don't match existing values")
    
    # Remove outliers (values beyond 3 standard deviations)
    for col in ['marketing_roas', 'total_revenue', 'orders']:
        if col in df.columns:
            mean_val = df[col].mean()
            std_val = df[col].std()
            df = df[abs(df[col] - mean_val) <= 3 * std_val]
    
    logger.info(f"Data cleaning completed. Final shape: {df.shape}")
    return df

def calculate_derived_metrics(df):
    """
    Calculate additional derived metrics for analysis
    
    Args:
        df (pd.DataFrame): Input dataframe
    
    Returns:
        pd.DataFrame: Dataframe with additional metrics
    """
    logger.info("Calculating derived metrics")
    
    # Customer Acquisition Cost (CAC)
    df['cac'] = np.where(
        df['new customers'] > 0, 
        df['spend'] / df['new customers'], 
        0
    )
    
    # Average Order Value (AOV)
    df['aov'] = np.where(
        df['orders'] > 0, 
        df['total_revenue'] / df['orders'], 
        0
    )
    
    # Click-through Rate (CTR)
    df['ctr'] = np.where(
        df['impression'] > 0, 
        df['clicks'] / df['impression'], 
        0
    )
    
    # Cost Per Click (CPC)
    df['cpc'] = np.where(
        df['clicks'] > 0, 
        df['spend'] / df['clicks'], 
        0
    )
    
    # Conversion Rate
    df['conversion_rate'] = np.where(
        df['clicks'] > 0, 
        df['orders'] / df['clicks'], 
        0
    )
    
    # Platform-specific CTRs
    for platform in ['facebook', 'google', 'tiktok']:
        impression_col = f'{platform}_impression'
        clicks_col = f'{platform}_clicks'
        
        if impression_col in df.columns and clicks_col in df.columns:
            df[f'{platform}_ctr'] = np.where(
                df[impression_col] > 0,
                df[clicks_col] / df[impression_col],
                0
            )
    
    # Platform-specific CPCs
    for platform in ['facebook', 'google', 'tiktok']:
        spend_col = f'{platform}_spend'
        clicks_col = f'{platform}_clicks'
        
        if spend_col in df.columns and clicks_col in df.columns:
            df[f'{platform}_cpc'] = np.where(
                df[clicks_col] > 0,
                df[spend_col] / df[clicks_col],
                0
            )
    
    # Platform-specific ROAS
    for platform in ['facebook', 'google', 'tiktok']:
        spend_col = f'{platform}_spend'
        revenue_col = f'{platform}_attributed revenue'
        
        if spend_col in df.columns and revenue_col in df.columns:
            df[f'{platform}_roas'] = np.where(
                df[spend_col] > 0,
                df[revenue_col] / df[spend_col],
                0
            )
    
    # Revenue per impression
    df['revenue_per_impression'] = np.where(
        df['impression'] > 0,
        df['total_revenue'] / df['impression'],
        0
    )
    
    # Day of week analysis
    df['day_of_week'] = df['date'].dt.day_name()
    df['week_number'] = df['date'].dt.isocalendar().week
    df['month'] = df['date'].dt.month
    
    # Moving averages (7-day)
    df = df.sort_values('date')
    df['revenue_7d_ma'] = df['total_revenue'].rolling(window=7, min_periods=1).mean()
    df['roas_7d_ma'] = df['marketing_roas'].rolling(window=7, min_periods=1).mean()
    df['orders_7d_ma'] = df['orders'].rolling(window=7, min_periods=1).mean()
    
    logger.info("Derived metrics calculation completed")
    return df

def create_summary_stats(df):
    """
    Create summary statistics for the dataset
    
    Args:
        df (pd.DataFrame): Input dataframe
    
    Returns:
        dict: Summary statistics
    """
    summary = {
        'date_range': {
            'start': df['date'].min(),
            'end': df['date'].max(),
            'days': (df['date'].max() - df['date'].min()).days
        },
        'business_metrics': {
            'total_revenue': df['total_revenue'].sum(),
            'total_orders': df['orders'].sum(),
            'avg_aov': df['aov'].mean(),
            'avg_profit_margin': df['profit_margin'].mean()
        },
        'marketing_metrics': {
            'total_spend': df['spend'].sum(),
            'avg_roas': df['marketing_roas'].mean(),
            'total_clicks': df['clicks'].sum(),
            'avg_ctr': df['ctr'].mean()
        },
        'platform_breakdown': {}
    }
    
    # Platform-specific summaries
    for platform in ['facebook', 'google', 'tiktok']:
        spend_col = f'{platform}_spend'
        revenue_col = f'{platform}_attributed revenue'
        clicks_col = f'{platform}_clicks'
        
        if all(col in df.columns for col in [spend_col, revenue_col, clicks_col]):
            summary['platform_breakdown'][platform] = {
                'spend': df[spend_col].sum(),
                'attributed_revenue': df[revenue_col].sum(),
                'clicks': df[clicks_col].sum(),
                'roas': df[revenue_col].sum() / df[spend_col].sum() if df[spend_col].sum() > 0 else 0
            }
    
    return summary

def export_processed_data(df, output_path='data/processed/cleaned_unified_data.csv'):
    """
    Export processed data to CSV
    
    Args:
        df (pd.DataFrame): Processed dataframe
        output_path (str): Output file path
    """
    try:
        df.to_csv(output_path, index=False)
        logger.info(f"Processed data exported to {output_path}")
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage
    df = load_and_process_data()
    summary = create_summary_stats(df)
    print("Data Summary:")
    print(f"Date Range: {summary['date_range']['start']} to {summary['date_range']['end']}")
    print(f"Total Revenue: ${summary['business_metrics']['total_revenue']:,.2f}")
    print(f"Total Spend: ${summary['marketing_metrics']['total_spend']:,.2f}")
    print(f"Average ROAS: {summary['marketing_metrics']['avg_roas']:.2f}")