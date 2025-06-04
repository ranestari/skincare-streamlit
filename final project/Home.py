import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Skincare Review Dashboard", layout="wide")

# Load and clean data
df = pd.read_csv("skincare_merged.csv")
df = df.dropna(subset=['Product', 'Review', 'Rating', 'Merk', 'Category'])


# Title
st.title("🧴 Skincare Review Dashboard")
st.markdown("Welcome! This dashboard helps you explore user reviews of skincare products across all brands and categories.")

st.image("https://www.bellobello.my/wp-content/uploads/2022/08/boldlipessentials-2.jpg", caption="Top Skincare Products")
st.markdown("---")
st.markdown("## 🏆 Top Skincare Product by Year and Category")

# Pastikan format tanggal
df['PostDate'] = pd.to_datetime(df['PostDate'], errors='coerce')
df['Year'] = df['PostDate'].dt.year

# Bersihkan data
valid_df = df.dropna(subset=['Year', 'Category', 'Product', 'Merk'])

# Dropdown tahun
available_years = sorted(valid_df['Year'].dropna().unique())
selected_year = st.selectbox("Select Year", available_years)

# Filter data berdasarkan tahun terlebih dahulu
year_filtered_df = valid_df[valid_df['Year'] == selected_year]

# Dropdown kategori yang hanya tersedia di tahun tersebut
available_categories = sorted(year_filtered_df['Category'].dropna().unique())
selected_category = st.selectbox("Select Category", available_categories)

# Filter akhir berdasarkan tahun dan kategori
filtered = year_filtered_df[year_filtered_df['Category'] == selected_category]

# Hitung statistik produk
summary = filtered.groupby(['Product', 'Merk']).agg(
    Total_Reviews=('Review', 'count'),
    Avg_Rating=('Rating', 'mean')
).reset_index().sort_values(by='Total_Reviews', ascending=False)

# Slider untuk top-N
top_n = st.slider("How many top products to show?", min_value=1, max_value=10, value=5)
top_products = summary.head(top_n)

# Tampilkan tabel
st.markdown(f"### 📋 Top {top_n} Products in '{selected_category}' – {selected_year}")
st.dataframe(top_products)

# Visualisasi bar chart
fig = px.bar(top_products, x='Product', y='Total_Reviews', color='Merk',
             text='Avg_Rating', title=f"Top {top_n} Products in {selected_category} ({selected_year})")
fig.update_traces(textposition='outside')
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("## 🌐 Explore All Brands & Categories")

# Filters
selected_brands = st.multiselect("Select Brands", sorted(df['Merk'].dropna().unique()))
selected_categories = st.multiselect("Select Categories", sorted(df['Category'].dropna().unique()))
sort_by = st.radio("Sort By", ["Total_Reviews", "Average_Rating", "Unique_Reviewers"])

# Apply filters
filtered_df = df.copy()
if selected_brands:
    filtered_df = filtered_df[filtered_df['Merk'].isin(selected_brands)]
if selected_categories:
    filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]

# Display results
if filtered_df.empty:
    st.info("No data available for the selected filters.")
else:
    summary = filtered_df.groupby(['Merk', 'Product', 'Category']).agg(
        Total_Reviews=('Review', 'count'),
        Average_Rating=('Rating', 'mean'),
        Unique_Reviewers=('UserName', pd.Series.nunique)
    ).reset_index().sort_values(by=sort_by, ascending=False)

    st.dataframe(summary)

