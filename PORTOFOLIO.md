## Masalah
Tim engineering sering membiarkan requirements.txt membusuk. Pin longgar seperti `flask>=0.10` dan paket tanpa pin membuat build tidak reproducible. Duplikat dan versi tidak valid lolos review karena tidak ada pemeriksaan otomatis.

## Yang Dibangun
depsaudit, CLI yang mengaudit requirements.txt. Ia mendeteksi pin longgar, baris duplikat, versi tidak valid, dan paket tanpa pin. Setiap temuan mengikuti format konsisten. Flag `--json` mengeluarkan hasil mesin-baca agar langsung masuk pipeline CI.

## Keputusan Teknis
Audit berjalan murni di lapisan kode. Satu berkas Python (7043 B) menangani parsing, validasi, dan pelaporan tanpa dependensi eksternal. README 1157 B mendokumentasikan pemakaian dan format keluaran. Keputusan ini menjaga alat ringan dan mudah ditanam di runner mana pun. Logika validasi dipisah dari presentasi agar kelak bisa menambah format keluaran tanpa mengubah inti.

## Bukti (angka QC)
QC mencatat 0,97 detik untuk seluruh pemeriksaan. Lapis aktif: kode. Lapis lulus: kode. Temuan QC: 0. Komposisi kode: 1 Python, 1 berkas lain. Tidak ada lapis JS, JSON, atau Lua; cakupan itu tidak diklaim.

## Batasan
Alat hanya membaca requirements.txt, belum menangani poetry, pipenv, atau constraint files. Deteksi duplikat berbasis baris, bukan resolusi dependensi transitif. Belum ada uji adversarial terhadap nama paket eksotis. Angka 0 temuan berlaku pada berkas uji saat QC, bukan jaminan untuk semua repositori.