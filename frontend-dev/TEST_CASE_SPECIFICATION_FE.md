# Spesifikasi Kasus Uji Unit Testing Frontend (Test Case Specification)

Dokumen ini memuat spesifikasi kasus uji (*Unit Testing*) berbasis *White-Box Testing* (*Statement, Branch, State, & Component Rendering Coverage*) untuk halaman utama frontend pada aplikasi web *Software Testing*:
1. `CreateTestCasePage`
2. `ExecutionTestCaseFailPage`
3. `ExecutionTestCasePassPage`

### Ringkasan Hasil Eksekusi Pengujian (Setelah Refactoring):
- **Total Test Cases**: 38 Kasus Uji
- **Lulus (PASS)**: 38 Kasus Uji (100%)
- **Gagal (FAIL)**: 0 Kasus Uji
- **Status Build**: Production Build Lolos Validasi (`tsc && vite build`)

---

## 1. Unit: `CreateTestCasePage`

| Test ID | Unit | Struktur yang diuji | Kondisi | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-FE-CTP-01** | `CreateTestCasePage` | Render Komponen Utama | Pengguna login dengan sesi siswa valid | Komponen tata letak utama (`Layout`, `Menu`, `ModuleSpecificationCard`, dan `CodeAndCfgPanels`) berhasil ditampilkan | **PASS** |
| **TC-FE-CTP-02** | `CreateTestCasePage` | Pengecekan Data Sesi (`sessionData != null`) | Item `session` tidak ditemukan di `localStorage` | Sistem mendeteksi ketiadaan sesi dan otomatis mengarahkan pengguna ke `/login` | **PASS** |
| **TC-FE-CTP-03** | `CreateTestCasePage` | Pengecekan Data Sesi (`sessionData != null`) | Data `session` tersimpan dalam format JSON yang valid | Data sesi berhasil dibaca (*parsed*) dan status login pengguna aktif | **PASS** |
| **TC-FE-CTP-04** | `CreateTestCasePage` | Penanganan Data Sesi Rusak | Data `session` di `localStorage` rusak / tidak valid | Sistem menangani galat secara aman tanpa membuat tampilan aplikasi membeku (*white-screen crash*) | **PASS** |
| **TC-FE-CTP-05** | `CreateTestCasePage` | Validasi Status Login (`session == null`) | Pengguna belum melakukan login | Pengguna langsung diarahkan (*redirect*) ke rute `/login` | **PASS** |
| **TC-FE-CTP-06** | `CreateTestCasePage` | Validasi Status Login (`session == null`) | Pengguna telah login secara sah | Pengguna tetap berada pada halaman pembuatan test case | **PASS** |
| **TC-FE-CTP-07** | `CreateTestCasePage` | Hak Akses Siswa (`login_type === "student"`) | Akun teridentifikasi sebagai peran siswa | Form penambahan test case (`AddTestCaseCard` dan `MinimalCard`) ditampilkan | **PASS** |
| **TC-FE-CTP-08** | `CreateTestCasePage` | Hak Akses Siswa (`login_type === "student"`) | Akun memiliki peran selain siswa (misal: pengajar) | Form penambahan test case disembunyikan dari tampilan | **PASS** |
| **TC-FE-CTP-09** | `CreateTestCasePage` $\rightarrow$ `CodeProgramCard` | Render Kode Program Java | Data kode sumber Java berhasil dimuat dari server | Potongan kode Java ditampilkan lengkap dengan penomoran baris dan pewarnaan sintaks | **PASS** |
| **TC-FE-CTP-10** | `CreateTestCasePage` $\rightarrow$ `CodeProgramCard` | Penanganan Gagal Muat Kode Java | Koneksi bermasalah atau data kode bernilai `null` | Menampilkan indikator pemuatan (*skeleton loader*) atau pesan galat yang informatif | **PASS** |
| **TC-FE-CTP-11** | `CreateTestCasePage` $\rightarrow$ `CFGCard` | Render Graf Alir Kontrol (CFG) | Data struktur graf tersedia dan valid | Diagram graf alir kontrol (CFG) muncul secara utuh dan interaktif pada kanvas | **PASS** |
| **TC-FE-CTP-12** | `CreateTestCasePage` $\rightarrow$ `CFGCard` | Penanganan Struktur Graf Kosong | Data simpul (*node*) graf tidak tersedia | Menampilkan pesan keterangan bahwa visualisasi struktur CFG belum tersedia | **PASS** |
| **TC-FE-CTP-13** | `CreateTestCasePage` $\rightarrow$ `CodeAndCfgPanels` | Sinkronisasi Interaksi CFG ke Kode | Pengguna mengklik salah satu simpul (*node*) pada graf | Baris kode Java yang terkait langsung tersorot (*highlighted*) secara otomatis | **PASS** |

---

## 2. Unit: `ExecutionTestCaseFailPage`

| Test ID | Unit | Struktur yang diuji | Kondisi | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-FE-ETCF-01** | `ExecutionTestCaseFailPage` | Render Komponen Utama | Sesi siswa valid dan data ringkasan eksekusi tersedia | Seluruh elemen halaman, kartu hasil gagal (`FailCard`), dan tombol *"Laporan Pengujian"* ditampilkan | **PASS** |
| **TC-FE-ETCF-02** | `ExecutionTestCaseFailPage` | Validasi Status Login (`session != null`) | Pengguna mengakses halaman tanpa sesi login | Pengguna otomatis dialihkan ke halaman `/login` | **PASS** |
| **TC-FE-ETCF-03** | `ExecutionTestCaseFailPage` | Proteksi Peran Pengguna (`login_type != "student"`) | Pengguna masuk menggunakan akun pengajar (`teacher`) | Pengguna dialihkan ke halaman `/dashboard-teacher` | **PASS** |
| **TC-FE-ETCF-04** | `ExecutionTestCaseFailPage` | Proteksi Peran Pengguna (`login_type != "student"`) | Pengguna masuk menggunakan akun siswa (`student`) | Pengguna diberikan izin penuh untuk melihat detail hasil eksekusi | **PASS** |
| **TC-FE-ETCF-05** | `ExecutionTestCaseFailPage` | Penyajian Metrik Pengujian pada `FailCard` | Data hasil uji gagal (cakupan kode < batas minimum) tersedia | Kartu menampilkan persentase cakupan kode, batas minimum, dan status tidak lulus secara akurat | **PASS** |
| **TC-FE-ETCF-06** | `ExecutionTestCaseFailPage` | Penanganan Akses Langsung (`navigationData` kosong) | Halaman diakses langsung / di-refresh tanpa membawa data navigasi | Kartu menerapkan nilai *default* cadangan tanpa menimbulkan galat pada aplikasi | **PASS** |
| **TC-FE-ETCF-07** | `ExecutionTestCaseFailPage` | Aksi Tombol *"Laporan Pengujian"* | Tombol diklik dengan parameter ID modul yang valid | Pengguna diarahkan ke rute `/test-result?topikModulId=<modulId>` dengan membawa data modul | **PASS** |
| **TC-FE-ETCF-08** | `ExecutionTestCaseFailPage` | Aksi Tombol *"Laporan Pengujian"* (Tanpa Modul) | Tombol diklik saat parameter ID modul tidak terdefinisi | Navigasi tetap berjalan aman dengan nilai parameter default | **PASS** |
| **TC-FE-ETCF-09** | `ExecutionTestCaseFailPage` $\rightarrow$ `CodeAndCfgPanels` | Render Kode & Graf Pendukung | Data modul dan struktur program tersedia | Panel kode sumber dan graf CFG ditampilkan untuk membantu siswa mengevaluasi kesalahan | **PASS** |
| **TC-FE-ETCF-10** | `ExecutionTestCaseFailPage` | Perilaku Pengguliran Layar Otomatis | Komponen selesai dimuat pada layar | Halaman otomatis menggulir (*smooth scroll*) ke posisi kartu hasil pengujian di bagian bawah | **PASS** |

---

## 3. Unit: `ExecutionTestCasePassPage`

| Test ID | Unit | Struktur yang diuji | Kondisi | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-FE-ETCP-01** | `ExecutionTestCasePassPage` | Render Komponen Utama | Sesi siswa valid dan data ringkasan eksekusi berhasil | Menampilkan seluruh tata letak, kartu kelulusan (`PassCard`), tombol *"Hasil Pengujian"*, dan tombol *"Kasus Selanjutnya"* | **PASS** |
| **TC-FE-ETCP-02** | `ExecutionTestCasePassPage` | Validasi Status Login (`session != null`) | Pengguna mengakses halaman tanpa sesi aktif | Pengguna langsung diarahkan ke halaman `/login` | **PASS** |
| **TC-FE-ETCP-03** | `ExecutionTestCasePassPage` | Proteksi Peran Pengguna (`login_type != "student"`) | Pengguna masuk menggunakan akun selain siswa (misal: `teacher`) | Pengguna dialihkan ke halaman dashboard pengajar (`/dashboard-teacher`) | **PASS** |
| **TC-FE-ETCP-04** | `ExecutionTestCasePassPage` | Proteksi Peran Pengguna (`login_type != "student"`) | Pengguna terdaftar sebagai siswa aktif | Pengguna diizinkan mengakses halaman hasil kelulusan uji | **PASS** |
| **TC-FE-ETCP-05** | `ExecutionTestCasePassPage` | Penyajian Metrik Kelulusan pada `PassCard` | Pengujian memenuhi batas kelulusan (cakupan $\ge$ minimum) | Kartu menyajikan capaian persentase cakupan, status lulus, perolehan poin, dan tanggal eksekusi | **PASS** |
| **TC-FE-ETCP-06** | `ExecutionTestCasePassPage` | Penanganan Akses Langsung (`navigationData` kosong) | Halaman di-refresh atau dibuka langsung melalui tautan URL | Komponen menggunakan nilai cadangan (*default*) tanpa mengalami kegagalan *rendering* | **PASS** |
| **TC-FE-ETCP-07** | `ExecutionTestCasePassPage` | Aksi Tombol *"Hasil Pengujian"* | Pengguna menekan tombol *"Hasil Pengujian"* | Sistem memicu perpindahan rute ke `/test-result?topikModulId=<modulId>` dengan *payload* data modul | **PASS** |
| **TC-FE-ETCP-08** | `ExecutionTestCasePassPage` | Navigasi Tantangan: Respon Akses Ditolak | API `nextChallenge` mengembalikan kode status `403 Forbidden` | Pengguna dialihkan ke halaman pemberitahuan kesalahan (`/error`) | **PASS** |
| **TC-FE-ETCP-09** | `ExecutionTestCasePassPage` | Navigasi Tantangan: Gangguan Server API | API `nextChallenge` mengembalikan kode status galat `500 Server Error` | Galat tertangkap pada blok penanganan error dan antarmuka pengguna tetap stabil | **PASS** |
| **TC-FE-ETCP-10** | `ExecutionTestCasePassPage` | Navigasi Tantangan: Gangguan Jaringan | Terjadi kegagalan koneksi jaringan saat memanggil API | Sistem menangani kegagalan pemanggilan data dan mencatat informasi kendala ke log konsol | **PASS** |
| **TC-FE-ETCP-11** | `ExecutionTestCasePassPage` | Navigasi Tantangan: Modul Selanjutnya Tersedia | API memberikan respon sukses berisi ID modul berikutnya | Pengguna diarahkan ke modul latihan berikutnya (`/topikModul?topikModulId=...`) | **PASS** |
| **TC-FE-ETCP-12** | `ExecutionTestCasePassPage` | Navigasi Tantangan: Modul Selesai, Topik Tersedia | Seluruh modul pada topik selesai, namun ID topik aktif tersedia | Pengguna diarahkan kembali ke daftar tantangan topik (`/list-challanges?idTopik=...`) | **PASS** |
| **TC-FE-ETCP-13** | `ExecutionTestCasePassPage` | Navigasi Tantangan: Seluruh Topik Selesai | Tidak ada data modul maupun topik berikutnya dari server | Pengguna diarahkan ke halaman utama daftar topik pembelajaran (`/list-topics`) | **PASS** |
| **TC-FE-ETCP-14** | `ExecutionTestCasePassPage` $\rightarrow$ `CodeAndCfgPanels` | Render Kode & Graf Pendukung | Data modul sukses dimuat | Komponen kode sumber Java dan visualisasi graf alir kontrol (CFG) ditampilkan secara interaktif | **PASS** |
| **TC-FE-ETCP-15** | `ExecutionTestCasePassPage` | Perilaku Pengguliran Layar Otomatis | Komponen selesai dimuat pada layar | Tampilan halaman otomatis bergulir (*smooth scroll*) ke posisi kartu kelulusan dan tombol navigasi | **PASS** |
