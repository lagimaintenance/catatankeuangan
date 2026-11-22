# Financial Dashboard — Personal Finance, Cash Flow & Investments

Aplikasi web berbasis **Streamlit** untuk mengonversi laporan keuangan PDF (Rekening Koran BCA, Billing Kartu Kredit BCA, dan Statement of Account / Tax Report Stockbit) menjadi database terstruktur di **Google Sheets** dan file backup SQLite (`.ckbak` & `.db`), lengkap dengan analisis arus kas, kesehatan likuiditas, serta performa portofolio saham.

---

## Fitur Utama

### 1. Konversi & Sinkronisasi PDF (`Konversi PDF`)
* **Rekening Koran BCA:** Ekstraksi otomatis mutasi debit/kredit, pembersihan deskripsi transaksi, deteksi duplikat, serta pembacaan `SALDO AKHIR` terbaru.
* **Billing Kartu Kredit BCA:** Mendukung file PDF terproteksi *password*, menyaring baris pembayaran/cicilan berjalan agar tidak tercatat ganda, serta membaca `TOTAL TAGIHAN`.
* **Stockbit SoA & Annual Tax Report:** Ekstraksi kepemilikan saham bulanan, `Equity NAB`, riwayat transaksi harian (beli/jual saham, obligasi, bunga obligasi), serta riwayat dividen tahunan.
* **Export Database Lokal:**
  * `CK(dd-mm-yyyy-HHMMSS).ckbak` — File backup SQLite yang dioptimasi (`VACUUM`, `REINDEX`, `journal_mode=DELETE`) agar siap langsung di-restore ke aplikasi Android **Catatan Keuangan**.
  * `INV(dd-mm-yyyy-HHMMSS).db` — File database SQLite untuk data portofolio dan transaksi investasi.

### 2. Analisis Cashflow & Kesehatan Pinjaman (`Dashboard`)
* **Posisi Aktual Cash & Diagnosa Likuiditas:** Menghitung selisih `Saldo Akhir BCA − Limit CC Terpakai` dan mengevaluasi kesehatan pinjaman melalui 4 indikator: *Cash Coverage Ratio*, *Credit Utilization Ratio (CUR)*, *Eksposur CC terhadap Pemasukan*, dan *Net Liquid Worth* (kas bersih + ekuitas portofolio).
* **Ringkasan Arus Kas Tahunan & Bulanan:** Metrik total pemasukan, pengeluaran, *net cashflow*, serta grafik batang pengeluaran per kategori.
* **Filter & Pengurutan ala Excel:** Filter transaksi berdasarkan cakupan waktu (bulan/tahun/semua waktu), jenis transaksi (pengeluaran/pemasukan), multi-pilih kategori, pencarian kata kunci deskripsi, serta pengurutan nominal terbesar–terkecil atau tanggal.
* **Self-Learning Category Rules (`CATEGORY_RULES`):** Perubahan kategori transaksi langsung di tabel otomatis disimpan sebagai aturan kata kunci di Google Sheets, diterapkan secara retroaktif ke seluruh data historis, dan digunakan sebagai prioritas utama saat memproses PDF berikutnya.

### 3. Pelacakan Portofolio Investasi (`Investasi`)
* **Metrik Kinerja Portofolio:** Menghitung *Total Modal*, *Total Aset*, *Unrealized P/L*, *Total Dividen*, **XIRR** (berbasis arus kas RDN dari mutasi BCA dan `Equity NAB`), serta **CAGR**.
* **Visualisasi Interaktif:** Grafik donat alokasi aset per emiten, tabel performa per saham, log transaksi harian, grafik perbandingan *Market Value vs Buying Value*, dan grafik historis *Portfolio Return vs XIRR (%)*.

---

## Struktur Repositori

```text
catatankeuangan/
├── app.py              # Aplikasi utama Streamlit (Parser PDF, Dashboard Cashflow & Investasi)
├── requirements.txt    # Daftar dependensi Python
├── packages.txt        # Dependensi sistem (opsional)
└── README.md           # Dokumentasi proyek
