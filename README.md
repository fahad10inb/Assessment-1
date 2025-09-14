# Marketing Performance Dashboard

A comprehensive Streamlit-based dashboard for analyzing marketing performance across multiple platforms including Facebook, Google, and TikTok.

## 📊 Features

- **Multi-Platform Analytics**: Track performance across Facebook, Google, and TikTok advertising platforms
- **Key Metrics**: Monitor ROAS, CTR, CPC, CPM, and revenue attribution
- **Interactive Visualizations**: Dynamic charts for spend vs revenue comparison and ROAS analysis
- **Real-time Data**: Cached data loading for optimal performance
- **Responsive Design**: Modern dark theme with responsive layout

## 🚀 Technologies Used

- **Streamlit** - Web application framework
- **Pandas** - Data manipulation and analysis
- **Plotly** - Interactive data visualization
- **NumPy** - Numerical computing

## 📋 Prerequisites

- Python 3.7 or higher
- pip package manager

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/fahad10inb/Assessment-1.git
   cd Assessment-1
   ```

2. **Install required packages**
   ```bash
   pip install streamlit pandas plotly numpy
   ```

3. **Prepare your data**
   - Ensure your CSV file is named `unified_marketing_business_data.csv`
   - Place it in either the root directory or `data/processed/` folder
   - Required columns:
     - `date` - Date column
     - `facebook_spend`, `google_spend`, `tiktok_spend` - Platform spending
     - `facebook_attributed revenue`, `google_attributed revenue`, `tiktok_attributed revenue` - Revenue attribution
     - `facebook_clicks`, `google_clicks`, `tiktok_clicks` - Click data
     - `facebook_impression`, `google_impression`, `tiktok_impression` - Impression data

## 🏃‍♂️ Running the Application

```bash
streamlit run marketing_performance.py
```

The application will open in your default web browser at `http://localhost:8501`

## 📊 Dashboard Sections

### Platform Performance Overview
- **ROAS Metrics**: Return on Ad Spend for each platform
- **Spend Analysis**: Total advertising spend per platform
- **Revenue Tracking**: Attributed revenue from each platform
- **Performance Indicators**: CTR, CPC, and other key metrics

### Performance Charts
- **Spend vs Revenue**: Side-by-side comparison of investment and returns
- **ROAS Comparison**: Visual comparison of return on ad spend across platforms

## 📁 Project Structure

```
Assessment-1/
├── marketing_performance.py    # Main dashboard application
├── shared_style.py            # Styling and theme configuration
├── unified_marketing_business_data.csv  # Data file
├── data/
│   └── processed/
│       └── unified_marketing_business_data.csv
└── README.md
```

## 🎨 Styling

The dashboard uses a custom dark theme with:
- Modern gradient backgrounds
- Consistent color palette
- Responsive design elements
- Interactive hover effects
- Professional typography (Montserrat & Open Sans)

## 📈 Metrics Calculated

| Metric | Description | Formula |
|--------|-------------|---------|
| ROAS | Return on Ad Spend | Revenue ÷ Spend |
| CTR | Click Through Rate | (Clicks ÷ Impressions) × 100 |
| CPC | Cost Per Click | Spend ÷ Clicks |
| CPM | Cost Per Mille | (Spend ÷ Impressions) × 1000 |
| Revenue per Click | Average revenue per click | Revenue ÷ Clicks |

## 🔧 Customization

### Adding New Platforms
To add a new advertising platform:
1. Update the `platforms` list in the `main()` function
2. Ensure your CSV has the corresponding columns (e.g., `newplatform_spend`, `newplatform_attributed revenue`)
3. The dashboard will automatically include the new platform in calculations and visualizations

### Modifying Metrics
Edit the `calculate_platform_metrics()` function to add or modify calculated metrics.

### Styling Changes
Modify `shared_style.py` to customize colors, fonts, and layout elements.

## 📊 Data Format Requirements

Your CSV file should contain the following columns:
- `date`: Date in YYYY-MM-DD format
- Platform-specific columns for each platform (facebook, google, tiktok):
  - `{platform}_spend`: Advertising spend
  - `{platform}_attributed revenue`: Revenue attributed to the platform
  - `{platform}_clicks`: Number of clicks
  - `{platform}_impression`: Number of impressions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Fahad**
- GitHub: [@fahad10inb](https://github.com/fahad10inb)

## 📞 Support

If you encounter any issues or have questions:
1. Check the existing [Issues](https://github.com/fahad10inb/Assessment-1/issues)
2. Create a new issue if your problem isn't already addressed
3. Provide detailed information about your environment and the issue

---

⭐ **Star this repository if it helped you!**
