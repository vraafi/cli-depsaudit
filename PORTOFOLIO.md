## Masalah

Tim engineering menumpuk dependensi di `requirements.txt` tanpa disiplin. Pin longgar, duplikat, versi tidak valid, dan paket tanpa pin lolos ke review. Audit manual lambat dan tidak konsisten.

## Yang Dibangun

`depsaudit` adalah CLI Python yang membaca `requirements.txt` dan melaporkan empat kelas masalah: pin longgar, duplikat, versi tidak valid, dan paket tanpa pin. Mode `--json` menghasilkan keluaran terstruktur untuk dipakai pipeline CI. Kode inti ada di `depsaudit.py` (6852 B) dengan dokumentasi `README.md` (1404 B).

## Keputusan Teknis

Kami pisahkan lapis kode sebagai satu-satunya lapis yang diuji. Audit berjalan tanpa dependensi eksternal berat agar bisa dipanggil di runner mana pun. Format `--json` dipilih supaya hasil bisa dikonsumsi mesin lain, bukan dibaca manusia saja.

## Bukti

QC selesai dalam 0,5 detik. Lapis aktif: kode. Lapis lulus: kode. Temuan: 0. Berkas diperiksa: 1 Python, 0 JavaScript, 1 JSON, 0 Lua, 4 lain.

## Batasan

QC baru mencakup lapis kode. Lapis runtime dan integrasi belum diaktifkan. Angka temuan 0 berlaku pada berkas uji, bukan pada seluruh repositori pengguna.