import csv
from flask import Flask, render_template, request
import pandas as pd
from backend import UCS, full_graph, greedy_notransit, load_menu, knapsack, hitung_kembalian
import pickle
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, 'data', 'Full_Data_Ticket.csv')

print(f"Looking for CSV file at: {csv_path}")

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
else:
    raise FileNotFoundError(f"File not found: {csv_path}")

nama_kota_asal = df['Kota Asal']
nama_kota_tujuan = df['Kota Tujuan']
jenis_kendaraan = df['Jenis Kendaraan']
kota_asal = nama_kota_asal.unique()
kota_tujuan = nama_kota_tujuan.unique()
kota_tujuan.sort()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pickle_path = os.path.join(BASE_DIR, 'data', 'ticket_graph.pickle')

print(f"Looking for pickle file at: {pickle_path}")

if os.path.exists(pickle_path):
    graph = pickle.load(open(pickle_path, 'rb'))
else:
    raise FileNotFoundError(f"File not found: {pickle_path}")


@app.route('/')
def home():
    return render_template('index.html', kota_asal=kota_asal, kota_tujuan=kota_tujuan)

@app.route('/cari-rute', methods=['GET', 'POST'])
def cari_rute():
    hasil_rekomendasi = None

    if request.method == 'POST':
        asal = request.form.get('asal')
        tujuan = request.form.get('tujuan')
        waktu = request.form.get('Jam')
        kategori = request.form.get('Kategori')
        biaya = request.form.get('Biaya')
        durasi = request.form.get('Durasi')
        transit = request.form.get('transit')

        if transit == 'Non Transit':
            hasil = greedy_notransit(full_graph, asal, tujuan, kat=kategori, biaya_user=int(biaya), waktu_user=int(durasi), berangkat=waktu)
        else:
            hasil = UCS(full_graph, asal, tujuan, berangkat=waktu, kat=kategori, biaya_user=int(biaya), waktu_user=int(durasi))

        if isinstance(hasil, list) and hasil:
            hasil_rekomendasi = {
                'rute': hasil[0][0],
                'kendaraan': hasil[0][1],
                'harga': hasil[0][2],
                'durasi': hasil[0][3],
                'berangkat': hasil[0][4],
                'tiba': hasil[0][5],
                'bobot': hasil[0][7],
                'transit': transit
            }

    return render_template(
        'index.html', 
        kota_asal=kota_asal, 
        kota_tujuan=kota_tujuan, 
        hasil_rekomendasi=hasil_rekomendasi
    )

def filter_data(asal, tujuan):
    filtered_data = []
    filtered_data = df[
        (df['Kota Asal'].str.lower() == asal.lower()) &
        (df['Kota Tujuan'].str.lower() == tujuan.lower())
    ]

    return filtered_data.to_dict(orient='records')

@app.route('/hasil-pencarian')
def hasil_pencarian():
    asal = request.args.get('asal')
    tujuan = request.args.get('tujuan')

    if not asal or not tujuan:
        return "Kota asal dan tujuan harus diisi.", 400

    data = filter_data(asal, tujuan)

    return render_template('hasil_pencarian.html', asal=asal, tujuan=tujuan, data=data)

@app.route('/vending', methods=['GET', 'POST'])
def vending_machine():
    menu = load_menu()
    selected_items = []
    total_harga = 0
    total_gizi = 0
    uang_user = 0
    kembalian = []
    error_message = None

    if request.method == 'POST':
        uang_user = int(request.form.get("uang_user", 0))

        # Menggunakan fungsi knapsack untuk menghitung kombinasi optimal
        selected_items, total_harga, total_gizi = knapsack(menu, uang_user)

        if not selected_items:
            error_message = "Uang Anda tidak cukup untuk membeli apa pun."
        elif uang_user > total_harga:
            kembalian = hitung_kembalian(uang_user, total_harga)

    return render_template(
        'vending.html',
        menu=menu,
        selected_items=selected_items,
        total_harga=total_harga,
        total_gizi=total_gizi,
        uang_user=uang_user,
        kembalian=kembalian,
        error_message=error_message
    )


@app.template_filter('format_ribuan')
def format_ribuan(value):
    try:
        return f"{int(value):,}".replace(",", ".")
    except (ValueError, TypeError):
        return value


if __name__ == '__main__':
    app.run(debug=True)