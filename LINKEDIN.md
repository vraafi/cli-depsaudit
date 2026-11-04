Kami menutup QC depsaudit di lapis kode. Waktu: 0,5 detik. Temuan: 0. Lapis aktif hanya kode, dan lapis itu lulus.

depsaudit adalah CLI yang mengaudit requirements.txt: pin longgar, duplikat, versi tidak valid, dan paket tanpa pin. Keluaran --json membuat hasilnya bisa dipakai pipeline, bukan hanya dibaca mata.

Kami tidak mengklaim lebih dari yang diuji. Lapis runtime dan integrasi belum aktif. Angka 0 temuan berlaku pada berkas uji, bukan seluruh repositori.

Langkah berikutnya konkret: jalankan `depsaudit --json` di CI pada satu repositori nyata minggu ini, lalu perluas cakupan lapis QC. #Python #CLI #DevOps