#Fun-Project-2---AI-Chatbot-with-Streamlit

==============================

#🤖 AI Chatbot with Streamlit And Hugging Face
==============================

Deskripsi:
-----------
Aplikasi chatbot berbasis Streamlit yang terhubung ke OpenRouter AI.
Fitur utama:
- Membuat chat baru dan menyimpan chat history.
- Upload file .txt atau .pdf untuk diringkas AI.
- Memilih model AI dan mengatur parameter temperature dan max tokens.
- Sidebar untuk navigasi chat history dan pengaturan model.
- Input chat sticky di bagian bawah layar.

Preview Aplikasi:
-----------------
[Masukkan screenshot atau link preview aplikasi di sini]

Fitur Utama:
------------
1. Sidebar Settings:
   - Masukkan API Key.
   - Pilih model AI.
   - Atur Temperature dan Max Tokens.
   - Navigasi chat history dan buat chat baru.

2. Halaman Chat Baru:
   - Ketik chat di bagian bawah.
   - Chat AI ditampilkan dengan st.chat_message.
   - Upload file .txt atau .pdf.

3. History Chat:
   - Melihat chat sebelumnya.
   - Pilih chat tertentu atau hapus chat.

Instruksi Penggunaan:
--------------------
1. Persiapan:
   - Install dependencies:
     pip install streamlit requests PyPDF2
   - Siapkan API Key OpenRouter.

2. Menjalankan Aplikasi:
   - Jalankan perintah di terminal:
     streamlit run app.py
   - Ganti 'app.py' dengan nama file script jika berbeda.

3. Menggunakan Sidebar:
   - Masukkan API Key.
   - Pilih model AI.
   - Atur Temperature dan Max Tokens.
   - Klik 'New Chat' untuk chat baru atau pilih chat dari 'Chat History'.

4. Menggunakan Chat:
   - Ketik pesan di input chat bawah dan tekan Enter.
   - Upload file .txt atau .pdf menggunakan tombol upload.
   - AI akan membaca dan merespon file yang diupload.

5. Mengelola Chat History:
   - Pilih chat dari sidebar untuk membuka.
   - Klik ikon '🗑️' untuk menghapus chat tertentu.

Tips:
-----
- Gunakan file PDF yang tidak terenkripsi agar AI bisa membaca teks.
- Pastikan koneksi internet stabil saat menggunakan aplikasi.

==============================

