# Spesifikasi Kasus Uji Unit Testing Frontend (Test Case Specification)

Dokumen ini memuat spesifikasi kasus uji (*Unit Testing*) berbasis *White-Box Testing* (*Statement, Branch, State, & Component Rendering Coverage*) untuk halaman utama frontend pada aplikasi web *Software Testing*:
1. `CreateTestCasePage`
2. `ExecutionTestCaseFailPage`
3. `ExecutionTestCasePassPage`
4. Custom Hook: `useAuthGuard`
5. Template Komponen: `ModuleWorkspaceLayout`
6. Komponen Kartu: `FailCard`, `PassCard`, dan `MinimalCard`

### Ringkasan Hasil Eksekusi Pengujian:
- **Total Test Cases**: 50 Kasus Uji
- **Lulus (PASS)**: 50 Kasus Uji (100%)
- **Gagal (FAIL)**: 0 Kasus Uji
- **Total Berkas Uji**: 6 Berkas Uji di `src/__tests__/`
- **Status Build**: Production Build Lolos Validasi (`tsc && vite build`)

---

## 1. Unit: `CreateTestCasePage`

| Test ID | Unit | Struktur yang diuji | Kondisi | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-FE-CTP-01** | `CreateTestCasePage` | Render Komponen Utama | Pengguna login dengan sesi akun siswa yang valid | Aplikasi menampilkan komponen layout utama: `Layout`, `Menu`, `ModuleSpecificationCard`, dan `CodeAndCfgPanels` | **PASS** |
| **TC-FE-CTP-02** | `CreateTestCasePage` | Pengecekan Keberadaan Sesi | Data `session` tidak ditemukan di `localStorage` | Aplikasi mendeteksi ketiadaan sesi dan otomatis mengarahkan pengguna ke halaman `/login` | **PASS** |
| **TC-FE-CTP-03** | `CreateTestCasePage` | Pembacaan Data Sesi | Data `session` tersimpan dalam format JSON yang valid | Aplikasi berhasil membaca data sesi dan menetapkan status login pengguna sebagai aktif | **PASS** |
| **TC-FE-CTP-04** | `CreateTestCasePage` | Penanganan Data Sesi Rusak | Data `session` di `localStorage` rusak atau bukan JSON valid | Aplikasi menangani error dengan aman melalui `try-catch` tanpa menyebabkan halaman *blank/crash* | **PASS** |
| **TC-FE-CTP-05** | `CreateTestCasePage` | Validasi Sesi Kosong | Nilai variabel `session` bernilai `null` | Aplikasi langsung memindahkan rute (*redirect*) ke `/login` | **PASS** |
| **TC-FE-CTP-06** | `CreateTestCasePage` | Validasi Sesi Aktif | Nilai variabel `session` terisi data login | Aplikasi mempertahankan tampilan halaman pembuatan test case tanpa berpindah rute | **PASS** |
| **TC-FE-CTP-07** | `CreateTestCasePage` | Pengecekan Peran Akun Siswa | Nilai `session.login_type === "student"` bernilai `True` | Aplikasi menampilkan form pembuatan test case: `AddTestCaseCard` dan `MinimalCard` | **PASS** |
| **TC-FE-CTP-08** | `CreateTestCasePage` | Pengecekan Peran Akun Siswa | Nilai `session.login_type` bukan `'student'` (misal: `'teacher'`) | Aplikasi menyembunyikan komponen `AddTestCaseCard` dan `MinimalCard` dari tampilan | **PASS** |
| **TC-FE-CTP-09** | `CreateTestCasePage` $\rightarrow$ `CodeProgramCard` | Render Kode Program Java | Data kode sumber Java berhasil dimuat dari server | Panel menampilkan baris kode program Java lengkap dengan nomor baris dan pewarnaan sintaks | **PASS** |
| **TC-FE-CTP-10** | `CreateTestCasePage` $\rightarrow$ `CodeProgramCard` | Penanganan Gagal Muat Kode Java | Data kode bernilai `null` atau terjadi gangguan koneksi | Panel menampilkan indikator pemuatan (*skeleton loading*) tanpa merusak tampilan antarmuka | **PASS** |
| **TC-FE-CTP-11** | `CreateTestCasePage` $\rightarrow$ `CFGCard` | Render Graf Alir Kontrol (CFG) | Data struktur graf alir kontrol tersedia dan valid | Aplikasi merender kanvas graf CFG secara utuh dan interaktif | **PASS** |
| **TC-FE-CTP-12** | `CreateTestCasePage` $\rightarrow$ `CFGCard` | Penanganan Data Graf Kosong | Data simpul (*node*) dan sisi (*edge*) graf tidak tersedia | Aplikasi menampilkan keterangan bahwa visualisasi struktur CFG belum tersedia | **PASS** |
| **TC-FE-CTP-13** | `CreateTestCasePage` $\rightarrow$ `CodeAndCfgPanels` | Sinkronisasi Interaksi Node CFG ke Baris Kode | Pengguna mengklik salah satu simpul (*node*) pada graf CFG | Baris kode Java yang terhubung dengan node tersebut otomatis tersorot (*highlighted*) | **PASS** |

---

## 2. Unit: `ExecutionTestCaseFailPage`

| Test ID | Unit | Struktur yang diuji | Kondisi | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-FE-ETCF-01** | `ExecutionTestCaseFailPage` | Render Komponen Utama | Pengguna login sebagai siswa dan data eksekusi gagal tersedia | Aplikasi menampilkan seluruh komponen halaman, kartu `FailCard`, dan tombol `"Laporan Pengujian"` | **PASS** |
| **TC-FE-ETCF-02** | `ExecutionTestCaseFailPage` | Pengecekan Keberadaan Sesi | Pengguna membuka halaman tanpa memiliki sesi login | Aplikasi otomatis mengarahkan pengguna kembali ke halaman `/login` | **PASS** |
| **TC-FE-ETCF-03** | `ExecutionTestCaseFailPage` | Proteksi Peran Pengguna | Pengguna login menggunakan akun pengajar (`teacher`) | Aplikasi mengalihkan pengguna ke halaman dashboard pengajar di `/dashboard-teacher` | **PASS** |
| **TC-FE-ETCF-04** | `ExecutionTestCaseFailPage` | Proteksi Peran Pengguna | Pengguna login menggunakan akun siswa (`student`) | Aplikasi mengizinkan pengguna tetap berada di halaman untuk melihat hasil eksekusi | **PASS** |
| **TC-FE-ETCF-05** | `ExecutionTestCaseFailPage` | Penyajian Metrik pada `FailCard` | Data hasil uji gagal (cakupan < batas minimum) tersedia | Kartu `FailCard` menampilkan persentase cakupan kode, batas minimal, tanggal eksekusi, dan status gagal secara akurat | **PASS** |
| **TC-FE-ETCF-06** | `ExecutionTestCaseFailPage` | Penanganan Akses Langsung URL | Halaman dibuka langsung atau di-refresh tanpa membawa data navigasi | Kartu `FailCard` menerapkan nilai default cadangan (coverage 0%) tanpa memicu error | **PASS** |
| **TC-FE-ETCF-07** | `ExecutionTestCaseFailPage` | Aksi Tombol `"Laporan Pengujian"` | Pengguna menekan tombol `"Laporan Pengujian"` dengan ID modul yang valid | Aplikasi berpindah ke rute `/test-result?topikModulId=<modulId>` dengan membawa data modul | **PASS** |
| **TC-FE-ETCF-08** | `ExecutionTestCaseFailPage` | Aksi Tombol `"Laporan Pengujian"` | Pengguna menekan tombol `"Laporan Pengujian"` saat ID modul bernilai `null` | Aplikasi tetap berpindah rute secara aman dengan parameter default tanpa terjadi error | **PASS** |
| **TC-FE-ETCF-09** | `ExecutionTestCaseFailPage` $\rightarrow$ `CodeAndCfgPanels` | Render Panel Kode dan Graf CFG | Data modul dan struktur program tersedia | Panel kode sumber Java dan graf CFG ditampilkan secara berdampingan | **PASS** |
| **TC-FE-ETCF-10** | `ExecutionTestCaseFailPage` | Efek Pengguliran Layar Otomatis | Komponen halaman selesai dimuat ke layar | Halaman otomatis melakukan *smooth scroll* ke bawah menuju kartu hasil pengujian | **PASS** |

---

## 3. Unit: `ExecutionTestCasePassPage`

| Test ID | Unit | Struktur yang diuji | Kondisi | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-FE-ETCP-01** | `ExecutionTestCasePassPage` | Render Komponen Utama | Pengguna login sebagai siswa dan data eksekusi lulus tersedia | Aplikasi menampilkan seluruh tata letak, kartu kelulusan `PassCard`, tombol `"Hasil Pengujian"`, dan tombol `"Kasus Selanjutnya"` | **PASS** |
| **TC-FE-ETCP-02** | `ExecutionTestCasePassPage` | Pengecekan Keberadaan Sesi | Pengguna membuka halaman tanpa memiliki sesi login aktif | Aplikasi langsung memindahkan rute pengguna ke halaman `/login` | **PASS** |
| **TC-FE-ETCP-03** | `ExecutionTestCasePassPage` | Proteksi Peran Pengguna | Pengguna login menggunakan akun pengajar (`teacher`) | Aplikasi mengalihkan pengguna ke dashboard pengajar di `/dashboard-teacher` | **PASS** |
| **TC-FE-ETCP-04** | `ExecutionTestCasePassPage` | Proteksi Peran Pengguna | Pengguna login menggunakan akun siswa (`student`) | Aplikasi mengizinkan siswa mengakses halaman hasil kelulusan pengujian | **PASS** |
| **TC-FE-ETCP-05** | `ExecutionTestCasePassPage` | Penyajian Metrik pada `PassCard` | Data hasil uji memenuhi batas kelulusan (cakupan $\ge$ batas minimum) | Kartu `PassCard` menampilkan persentase cakupan kode, batas minimal, perolehan poin, status lulus, dan tanggal eksekusi | **PASS** |
| **TC-FE-ETCP-06** | `ExecutionTestCasePassPage` | Penanganan Akses Langsung URL | Halaman dibuka langsung atau di-refresh tanpa membawa data navigasi | Kartu `PassCard` mengisi nilai default cadangan secara aman tanpa mengalami error rendering | **PASS** |
| **TC-FE-ETCP-07** | `ExecutionTestCasePassPage` | Aksi Tombol `"Hasil Pengujian"` | Pengguna menekan tombol `"Hasil Pengujian"` | Aplikasi berpindah ke rute `/test-result?topikModulId=<modulId>` dengan membawa data modul | **PASS** |
| **TC-FE-ETCP-08** | `ExecutionTestCasePassPage` | Respon API Tantangan: Akses Ditolak | API `nextChallenge` mengembalikan status `403 Forbidden` | Aplikasi mengarahkan pengguna ke halaman pemberitahuan kesalahan di `/error` | **PASS** |
| **TC-FE-ETCP-09** | `ExecutionTestCasePassPage` | Respon API Tantangan: Error Server | API `nextChallenge` mengembalikan status error `500 Server Error` | Aplikasi menangkap error pada blok `catch` dan mencatatnya ke konsol tanpa membuat antarmuka rusak | **PASS** |
| **TC-FE-ETCP-10** | `ExecutionTestCasePassPage` | Respon API Tantangan: Masalah Jaringan | Terjadi kegagalan koneksi jaringan saat memanggil API | Aplikasi menangani kegagalan jaringan secara aman dan mencatat pesan error ke log konsol | **PASS** |
| **TC-FE-ETCP-11** | `ExecutionTestCasePassPage` | Navigasi Tantangan: Modul Berikutnya Tersedia | API mengembalikan data ID modul berikutnya (`ms_id_topik_modul`) | Aplikasi mengarahkan pengguna ke modul selanjutnya di `/topikModul?topikModulId=...` | **PASS** |
| **TC-FE-ETCP-12** | `ExecutionTestCasePassPage` | Navigasi Tantangan: Modul Habis, Topik Tersedia | Seluruh modul pada topik telah selesai, namun ID topik aktif tersedia | Aplikasi mengarahkan pengguna kembali ke daftar tantangan topik di `/list-challanges?idTopik=...` | **PASS** |
| **TC-FE-ETCP-13** | `ExecutionTestCasePassPage` | Navigasi Tantangan: Seluruh Topik Selesai | Respon API tidak memiliki data modul maupun data topik berikutnya | Aplikasi mengarahkan pengguna ke halaman utama daftar topik pembelajaran di `/list-topics` | **PASS** |
| **TC-FE-ETCP-14** | `ExecutionTestCasePassPage` $\rightarrow$ `CodeAndCfgPanels` | Render Panel Kode dan Graf CFG | Data modul dan struktur program berhasil dimuat | Panel menampilkan kode sumber Java dan visualisasi graf CFG secara berdampingan | **PASS** |
| **TC-FE-ETCP-15** | `ExecutionTestCasePassPage` | Efek Pengguliran Layar Otomatis | Komponen halaman selesai dimuat ke layar | Halaman otomatis melakukan *smooth scroll* ke bawah menuju kartu hasil pengujian dan tombol aksi | **PASS** |

---

## 4. Unit: Custom Hook `useAuthGuard`

| Test ID | Unit | Struktur yang diuji | Kondisi | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-FE-AUTH-01** | `useAuthGuard` | Validasi Sesi Kosong | Item `session` tidak ditemukan di `localStorage` | Hook mengembalikan status `isAuthenticated: false` dan otomatis mengarahkan ke rute `/login` | **PASS** |
| **TC-FE-AUTH-02** | `useAuthGuard` | Pembacaan Sesi Valid | Data JSON sesi siswa yang valid tersimpan di `localStorage` | Hook mengembalikan `isAuthenticated: true`, `userRole: 'student'`, dan nilai `token` otentikasi yang sesuai | **PASS** |
| **TC-FE-AUTH-03** | `useAuthGuard` | Penanganan Format JSON Rusak | Data `session` berisi teks acak yang rusak / bukan format JSON | Blok `try-catch` menangkap error, mencatat pesan error ke konsol, dan mengembalikan `isAuthenticated: false` tanpa menyebabkan aplikasi crash | **PASS** |
| **TC-FE-AUTH-04** | `useAuthGuard` | Proteksi Hak Akses Peran Akun | Hook dipanggil dengan opsi `{ requiredRole: 'student' }`, namun pengguna login sebagai `'teacher'` | Hook otomatis mengalihkan rute pengguna ke halaman `/dashboard-teacher` | **PASS** |
| **TC-FE-AUTH-05** | `useAuthGuard` | Kustomisasi Rute Pengalihan | Hook dipanggil dengan rute pengalihan kustom pada `redirectToLogin` dan `redirectToUnauthorized` | Aplikasi mengeksekusi perpindahan rute sesuai alamat URL kustom yang dikonfigurasi | **PASS** |

---

## 5. Unit: Template Komponen `ModuleWorkspaceLayout`

| Test ID | Unit | Struktur yang diuji | Kondisi | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-FE-MWL-01** | `ModuleWorkspaceLayout` | Render Struktur Layout Bersama | Komponen di-mount dengan menyertakan elemen anak (*children*) | Aplikasi merender komponen `Layout`, `Menu`, `ModuleSpecificationCard`, `CodeAndCfgPanels`, serta menampilkan elemen anak di area bawah | **PASS** |
| **TC-FE-MWL-02** | `ModuleWorkspaceLayout` | Penerusan Konfigurasi Panel CFG | Komponen dipanggil dengan properti `showCyclomaticComplexity={false}` | Aplikasi meneruskan nilai properti tersebut ke sub-komponen `CodeAndCfgPanels` dengan tepat | **PASS** |

---

## 6. Unit: Komponen Kartu Hasil Eksekusi (`FailCard`, `PassCard`, `MinimalCard`)

| Test ID | Unit | Struktur yang diuji | Kondisi | Expected Result | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-FE-CARD-01** | `FailCard` | Tampilan Pesan Gagal: Cakupan Kurang | Properti `statusEksekusi={true}` dan `minimumCoverage={80}` (Semua kasus uji lulus, tetapi cakupan belum mencapai batas minimal) | Kartu menampilkan pesan: `"Mohon maaf, belum bisa melanjutkan ke case berikutnya. Minimal coverage test 80%."` | **PASS** |
| **TC-FE-CARD-02** | `FailCard` | Tampilan Pesan Gagal: Ada Test Case Gagal | Properti `statusEksekusi={false}` (Terdapat kasus uji yang berstatus FAILED) | Kartu menampilkan pesan: `"Mohon maaf, belum bisa melanjutkan ke case berikutnya. Ubah kembali test case sampai semua hasil test result berstatus PASS."` | **PASS** |
| **TC-FE-CARD-03** | `PassCard` | Penyajian Informasi Poin dan Tanggal | Komponen diberikan properti `poin={150}` dan `tanggalEksekusi="2026-08-17"` | Kartu menampilkan teks perolehan `"150 Poin"` dan label `"Tanggal Eksekusi: 2026-08-17"` secara tepat | **PASS** |
| **TC-FE-CARD-04** | `MinimalCard` | Nilai Batas Cakupan Default | Komponen di-mount tanpa memberikan properti `minimumCoverage` | Kartu menampilkan teks informasi: `"Minimal Coverage Test Bernilai: 80%"` | **PASS** |
| **TC-FE-CARD-05** | `MinimalCard` | Nilai Batas Cakupan Kustom | Komponen di-mount dengan properti `minimumCoverage={90}` | Kartu menampilkan teks informasi: `"Minimal Coverage Test Bernilai: 90%"` | **PASS** |
