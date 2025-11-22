import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(
    page_title="Shopping Trends Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    h1 {
        color: #1f2937;
        font-weight: 700;
    }
    h2 {
        color: #374151;
        font-weight: 600;
        margin-top: 2rem;
    }
    .stButton button {
        width: 100%;
    }
    .section-header {
        background-color: #3b82f6;
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 30px 0 20px 0;
        text-align: center;
        font-size: 1.5em;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_items' not in st.session_state:
    st.session_state.selected_items = []
if 'selected_age_group' not in st.session_state:
    st.session_state.selected_age_group = []
if 'selected_categories' not in st.session_state:
    st.session_state.selected_categories = []
if 'checkbox_reset_counter' not in st.session_state:
    st.session_state.checkbox_reset_counter = 0

# Load Data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('Shopping_behavior_updated.csv')
    except FileNotFoundError:
        st.error("Error: 'Shopping_behavior_updated.csv' not found. Please ensure the file is in the correct path.")
        return pd.DataFrame() 
        
    # Clean data
    df = df.dropna()
    df = df.drop_duplicates()
    df['Review Rating'] = pd.to_numeric(df['Review Rating'], errors='coerce')
    df['Purchase Amount (USD)'] = pd.to_numeric(df['Purchase Amount (USD)'], errors='coerce')
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    return df

df = load_data()

# Handle empty data case
if df.empty:
    st.stop()

# SIDEBAR 
st.sidebar.title("Dashboard Filters")
st.sidebar.markdown("---")

# Reset all filters button
if st.sidebar.button("Reset All Filters", use_container_width=True):
    st.session_state.selected_items = []
    st.session_state.selected_age_group = []
    st.session_state.selected_categories = []
    st.session_state.checkbox_reset_counter += 1
    st.rerun()

st.sidebar.markdown("### Manual Filters")

# Gender filter
selected_gender = st.sidebar.multiselect(
    "Gender",
    options=df['Gender'].unique(),
    default=df['Gender'].unique()
)

# Season filter
selected_season = st.sidebar.multiselect(
    "Season",
    options=df['Season'].unique(),
    default=df['Season'].unique()
)

# Category filter
selected_category = st.sidebar.multiselect(
    "Category",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

# Age range slider
age_range = st.sidebar.slider(
    "Age Range",
    int(df['Age'].min()),
    int(df['Age'].max()),
    (int(df['Age'].min()), int(df['Age'].max()))
)

# Purchase amount range slider
purchase_range = st.sidebar.slider(
    "Purchase Amount Range (USD)",
    int(df['Purchase Amount (USD)'].min()),
    int(df['Purchase Amount (USD)'].max()),
    (int(df['Purchase Amount (USD)'].min()), int(df['Purchase Amount (USD)'].max()))
)

# Show active interactive filters
st.sidebar.markdown("---")
st.sidebar.markdown("### Active Interactive Filters")

if st.session_state.selected_items:
    st.sidebar.info(f"Items: {len(st.session_state.selected_items)} selected")

if st.session_state.selected_age_group:
    st.sidebar.info(f"Age Groups: {', '.join(st.session_state.selected_age_group)}")

if st.session_state.selected_categories:
    st.sidebar.info(f"Categories: {', '.join(st.session_state.selected_categories)}")

# Apply manual filters only (no interactive filters yet)
filtered_df = df[
    (df['Gender'].isin(selected_gender)) &
    (df['Season'].isin(selected_season)) &
    (df['Category'].isin(selected_category)) &
    (df['Age'].between(age_range[0], age_range[1])) &
    (df['Purchase Amount (USD)'].between(purchase_range[0], purchase_range[1]))
]

# Apply interactive filters for other visualizations
final_filtered_df = filtered_df.copy()

if st.session_state.selected_items:
    final_filtered_df = final_filtered_df[final_filtered_df['Item Purchased'].isin(st.session_state.selected_items)]

if st.session_state.selected_age_group:
    age_groups_temp = pd.cut(final_filtered_df['Age'], bins=[0, 25, 35, 45, 55, 65, 100], 
                        labels=['18-25', '26-35', '36-45', '46-55', '56-65', '65+'])
    final_filtered_df = final_filtered_df[age_groups_temp.isin(st.session_state.selected_age_group)]

if st.session_state.selected_categories:
    final_filtered_df = final_filtered_df[final_filtered_df['Category'].isin(st.session_state.selected_categories)]

st.sidebar.markdown("---")
st.sidebar.metric("Filtered Records", f"{len(final_filtered_df):,} / {len(df):,}")

# Handle empty data after filtering
if final_filtered_df.empty:
    st.warning("No data matches the current filters. Please adjust your selections.")
    st.stop()

# MAIN CONTENT 
st.title("Interactive Shopping Trends Analysis Dashboard")
st.markdown("""
Welcome to the Interactive Shopping Dashboard. Click on any visualization to filter all others dynamically.
- **3 Basic + 6 Advanced Visualizations** with full interactivity
- Real-time filtering across all charts
- Business insights for strategic decision-making
""")

# VISUALIZATION 1: PIE CHART - Sales Distribution by Category
st.header("1. Pie Chart - Sales Distribution by Category")
col1, col2 = st.columns([3, 1])

with col1:
    category_sales = final_filtered_df.groupby('Category')['Purchase Amount (USD)'].sum().reset_index()
    
    fig3 = px.pie(
        category_sales,
        values='Purchase Amount (USD)',
        names='Category',
        title='Sales Distribution by Category',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig3.update_traces(textposition='inside', textinfo='percent+label')
    fig3.update_layout(height=450)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.markdown("**Select Categories:**")
    category_list = df['Category'].unique().tolist()
    
    new_cat_selection = []
    
    for cat in category_list:
        if st.checkbox(cat, value=cat in st.session_state.selected_categories, 
                      key=f'cat_checkbox_{cat}_{st.session_state.checkbox_reset_counter}'):
            new_cat_selection.append(cat)
    
    if set(new_cat_selection) != set(st.session_state.selected_categories):
        st.session_state.selected_categories = new_cat_selection
        st.rerun()
    
    if st.button("Clear Categories", key='clear_cat', use_container_width=True):
        st.session_state.selected_categories = []
        st.session_state.checkbox_reset_counter += 1
        st.rerun()

with st.expander("View Insights - Pie Chart"):
    st.write("""
    **Purpose:** Shows the proportion of total sales contributed by each product category
    
    **Insight:** Reveals which categories dominate the revenue stream
    
    **Business Value:** Guides resource allocation and category-specific strategies
    """)

st.markdown("---")

# VISUALIZATION 2: TREEMAP - Sales Hierarchy
st.header("2. Treemap - Sales Hierarchy")
if len(final_filtered_df) > 0:
    treemap_data = final_filtered_df.groupby(['Category', 'Item Purchased'])['Purchase Amount (USD)'].sum().reset_index()
    
    fig4 = px.treemap(
        treemap_data,
        path=['Category', 'Item Purchased'],
        values='Purchase Amount (USD)',
        color='Purchase Amount (USD)',
        color_continuous_scale='Blues',
        title='Category to Item Hierarchy (Hover for details)'
    )
    fig4.update_layout(height=500)
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("Insufficient data for Treemap.")

with st.expander("View Insights - Treemap"):
    st.write("""
    **Purpose:** Hierarchical view of sales by category and individual items
    
    **Insight:** Larger rectangles indicate higher sales volume, allowing quick visual comparison
    
    **Business Value:** Identifies top-performing products within each category for strategic stocking
    """)

st.markdown("---")

# VISUALIZATION 3: CORRELATION HEATMAP - Numerical Variables
st.header("3. Correlation Heatmap - Numerical Variables")

numeric_cols = ['Age', 'Purchase Amount (USD)', 'Review Rating', 'Previous Purchases']

if len(final_filtered_df) > 1:
    correlation_data = final_filtered_df[numeric_cols].corr()
    
    fig9, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        correlation_data, 
        annot=True, 
        fmt='.2f',
        cmap='RdBu_r', 
        center=0, 
        square=True, 
        linewidths=1,
        vmin=-1, 
        vmax=1,
        cbar_kws={'label': 'Correlation Coefficient'}
    )
    plt.title('Correlation Matrix of Numerical Variables', fontsize=16, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig9)
    plt.close()
else:
    st.info("Insufficient data for Correlation Heatmap.")

with st.expander("View Insights - Correlation Heatmap"):
    st.write("""
    **Purpose:** Shows statistical correlations between all numerical variables in the dataset
    
    **Insight:** Values close to 1 or -1 indicate strong positive or negative relationships
    
    **Business Value:** Helps understand which factors most strongly influence purchase behavior
    """)

st.markdown("---")