import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import calendar

sns.set(style='dark')

def rent_by_day_df(df):
    # Menggunakan pivot_table untuk menghitung nilai casual dan registered berdasarkan weekday
    rent_by_day = df.pivot_table(values=['casual', 'registered'], index='weekday', aggfunc='sum').reset_index()

    # Mengganti nilai indeks 'weekday' dengan nama hari
    nama_hari = {0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'}
    rent_by_day.index = rent_by_day.index.map(nama_hari)

    return rent_by_day

def monthly_rent_df(df):
    monthly_rent = df.pivot_table(index='mnth', values='cnt', aggfunc='sum').reset_index()

    # Mengonversi angka bulan menjadi nama bulan pada kolom 'mnth'
    monthly_rent['mnth'] = monthly_rent['mnth'].apply(lambda x: calendar.month_name[x])

    # Mengubah nama kolom
    monthly_rent.columns = ['month', 'total_rent']

    return monthly_rent

def categorize_day(weekday):
    if weekday <= 5:
        return 'Weekday'
    else:
        return 'Weekend'
    
def hourly_rent_df(df):
    # Menambahkan kolom 'day_group' dengan menggunakan fungsi apply
    df['day_group'] = df['weekday'].apply(categorize_day)

    # Membuat tabel pivot jumlah sewa berdasarkan jam
    hour_rent = df.pivot_table(index='hr', values='cnt', columns='day_group', aggfunc='sum')

    # Menghitung total weekday per jam
    weekday_total = df[df['day_group'] == 'Weekday']['cnt'].sum()

    # Menghitung total weekend per jam
    weekend_total = df[df['day_group'] == 'Weekend']['cnt'].sum()

    # Menghitung persentase dari total keseluruhan untuk setiap kategori pada setiap jam
    hour_rent_percentage = hour_rent.copy()
    hour_rent_percentage['Weekday'] = (hour_rent['Weekday'] / weekday_total) * 100
    hour_rent_percentage['Weekend'] = (hour_rent['Weekend'] / weekend_total) * 100

    return hour_rent_percentage

df_hour = pd.read_csv("df_hour.csv")

datetime_columns = ["dteday"]
df_hour.sort_values(by="dteday", inplace=True)
df_hour.reset_index(inplace=True)

st.header('Bike Rental Analysis')

for column in datetime_columns:
    df_hour[column] = pd.to_datetime(df_hour[column])

min_date = df_hour["dteday"].min()
max_date = df_hour["dteday"].max()

# Mengambil start_date & end_date dari date_input
start_date, end_date = st.date_input(
label='Select Period',min_value=min_date,
max_value=max_date,
value=[min_date, max_date]
)

main_df = df_hour[(df_hour["dteday"] >= str(start_date)) & 
                (df_hour["dteday"] <= str(end_date))]

df_rent_weekday = rent_by_day_df(main_df)
df_monthly_rent = monthly_rent_df(main_df)
df_hourly_rent = hourly_rent_df(main_df)

#MEMBUAT GRAFIK 1
st.subheader('Jumlah Sewa Berdasarkan Hari')
fig, ax = plt.subplots( figsize=(12, 5))  # Mengatur ukuran grafik
colors = ["#E66F4E", "#E8C567"]

# Memplot bar untuk kolom 'casual'
sns.barplot(data=df_rent_weekday, x=df_rent_weekday.index, y='casual', color="#E66F4E", label='Casual')

# Memplot bar untuk kolom 'registered' di atas bar 'casual'
sns.barplot(data=df_rent_weekday, x=df_rent_weekday.index, y='registered', color="#E8C567", label='Registered', bottom=df_rent_weekday['casual'])

# mengatur label sumbu
ax.set_xlabel('Hari')
ax.set_ylabel('Jumlah Sewa')

# menempatkan legend di luar kotak grafik
ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.3), ncol=2)

# menampilkan grafik
st.pyplot(fig)


#MEMBUAT GRAFIK 2
st.subheader('Jumlah Sewa Berdasarkan Bulan')
fig, ax = plt.subplots(figsize=(12, 5))  # Mengatur ukuran grafik

sns.lineplot( 
        x="month", 
        y="total_rent",
        data=df_monthly_rent,
        color='#E66F4E',
        marker='o',
        markersize=7,
        linewidth=3,
        ax=ax)

# mengatur judul dan label sumbu
ax.set_xlabel('Bulan')
ax.set_ylabel('Jumlah Sewa')

st.pyplot(fig)

#MEMBUAT GRAFIK 3
st.subheader('Jumlah Sewa Berdasarkan Jam dan Jenis Hari')
st.write('Persentase Terhadap Total Masing - Masing Kelompok')

fig, ax = plt.subplots(figsize=(12, 5))  # Mengatur ukuran grafik
for i, column in enumerate(df_hourly_rent.columns):
    ax.plot(df_hourly_rent.index, 
            df_hourly_rent[column], marker='o', markersize=7, linewidth=3,
            label=str(column), color=colors[i])

#mengatur sumbu
ax.set_xlabel('Jam')
ax.set_ylabel('Jumlah')

# Mengatur sumbu x agar menampilkan setiap nilai indeks
ax.set_xticks(df_hourly_rent.index)
ax.set_xticklabels(df_hourly_rent.index)

ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.3), ncol=2)
st.pyplot(fig)
