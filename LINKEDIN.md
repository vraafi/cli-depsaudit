Kami mengaudit requirements.txt dengan alat sendiri. depsaudit menemukan pin longgar, duplikat, versi tidak valid, dan paket tanpa pin. Keluarannya bisa JSON, jadi langsung dipakai di CI.

Satu berkas Python, 7043 B, tanpa dependensi eksternal. README 1157 B menjelaskan pemakaian dan format keluaran. QC lapis kode lulus penuh dalam 0,97 detik dengan 0 temuan.

Kami tidak mengklaim lebih dari itu. Cakupan baru requirements.txt, belum poetry atau pipenv. Deteksi duplikat masih per baris, bukan resolusi transitif. Angka 0 temuan berlaku pada berkas uji, bukan jaminan untuk semua repo.

Langkah berikut: jalankan `depsaudit --json` di satu repositori Anda minggu ini dan bagikan temuan pertama ke tim. #depsaudit #ci #python