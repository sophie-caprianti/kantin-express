MENU = {
    1: ("Indomie", 8000),
    2: ("Chicken Katsu", 17000),
    3: ("Nasi Bakar", 10000),
    4: ("Es Teh Jumbo ", 5000),
}

daftar_pesanan = []  # semua pesanan yang sudah dibuat


def harga_dalam_rupiah(angka):
    return f"Rp{angka:,}".replace(",", ".")


def tampilkan_menu():
    print("\n=== MENU ===")
    for nama, harga in MENU.items():
        print(f"{nama} - {harga_dalam_rupiah(harga)}")


def tambah_ke_keranjang(keranjang):
    tampilkan_menu()
    pilihan = input("Nomor menu: ")
    if not pilihan.isdigit() or int(pilihan) not in MENU:
        print("Nomor menu tidak ditemukan.")
        return
    jumlah = input("Jumlah porsi: ")
    if not jumlah.isdigit() or int(jumlah) < 1:
        print("Jumlah harus dalam angka minimal 1.")
        return
    id_menu = int(pilihan)
    keranjang[id_menu] = keranjang.get(id_menu, 0) + int(jumlah)
    print(f"Ditambahkan: {MENU[id_menu][0]} x{jumlah}")


def hitung_total(keranjang):
    total = 0
    for id_menu, jumlah in keranjang.items():
        total += MENU[id_menu][1] * jumlah
    return total


def tampilkan_keranjang(keranjang):
    if not keranjang:
        print("\nKeranjang masih kosong.")
        return
    print("\n=== KERANJANG ===")
    for id_menu, jumlah in keranjang.items():
        nama, harga = MENU[id_menu]
        print(f"{nama} x{jumlah} = {harga_dalam_rupiah(harga * jumlah)}")
    print(f"Total: {harga_dalam_rupiah(hitung_total(keranjang))}")


def buat_pesanan(keranjang):
    if not keranjang:
        print("Keranjang kosong, pilih menu dulu.")
        return
    nama = input("Nama pemesan: ").strip()
    if nama == "":
        print("Nama tidak boleh kosong.")
        return

    pesanan = {
        "nomor": len(daftar_pesanan) + 1,
        "nama": nama,
        "isi": dict(keranjang),  # salinan, bukan keranjang aslinya
        "total": hitung_total(keranjang),
        "status": "menunggu",
    }
    daftar_pesanan.append(pesanan)
    keranjang.clear()

    print("\nPesanan berhasil dibuat!")
    print(f"Nomor antrean kamu: {pesanan['nomor']}")
    print(f"Total: {harga_dalam_rupiah(pesanan['total'])} (silahkan bayar di kantin)")


def cek_status():
    nomor = input("Nomor antrean kamu: ")
    if not nomor.isdigit():
        print("Masukkan angka.")
        return
    for pesanan in daftar_pesanan:
        if pesanan["nomor"] == int(nomor):
            print(f"Antrean {pesanan['nomor']} a/n {pesanan['nama']}: {pesanan['status']}")
            return
    print("Nomor antrean tidak ditemukan.")


keranjang = {}
while True:
    print("\n=== KANTIN DIGITAL ===")
    print("1. Lihat menu")
    print("2. Tambah ke keranjang")
    print("3. Lihat keranjang")
    print("4. Pesan sekarang")
    print("5. Cek status pesanan")
    print("0. Keluar")
    pilihan = input("Pilih: ")
    if pilihan == "1":
        tampilkan_menu()
    elif pilihan == "2":
        tambah_ke_keranjang(keranjang)
    elif pilihan == "3":
        tampilkan_keranjang(keranjang)
    elif pilihan == "4":
        buat_pesanan(keranjang)
    elif pilihan == "5":
        cek_status()
    elif pilihan == "0":
        print("Terima kasih!")
        break
    else:
        print("Pilihan tidak dikenal.")