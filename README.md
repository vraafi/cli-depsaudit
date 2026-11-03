# depsaudit

Alat CLI Python 3.11 untuk mengaudit berkas `requirements.txt`. Mendeteksi:

- Pin longgar (misalnya `>=`, `~=`, atau tanpa pin)
- Paket duplikat
- Versi tidak valid atau operator tidak dikenal
- Paket tanpa pin versi

Hanya menggunakan pustaka standar Python. Tidak ada dependensi eksternal.

## Penggunaan

```bash
python depsaudit.py requirements.txt
python depsaudit.py requirements.txt --json
```

### Opsi

- `berkas`: Path ke berkas requirements.txt (wajib)
- `--json`: Keluarkan hasil dalam format JSON

### Exit code

- `0`: Tidak ada masalah ditemukan
- `1`: Ada masalah ditemukan
- `2`: Berkas tidak ditemukan, tidak dapat dibaca, atau kesalahan argumen

### Contoh keluaran JSON

```json
{
  "berkas": "requirements.txt",
  "jumlah_masalah": 2,
  "temuan": [
    {
      "baris": 1,
      "paket": "requests",
      "tipe": "pin_longgar",
      "pesan": "pin longgar (operator: >=)"
    },
    {
      "baris": 3,
      "paket": "flask",
      "tipe": "duplikat",
      "pesan": "paket duplikat pada baris [3, 5]"
    }
  ]
}
```

## Lisensi

Bebas digunakan dan dimodifikasi.
