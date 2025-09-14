# shared_style.py
import streamlit as st

# 🎨 Unified Design System
DESIGN_SYSTEM = {
    # Color Palette
    "background_primary": "#1e1e2f",
    "background_secondary": "#2a2a40", 
    "surface_elevated": "#353551",
    "primary": "#4f92ff",
    "primary_light": "#7bb4ff",
    "primary_dark": "#1a52c2",
    "secondary": "#5f40d4",
    "success": "#3edd98",
    "warning": "#f0b30b",
    "error": "#ff5c5c",
    "text_primary": "#f8faff",
    "text_secondary": "#c9c9d8",
    "text_muted": "#a3a3b2",
    "border": "#444555",
    "accent": "#ffffff",
    
    # Typography
    "font_heading": "'Montserrat', sans-serif",
    "font_body": "'Open Sans', sans-serif",
    "font_mono": "'JetBrains Mono', monospace"
}

def apply_shared_styles():
    """Apply consistent styling across all pages"""
    css = f'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&family=Open+Sans:wght@400;500;600&display=swap');

    /* Global Styles */
    body, .main, .stApp {{
        background: {DESIGN_SYSTEM['background_primary']};
        color: {DESIGN_SYSTEM['text_primary']};
        font-family: {DESIGN_SYSTEM['font_body']};
        line-height: 1.6;
    }}

    /* Typography */
    h1, h2, h3, h4, h5, h6, .dashboard-title {{
        font-family: {DESIGN_SYSTEM['font_heading']};
        color: {DESIGN_SYSTEM['primary']};
    }}

    .dashboard-title {{
        font-size: 2.75rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-align: center;
        background: linear-gradient(135deg, {DESIGN_SYSTEM['primary']}, {DESIGN_SYSTEM['primary_light']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
    }}

    .dashboard-subtitle {{
        font-size: 1.1rem;
        color: {DESIGN_SYSTEM['text_secondary']};
        margin-bottom: 2.5rem;
        text-align: center;
        font-weight: 400;
    }}

    .section-header {{
        font-family: {DESIGN_SYSTEM['font_heading']};
        font-size: 1.6rem;
        font-weight: 600;
        color: {DESIGN_SYSTEM['text_primary']};
        border-bottom: 3px solid {DESIGN_SYSTEM['primary']};
        padding-bottom: 0.5rem;
        margin: 2rem 0 1.5rem 0;
        position: relative;
    }}

    .section-header::after {{
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 60px;
        height: 3px;
        background: {DESIGN_SYSTEM['primary_light']};
    }}

    /* Card System */
    .metric-card {{
        background: linear-gradient(145deg, {DESIGN_SYSTEM['background_secondary']}, {DESIGN_SYSTEM['surface_elevated']});
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.2rem;
        border: 1px solid {DESIGN_SYSTEM['border']};
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }}

    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, {DESIGN_SYSTEM['primary']}, {DESIGN_SYSTEM['secondary']});
        opacity: 0;
        transition: opacity 0.3s ease;
    }}

    .metric-card:hover {{
        transform: translateY(-3px);
        border-color: {DESIGN_SYSTEM['primary_light']};
        box-shadow: 0 8px 25px rgba(79, 146, 255, 0.15);
    }}

    .metric-card:hover::before {{
        opacity: 1;
    }}

    .metric-label {{
        font-family: {DESIGN_SYSTEM['font_body']};
        font-weight: 600;
        font-size: 0.85rem;
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
        font-weight: 700;
        font-size: 2.2rem;
        color: {DESIGN_SYSTEM['text_primary']};
        margin-bottom: 0.75rem;
        letter-spacing: -0.02em;
    }}

    .metric-delta {{
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.375rem 0.75rem;
        border-radius: 20px;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.2s ease;
    }}

    .metric-delta.positive {{
        background-color: rgba(61, 221, 152, 0.15);
        color: {DESIGN_SYSTEM['success']};
        border: 1px solid rgba(61, 221, 152, 0.3);
    }}

    .metric-delta.negative {{
        background-color: rgba(255, 92, 92, 0.15);
        color: {DESIGN_SYSTEM['error']};
        border: 1px solid rgba(255, 92, 92, 0.3);
    }}

    .metric-delta.neutral {{
        background-color: rgba(240, 179, 11, 0.15);
        color: {DESIGN_SYSTEM['warning']};
        border: 1px solid rgba(240, 179, 11, 0.3);
    }}

    /* Insight Cards */
    .insight-card {{
        background: {DESIGN_SYSTEM['background_secondary']};
        border: 1px solid {DESIGN_SYSTEM['border']};
        border-left: 4px solid {DESIGN_SYSTEM['primary']};
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}

    .insight-card:hover {{
        border-left-color: {DESIGN_SYSTEM['primary_light']};
        transform: translateX(4px);
        box-shadow: 0 8px 25px rgba(79, 146, 255, 0.1);
    }}

    .insight-icon {{
        font-size: 1.5rem;
        margin-bottom: 0.75rem;
        color: {DESIGN_SYSTEM['primary']};
    }}

    .insight-title {{
        font-family: {DESIGN_SYSTEM['font_heading']};
        font-size: 1.1rem;
        font-weight: 600;
        color: {DESIGN_SYSTEM['text_primary']};
        margin-bottom: 0.5rem;
    }}

    .insight-description {{
        font-size: 0.9rem;
        color: {DESIGN_SYSTEM['text_secondary']};
        line-height: 1.5;
    }}

    /* Sidebar Styling */
    .sidebar .sidebar-content {{
        background: {DESIGN_SYSTEM['background_secondary']};
        border-right: 1px solid {DESIGN_SYSTEM['border']};
    }}

    .sidebar-section {{
        background: {DESIGN_SYSTEM['background_primary']};
        border: 1px solid {DESIGN_SYSTEM['border']};
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}

    .sidebar-title {{
        font-family: {DESIGN_SYSTEM['font_heading']};
        font-size: 0.9rem;
        font-weight: 600;
        color: {DESIGN_SYSTEM['primary']};
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    /* Form Controls */
    .stSelectbox > div > div {{
        background-color: {DESIGN_SYSTEM['background_secondary']};
        border: 1px solid {DESIGN_SYSTEM['border']};
        color: {DESIGN_SYSTEM['text_primary']};
    }}

    .stMultiSelect > div > div {{
        background-color: {DESIGN_SYSTEM['background_secondary']};
        border: 1px solid {DESIGN_SYSTEM['border']};
    }}

    .stDateInput > div > div > div {{
        background-color: {DESIGN_SYSTEM['background_secondary']};
        border: 1px solid {DESIGN_SYSTEM['border']};
        color: {DESIGN_SYSTEM['text_primary']};
    }}

    /* Hide Streamlit Elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stApp > header {{visibility: hidden;}}

    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}

    ::-webkit-scrollbar-track {{
        background: {DESIGN_SYSTEM['background_primary']};
    }}

    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(135deg, {DESIGN_SYSTEM['primary']}, {DESIGN_SYSTEM['primary_light']});
        border-radius: 4px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(135deg, {DESIGN_SYSTEM['primary_light']}, {DESIGN_SYSTEM['primary']});
    }}

    /* Responsive Design */
    @media (max-width: 768px) {{
        .dashboard-title {{
            font-size: 2.2rem;
        }}
        
        .metric-card {{
            padding: 1rem;
        }}
        
        .metric-value {{
            font-size: 1.8rem;
        }}
        
        .section-header {{
            font-size: 1.4rem;
        }}
    }}
    </style>
    '''
    st.markdown(css, unsafe_allow_html=True)

def apply_chart_theme(fig):
    """Apply consistent theme to charts"""
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor=DESIGN_SYSTEM['background_secondary'],
        font=dict(
            family=DESIGN_SYSTEM['font_body'], 
            color=DESIGN_SYSTEM['text_primary']
        ),
        title_font=dict(
            family=DESIGN_SYSTEM['font_heading'], 
            size=16, 
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
            color=DESIGN_SYSTEM['text_secondary']
        ),
        yaxis=dict(
            gridcolor=DESIGN_SYSTEM['border'], 
            color=DESIGN_SYSTEM['text_secondary']
        )
    )
    return fig

def safe_plotly_chart(fig, **kwargs):
    """Display charts with consistent theming"""
    try:
        fig = apply_chart_theme(fig)
        st.plotly_chart(fig, **kwargs)
    except Exception as e:
        st.error(f"Chart rendering error: {str(e)}")
