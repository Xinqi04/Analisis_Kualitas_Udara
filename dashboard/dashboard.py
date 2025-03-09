import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
@st.cache_data
def load_data():
    data = pd.read_csv('all_data.csv')
    data['date'] = pd.to_datetime(data['date'])
    return data

data = load_data()

# Sidebar untuk filter
st.sidebar.header("Filter Data")
date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [df['date'].min(), df['date'].max()])

# Filter berdasarkan tanggal
df_filtered = df[(df['date'] >= pd.to_datetime(date_range[0])) & (df['date'] <= pd.to_datetime(date_range[1]))]

st.title("Analisis Polusi Udara")

# Rata-rata tahunan polutan
pollutants = ['PM2.5', 'NO2', 'SO2', 'CO', 'O3']
pollutants_yearly = df_filtered.groupby('year')[pollutants].mean()

st.subheader("Perkembangan Polutan Setiap Tahun")
fig, ax = plt.subplots(figsize=(10, 5))
for pollutant in pollutants:
    ax.plot(pollutants_yearly.index, pollutants_yearly[pollutant], marker='o', linestyle='-', label=pollutant)
ax.set_xlabel('Tahun')
ax.set_ylabel('Rata-rata Konsentrasi')
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Polusi berdasarkan jam
st.subheader("Rata-rata Polutan Berdasarkan Jam")
fig, axes = plt.subplots(len(pollutants), 1, figsize=(12, 20), sharex=True)
colors = ["b", "r", "g", "purple", "orange"]
for ax, pol, col in zip(axes, pollutants, colors):
    sns.lineplot(x="hour", y=pol, data=df_filtered, estimator="mean", errorbar=None, color=col, ax=ax)
    ax.set_title(f"Rata-rata {pol} Berdasarkan Jam", fontsize=14)
    ax.set_ylabel("Konsentrasi")
    ax.grid()
axes[-1].set_xlabel("Jam")
st.pyplot(fig)

# Scatter plot hubungan polutan dan cuaca
st.subheader("Hubungan Polutan dengan Faktor Cuaca")
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
sns.scatterplot(data=df_filtered, x='TEMP', y='CO', ax=axes[0,0])
axes[0,0].set_title('Hubungan CO dengan Suhu')
sns.scatterplot(data=df_filtered, x='RAIN', y='PM2.5', ax=axes[0,1])
axes[0,1].set_title('Hubungan PM2.5 dengan Curah Hujan')
sns.scatterplot(data=df_filtered, x='WSPM', y='NO2', ax=axes[1,0])
axes[1,0].set_title('Hubungan NO2 dengan Kecepatan Angin')
sns.scatterplot(data=df_filtered, x='DEWP', y='O3', ax=axes[1,1])
axes[1,1].set_title('Hubungan O3 dengan Titik Embun')
st.pyplot(fig)

# Analisis stasiun dengan curah hujan dan CO tertinggi
st.subheader("Curah Hujan dan Konsentrasi CO per Stasiun")
df_station = df_filtered.groupby('station')[['RAIN', 'CO']].mean()
df_station_sorted = df_station.sort_values('RAIN', ascending=False)

fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.bar(df_station_sorted.index, df_station_sorted['RAIN'], color='blue', alpha=0.6, label='Curah Hujan')
ax2 = ax1.twinx()
ax2.plot(df_station_sorted.index, df_station_sorted['CO'], color='red', marker='o', linestyle='-', label='CO')
ax1.set_xlabel('Stasiun')
ax1.set_ylabel('Curah Hujan (mm)', color='blue')
ax2.set_ylabel('CO (ppm)', color='red')
ax1.grid(alpha=0.3)
plt.xticks(rotation=45)
st.pyplot(fig)
