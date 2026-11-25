import os
import sqlite3
from datetime import datetime

# file database disimpan di folder yang sama dengan program ini
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "warmindo_express.db")

# status hanya boleh maju satu langkah: menunggu -> diproses -> selesai
URUTAN_STATUS = {"menunggu": "diproses", "diproses": "selesai"}

db = sqlite3.connect(DB_FILE)
db.row_factory = sqlite3.Row  # hasil query bisa dibaca per nama kolom

HARI_INI = "date(waktu_pesan) = date('now', 'localtime')"


# ---------- Database ----------
def siapkan_database():
    db.executescript("""
    CREATE TABLE IF NOT EXISTS makanan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        harga INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS pesanan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_pemesan TEXT NOT NULL,
        nomor_antrean INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'menunggu',
        total INTEGER NOT NULL,
        waktu_pesan TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS detail_pesanan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pesanan_id INTEGER NOT NULL REFERENCES pesanan(id),
        makanan_id INTEGER NOT NULL REFERENCES makanan(id),
        jumlah INTEGER NOT NULL,
        harga_satuan INTEGER NOT NULL
    );
    """)
    jumlah = db.execute("SELECT COUNT(*) FROM makanan").fetchone()[0]
    if jumlah == 0:  # isi daftar makanan hanya saat database masih kosong
        db.executemany(
            "INSERT INTO makanan (nama, harga) VALUES (?, ?)",
            [("Indomie Goreng", 8000), ("Indomie Kuah", 8000),
             ("Indomie Jumbo", 13000), ("Sayur", 0),
             ("Ekstra Telur", 4000), ("Ekstra Kornet", 2000),],
        )
    db.commit()


def ambil_makanan():
    makanan = {}
    for baris in db.execute("SELECT id, nama, harga FROM makanan ORDER BY id"):
        makanan[baris["id"]] = (baris["nama"], baris["harga"])
    return makanan


def cari_pesanan(nomor):
    # nomor antrean mengulang tiap hari, jadi hanya cari pesanan hari ini
    return db.execute(
        f"SELECT * FROM pesanan WHERE nomor_antrean = ? AND {HARI_INI}",
        (nomor,)).fetchone()


def ambil_detail(pesanan_id):
    return db.execute(
        """SELECT m.nama, d.jumlah
           FROM detail_pesanan d JOIN makanan m ON m.id = d.makanan_id
           WHERE d.pesanan_id = ?""", (pesanan_id,)).fetchall()


# ---------- Fungsi bantu untuk pembeli ----------
def harga_dalam_rupiah(angka):
    return f"Rp{angka:,}".replace(",", ".")


def buat_pesanan_baru(makanan):
    print("\n=== DAFTAR MAKANAN ===")
    for id_makanan, (nama, harga) in makanan.items():
        print(f"{id_makanan}. {nama} - {harga_dalam_rupiah(harga)}")


def hitung_total(daftar_sementara):
    makanan = ambil_makanan()
    total = 0
    for id_makanan, jumlah in daftar_sementara.items():
        total += makanan[id_makanan][1] * jumlah
    return total


def tampilkan_daftar_sementara(daftar_sementara):
    makanan = ambil_makanan()
    for id_makanan, jumlah in daftar_sementara.items():
        nama, harga = makanan[id_makanan]
        print(f"{nama} x{jumlah} = {harga_dalam_rupiah(harga * jumlah)}")
    print(f"Total: {harga_dalam_rupiah(hitung_total(daftar_sementara))}")


def tunggu_kembali():
    while input("\nKetik 0 untuk kembali: ") != "0":
        print("Ketik angka 0 untuk kembali.")

# ---------- Fungsi bantu untuk penjual ----------
def catat_ke_file_harian(nomor, nama, daftar_sementara, total):
    makanan = ambil_makanan()
    sekarang = datetime.now()
    nama_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        f"list_pesanan_{sekarang:%Y-%m-%d}.txt")
    file_baru = not os.path.exists(nama_file)

    with open(nama_file, "a") as f:
        if file_baru:  # judul hanya ditulis sekali, saat file baru dibuat
            f.write(f"LIST PESANAN TANGGAL {sekarang:%Y-%m-%d}\n")
            f.write("=" * 40 + "\n")
        f.write(f"Tanggal : {sekarang:%Y-%m-%d}\n")
        f.write(f"Antrean : {nomor}\n")
        f.write(f"Nama    : {nama}\n")
        f.write("Pesanan :\n")
        for id_makanan, jumlah in daftar_sementara.items():
            f.write(f"  - {makanan[id_makanan][0]} x{jumlah}\n")
        f.write(f"Total   : {harga_dalam_rupiah(total)}\n")
        f.write("-" * 40 + "\n")


# ---------- Fitur pembeli ----------
def buat_pesanan_baru(daftar_sementara):
    makanan = ambil_makanan()
    while True:
        buat_pesanan_baru(makanan)
        pilihan = input("\nMasukkan nomor makanan yang ingin dipesan (0 = kembali): ")
        if pilihan == "0":
            return
        if not pilihan.isdigit() or int(pilihan) not in makanan:
            print("Nomor makanan tidak ada.")
            continue

        id_makanan = int(pilihan)
        nama = makanan[id_makanan][0]
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

    makanan = ambil_makanan()
    nomor = db.execute(
        f"SELECT COALESCE(MAX(nomor_antrean), 0) + 1 FROM pesanan WHERE {HARI_INI}"
    ).fetchone()[0]
    total = hitung_total(daftar_sementara)

    cur = db.execute(
        "INSERT INTO pesanan (nama_pemesan, nomor_antrean, total, waktu_pesan) "
        "VALUES (?, ?, ?, datetime('now', 'localtime'))",
        (nama, nomor, total))
    pesanan_id = cur.lastrowid  # id pesanan yang baru saja dibuat

    for id_makanan, jumlah in daftar_sementara.items():
        db.execute(
            "INSERT INTO detail_pesanan (pesanan_id, makanan_id, jumlah, harga_satuan) "
            "VALUES (?, ?, ?, ?)",
            (pesanan_id, id_makanan, jumlah, makanan[id_makanan][1]))
    db.commit()  # tanpa commit, perubahan tidak tersimpan permanen
    catat_ke_file_harian(nomor, nama, daftar_sementara, total)
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

        pesanan = cari_pesanan(int(nomor))
        if pesanan is None:
            print("Nomor antrean tidak ditemukan.")
        else:
            print(f"Antrean {pesanan['nomor_antrean']} a.n. "
                  f"{pesanan['nama_pemesan']}: {pesanan['status']}")


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
password_penjual = "warmindo.pacil"  # contoh password penjual
def minta_password():
    isi = input("Password penjual (0 = kembali): ")
    if isi == "0":
        return False
    if isi == password_penjual:
        return True
    else: 
        print("Password salah.")
        return False

def tampilkan_pesanan_masuk():
    print("\n=== PESANAN MASUK HARI INI ===")
    baris_pesanan = db.execute(
        f"SELECT * FROM pesanan WHERE status != 'selesai' AND {HARI_INI} "
        "ORDER BY nomor_antrean").fetchall()
    if not baris_pesanan:
        print("Tidak ada pesanan yang sedang aktif.")
    for p in baris_pesanan:
        print(f"\nAntrean {p['nomor_antrean']} - {p['nama_pemesan']} [{p['status']}]")
        for d in ambil_detail(p["id"]):
            print(f"  {d['nama']} x{d['jumlah']}")
        print(f"  Total: {harga_dalam_rupiah(p['total'])}")


def lihat_pesanan_masuk():
    tampilkan_pesanan_masuk()
    tunggu_kembali()


def ubah_status_pesanan():
    while True:
        tampilkan_pesanan_masuk()
        nomor = input("\nNomor antrean yang diubah statusnya (0 = kembali): ")
        if nomor == "0":
            return
        if not nomor.isdigit():
            print("Nomor antrean harus berupa angka.")
            continue

        pesanan = cari_pesanan(int(nomor))
        if pesanan is None:
            print("Nomor antrean tidak ditemukan.")
            continue
        if pesanan["status"] == "selesai":
            print("Pesanan ini sudah selesai.")
            continue

        status_lama = pesanan["status"]
        status_baru = URUTAN_STATUS[status_lama]
        db.execute("UPDATE pesanan SET status = ? WHERE id = ?",
                   (status_baru, pesanan["id"]))
        db.commit()
        print(f"Antrean {pesanan['nomor_antrean']}: {status_lama} -> {status_baru}")


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
    daftar_sementara = {}  # daftar_sementara belum disimpan ke database sampai pembeli memesan
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


siapkan_database()
main()
db.close()
