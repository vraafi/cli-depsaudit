# depsaudit

Alat CLI Python 3.11 untuk mengaudit berkas `requirements.txt`.

## Fitur

- Mendeteksi pin longgar (misalnya `>=1.0`, `~=2.0`, `>1.0`, `!=1.0`, `<=1.0`, `<1.0`).
- Mendeteksi paket duplikat (nama sama, abaikan case dan ekstra).
- Mendeteksi versi tidak valid (format versi tidak sesuai PEP 440 secara sederhana).
- Mendeteksi paket tanpa pin versi.
- Mendeteksi baris dengan format tidak dikenal.
- Keluaran teks ringkas berbahasa Indonesia atau JSON via `--json`.
- Hanya menggunakan pustaka standar Python 3.11.

## Instalasi

Tidak perlu instalasi dependensi. Cukup salin `depsaudit.py` dan jalankan dengan Python 3.11+.

## Penggunaan

```bash
python depsaudit.py [berkas] [--json]
```

- `berkas`: path ke requirements.txt (default: `requirements.txt`).
- `--json`: keluarkan hasil dalam format JSON.

Contoh:

```bash
python depsaudit.py requirements.txt
python depsaudit.py requirements.txt --json
```

## Keluaran JSON

Kunci yang dihasilkan:

- `pin_longgar`: daftar objek `{baris, nama, versi}`.
- `duplikat`: daftar objek `{baris, nama, kemunculan_pertama}`.
- `versi_tidak_valid`: daftar objek `{baris, nama, versi}`.
- `tanpa_pin`: daftar objek `{baris, nama}`.
- `format_tidak_dikenal`: daftar objek `{baris, konten}`.

## Kode Keluar

- `0`: berhasil.
- `2`: berkas tidak ditemukan atau tidak bisa dibaca.

## Lisensi

MIT
