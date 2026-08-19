# Prototaip Saringan DASS-21 + TF-CBT-DHT

Aplikasi Streamlit setempat untuk pengumpulan DASS-21, pengiraan skor Kemurungan/Kebimbangan/Stres, saringan trauma eksploratori berasaskan domain DHT, storan Excel dan dashboard admin.

> **Penting:** Ini prototaip penyelidikan, bukan peranti perubatan, diagnosis atau triage klinikal. Item trauma TF-CBT-DHT ialah item baharu yang belum divalidasi. Dapatkan semakan pakar, kelulusan etika dan SOP respons risiko sebelum penggunaan sebenar.

## Cara paling mudah (Windows)

1. Pastikan Python 3.10 atau lebih baharu dipasang.
2. Klik dua kali `MULA_APLIKASI.bat`.
3. Pada penggunaan pertama, tunggu pemasangan komponen selesai.
4. Masukkan kata laluan admin apabila diminta. Kata laluan tidak disimpan dalam fail projek.
5. Pelayar akan membuka aplikasi. Pilih **Borang Pelajar** atau **Dashboard Admin**.

Jika Windows menghalang skrip, buka PowerShell di folder ini dan jalankan:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_app.ps1
```

## Cara manual

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:DASS_ADMIN_PASSWORD = "tetapkan-kata-laluan-yang-kuat"
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Lokasi data

Pada kali pertama dijalankan, aplikasi menyalin `database_template.xlsx` ke:

```text
data/dass_tfcbt_dht_database.xlsx
```

Anda boleh memilih lokasi lain sebelum memulakan aplikasi:

```powershell
$env:DASS_DATABASE_PATH = "D:\Kajian\data\dass_kajian.xlsx"
```

Tutup fail pangkalan data di Microsoft Excel sebelum pelajar menghantar borang. Excel boleh mengunci fail dan menghalang submission baharu.

## Aliran penggunaan

### Pelajar

- Masukkan ID kajian/pelajar sahaja; jangan masukkan nama atau nombor IC.
- Jawab semua 21 item DASS berdasarkan minggu yang lalu.
- Bahagian trauma ialah pilihan dan boleh dilangkau.
- Selepas submission, skor dan kategori dipaparkan serta disimpan ke Excel.

### Pensyarah / penyelidik

- Log masuk ke Dashboard Admin menggunakan kata laluan yang ditetapkan semasa aplikasi dimulakan.
- Tapis rekod mengikut kohort, fasa, skor, kategori, keutamaan, bendera keselamatan, domain DHT atau item trauma.
- Muat turun CSV rekod ditapis atau salinan pangkalan data Excel penuh.

## Struktur workbook

- `README` — tujuan, privasi dan amaran penggunaan.
- `Submissions_Raw` — satu baris bagi setiap submission; jangan ubah data mentah.
- `Trauma_Long` — satu baris bagi setiap respons trauma untuk sorting/analisis.
- `Codebook_DASS` — teks item dan subskala.
- `Codebook_Trauma` — pemetaan domain DHT, tahap keperluan dan impak TF-CBT.
- `Thresholds` — julat kategori DASS-21.
- `Scoring_Check` — kalkulator audit manual berasaskan formula Excel.
- `Dashboard_Summary` — ringkasan formula apabila workbook dibuka dalam Excel.
- `Audit_Log` — log penciptaan rekod tanpa menyimpan ID pelajar asal.

## Logik pemarkahan

- Kemurungan: item 3, 5, 10, 13, 16, 17, 21.
- Kebimbangan: item 2, 4, 7, 9, 15, 19, 20.
- Stres: item 1, 6, 8, 11, 12, 14, 18.
- Jumlah mentah setiap subskala didarab 2 sebelum kategori ditentukan.
- Respons trauma `2` atau `3` dianggap indikator positif untuk sorting penyelidikan.
- `TR01` atau `TR07` pada respons sekurang-kurangnya `1` menghasilkan bendera keselamatan.
- Keutamaan `Segera/Tinggi/Sederhana/Rutin` ialah peraturan operasi prototaip, bukan klasifikasi klinikal.

## Privasi dan tadbir urus minimum

- Gunakan kod peserta; simpan jadual padanan nama secara berasingan dan terenkripsi.
- Hadkan akses folder data kepada penyelidik yang diluluskan.
- Sandarkan fail dengan kaedah terkawal dan dokumentasikan versi data.
- Jangan letakkan fail data mentah dalam WhatsApp, e-mel biasa atau storan awam.
- Aplikasi tidak menghantar notifikasi automatik. Tetapkan jadual semakan dan SOP respons sebelum mengumpul data sebenar.
- Tentukan tempoh penyimpanan, proses pembetulan rekod, pemadaman dan pelaporan insiden dalam protokol kajian.

## Rujukan

- Borang awam DASS KKM: <https://mits.moh.gov.my/Modules/Patient/public-dass/>
- Pemarkahan DASS-21 dalam kajian Malaysia: <https://pmc.ncbi.nlm.nih.gov/articles/PMC6805560/>
- Aplikasi Dharuriyyat, Hajiyyat dan Tahsiniyyat dalam kaunseling: <https://doi.org/10.37134/bitara.vol10.7.2017>
- Domain impak dan prinsip TF-CBT: <https://pmc.ncbi.nlm.nih.gov/articles/PMC4476061/>
- Talian HEAL 15555: <https://jknselangor.moh.gov.my/htar/index.php/en/pengumuman-awam/661-talian-heal-15555>

## Ujian teknikal

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_scoring.py
```

