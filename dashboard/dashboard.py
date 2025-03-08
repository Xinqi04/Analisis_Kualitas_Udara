import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data
def load_data():
    data = pd.read_csv('all_data.csv')
    data['date'] = pd.to_datetime(data['date'])
    return data

data = load_data()

def categorize_air_quality(pm25):
    if pm25 <= 15.5:
        return "Baik"
    elif 15.6 <= pm25 <= 55.4:
        return "Sedang"
    elif 55.5 <= pm25 <= 150.4:
        return "Tidak Sehat"
    elif 150.5 <= pm25 <= 250.4:
        return "Sangat Tidak Sehat"
    else:
        return "Berbahaya"

# Sidebar untuk filter
st.sidebar.header('Filter Data')
station_options = ['All'] + list(data['station'].unique())
station = st.sidebar.selectbox('Pilih Stasiun', station_options)
start_date = st.sidebar.date_input('Tanggal Mulai', data['date'].min())
end_date = st.sidebar.date_input('Tanggal Akhir', data['date'].max())

if station == 'All':
    filtered_data = data[(data['date'] >= pd.to_datetime(start_date)) & 
                         (data['date'] <= pd.to_datetime(end_date))]
    title = "Analisis Kualitas Udara di Semua Stasiun"
else:
    filtered_data = data[(data['station'] == station) & 
                         (data['date'] >= pd.to_datetime(start_date)) & 
                         (data['date'] <= pd.to_datetime(end_date))]
    title = f"Analisis Kualitas Udara di Stasiun {station}"

st.title(title)

st.header('Visualisasi Data')

# 1. Tren Rata-rata Polusi Udara per Tahun
st.subheader('Tren Rata-rata Polusi Udara per Tahun')
filtered_data['year'] = filtered_data['date'].dt.year
yearly_trend = filtered_data.groupby('year')['PM2.5'].mean()

fig, ax = plt.subplots()
sns.lineplot(x=yearly_trend.index, y=yearly_trend.values, ax=ax)
ax.set_title('Tren Rata-rata PM2.5 per Tahun')
ax.set_xlabel('Tahun')
ax.set_ylabel('Rata-rata PM2.5 (µg/m³)')
ax.set_ylim(0, None)
st.pyplot(fig)

# 2. Jam dengan Polusi Udara Tertinggi dan Terendah (jika ada kolom hour)
if 'hour' in filtered_data.columns:
    st.subheader('Jam dengan Polusi Udara Tertinggi dan Terendah')
    hourly_pollution = filtered_data.groupby('hour')['PM2.5'].mean()

    fig, ax = plt.subplots()
    sns.lineplot(x=hourly_pollution.index, y=hourly_pollution.values, ax=ax)
    ax.set_title('Rata-rata PM2.5 per Jam')
    ax.set_xlabel('Jam')
    ax.set_ylabel('Rata-rata PM2.5 (µg/m³)')
    st.pyplot(fig)

# 3. Rata-rata Variabel Cuaca
st.subheader('Rata-rata Variabel Cuaca')
weather_vars = ['TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
weather_means = filtered_data[weather_vars].mean()

weather_means_converted = {
    "Variabel": ["Suhu", "Tekanan Udara", "Titik Embun", "Curah Hujan", "Kecepatan Angin"],
    "Rata-rata": [
        weather_means['TEMP'],
        weather_means['PRES'],
        weather_means['DEWP'],
        weather_means['RAIN'],
        weather_means['WSPM'] * 3.6  # m/s ke km/jam
    ],
    "Satuan": ["°C", "hPa", "°C", "mm", "km/jam"]
}

weather_df = pd.DataFrame(weather_means_converted)
st.table(weather_df)

st.subheader("Hubungan antara Curah Hujan dan PM2.5")
fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(x=filtered_data['RAIN'], y=filtered_data['PM2.5'], alpha=0.6, ax=ax)
ax.set_title("Scatter Plot: Curah Hujan vs PM2.5")
ax.set_xlabel("Curah Hujan (mm)")
ax.set_ylabel("PM2.5 (µg/m³)")
st.pyplot(fig)

# 4. Wilayah dengan Tingkat Polusi Tertinggi dan Terendah
if station == 'All':
    st.subheader('Wilayah dengan Tingkat Polusi Tertinggi dan Terendah')
    station_avg_pm25 = filtered_data.groupby('station')['PM2.5'].mean().reset_index()
    station_avg_pm25['air_quality_category'] = station_avg_pm25['PM2.5'].apply(categorize_air_quality)

    colors = {
        "Baik": "green",
        "Sedang": "yellow",
        "Tidak Sehat": "orange",
        "Sangat Tidak Sehat": "red",
        "Berbahaya": "purple"
    }

    plt.figure(figsize=(12, 6))
    bars = plt.bar(station_avg_pm25['station'], station_avg_pm25['PM2.5'],
                   color=[colors[cat] for cat in station_avg_pm25['air_quality_category']])

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 1), ha='center', va='bottom')

    plt.title("Rata-rata PM2.5 di Setiap Stasiun dengan Kategorisasi Kualitas Udara")
    plt.xlabel("Stasiun")
    plt.ylabel("Rata-rata PM2.5 (µg/m³)")
    plt.xticks(rotation=45)
    plt.legend(title="Kategori Udara", loc="upper right")
    st.pyplot(plt)
else:
    st.subheader(f"Kualitas Udara di Stasiun {station}")
    avg_pm25 = filtered_data['PM2.5'].mean()
    category = categorize_air_quality(avg_pm25)
    quality_data = pd.DataFrame({
        "Parameter": ["Rata-rata PM2.5", "Kategori Kualitas Udara"],
        "Nilai": [f"{avg_pm25:.2f} µg/m³", category]
    })
    st.table(quality_data)

# 5. Kategori Kualitas Udara selama 5 Tahun Terakhir
st.subheader('Kategori Kualitas Udara selama 5 Tahun Terakhir')

filtered_data['year'] = filtered_data['date'].dt.year
last_5_years = filtered_data[filtered_data['year'] >= (filtered_data['year'].max() - 4)]

yearly_avg_pm25 = last_5_years.groupby('year')['PM2.5'].mean().reset_index()
yearly_avg_pm25['air_quality_category'] = yearly_avg_pm25['PM2.5'].apply(categorize_air_quality)

st.write(yearly_avg_pm25)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x=yearly_avg_pm25['year'], y=yearly_avg_pm25['PM2.5'], hue=yearly_avg_pm25['air_quality_category'], 
            palette={"Baik": "green", "Sedang": "yellow", "Tidak Sehat": "orange", "Sangat Tidak Sehat": "red", "Berbahaya": "purple"}, ax=ax)

ax.set_title('Rata-rata PM2.5 per Tahun dengan Kategorisasi Kualitas Udara')
ax.set_xlabel('Tahun')
ax.set_ylabel('Rata-rata PM2.5 (µg/m³)')
st.pyplot(fig)

# Download filtered data
st.header('Unduh Data yang Difilter')
st.download_button(
    label="Unduh Data",
    data=filtered_data.to_csv(index=False).encode('utf-8'),
    file_name='filtered_data.csv',
    mime='text/csv',
)
