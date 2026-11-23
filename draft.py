MENU = {
    1: ("Nasi Goreng", 15000),
    2: ("Mie Ayam", 13000),
    3: ("Es Teh", 4000),
    4: ("Gorengan", 2000),
}

daftar_pesanan = []  # semua pesanan yang sudah dibuat


def rp(angka):
    return f"Rp{angka:,}".replace(",", ".")


def tampilkan_menu():
    print("\n=== MENU ===")
    for id_menu, (nama, harga) in MENU.items():
        print(f"{id_menu}. {nama} - {rp(harga)}")


def hitung_total(list_pesanan_sementara):
    total = 0
    for id_menu, jumlah in list_pesanan_sementara.items():
        total += MENU[id_menu][1] * jumlah
    return total


def tampilkan_list_pesanan_sementara(list_pesanan_sementara):
    for id_menu, jumlah in list_pesanan_sementara.items():
        nama, harga = MENU[id_menu]
        print(f"{nama} x{jumlah} = {rp(harga * jumlah)}")
    print(f"Total: {rp(hitung_total(list_pesanan_sementara))}")


def tunggu_kembali():
    while input("\nKetik 0 untuk kembali: ") != "0":
        print("Ketik angka 0 untuk kembali.")


def cari_pesanan(nomor):
    for pesanan in daftar_pesanan:
        if pesanan["nomor"] == nomor:
            return pesanan
    return None


# ---------- Pilihan 1 ----------
def lihat_daftar_makanan_dan_pesan(list_pesanan_sementara):
    while True:
        tampilkan_menu()
        pilihan = input("\nMasukkan nomor menu yang ingin dipesan (0 = kembali ke menu sebelumnya): ")
        if pilihan == "0":
            return
        if not pilihan.isdigit() or int(pilihan) not in MENU:
            print("Nomor menu tidak ditemukan.")
            continue

        id_menu = int(pilihan)
        nama = MENU[id_menu][0]
        jumlah = input(f"Jumlah {nama} (0 = batal): ")
        if not jumlah.isdigit():
            print("Jumlah harus berupa angka.")
            continue
        jumlah = int(jumlah)
        if jumlah == 0:
            print("Dibatalkan.")
            continue

        list_pesanan_sementara[id_menu] = list_pesanan_sementara.get(id_menu, 0) + jumlah
        print(f"Ditambahkan: {nama} x{jumlah}")


# ---------- Pilihan 2 ----------
def lihat_list_pesanan_sementara(list_pesanan_sementara):
    print("\n=== LIST PESANAN SEMENTARA ===")
    if not list_pesanan_sementara:
        print("Belum ada menu yang dipilih.")
    else:
        tampilkan_list_pesanan_sementara(list_pesanan_sementara)
    tunggu_kembali()


# ---------- Pilihan 3 ----------
def lakukan_pemesanan(list_pesanan_sementara):
    if not list_pesanan_sementara:
        print("\nList pesanan masih kosong. Pilih menu di pilihan 1.")
        tunggu_kembali()
        return

    print("\n=== KONFIRMASI PESANAN ===")
    tampilkan_list_pesanan_sementara(list_pesanan_sementara)

    while True:
        nama = input("\nNama pemesan (0 = kembali ke menu sebelumnya): ").strip()
        if nama == "0":
            return
        if nama != "":
            break
        print("Nama tidak boleh kosong.")

    pesanan = {
        "nomor": len(daftar_pesanan) + 1,
        "nama": nama,
        "isi": dict(list_pesanan_sementara),  # salinan, bukan daftar pesanan aslinya
        "total": hitung_total(list_pesanan_sementara),
        "status": "menunggu",
    }
    daftar_pesanan.append(pesanan)
    list_pesanan_sementara.clear()

    print("\nPesanan berhasil dibuat!")
    print(f"Nomor antrean kamu: {pesanan['nomor']}")
    print(f"Total: {rp(pesanan['total'])} (bayar langsung di kantin)")
    tunggu_kembali()


# ---------- Pilihan 4 ----------
def lihat_status_antrean():
    while True:
        nomor = input("\nNomor antrean kamu (0 = kembali ke menu sebelumnya): ")
        if nomor == "0":
            return
        if not nomor.isdigit():
            print("Masukkan angka.")
            continue

        pesanan = cari_pesanan(int(nomor))
        if pesanan is None:
            print("Nomor antrean tidak ditemukan.")
        else:
            print(f"Antrean {pesanan['nomor']} a.n. {pesanan['nama']}: {pesanan['status']}")


def main():
    list_pesanan_sementara = {}
    while True:
        print("\n=== KANTIN ===")
        print("1 = Lihat daftar makanan dan pesan")
        print("2 = Lihat list pesanan sementara")
        print("3 = Lakukan pemesanan")
        print("4 = Lihat status antrean")
        print("0 = Selesai")
        pilihan = input("Pilih : ")

        if pilihan == "1":
            lihat_daftar_makanan_dan_pesan(list_pesanan_sementara)
        elif pilihan == "2":
            lihat_list_pesanan_sementara(list_pesanan_sementara)
        elif pilihan == "3":
            lakukan_pemesanan(list_pesanan_sementara)
        elif pilihan == "4":
            lihat_status_antrean()
        elif pilihan == "0":
            print("Terima kasih!")
            break
        else:
            print("Pilihan tidak dikenal.")


main()
