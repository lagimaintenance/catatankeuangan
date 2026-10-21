# ConvertRK Cloud Fix

Patch dari ConvertRK Multi-Bank untuk Streamlit Community Cloud.

## Perubahan
- Identifikasi BCA tidak lagi hanya bergantung pada frasa persis `REKENING GIRO` + `MUTASI`; mengenali indikasi `REKENING TAHAPAN`, `TAHAPAN BCA`, dan header BCA lain.
- Mengerti bulan/tahun dari nama file `JAN_2022.pdf` atau `JANUARI-2022.pdf` bila periode header tidak terbaca.
- Jika PDF gagal diproses, tampilkan diagnostik versi Python/pdfplumber, jumlah halaman, jumlah karakter teks, format bank yang terdeteksi, dan indikator umum (tanpa isi transaksi).
- `pdfplumber==0.11.9` disamakan dengan environment pengujian; `packages.txt` tetap memakai Poppler yang dibutuhkan untuk parsing Permata cepat.
- Format Excel asli, 1 sheet GL dan logika saldo tetap sama.

## Memperbarui GitHub
1. Ganti `app.py`, `multi_bank_parser.py`, `requirements.txt`, `packages.txt`, dan `Bank_template.xlsx` di root repository GitHub yang digunakan Streamlit. Jangan upload PDF berisi data rahasia ke repository GitHub.
2. Commit ke branch yang benar (umumnya `main`).
3. Streamlit Community Cloud > Manage app > Reboot app; jalankan tes PDF yang sama di lokal dan Cloud.
4. Jika masih gagal, salin hasil diagnostik teknis, terutama "Bank terbaca", "Karakter teks halaman 1", dan `pdfplumber`.

## Batasan
Parser khusus BCA masih bergantung pada lokasi kolom seperti pada contoh BCA Januari 2026. Jika PDF BCA 2022 memakai layout transaksi lain, patch ini **belum tentu** dapat mengonversinya. PDF 2022 yang menimbulkan masalah tidak tersedia untuk diuji, sehingga jangan gunakan output tanpa memeriksa saldo dan jumlah transaksi.
