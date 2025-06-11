<p align="center">
  <a href="https://github.com/faniabdullah/bangkit-final-project">
     <img src="https://raw.githubusercontent.com/jessdytan/racikcepat-machinelearning/main/app/static/logo.png" alt="Alt Text" width="100" height="100">
  </a>
  <h3 align="center">Racik Cepat: Resep Lezat Kilat dari Isi Dapurmu!</h3>
  <br></br>
  
  <p align="justify">
    Halo! Selamat datang di repository proyek Capstone tim CC25-CF298 kami dari program Coding Camp Powered by DBS Foundation. Proyek ini adalah hasil dari pembelajaran dan implementasi mendalam kami di bidang Machine Learning, dengan fokus pada solusi praktis yang bisa langsung digunakan dalam kehidupan sehari-hari.
  </p>
  <p>
    Repository ini berisi semua kode dan aset yang terkait dengan alur kerja Machine Learning tim kami, mulai dari pengumpulan data hingga deployment model sebagai API. Tim Web akan menggunakan API ini untuk menampilkan rekomendasi kepada pengguna.
    <br />
    <a href="https://github.com/jessdytan/racikcepat-machinelearning"><strong>Explore the docs »</strong></a>
    <br />
    <br />
  </p>
</p>

# Tentang Aplikasi
Kami mengembangkan sebuah sistem rekomendasi resep yang cerdas dan inovatif. Bayangkan ini: Anda baru pulang dari belanja, punya beberapa bahan sisa di kulkas, tapi bingung mau masak apa. Sistem kami hadir untuk jadi asisten dapur pribadi Anda! Cukup masukkan bahan yang ada di dapur Anda atau foto struk belanja Anda, dan kami akan memberikan ide resep yang paling pas. Tujuan utama kami adalah membantu Anda memaksimalkan setiap bahan makanan yang ada, mengurangi limbah di dapur, dan tentu saja, membuat kegiatan memasak jadi lebih mudah dan menyenangkan.

# Arsitektur dan Implementasi Machine Learning
Berikut adalah bagaimana sistem ML ini dibangun dan diimplementasikan:

1. Pengumpulan dan Pra-pemrosesan Data
    - Web Scraping Cookpad:
  
       Mengumpulkan dataset resep yang komprehensif dari Cookpad menggunakan teknik web scraping. Ini memastikan kita memiliki basis data resep yang luas untuk dilatih.

    - Pra-pemrosesan Data Lanjut:

      Data mentah hasil scraping menjalani proses pra-pemrosesan teks yang mendalam. Ini mencakup lowercasing, penghapusan angka dan simbol, tokenisasi, normalisasi slang (menggunakan slang_dict kustom), penghapusan stopwords spesifik (custom_stopwords), dan stemming. Langkah-langkah ini krusial untuk menstandardisasi teks bahan dan meningkatkan kualitas data.
      
    - Ekstraksi Fitur TF-IDF:

      Untuk merepresentasikan bahan secara numerik dan menangkap relevansinya dalam setiap resep, kita menggunakan metode TF-IDF (Term Frequency-Inverse Document Frequency). Ini mengubah daftar bahan setiap resep menjadi vektor numerik yang siap diproses model.
      
2. Pemodelan dan Inferensi
    - Pemodelan dengan TensorFlow:

       Model rekomendasi utama kita dibangun menggunakan framework TensorFlow. Model ini dirancang untuk memahami hubungan kompleks antara bahan dan resep, memfasilitasi perhitungan skor kemiripan yang akurat.
    - Penyimpanan Aset Model:

      Setelah model dilatih, aset-aset penting seperti daftar judul resep, daftar bahan yang dikenal sistem (ingredient_list), dan bobot model diekspor serta disimpan dalam format .pkl. Ini memungkinkan loading model yang efisien saat API dijalankan.
      
    - Logika Rekomendasi Inti:
      
      Fungsi rekomendasi utama mengimplementasikan perhitungan skor kemiripan antara input bahan pengguna (dari OCR atau manual) dan resep dalam database. Logika ini mengandalkan prinsip yang menyerupai Jaccard Similarity untuk mengidentifikasi kecocokan. Sistem mampu menemukan perfect match atau merekomendasikan resep teratas berdasarkan ambang batas skor yang ditentukan.
      
3. Integrasi Input dan OCR
    - OCR dengan Tesseract:

      Untuk memproses input dari foto struk belanja, kita mengintegrasikan teknologi OCR (Optical Character Recognition) menggunakan Tesseract. Tesseract bertanggung jawab mengekstrak teks (nama bahan) dari gambar struk.
    - Kategorisasi dan Normalisasi Bahan:

      Teks hasil OCR kemudian diproses lebih lanjut untuk mengkategorikan item sebagai bahan makanan dan menormalisasikannya agar sesuai dengan format dan terminologi bahan yang digunakan oleh model kita.
      
4. API dan Deployment
    - Pengembangan API dengan FastAPI:

      Seluruh fungsionalitas Machine Learning dienkapsulasi dan diekspos melalui sebuah API (Application Programming Interface) yang dibangun menggunakan FastAPI. FastAPI dipilih karena performanya yang tinggi, kemudahan dalam membangun endpoint yang robust, dan fitur dokumentasi API otomatisnya.
    - Deployment:
      
      API ini kemudian dideploy ke lingkungan server agar dapat diakses oleh tim frontend dan, pada akhirnya, oleh pengguna akhir.

# Cara menggunakan program
1. Clone Repositori
   ``` bash
   git clone https://github.com/jessdytan/racikcepat-machinelearning.git
   ```
   
2. Masuk ke Folder Repositori
    ``` bash
   cd racikcepat-machinelearning
   ```
    
3. Install Dependensi:
   
   Install semua library Python yang diperlukan dari file requirements.txt:
   ``` bash
   pip install -r requirements.txt
   ```

4. Jalankan API secara lokal
   ``` bash
   uvicorn app.main:app --reload --port=${PORT:-5000}
   ```

5. Buka `http://localhost:5000/docs` untuk melihat dokumentasi API.
   
# Anggota 

|          Nama         | Cohort ID |    Learning Path    |
|:---------------------:|:----------:|:----------------:|
|  Aulia Halimatusyaddiah  |  MC319D5X2048  | Machine Learning |
|  Cut Nabilah Putri Ulanty  |  MC319D5X2391  | Machine Learning |
|  Jessindy Tanuwijaya  |  MC319D5X2462  | Machine Learning |
|   Esra Silvia Sihite  |  FC189D5X0430  |  FrontEnd BackEnd Web |
|   Erika Manik  |  FC189D5X0465  |  FrontEnd BackEnd Web |
|   Glori Pesta Pince Sitorus  |  FC189D5X0839 |  FrontEnd BackEnd Web |
