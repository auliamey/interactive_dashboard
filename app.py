import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ================================
# 1. Konfigurasi Halaman Streamlit
# ================================
st.set_page_config(
    page_title="Dashboard EV AS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# 2. Judul dan Deskripsi Umum
# ================================
st.title("Dashboard Interaktif: Tren Kendaraan Listrik di Amerika Serikat")
# st.markdown(
#     """
#     Dashboard ini menampilkan berbagai visualisasi interaktif terkait **pertumbuhan** dan **komposisi**  
#     kendaraan listrik (EV) di Amerika Serikat.  
#     Data yang digunakan merupakan _Electric Vehicle Population Data_ (dataset resmi dari data.gov).  
#     Gunakan panel di samping untuk melakukan **filtering** berdasarkan tahun dan jenis kendaraan.
#     """
# )

# ================================
# 3. Load dan Persiapan Data
# ================================
@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Konversi kolom numerik
    df["Model Year"] = pd.to_numeric(df["Model Year"], errors="coerce")
    df["Base MSRP"] = pd.to_numeric(df["Base MSRP"], errors="coerce")
    df["Electric Range"] = pd.to_numeric(df["Electric Range"], errors="coerce")
    # Buang baris yang tidak valid jika perlu
    df = df.dropna(subset=["Model Year"])  # minimal harus ada tahun
    return df

df = load_data("Electric_Vehicle_Population_Data.csv")

# ================================
# 4. Panel Sidebar: Filter Interaktif
# ================================
st.sidebar.header("🔍 Filter Data")

# 4.1 Slider Rentang Tahun
min_year = int(df["Model Year"].min())
max_year = int(df["Model Year"].max())
tahun_range = st.sidebar.slider(
    "Pilih Rentang Tahun", 
    min_value=min_year, 
    max_value=max_year, 
    value=(min_year, max_year),
    step=1
)

# 4.2 Multiselect Jenis Kendaraan (BEV / PHEV, dsb.)
all_types = sorted(df["Electric Vehicle Type"].dropna().unique())
selected_types = st.sidebar.multiselect(
    "Pilih Jenis Kendaraan Listrik", 
    options=all_types, 
    default=all_types
)

# 4.3 Multiselect Kota (opsional): Biasanya kita fokus pada top 10
all_cities = sorted(df["City"].dropna().unique())
selected_cities = st.sidebar.multiselect(
    "Pilih Kota", 
    options=all_cities,
    default=[]
)

# 4.4 Multiselect Merek (opsional)
all_makes = sorted(df["Make"].dropna().unique())
selected_makes = st.sidebar.multiselect(
    "Pilih Merek", 
    options=all_makes,
    default=[]
)

# Terapkan filter ke DataFrame
df_filtered = df[
    (df["Model Year"] >= tahun_range[0]) & 
    (df["Model Year"] <= tahun_range[1]) &
    (df["Electric Vehicle Type"].isin(selected_types))
]

if selected_cities:
    df_filtered = df_filtered[df_filtered["City"].isin(selected_cities)]
if selected_makes:
    df_filtered = df_filtered[df_filtered["Make"].isin(selected_makes)]

# ================================
# 5. Visualisasi 1: Top 10 Kota Terbanyak (Bar Chart)
# ================================
st.subheader("Kota dengan Jumlah Kendaraan Listrik")
# Hitung frekuensi per City (berdasarkan data terfilter)
city_counts = df_filtered["City"].value_counts().nlargest(10)
fig_bar_cities = px.bar(
    x=city_counts.values,
    y=city_counts.index,
    orientation="h",
    labels={"x": "Jumlah Kendaraan", "y": "Kota"},
    color=city_counts.values,
    color_continuous_scale="Viridis",
)
fig_bar_cities.update_layout(
    yaxis={"autorange": "reversed"},
    margin={"l": 150, "r": 50, "t": 50, "b": 50},
    height=450,
)
# Tampilkan dengan tooltip
fig_bar_cities.update_traces(
    hovertemplate="<b>%{y}</b><br>Jumlah: %{x}<extra></extra>"
)

st.plotly_chart(fig_bar_cities, use_container_width=True)

# Narasi sesuai poster
# st.markdown(
#     """
#     Dari sisi jumlah akumulasi, Seattle jauh memimpin dengan lebih dari 38.000 kendaraan listrik terdaftar,  
#     diikuti oleh Bellevue dan Vancouver. Konsentrasi kendaraan listrik ini mengindikasikan bahwa wilayah  
#     negara bagian Washington menjadi pionir dalam transisi menuju sistem transportasi yang lebih bersih.  
#     Dukungan infrastruktur pengisian daya, insentif lokal, serta kampanye edukasi publik menjadi faktor penting  
#     yang mendorong tingginya angka adopsi di kota-kota tersebut.
#     """
# )

# ================================
# 6. Visualisasi 2: Pertumbuhan Kendaraan per Tahun (Line Chart)
# ================================
st.subheader("Pertumbuhan Jumlah Kendaraan Listrik (per Tahun)")

# Tentukan 10 kota teratas berdasarkan df_filtered (akumulasi total)
top10_cities_main = df_filtered["City"].value_counts().nlargest(10).index.tolist()
df_top10 = df_filtered[df_filtered["City"].isin(top10_cities_main)]

# Hitung jumlah per tahun-per-kota
growth = (
    df_top10
    .groupby(["Model Year", "City"])
    .size()
    .reset_index(name="Count")
)
# Buat line chart
fig_growth = px.line(
    growth,
    x="Model Year",
    y="Count",
    color="City",
    markers=True,
    labels={"Count": "Jumlah Kendaraan", "Model Year": "Tahun"},
    title=""
)
fig_growth.update_layout(
    margin={"l": 80, "r": 200, "t": 30, "b": 50},
    height=500,
    legend={"title": "Kota", "x": 1.02, "y": 1}
)
fig_growth.update_traces(
    hovertemplate="<b>%{fullData.name}</b><br>Tahun: %{x}<br>Jumlah: %{y}<extra></extra>"
)

st.plotly_chart(fig_growth, use_container_width=True)

# Narasi sesuai poster
# st.markdown(
#     """
#     Seattle mencatatkan pertumbuhan kendaraan listrik tertinggi selama enam tahun terakhir,  
#     mencapai puncaknya pada tahun 2023 dengan lebih dari 9.000 unit. Kota-kota seperti Bellevue, Vancouver,  
#     dan Redmond juga menunjukkan tren positif, meskipun dalam jumlah yang lebih rendah. Setelah tahun 2023,  
#     sebagian besar kota mengalami penurunan, namun tetap berada di atas level awal. Grafik ini mencerminkan  
#     meningkatnya adopsi kendaraan ramah lingkungan di wilayah barat laut Amerika Serikat, dipengaruhi oleh  
#     kebijakan hijau dan kesadaran masyarakat terhadap lingkungan.
#     """
# )

# ================================
# 7. Visualisasi 3: Distribusi Jenis Kendaraan Listrik (Pie Chart)
# ================================
st.subheader("Distribusi Jenis Kendaraan Listrik")

type_counts = df_filtered["Electric Vehicle Type"].value_counts()
fig_pie_type = px.pie(
    names=type_counts.index,
    values=type_counts.values,
    hole=0.3,
    labels={"label": "Jenis Kendaraan", "value": "Jumlah"},
)
# Perbaikan: ganti colorway ke schema yang valid (“qualitative.Pastel”)
fig_pie_type.update_traces(
    textinfo="percent+label",
    textposition="inside",
    hovertemplate="<b>%{label}</b><br>Jumlah: %{value}<br>(%{percent})<extra></extra>"
)
fig_pie_type.update_layout(
    margin={"l": 50, "r": 50, "t": 50, "b": 30},
    height=450,
    colorway=px.colors.qualitative.Pastel
)

st.plotly_chart(fig_pie_type, use_container_width=True)

# Narasi sesuai poster
# st.markdown(
#     """
#     Dari jenis kendaraannya, mayoritas masyarakat telah beralih ke **Battery Electric Vehicle (BEV)**  
#     yang sepenuhnya menggunakan tenaga listrik tanpa emisi, mencakup sekitar 79% dari total kendaraan  
#     listrik yang terdaftar. Sementara itu, **Plug-in Hybrid Electric Vehicle (PHEV)** masih digunakan  
#     oleh sebagian pengguna sebagai langkah transisi. Proporsi ini menunjukkan preferensi yang kuat terhadap  
#     teknologi nol-emisi penuh, seiring dengan semakin matangnya ekosistem kendaraan listrik di Amerika Serikat.
#     """
# )

# ================================
# 9. Visualisasi 5: Distribusi Harga MSRP per Top 5 Merek (Box Plot)
# ================================
# st.subheader("5. Distribusi Harga (Base MSRP) Mobil Listrik")
# top5_makes = makes_counts.index.tolist()[:5]
# df_top5 = df_filtered[df_filtered["Make"].isin(top5_makes) & df_filtered["Base MSRP"].notna()]

# fig_box_make = go.Figure()
# for m in top5_makes:
#     fig_box_make.add_trace(
#         go.Box(
#             y=df_top5[df_top5["Make"] == m]["Base MSRP"],
#             name=m,
#             boxpoints="suspectedoutliers",
#             hovertemplate="<b>%{name}</b><br>Harga: %{y}<extra></extra>"
#         )
#     )
# fig_box_make.update_layout(
#     yaxis_title="Base MSRP (USD)",
#     margin={"l": 80, "r": 50, "t": 50, "b": 50},
#     height=500
# )
# st.plotly_chart(fig_box_make, use_container_width=True)

# ================================
# 10. Visualisasi 6: Histogram Tahun Produksi
# ================================
# st.subheader("6. Distribusi Tahun Model Kendaraan Listrik")
# fig_hist_year = px.histogram(
#     df_filtered,
#     x="Model Year",
#     nbins=20,
#     labels={"Model Year": "Tahun Model", "count": "Jumlah"},
#     marginal="rug",
#     opacity=0.75,
#     title="",
#     histnorm=""
# )
# fig_hist_year.update_layout(
#     margin={"l": 80, "r": 50, "t": 30, "b": 50},
#     height=450
# )
# fig_hist_year.update_traces(
#     hovertemplate="Tahun: %{x}<br>Jumlah: %{y}<extra></extra>",
#     marker_color="skyblue"
# )
# st.plotly_chart(fig_hist_year, use_container_width=True)

# ================================
# 11. Visualisasi 7: Scatter Harga vs Jangkauan (Top 5 Merek)
# ================================
# st.subheader("7. Hubungan Harga dan Jangkauan Listrik Berdasarkan Top 5 Merek")
# df_scatter = df_filtered[
#     df_filtered["Make"].isin(top5_makes) &
#     df_filtered["Base MSRP"].notna() &
#     df_filtered["Electric Range"].notna()
# ]

# fig_scatter = px.scatter(
#     df_scatter,
#     x="Base MSRP",
#     y="Electric Range",
#     color="Make",
#     labels={"Base MSRP": "Base MSRP (USD)", "Electric Range": "Electric Range (Miles)"},
#     hover_data=["City", "Model Year"],
#     title=""
# )
# fig_scatter.update_layout(
#     margin={"l": 80, "r": 200, "t": 30, "b": 50},
#     height=500,
#     legend={"title": "Merek", "x": 1.02, "y": 1}
# )
# fig_scatter.update_traces(
#     marker=dict(size=8, opacity=0.7),
#     hovertemplate="<b>%{customdata[0]}</b><br>Model Year: %{customdata[1]}<br>Harga: %{x}<br>Range: %{y}<extra></extra>"
# )
# st.plotly_chart(fig_scatter, use_container_width=True)

# ================================
# 12. Visualisasi 8: Heatmap Jumlah EV per State per Tahun
# ================================
# st.subheader("8. Heatmap Jumlah Kendaraan Listrik per State per Tahun")
# # Pivot tabel (state vs tahun)
# heatmap_data = (
#     df_filtered
#     .pivot_table(
#         index="State",
#         columns="Model Year",
#         values="VIN (1-10)",
#         aggfunc="count",
#         fill_value=0
#     )
# )

# fig_heatmap = px.imshow(
#     heatmap_data.values,
#     x=heatmap_data.columns,
#     y=heatmap_data.index,
#     labels={"x": "Tahun", "y": "State", "color": "Jumlah"},
#     aspect="auto",
#     color_continuous_scale="YlGnBu"
# )
# fig_heatmap.update_layout(
#     margin={"l": 120, "r": 50, "t": 50, "b": 50},
#     height=700
# )
# fig_heatmap.update_traces(
#     hovertemplate="State: %{y}<br>Tahun: %{x}<br>Jumlah: %{z}<extra></extra>"
# )

# st.plotly_chart(fig_heatmap, use_container_width=True)

# ================================
# 13. Visualisasi 9: Box Plot Harga per Tipe Kendaraan
# ================================
st.subheader("Perbandingan Harga MSRP Berdasarkan Tipe Kendaraan Listrik")
df_type_price = df_filtered[df_filtered["Base MSRP"].notna()]

fig_box_type = go.Figure()
for tipe in sorted(df_type_price["Electric Vehicle Type"].unique()):
    fig_box_type.add_trace(
        go.Box(
            y=df_type_price[df_type_price["Electric Vehicle Type"] == tipe]["Base MSRP"],
            name=tipe,
            hovertemplate="<b>%{name}</b><br>Harga: %{y}<extra></extra>"
        )
    )
fig_box_type.update_layout(
    yaxis_title="Base MSRP (USD)",
    margin={"l": 80, "r": 50, "t": 50, "b": 50},
    height=500
)
st.plotly_chart(fig_box_type, use_container_width=True)

# ================================
# 8. Visualisasi 4: Top 10 Merek Mobil Listrik (Bar Chart)
# ================================
st.subheader("Jumlah Kendaraan Merek Mobil Listrik")
makes_counts = df_filtered["Make"].value_counts().nlargest(10)
fig_bar_makes = px.bar(
    x=makes_counts.values,
    y=makes_counts.index,
    orientation="h",
    labels={"x": "Jumlah Kendaraan", "y": "Merek"},
    color=makes_counts.values,
    color_continuous_scale="RdBu",
)
fig_bar_makes.update_layout(
    yaxis={"autorange": "reversed"},
    margin={"l": 150, "r": 50, "t": 50, "b": 50},
    height=450,
)
fig_bar_makes.update_traces(
    hovertemplate="<b>%{y}</b><br>Jumlah: %{x}<extra></extra>"
)

st.plotly_chart(fig_bar_makes, use_container_width=True)

# ================================
# 14. Penutup dan Narasi Umum
# ================================
st.markdown("---")
st.markdown(
    """
    Dashboard ini dirancang untuk memberikan gambaran **dinamis** mengenai tren dan komposisi kendaraan listrik di Amerika Serikat.  
    - Anda dapat **mengubah rentang tahun**, **memilih jenis kendaraan** (BEV, PHEV), atau **memilih kota/merek tertentu**  
      melalui panel di sebelah kiri untuk melihat bagaimana grafik berubah sesuai filter.  
    - Heatmap menggambarkan distribusi jumlah EV per tiap negara bagian (State) dan per tahun, sehingga memudahkan  
      identifikasi “hotspot” adopsi EV.  
    """
)
