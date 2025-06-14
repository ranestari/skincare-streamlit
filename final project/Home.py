import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re

# Page config
st.set_page_config(page_title="Skincare Review Dashboard", layout="wide")

# Load and clean data
df = pd.read_csv("final project/skincare_merged.csv")
df = df.dropna(subset=['Product', 'Review', 'Rating', 'Merk', 'Category'])
df['Price'] = df['Price'].astype(str).str.replace(r'[^\d]', '', regex=True)
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
df['PostDate'] = pd.to_datetime(df['PostDate'], errors='coerce')
df['Year'] = df['PostDate'].dt.year

# Title
st.title("Skincare Review Dashboard")
st.markdown("Welcome! This dashboard helps you explore user reviews of skincare products across all brands and categories.")
st.markdown('<img src="https://www.bellobello.my/wp-content/uploads/2022/08/boldlipessentials-2.jpg" alt="Top Skincare Products" style="width:100%; max-width:700px; border-radius:10px; display:block; margin:auto;">', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Year & Category", "All Brands", "Price vs Rating", "Dashboard Overview", "Additional Insights"])

with tab1:
    st.markdown("## Top Skincare Product by Year and Category")
    valid_df = df.dropna(subset=['Year', 'Category', 'Product', 'Merk'])
    available_years = sorted(valid_df['Year'].dropna().unique())
    selected_year = st.selectbox("Select Year", available_years)
    year_filtered_df = valid_df[valid_df['Year'] == selected_year]
    available_categories = sorted(year_filtered_df['Category'].dropna().unique())
    selected_category = st.selectbox("Select Category", available_categories)
    filtered = year_filtered_df[year_filtered_df['Category'] == selected_category]
    summary = filtered.groupby(['Product', 'Merk']).agg(
        Total_Reviews=('Review', 'count'),
        Avg_Rating=('Rating', 'mean')
    ).reset_index().sort_values(by='Total_Reviews', ascending=False)
    top_n = st.slider("How many top products to show?", min_value=1, max_value=10, value=5)
    top_products = summary.head(top_n)
    st.dataframe(top_products)
    fig = px.bar(top_products, x='Product', y='Total_Reviews', color='Merk',
                 text='Avg_Rating', title=f"Top {top_n} Products in {selected_category} ({selected_year})")
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("## Explore All Brands & Categories")
    selected_brands = st.multiselect("Select Brands", sorted(df['Merk'].dropna().unique()))
    selected_categories = st.multiselect("Select Categories", sorted(df['Category'].dropna().unique()))
    sort_by = st.radio("Sort By", ["Total_Reviews", "Average_Rating", "Unique_Reviewers"])
    filtered_df = df.copy()
    if selected_brands:
        filtered_df = filtered_df[filtered_df['Merk'].isin(selected_brands)]
    if selected_categories:
        filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]
    if filtered_df.empty:
        st.info("No data available for the selected filters.")
    else:
        summary = filtered_df.groupby(['Merk', 'Product', 'Category']).agg(
            Total_Reviews=('Review', 'count'),
            Average_Rating=('Rating', 'mean'),
            Unique_Reviewers=('UserName', pd.Series.nunique)
        ).reset_index().sort_values(by=sort_by, ascending=False)
        st.dataframe(summary)

with tab3:
    st.markdown("## Price vs Rating")
    valid_df = df.dropna(subset=['Price', 'Rating', 'Product', 'Merk', 'Category'])
    valid_df = valid_df[valid_df['Price'] > 0]
    if valid_df.empty:
        st.warning("No valid data available for visualization.")
    else:
        st.markdown("### Filter")
        min_price = int(valid_df['Price'].min())
        max_price = int(valid_df['Price'].max())
        col1, col2 = st.columns(2)
        with col1:
            min_price_input = st.number_input("Minimum Price (IDR)", min_value=min_price, max_value=max_price, value=min_price, step=1000)
        with col2:
            max_price_input = st.number_input("Maximum Price (IDR)", min_value=min_price, max_value=max_price, value=max_price, step=1000)
        rating_range = st.slider("Select Rating Range", 0.0, 5.0, (3.0, 5.0), step=0.1)
        selected_categories = st.multiselect("Select Product Categories", sorted(valid_df['Category'].dropna().unique()), key="category_filter_price_rating")
        filtered_df = valid_df[
            (valid_df['Price'] >= min_price_input) &
            (valid_df['Price'] <= max_price_input) &
            (valid_df['Rating'] >= rating_range[0]) &
            (valid_df['Rating'] <= rating_range[1])
        ]
        if selected_categories:
            filtered_df = filtered_df[filtered_df['Category'].isin(selected_categories)]
        if filtered_df.empty:
            st.info("No data available for the selected filter combination.")
        else:
            fig_price = px.scatter(
                filtered_df,
                x='Price',
                y='Rating',
                color='Category',
                hover_data=['Product', 'Merk'],
                title="Price vs Rating",
                labels={'Price': 'Price (IDR)', 'Rating': 'User Rating'}
            )
            fig_price.update_traces(marker=dict(opacity=0.6))
            fig_price.update_layout(xaxis_title="Price (Rp)", yaxis_title="Rating (1–5)")
            st.plotly_chart(fig_price, use_container_width=True)
            st.markdown("### Rating Distribution (Pie Chart)")
            rating_bins = filtered_df['Rating'].round(1)
            rating_count = rating_bins.value_counts().sort_index()
            fig_pie = px.pie(
                names=rating_count.index,
                values=rating_count.values,
                title="Rating Distribution (Rounded to 0.1)",
                labels={'names': 'Rating', 'values': 'Count'}
            )
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
            sorted_table = filtered_df.sort_values(by=['Rating', 'Price'], ascending=[False, True])[
                ['Category', 'Merk', 'Product', 'Price', 'Rating']
            ].reset_index(drop=True)
            st.dataframe(sorted_table)

with tab4:
    st.markdown("## Dashboard Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reviews", f"{len(df):,}")
    col2.metric("Most Reviewed Product", df['Product'].value_counts().idxmax())
    col3.metric("Highest Rated Product", df.loc[df['Rating'].idxmax()]['Product'])
    st.markdown("---")
    st.markdown("### Trend of Reviews and Ratings")
    yearly_trend = df.groupby('Year').agg(Review_Count=('Review', 'count'), Avg_Rating=('Rating', 'mean')).reset_index()
    fig_trend = px.line(yearly_trend, x='Year', y='Review_Count', title='Total Reviews per Year')
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown("---")
    st.markdown("### Wordcloud from User Reviews")
    text = " ".join(df['Review'].dropna().astype(str).tolist())
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    fig_wc, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig_wc)
    st.markdown("---")
    st.markdown("### Best & Worst Reviewed Products")
    top_rated = df[df['Rating'] >= 4.5].groupby(['Merk', 'Product']).size().reset_index(name='Total_Reviews').sort_values(by='Total_Reviews', ascending=False).head(5)
    low_rated = df[df['Rating'] <= 2.5].groupby(['Merk', 'Product']).size().reset_index(name='Total_Reviews').sort_values(by='Total_Reviews', ascending=False).head(5)
    st.markdown("#### Top Rated Products")
    st.dataframe(top_rated)
    st.markdown("#### Low Rated Products")
    st.dataframe(low_rated)
    st.markdown("---")
    st.markdown("### Average Rating and Price per Brand")
    pivot = df.groupby('Merk').agg(Avg_Price=('Price', 'mean'), Avg_Rating=('Rating', 'mean')).dropna().sort_values(by='Avg_Rating', ascending=False)
    pivot = pivot[(pivot['Avg_Price'] > 0) & (pivot['Avg_Rating'] > 0)]
    fig_heatmap = px.imshow(pivot.T, aspect='auto', labels={'x': 'Brand', 'y': 'Metric', 'color': 'Value'}, title="Heatmap of Average Price and Rating per Brand")
    st.plotly_chart(fig_heatmap, use_container_width=True)
    st.markdown("---")
    st.markdown("### Export All Cleaned Data")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name="skincare_cleaned_data.csv", mime='text/csv')

with tab5:
    df = df[df['Price'] > 0]
    st.markdown("### 📊 Histogram of Ratings")
    fig_hist_rating = px.histogram(df, x='Rating', nbins=20, title="Distribution of Ratings")
    st.plotly_chart(fig_hist_rating, use_container_width=True)

    st.markdown("### 📊 Histogram of Prices")
    price_df = df[df['Price'] > 0]
    fig_hist_price = px.histogram(price_df, x='Price', nbins=30, title="Distribution of Prices")
    st.plotly_chart(fig_hist_price, use_container_width=True)

    st.markdown("### 📦 Box Plot of Rating per Category")
    fig_box = px.box(df, x="Category", y="Rating", title="Rating Distribution by Category")
    st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("### 📈 Top 10 Reviewed Products")
    top_reviewed = df.groupby(['Product', 'Category', 'Merk'])['Review'].count().reset_index(name='Total_Reviews')
    top_reviewed = top_reviewed.sort_values(by='Total_Reviews', ascending=False).head(10)
    fig_bar = px.bar(top_reviewed, x='Product', y='Total_Reviews', color='Category', title='Top 10 Most Reviewed Products', hover_data=['Merk'])
    st.plotly_chart(fig_bar, use_container_width=True)
