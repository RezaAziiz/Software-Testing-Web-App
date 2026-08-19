# Analisis dan Rekomendasi Solusi: Penanganan Sesi Habis (Session Expiration) & UX Feedback di Seluruh Halaman & Peran

## 1. Ringkasan Eksekutif & Latar Belakang Masalah

Saat ini terdapat kendala sistemik pada aplikasi web pengujian (*Software Testing Web App*) terkait manajemen sesi pengguna. Masalah ini berdampak luas pada **seluruh peran (Mahasiswa dan Dosen)** serta terjadi di **semua halaman dan fitur aplikasi**:

1. **Kegagalan Tersembunyi (*Silent Failure*) di Seluruh Aksi & Form**:
   - **Bagi Dosen**: Saat menyusun topik baru, menambahkan modul, mengunggah kode sumber (*source code*), mengunggah data mahasiswa (*upload Excel/CSV*), atau mengunduh rekap nilai. Jika sesi kedaluwarsa (*expired*), aksi klik tombol simpan/unggah tidak memberikan respon apa pun atau hanya memunculkan error generik tanpa memberitahu bahwa sesi telah habis.
   - **Bagi Mahasiswa**: Saat menyusun test case, mengedit test case, menjalankan eksekusi pengujian, atau membuka tantangan (*challenge*). Ketika sesi habis, data tidak tersimpan dan eksekusi terhenti diam-diam.
2. **Ketergantungan pada *Refresh* Manual (F5)**:
   - Pengguna di seluruh halaman baru menyadari sesinya habis setelah merasa curiga tombol tidak merespon lalu melakukan *refresh* halaman secara manual (F5), di mana halaman merah `/error` (*Sesi Anda Telah Habis*) baru muncul.
3. **Dampak Kehilangan Data Input (*Data Loss*)**:
   - Jika pengguna dialihkan secara paksa ke halaman merah `/error`, seluruh input formulir yang sedang diketik (seperti formulir topik dosen, konfigurasi modul, maupun draft test case mahasiswa) akan hilang seketika (*frustrating user experience*).
4. **Kendala saat UAT & Jaringan Lambat (*High Latency / Network Timeout*)**:
   - Pada pengujian lapangan (UAT) atau saat jaringan lambat, jeda waktu transaksi data memakan waktu lama. Jika token kedaluwarsa di tengah proses, aplikasi tidak memberikan umpan balik yang jelas apakah request sedang menunggu jaringan (*timeout*) atau ditolak karena sesi habis.

---

## 2. Pemetaan Masalah di Seluruh Halaman & Fitur Aplikasi

Berikut adalah inventarisasi fitur dan halaman yang terdampak oleh masalah sesi kedaluwarsa:

### A. Fitur & Halaman Peran Dosen (Teacher)

| Halaman / Fitur | Berkas Kode (*Source File*) | Aksi Pengguna saat Sesi Habis | Dampak UX saat Ini |
| :--- | :--- | :--- | :--- |
| **Kelola Topik (Tambah/Edit)** | `AddTopicPage.tsx` | Menekan tombol "Simpan Topik" atau "Mapping Modul" | Form tidak terkirim, error 403 ditelan, data isian form topik panjang berisiko hilang saat refresh. |
| **Kelola Modul & Upload Source Code** | `ModuleTestPage.tsx`, `AddModuleForm.tsx` | Menekan tombol "Simpan Modul" atau "Upload Source Code" | Upload file gagal tanpa notifikasi sesi habis; dosen mengira sistem/file upload rusak. |
| **Daftar Topik & Modul** | `ListTopicsPage.tsx`, `ListModulesPage.tsx` | Menekan tombol "Publish Topik" atau "Hapus Modul/Topik" | Status publish/hapus tidak berubah, aksi gagal tanpa pesan kesalahan yang informatif. |
| **Kelola Data Mahasiswa** | `StudentPage.tsx`, `UploadStudentDataForm.tsx`, `AddStudentDataForm.tsx` | Menekan tombol "Upload Data Mahasiswa" atau "Tambah Mahasiswa Manual" | File Excel/CSV gagal diproses, form modal tetap terbuka tanpa kejelasan status sesi. |
| **Nilai & Progres Mahasiswa** | `GradeStudentPage.tsx`, `ProgressStudentPage.tsx` | Menekan tombol "Download Rekap Nilai" atau berpindah halaman (*pagination*) | File Excel tidak terunduh; tabel data kosong/stuck loading. |

---

### B. Fitur & Halaman Peran Mahasiswa (Student)

| Halaman / Fitur | Berkas Kode (*Source File*) | Aksi Pengguna saat Sesi Habis | Dampak UX saat Ini |
| :--- | :--- | :--- | :--- |
| **Pembuatan Test Case** | `CreateTestCasePage.tsx`, `TestCaseFormDialog.tsx` | Menekan tombol "Simpan / Tambah Test Case" | Form dialog tetap terbuka, data gagal masuk database, pesan 403 hanya tercatat di `console.log`. |
| **Perubahan Test Case** | `EditTestCaseFormDialog.tsx` | Menekan tombol "Simpan Perubahan" | Perubahan parameter/expected result tidak tersimpan tanpa notifikasi. |
| **Eksekusi Pengujian** | `AddTestCaseCard.tsx` | Menekan tombol "Eksekusi Test Case" | Spinner loading berhenti atau stuck, eksekusi tidak berjalan, hasil coverage tidak keluar. |
| **Akses Tantangan & Topik** | `AccessTopicsPage.tsx`, `ListChallangesPage.tsx`, `ChallengeCard.tsx` | Mengklik kartu challenge (Ongoing / Learning / Completed) | Halaman tidak berpindah ke workspace modul atau menampilkan data kosong. |
| **Hasil & Halaman Pass/Fail** | `ExecutionTestCasePassPage.tsx`, `ExecutionTestCaseFailPage.tsx`, `TestResultPage.tsx` | Mengklik "Next Challenge" atau melihat log hasil eksekusi | Tombol navigasi soal berikutnya macet / gagal mengambil data soal selanjutnya. |

---

## 3. Analisis Akar Masalah Teknis (*Root Cause Analysis*)

```
               [ DOSEN / MAHASISWA AKTIF BEKERJA ]
   (Menyusun Topik, Upload Data, Mengetik Test Case, Review Nilai)
                               │
                               ▼
            Masa Berlaku Token JWT Habis di Latar Belakang
                               │
                               ▼
                [ Pengguna Menekan Tombol Aksi ]
   (Simpan Form / Upload File / Eksekusi / Download / Navigasi)
                               │
                               ▼
        Backend FastAPI Mengembalikan HTTP 403 Forbidden
                   {"detail": "Expired token."}
                               │
                               ▼
   ┌──────────────────────────────────────────────────────────────┐
   │        Ketiadaan Centralized HTTP Client / Interceptor        │
   │  - Tiap komponen memanggil fetch() mentah secara terpisah    │
   │  - Blok try-catch lokal hanya console.log(error)             │
   │  - Tidak ada event global yang memicu notifikasi sesi habis   │
   └──────────────────────────────────────────────────────────────┘
                               │
                               ▼
             [ Tombol Diam / Form Macet / Silent Fail ]
                               │
                               ▼
           Pengguna Bingung & Melakukan Refresh (F5)
                               │
                               ▼
  [ Lifecycle Mounting GET jalan ──► Baru Terpindah ke Halaman Merah /error ]
       (Semua data form yang belum tersimpan HILANG SEKETIKA)
```

1. **Pemanggilan `fetch()` Tersebar Tanpa Interceptor Terpusat**:
   - Lebih dari 50 titik pemanggilan API di seluruh aplikasi memanggil `fetch()` secara langsung.
   - Penanganan respons `403` tidak seragam: sebagian kecil melakukan `navigate('/error')` (hanya saat pemuatan data awal), sedangkan mayoritas fungsi submit/aksi hanya menangkap error dengan `catch (error) { console.log(error); }`.
2. **Pengecekan Otentikasi Bersifat Pasif (*Passive Guard*)**:
   - Hook `useAuthGuard` hanya memvalidasi keberadaan item `session` di `localStorage` saat pertama kali komponen dirender.
   - Tidak ada proses pemantauan aktif terhadap masa berlaku token JWT (`exp` timestamp) selama pengguna berdiam di satu halaman.
3. **Pemisahan Sesi Antar-Peran Tidak Mengatasi Masalah Waktu Habis**:
   - Baik peran `teacher` maupun `student` menggunakan mekanisme autentikasi JWT yang sama pada backend (`JWTBearer` di `backend-dev/middleware/auth_bearer.py`). Ketika waktu kedaluwarsa tercapai, backend menolak semua request dari kedua peran dengan kode `403`.

---

## 4. Rekomendasi Solusi Berdasarkan Sisi UX & Arsitektur

Untuk memberikan pengalaman pengguna yang mulus (*seamless*), terhindar dari kehilangan data, dan responsif terhadap gangguan jaringan/sesi habis:

---

### Solusi 1: *Global Session Expired Modal* (Solusi Reaktif Terpusat)

Alih-alih memindahkan pengguna secara mendadak ke halaman merah `/error` (yang merusak alur kerja dan menghapus data input), pasang **Modal Sesi Habis Terpusat** di level aplikasi utama (`App.tsx` / `Layout.tsx`).

```
┌──────────────────────────────────────────────────────────────────┐
│  ⚠️ Sesi Anda Telah Berakhir                                     │
│                                                                  │
│  Sesi login Anda telah habis demi keamanan akun.                 │
│  Draft data yang sedang Anda isi telah diamankan ke penyimpanan  │
│  lokal sementara.                                                │
│                                                                  │
│  [  Login Kembali  ]                                             │
└──────────────────────────────────────────────────────────────────┘
```

#### Keunggulan UX:
* **Konsisten di Seluruh Halaman**: Bekerja otomatis untuk Dosen (saat buat topik/upload) maupun Mahasiswa (saat buat test case/eksekusi).
* **Langsung Terpicu Seketika**: Begitu ada aksi yang menerima respons `401`/`403`, modal langsung muncul seketika di atas layar tanpa perlu me-refresh halaman.
* **Anti-Kebingungan**: Pengguna langsung memahami alasan kegagalan aksi tanpa menduga sistem sedang *error/hang*.

---

### Solusi 2: *Centralized API Client & Global Auth Event* (Fondasi Arsitektur)

Membuat modul HTTP Client terpusat (misal: `src/lib/apiClient.ts`) untuk menggantikan seluruh pemanggilan `fetch` mentah di seluruh aplikasi.

```typescript
// Konsep apiClient terpusat
export async function apiClient(endpoint: string, options: RequestInit = {}) {
  const session = getLocalSession();
  
  const headers = {
    "Accept": "application/json",
    ...options.headers,
    ...(session?.token ? { Authorization: `Bearer ${session.token}` } : {}),
  };

  try {
    const response = await fetch(endpoint, { ...options, headers });

    // Deteksi Token Expired / Forbidden
    if (response.status === 403 || response.status === 401) {
      // 1. Simpan form draft aktif bila ada
      saveActiveFormDraft();
      
      // 2. Pancarkan event global
      window.dispatchEvent(new CustomEvent("app:session_expired"));
      
      throw new Error("SESSION_EXPIRED");
    }

    return response;
  } catch (error: any) {
    if (error.name === "TypeError" || error.message.includes("Failed to fetch")) {
      // Penanganan khusus Jaringan Putus / Slow Network
      window.dispatchEvent(new CustomEvent("app:network_error"));
    }
    throw error;
  }
}
```

---

### Solusi 3: *Proactive Session Countdown & Warning Banner* (Pencegahan Sebelum Habis)

Frontend dapat mengekstrak waktu kedaluwarsa (`exp`) langsung dari token JWT saat login berhasil:

1. **Peringatan 2-3 Menit Sebelum Habis**:
   - Menampilkan *toast* atau *banner* notifikasi di bagian atas layar:
     > *"Perhatian: Sesi Anda akan berakhir dalam 2 menit. Segera simpan perubahan Anda."*
2. **Auto-Trigger Saat Waktu Tepat Habis**:
   - Jika pengguna membiarkan aplikasi terbuka tanpa aksi hingga waktu habis, modal sesi habis langsung aktif otomatis di layar tanpa menunggu pengguna menekan tombol apa pun.

---

### Solusi 4: *Form Draft Auto-Save & Recovery* (Perlindungan Data Input)

Mencegah hilangnya hasil kerja panjang pengguna saat sesi terputus:

1. **Auto-Save Draft ke `sessionStorage`/`localStorage`**:
   - Untuk Dosen: Formulir data topik baru, konfigurasi modul, atau data input mahasiswa.
   - Untuk Mahasiswa: Nilai input parameter test case dan expected result.
2. **Pemulihan Otomatis (*Draft Recovery*)**:
   - Setelah pengguna login kembali dan membuka halaman/modul yang sama, sistem mendeteksi draft dan menampilkan pesan:
     > *"Ditemukan data yang belum tersimpan sebelumnya. [Pulihkan Data] | [Buang Draft]"*

---

### Solusi 5: *Penanganan Khusus Jaringan Lambat & UAT (Timeout vs Session Expiry)*

Untuk memastikan kelancaran saat pengujian UAT pada jaringan lambat:

1. **Indikator Loading Visual yang Jelas pada Seluruh Tombol**:
   - Semua tombol aksi (Simpan Topik, Upload File, Tambah Test Case, Eksekusi, Download) wajib mengunci tombol (*disable*) dan menampilkan *spinner* + teks progres (*"Menyimpan data..."*, *"Mengunggah berkas..."*, *"Mengeksekusi pengujian..."*).
   - Mencegah pengguna melakukan *multiple click/spam click* yang membebani server dan jaringan.
2. **Pemisahan Penanganan Error Jaringan vs Error Sesi**:
   - **Jika Jaringan Lambat / Timeout**: Munculkan alert kuning *"Koneksi jaringan terganggu/lambat. Silakan coba kembali."* (Pengguna **tidak** dikeluarkan dari akun).
   - **Jika Sesi Habis (403/401)**: Munculkan modal merah *"Sesi login telah berakhir. Silakan login kembali."*.

---

## 5. Matriks Perbandingan Penanganan di Seluruh Halaman

| Aspek | Kondisi Saat Ini | Rekomendasi Solusi Baru |
| :--- | :--- | :--- |
| **Cakupan Peran** | Terdampak pada Mahasiswa & Dosen | Ditangani seragam di seluruh peran |
| **Cakupan Halaman** | Tersebar tidak konsisten di 20+ file | Terpusat melalui 1 API Client & 1 Modal |
| **Respon saat Sesi Habis** | Diam / macet, baru ketahuan setelah F5 | Modal popup langsung muncul seketika di layar |
| **Nasib Data Input Form** | Hilang total jika di-redirect/refresh | Tersimpan otomatis via draft recovery |
| **Respon Jaringan Lambat** | Tidak jelas apakah loading, timeout, atau expired | Ada status loading tombol + pemisahan error timeout |
| **Pencegahan Dini** | Tidak ada indikator waktu sesi | Warning toast 2 menit sebelum sesi habis |

---

## 6. Rencana Tahapan Implementasi (*Roadmap*)

Rencana eksekusi teknis yang disarankan jika implementasi kode disetujui:

1. **Tahap 1: Centralized API Client & Global Auth Event**
   - Implementasikan `src/lib/apiClient.ts` untuk menangani otentikasi token, interceptor 401/403, dan error jaringan.
   - Refactor pemanggilan `fetch` di halaman Dosen dan Mahasiswa ke `apiClient`.
2. **Tahap 2: Global Session Expired Modal & Toast Warning**
   - Buat komponen modal sesi habis dan pasang di root (`App.tsx`).
   - Buat custom hook `useSessionWatcher` untuk memantau timestamp `exp` token JWT secara proaktif.
3. **Tahap 3: Visual Feedback & Loading State Optimization**
   - Pastikan seluruh tombol form dan aksi eksekusi memiliki status disabled + spinner loading yang konsisten.
4. **Tahap 4: Form Draft Auto-Save (Anti Data-Loss)**
   - Tambahkan mekanisme auto-save lokal pada form-form kritis (Form Topik Dosen, Form Test Case Mahasiswa).

---

## 7. Kesimpulan

Permasalahan *session expiration* dan perlunya *refresh* manual bukan hanya terjadi pada mahasiswa saat membuat test case, melainkan **masalah arsitektural menyeluruh yang dialami oleh dosen dan mahasiswa di semua fitur aplikasi**. 

Dengan menerapkan **API Client terpusat**, **Modal Sesi Habis In-Place**, **Pemantau Waktu Token Proaktif**, serta **Penyelamat Draft Formulir**, seluruh pengguna akan mendapatkan kepastian status sesi secara instan tanpa perlu me-refresh halaman dan tanpa khawatir kehilangan data hasil kerja mereka.
