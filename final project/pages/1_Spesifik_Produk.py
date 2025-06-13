import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
import string



try:
    stop_words = set(stopwords.words('indonesian'))
except LookupError:
    nltk.download('stopwords')
    stop_words = set(stopwords.words('indonesian'))

st.set_page_config(page_title="Skincare Product Explorer", layout="wide")
st.title("🧴 Skincare Review Dashboard")
st.markdown("A visual explorer for user-submitted skincare reviews. Dive into ratings, favorites, and product feedback.")


# Load and clean data
df = pd.read_csv("final project/skincare_merged.csv")
df = df.dropna(subset=['Product', 'Review', 'Rating', 'Merk', 'Category'])

# Filter options
selected_brand = st.selectbox("Select Brand", sorted(df['Merk'].dropna().unique()))
categories = df[df['Merk'] == selected_brand]['Category'].dropna().unique()
selected_category = st.selectbox("Select Category", sorted(categories))

# Filter data
filtered_df = df[(df['Merk'] == selected_brand) & (df['Category'] == selected_category)]

if filtered_df.empty:
    st.warning("No data available for the selected combination.")
else:
    # Section: User Reviews
    st.subheader("💬 What People Said")
    st.caption("Browse through real user reviews based on selected brand and category.")
    st.dataframe(filtered_df[['Product', 'Rating', 'SkinCond_Age', 'Review', 'PostDate']])

    # Section: Favorite Products
    st.subheader("🏆 Favorite Products")
    fav_by_review = filtered_df['Product'].value_counts().idxmax()
    review_count = filtered_df['Product'].value_counts().max()

    top_rated = filtered_df.groupby('Product').filter(lambda x: len(x) >= 5)
    if not top_rated.empty:
        top_rated_product = top_rated.groupby('Product')['Rating'].mean().sort_values(ascending=False).idxmax()
        top_rated_score = top_rated.groupby('Product')['Rating'].mean().max()
    else:
        top_rated_product = "Not available"
        top_rated_score = "–"

    st.markdown(f"📌 Most Reviewed Product: **`{fav_by_review}`** ({review_count} reviews)")
    st.markdown(f"🌟 Highest Rated Product: **`{top_rated_product}`** (Average Rating: {top_rated_score:.2f})")

    # Section: Product Summary
    st.subheader(f"📋 Product Summary for Brand '{selected_brand}' in Category '{selected_category}'")
    category_df = df[(df['Merk'] == selected_brand) & (df['Category'] == selected_category)]

    summary_table = category_df.groupby('Product').agg(
        Total_Reviews=('Review', 'count'),
        Average_Rating=('Rating', 'mean'),
        Unique_Reviewers=('UserName', pd.Series.nunique)
    ).sort_values(by='Total_Reviews', ascending=False).reset_index()

    st.dataframe(summary_table)

    # Section: Rating Distribution
    st.subheader("📊 Rating Distribution by Product")

    produk_terfilter = category_df['Product'].dropna().unique()
    selected_product = st.selectbox("Select a Product to View Rating Distribution:", sorted(produk_terfilter))
    data_produk = category_df[category_df['Product'] == selected_product]

    if not data_produk.empty:
        fig = px.histogram(data_produk, x='Rating', nbins=5,
                           title=f"Rating Distribution: {selected_product}",
                           labels={'Rating': 'Rating Score', 'count': 'Number of Reviews'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No rating data available for this product.")

    # Section: Word Cloud Bahasa Indonesia
    st.subheader("☁️ Word Cloud Ulasan Pengguna")
    st.caption("Visualisasi kata yang paling sering muncul dalam ulasan (setelah preprocessing sederhana).")

    # Gabungkan semua ulasan
    all_text = ' '.join(filtered_df['Review'].astype(str).tolist())

    # Preprocessing:
    all_text = all_text.lower()
    all_text = all_text.translate(str.maketrans('', '', string.punctuation + '0123456789'))

    # Ambil stopwords bahasa Indonesia
    stop_words = set(stopwords.words('indonesian'))
    # stopword kustom 
    with open("final project/stoplist.txt", "r", encoding="utf-8") as f:
        custom_stoplist = set([line.strip() for line in f if line.strip()])

    stop_words.update(custom_stoplist)

    # Tokenisasi, hapus stopword, filter token terlalu pendek
    tokens = [word for word in all_text.split() if word not in stop_words and len(word) > 2 and word.isalpha()]

    processed_text = ' '.join(tokens)

    # tampilkan wordcloud
    wc = WordCloud(width=800, height=400, background_color='white', collocations=False, max_words=100, font_path=None).generate(processed_text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)
