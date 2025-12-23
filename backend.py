import pickle
from datetime import datetime, timedelta
import csv
import pandas as pd
import os
import pickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pickle_path = os.path.join(BASE_DIR, 'data', 'full_graph.pickle')

if os.path.exists(pickle_path):
    full_graph = pickle.load(open(pickle_path, 'rb'))
else:
    raise FileNotFoundError(f"File not found: {pickle_path}")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path2 = os.path.join(BASE_DIR, 'data', 'rekom_menu.csv')


if os.path.exists(csv_path2):
    df2 = pd.read_csv(csv_path2)
else:
    raise FileNotFoundError(f"File not found: {csv_path2}")


def buble_sort(arr, idk):
    new_arr = arr
    for j in range(len(new_arr)):
        temp_dt = new_arr[j][idk]
        for i in range(j+idk, len(new_arr)):
            dt = new_arr[i]
            if dt[idk] <= temp_dt:
                new_arr.pop(i)
                new_arr.insert(j, dt)
                temp_dt = dt[idk]

    return new_arr


def simple_sort(arr, idk, new, jenis):
    new_arr = arr
    blm_msk = True
    if jenis == 'Satuan':
        for i in range(len(arr)):
            temp_dt = new_arr[i][idk]
            if new[idk] < temp_dt:
                new_arr.insert(i, new)
                blm_msk = False
                break
        if blm_msk:
            new_arr.append(new)
    elif jenis == 'Kumpulan':
        j = 0
        msk = False
        for k in range(len(new)):
            nw = new[k]
            for i in range(j, len(new_arr)):
                temp_dt = new_arr[i][idk]
                if nw[idk] < temp_dt:
                    new_arr.insert(i, nw)
                    blm_msk = False
                    j = i+1
                    break
                if i+1 >= len(new_arr):
                    j = i+1
                    if k+1 >= len(new):
                        new_arr.append(nw)
                    else:
                        new_arr.extend(new[k:])
                        msk = True
                        blm_msk = False
                    break
            if msk:
                break

        if blm_msk:
            new_arr.extend(new)


    return new_arr



def operasi_menit(waktu_awal: str, menit_tambah: int, opr: str = '+') -> str:
    waktu_obj = datetime.strptime(waktu_awal, "%H:%M")

    if opr == '+':
        waktu_baru = waktu_obj + timedelta(minutes=menit_tambah)
    elif opr == '-':
        waktu_baru = waktu_obj - timedelta(minutes=menit_tambah)

    return waktu_baru.strftime("%H:%M")


def selisih_menit(waktu1: str, waktu2: str) -> int:
    waktu_obj1 = datetime.strptime(waktu1, "%H:%M")
    waktu_obj2 = datetime.strptime(waktu2, "%H:%M")

    if waktu_obj2 < waktu_obj1:
        waktu_obj2 += timedelta(days=1)

    selisih = waktu_obj2 - waktu_obj1
    return int(selisih.total_seconds() // 60)


def bandingkan_waktu(waktu1: str, waktu2: str) -> bool:
    waktu_obj1 = datetime.strptime(waktu1, "%H:%M")
    waktu_obj2 = datetime.strptime(waktu2, "%H:%M")
    return waktu_obj1 <= waktu_obj2


def filtering(arr, idk, tambahan = None):
    global del_count
    new_arr = arr
    pop_list = []
    if tambahan == None:
        for i in range(len(new_arr)):
            if i + 1 > len(new_arr):
                break
            if type(new_arr[i][5]) != list:
                new_arr[i][5] = [new_arr[i][5]]
            for j in range(i+1, len(new_arr)):
                if type(new_arr[j][5]) != list:
                    new_arr[j][5] = [new_arr[j][5]]
                if new_arr[i][0] == new_arr[j][0] and new_arr[i][idk] <= new_arr[j][idk]:
                    if selisih_menit(new_arr[i][5][-1], new_arr[j][5][-1]) >= 30 or selisih_menit(new_arr[j][5][-1], new_arr[i][5][-1]) >= 30:
                        continue
                    pop_list.append(j)
            ip = 0
            for p in pop_list:
                new_arr.pop(p-ip)
                ip += 1
                del_count += 1
            pop_list.clear()

    return new_arr


def filtering_request(arr, harga_max, durasi_max):
    global del_count
    new_arr = []
    del_data = []
    for data in arr:
        if data[2] > harga_max or data[3] > durasi_max:
            del_count += 1
            if (data[0],data[1]) not in del_data:
                del_data.append((data[0],data[1]))
            continue
        new_arr.append(data)

    return new_arr

del_count = 0
def UCS(graph, asal, tujuan, berangkat = 'Bebas', kat: str ='Bobot', biaya_user: int = None, waktu_user: int = None):
    match kat:
        case 'Bobot': idk = 7
        case 'Harga': idk = 6
        case 'Durasi': idk = 3
    req = False

    if biaya_user != None and waktu_user != None:
        idk = 7
        req = True
    elif biaya_user != None:
        idk = 7
        waktu_user = 10**5
        req = True
    elif waktu_user != None:
        idk = 6
        biaya_user = 10**8
        req = True
    else:
        biaya_user = 10**8
        waktu_user = 10**5


    if berangkat != 'Bebas':
        antrian = buble_sort([n + [n[2], (n[2]*n[3])/1000] for n in graph[asal] if bandingkan_waktu(berangkat, n[4]) and bandingkan_waktu(n[4], operasi_menit(berangkat, 30, '+'))], idk)
    else:
        antrian = buble_sort([n + [n[2], (n[2]*n[3])/1000] for n in graph[asal]], idk)

    if req:
        antrian = filtering_request(antrian, harga_max=biaya_user, durasi_max=waktu_user)

    antrian = filtering(antrian, idk)


    total_jelajah = 0
    history = [asal]
    cache = []
    result = []

    while antrian != []:
        dt = antrian[0][0] 
        kend = antrian[0][1]
        harga_tiket = antrian[0][2]
        if type(harga_tiket) != list:
            harga_tiket = [harga_tiket]
        durasi = antrian[0][3]
        berangkat = antrian[0][4]
        tiba = antrian[0][5]
        harga = sum(harga_tiket)
        bobot = (harga * durasi)/1000

        node = dt
        if type(node) != str:
            node = node[-1]
        else:
            dt = [dt]
        if type(kend) != list:
            kend = [kend]

        if type(berangkat) != list:
            berangkat = [berangkat]

        if type(tiba) != list:
            tiba = [tiba]


        dt_cache = [dt, kend, berangkat[-1], tiba[-1]]
        if dt_cache in cache:
            antrian.pop(0)
            continue
        else:
            cache.append(dt_cache)

        if node == tujuan:
            result.append([dt, kend, harga_tiket, durasi, berangkat, tiba, harga, bobot])
            print(total_jelajah)
            if len(result) == 3:
                antrian.clear()
                return result
            else:
                antrian.pop(0)
                continue

        if node not in history:
            history.append(node)

        try:
            temp_antrian = []
            for n in graph[node]:
                total_jelajah += 1
                if n[0] in history:
                    continue
                dtrans = durasi + 15
                min_gass = operasi_menit(berangkat[0], int(dtrans))
                if kat == 'Harga':
                    max_gass = operasi_menit(min_gass, 180)
                else:
                    max_gass = operasi_menit(min_gass, 180)

                if bandingkan_waktu(n[4], min_gass) or bandingkan_waktu(max_gass, n[4]):
                    continue


                temp_path = dt.copy()
                temp_path.append(n[0])
                t_kend = kend.copy()
                t_kend.append(n[1])
                l_harga = harga_tiket.copy()
                l_harga.append(n[2])
                t_berangkat = berangkat.copy()
                t_berangkat.append(n[4])
                t_tiba = tiba.copy()
                t_tiba.append(n[5])
                t_harga = sum(l_harga)
                t_durasi = durasi + selisih_menit(tiba[-1],n[4]) + n[3]
                t_bobot = (t_harga * t_durasi)/1000


                if t_harga > biaya_user or t_durasi > waktu_user:
                    continue
                
                new = (temp_path, t_kend, l_harga, t_durasi, t_berangkat, t_tiba, t_harga, t_bobot)
                temp_antrian = simple_sort(temp_antrian, idk, new, jenis='Satuan')
            temp_antrian = filtering(temp_antrian, idk)
            antrian.pop(0)
            antrian = simple_sort(antrian, idk, temp_antrian, jenis='Kumpulan')


        except KeyError:
            antrian.pop(0)

    print(total_jelajah)
    if result == []:
        return 'Rute Tidak Tersedia'
    else:
        print(result)
        return result


def greedy_notransit(graph, asal, tujuan, kat='Bobot', biaya_user=None, waktu_user=None, berangkat='Bebas'):
    rekom = None
    if biaya_user != None or waktu_user != None:
        if biaya_user == None:
            biaya_user = 10**8
        elif waktu_user == None:
            waktu_user = 10**4
        else:
            pass
    else:
        biaya_user = 10**8
        waktu_user = 10**4

    try:
        match kat:
            case 'Harga':
                idx = 2
            case 'Durasi':
                idx = 3
            case 'Bobot':
                idx = 5
        if berangkat != 'Bebas':
            data = [n + [n[2], (n[2]*n[3])/1000] for n in graph[asal] if bandingkan_waktu(berangkat, n[4]) and bandingkan_waktu(n[4], operasi_menit(berangkat, 30, '+'))]
        else:
            data = graph[asal]
        for kota in data:
            if kota[0] == tujuan and rekom == None and kota[2] <= biaya_user and kota[3] <= waktu_user:
                rekom = kota
            elif kota[0] == tujuan and kota[2] <= biaya_user and kota[3] <= waktu_user:
                bobot = kota[2]*kota[3]
                kota.append(bobot)
                if kota[idx] < rekom[idx]:
                    rekom = kota

    except KeyError: return 'Rute tidak ditemukan'
    except IndexError: return 'Code Cacat'

    if rekom == None:
        return 'Rute tidak ditemukan'
    else:
        return [[[rekom[0]], [rekom[1]], [rekom[2]], rekom[3], [rekom[4]], [rekom[5]], rekom[2], rekom[6]]]


NOMINAL_UANG = [100000, 75000, 50000, 20000, 10000, 5000, 2000, 1000, 500]


def knapsack(menu, max_budget):
    n = len(menu)

    dp = [[0] * (max_budget + 1) for _ in range(n + 1)]

    for i in range(n):
        for budget in range(max_budget + 1):
            harga = menu[i]["harga"]
            gizi = menu[i]["gizi"]
            if harga <= budget:
                dp[i + 1][budget] = max(dp[i][budget], dp[i][budget - harga] + gizi)
            else:
                dp[i + 1][budget] = dp[i][budget]

    selected_items = []
    budget = max_budget
    for i in range(n, 0, -1):
        if dp[i][budget] != dp[i - 1][budget]:
            selected_items.append(menu[i - 1])
            budget -= menu[i - 1]["harga"]

    total_harga = sum(item["harga"] for item in selected_items)
    total_gizi = sum(item["gizi"] for item in selected_items)

    return selected_items, total_harga, total_gizi


def hitung_kembalian(uang_user, total_harga):
    kembalian = uang_user - total_harga
    hasil_kembalian = []

    for nominal in NOMINAL_UANG:
        jumlah = kembalian // nominal
        if jumlah > 0:
            hasil_kembalian.append((nominal, jumlah))
            kembalian -= jumlah * nominal

    return hasil_kembalian


def load_menu():
    menu = []
    menu = []
    for _, row in df2.iterrows():
        menu.append({
            "nama": row["Nama"],
            "harga": int(row["Harga"]),
            "gizi": float(row["Skor Gizi"]),
            
        })
    return menu


