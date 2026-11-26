import os # untuk akses file dan folder
from datetime import datetime

# file data disimpan di folder yang sama dengan program ini
FOLDER = os.path.dirname(os.path.abspath(__file__))

DAFTAR_MAKANAN = {
    1: ("Indomie Goreng", 8000), 
    2: ("Indomie Kuah", 8000),
    3: ("Indomie Jumbo", 13000),
    4: ("Ekstra Telur", 4000),
    5: ("Ekstra Kornet", 5000),
    6: ("Ekstra Sayur", 0)
}

# status hanya boleh maju satu langkah: menunggu -> diproses -> selesai
URUTAN_STATUS = {"menunggu": "diproses", "diproses": "selesai"}

password_penjual = "warmindo.pacil"  # contoh password penjual


# ---------- Penyimpanan ke file txt ----------
# Satu file per hari: pesanan_yyyy-mm-dd.txt
# Satu baris = satu pesanan, kolom dipisah tanda |
# Format: nomor|nama|waktu|status|total|makanan:jumlah;makanan:jumlah
def nama_file_hari_ini():
    return os.path.join(FOLDER, f"pesanan_{datetime.now():%Y-%m-%d}.txt")


def baca_pesanan():
    daftar = []
    nama_file = nama_file_hari_ini()
    if not os.path.exists(nama_file):  # jika belum ada pesanan hari ini
        return daftar

    with open(nama_file, "r") as f:
        for baris in f:
            baris = baris.strip()
            if baris == "":
                continue
            nomor, nama, waktu, status, total, isi_teks = baris.split("|")
            isi = {}
            for potongan in isi_teks.split(";"):
                nama_makanan, jumlah = potongan.split(":")
                isi[nama_makanan] = int(jumlah)
            daftar.append({
                "nomor": int(nomor),
                "nama": nama,
                "waktu": waktu,
                "status": status,
                "total": int(total),
                "isi": isi,
            })
    return daftar


def simpan_semua_pesanan(daftar):
    # mode "w" menimpa isi file, jadi semua pesanan ditulis ulang
    with open(nama_file_hari_ini(), "w") as f:
        for p in daftar:
            potongan = []
            for nama_makanan, jumlah in p["isi"].items():
                potongan.append(f"{nama_makanan}:{jumlah}")
            isi_teks = ";".join(potongan)
            f.write(f"{p['nomor']}|{p['nama']}|{p['waktu']}|"
                    f"{p['status']}|{p['total']}|{isi_teks}\n")


def cari_pesanan(daftar, nomor):
    for pesanan in daftar:
        if pesanan["nomor"] == nomor:
            return pesanan
    return None


# ---------- Fungsi bantu ----------
def harga_dalam_rupiah(angka):
    return f"Rp{angka:,}".replace(",", ".")


def tampilkan_daftar_makanan():
    print("\n=== DAFTAR MAKANAN ===")
    for id_makanan, (nama, harga) in DAFTAR_MAKANAN.items():
        print(f"{id_makanan}. {nama} - {harga_dalam_rupiah(harga)}")


def hitung_total(daftar_sementara):
    total = 0
    for id_makanan, jumlah in daftar_sementara.items():
        total += DAFTAR_MAKANAN[id_makanan][1] * jumlah
    return total


def tampilkan_daftar_sementara(daftar_sementara):
    for id_makanan, jumlah in daftar_sementara.items():
        nama, harga = DAFTAR_MAKANAN[id_makanan]
        print(f"{nama} x{jumlah} = {harga_dalam_rupiah(harga * jumlah)}")
    print(f"Total: {harga_dalam_rupiah(hitung_total(daftar_sementara))}")


def tunggu_kembali():
    while input("\nKetik 0 untuk kembali: ") != "0":
        print("Ketik angka 0 untuk kembali.")


# ---------- Fitur pembeli ----------
def buat_pesanan_baru(daftar_sementara):
    while True:
        tampilkan_daftar_makanan()
        pilihan = input("\nMasukkan nomor makanan yang ingin dipesan (0 = kembali): ")
        if pilihan == "0":
            return
        if not pilihan.isdigit() or int(pilihan) not in DAFTAR_MAKANAN:
            print("Nomor makanan tidak ada.")
            continue

        id_makanan = int(pilihan)
        nama = DAFTAR_MAKANAN[id_makanan][0]
        try:
            jumlah = int(input(f"Jumlah {nama} (0 = batal): "))
        except ValueError:
            print("Jumlah harus berupa angka.")
            continue

        if jumlah == 0:
            print("Dibatalkan.")
            continue
        if jumlah < 0:
            print("Jumlah harus lebih dari nol.")
            continue

        daftar_sementara[id_makanan] = daftar_sementara.get(id_makanan, 0) + jumlah
        print(f"Ditambahkan: {nama} x{jumlah}")


def lihat_list_pesanan(daftar_sementara):
    print("\n=== LIST PESANAN ===")
    if not daftar_sementara:
        print("Belum ada makanan yang dipilih.")
    else:
        tampilkan_daftar_sementara(daftar_sementara)
    tunggu_kembali()


def lakukan_pemesanan(daftar_sementara):
    if not daftar_sementara:
        print("\nList pesanan masih kosong. Pilih makanan di pilihan 1.")
        tunggu_kembali()
        return

    print("\n=== KONFIRMASI PESANAN ===")
    tampilkan_daftar_sementara(daftar_sementara)

    while True:
        nama = input("\nNama pemesan (0 = kembali): ").strip()
        if nama == "0":
            return
        if nama != "":
            break
        print("Nama pemesan tidak boleh kosong.")
    nama = nama.replace("|", "-")  # tanda | dipakai sebagai pemisah kolom di file

    daftar = baca_pesanan()
    nomor = len(daftar) + 1  # file baru tiap hari, jadi nomor mulai dari 1 lagi

    isi = {}
    for id_makanan, jumlah in daftar_sementara.items():
        isi[DAFTAR_MAKANAN[id_makanan][0]] = jumlah
    total = hitung_total(daftar_sementara)

    daftar.append({
        "nomor": nomor,
        "nama": nama,
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "menunggu",
        "total": total,
        "isi": isi,
    })
    simpan_semua_pesanan(daftar)
    daftar_sementara.clear()

    print("\nPesanan berhasil dibuat!")
    print(f"Nomor antrean kamu: {nomor}")
    print(f"Total: {harga_dalam_rupiah(total)} (bayar langsung di kantin)")
    tunggu_kembali()


def lihat_status_antrean():
    while True:
        nomor = input("\nNomor antrean kamu (0 = kembali): ")
        if nomor == "0":
            return
        if not nomor.isdigit():
            print("Nomor antrean harus berupa angka.")
            continue

        pesanan = cari_pesanan(baca_pesanan(), int(nomor))
        if pesanan is None:
            print("Nomor antrean tidak ditemukan.")
        else:
            if pesanan['status'] == "selesai":
                print(f"Antrean {pesanan['nomor']} a.n. {pesanan['nama']}: {pesanan['status']}.")
                print("Segera ambil pesanan dan lakukan pembayaran di kantin")
            else:
                print(f"Antrean {pesanan['nomor']} a.n. {pesanan['nama']}: {pesanan['status']}")


def menu_pembeli(daftar_sementara):
    while True:
        print("\n=== MENU PEMBELI ===")
        print("1 = Tambah pesanan baru")
        print("2 = Lihat list pesanan")
        print("3 = Konfirmasi pemesanan")
        print("4 = Lihat status antrean")
        print("0 = Kembali")
        pilihan = input("Pilih: ")

        if pilihan == "1":
            buat_pesanan_baru(daftar_sementara)
        elif pilihan == "2":
            lihat_list_pesanan(daftar_sementara)
        elif pilihan == "3":
            lakukan_pemesanan(daftar_sementara)
        elif pilihan == "4":
            lihat_status_antrean()
        elif pilihan == "0":
            return
        else:
            print("Pilihan tidak valid.")


# ---------- Fitur penjual ----------
def minta_password():
    isi = input("Password penjual (0 = kembali): ")
    if isi == "0":
        return False
    if isi == password_penjual:
        return True
    print("Password salah.")
    return False


def tampilkan_pesanan_masuk():
    print("\n=== PESANAN MASUK HARI INI ===")
    ada = False
    for p in baca_pesanan():
        if p["status"] != "selesai":
            ada = True
            print(f"\nAntrean {p['nomor']} - {p['nama']} [{p['status']}]")
            for nama_makanan, jumlah in p["isi"].items():
                print(f"  {nama_makanan} x{jumlah}")
            print(f"  Total: {harga_dalam_rupiah(p['total'])}")
    if not ada:
        print("Tidak ada pesanan yang sedang aktif.")


def lihat_pesanan_masuk():
    tampilkan_pesanan_masuk()
    tunggu_kembali()


def ubah_status_pesanan():
    while True:
        tampilkan_pesanan_masuk()
        nomor = input("\nNomor antrean yang ingin diubah statusnya (0 = kembali): ")
        if nomor == "0":
            return
        if not nomor.isdigit():
            print("Nomor antrean harus berupa angka.")
            continue

        daftar = baca_pesanan()
        pesanan = cari_pesanan(daftar, int(nomor))
        if pesanan is None:
            print("Nomor antrean tidak ditemukan.")
            continue
        if pesanan["status"] == "selesai":
            print("Pesanan ini sudah selesai.")
            continue

        status_lama = pesanan["status"]
        pesanan["status"] = URUTAN_STATUS[status_lama]  # mengubah isi daftar juga
        simpan_semua_pesanan(daftar)
        print(f"Antrean {pesanan['nomor']}: {status_lama} -> {pesanan['status']}")


def menu_penjual():
    while True:
        print("\n=== MENU PENJUAL ===")
        print("1 = Lihat pesanan masuk")
        print("2 = Ubah status pesanan")
        print("0 = Kembali")
        pilihan = input("Pilih: ")

        if pilihan == "1":
            lihat_pesanan_masuk()
        elif pilihan == "2":
            ubah_status_pesanan()
        elif pilihan == "0":
            return
        else:
            print("Pilihan tidak valid.")


# ---------- Program utama ----------
def main():
    daftar_sementara = {}  # belum disimpan ke file sampai pembeli konfirmasi pemesanan
    while True:
        print("\n=== WARMINDO EXPRESS ===")
        print("1 = Masuk sebagai pembeli")
        print("2 = Masuk sebagai penjual")
        print("0 = Selesai")
        pilihan = input("Pilih: ")

        if pilihan == "1":
            menu_pembeli(daftar_sementara)
        elif pilihan == "2":
            if minta_password():
                menu_penjual()
        elif pilihan == "0":
            print("Terima kasih telah menggunakan Warmindo Express!")
            break
        else:
            print("Pilihan tidak valid.")


main()
