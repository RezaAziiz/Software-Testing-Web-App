# Dokumen Analisis & Rencana Refactoring Frontend (Refactoring Analysis & Plan)

Dokumen ini memuat hasil analisis arsitektur komponen, identifikasi *code smells*, pelanggaran prinsip rekayasa perangkat lunak, serta rekomendasi perbaikan (*refactoring plan*) untuk tiga halaman utama:
1. `CreateTestCasePage` (`frontend-dev/src/pages/CreateTestCasePage.tsx`)
2. `ExecutionTestCaseFailPage` (`frontend-dev/src/pages/ExecutionTestCaseFailPage.tsx`)
3. `ExecutionTestCasePassPage` (`frontend-dev/src/pages/ExecutionTestCasePassPage.tsx`)

---

## 1. Analisis Struktur Komponen Saat Ini

Ketiga halaman tersebut memiliki struktur antarmuka dan hierarki komponen (*UI Tree*) yang hampir serupa:

```
[ Page Component: CreatePage / FailPage / PassPage ]
 ├── [ Layout & Menu ] ───> Pembungkus halaman global dan navigasi atas
 ├── [ Section 1: ModuleSpecificationCard ] ───> Menampilkan detail modul & tabel parameter input
 ├── [ Section 2: CodeAndCfgPanels ] ───> Panel resizable interaktif:
 │    ├── [ CodeProgramCard ] ───> Penampil kode sumber Java dengan syntax highlighting
 │    └── [ CFGCard ] ───> Kanvas visualisasi Graf Alir Kontrol (Cytoscape) & Nilai CC
 └── [ Section 3: Bagian Aksi & Hasil Pengujian ]
      ├── [ AddTestCaseCard ] ───> Form pembuatan kasus uji (input parameter & ekspektasi)
      ├── [ MinimalCard ] (CreatePage) ───> Informasi batas minimal cakupan pengujian (80%)
      ├── [ FailCard ] (FailPage) ───> Ringkasan hasil uji gagal & metrik cakupan tidak tercapai
      ├── [ PassCard ] (PassPage) ───> Ringkasan kelulusan uji, perolehan poin & badge status
      └── [ Action Buttons ] ───> Tombol "Laporan Pengujian" & "Kasus Selanjutnya"
```

---

## 2. Tabel Analisis Rinci Rencana Refactoring

| ID Refactor | Komponen / Target Unit | Masalah Saat Ini & Pelanggaran Prinsip | Alasan Perlu Refactoring (*Kenapa*) | Rencana Solusi Refactoring (*Bagaimana*) | Dampak & Manfaat |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **RF-FE-01** | **Manajemen Sesi & Hak Akses**<br>`CreateTestCasePage`,<br>`ExecutionTestCaseFailPage`,<br>`ExecutionTestCasePassPage` | **1. Pelanggaran DRY (*Don't Repeat Yourself*) pada Logika Otentikasi**:<br>Kode pembacaan `localStorage.getItem('session')` dan logika verifikasi peran (`login_type != 'student'`) disalin secara identik pada 3 file halaman.<br><br>**2. Pelanggaran Robustness & Defensive Programming**:<br>Operasi `JSON.parse(sessionData)` dieksekusi langsung tanpa blok pelindung `try-catch`. | **Kenapa harus diperbaiki:**<br>1. Jika ada perubahan alur hak akses (misal penambahan peran baru atau perubahan kunci token), pengembang harus mengubahnya satu per satu di ketiga file, yang rawan menimbulkan inkonsistensi.<br>2. Jika data sesi di peramban rusak (*corrupted JSON*), aplikasi langsung mengalami kegagalan fatal (*white-screen crash*) seperti yang terbukti pada uji `TC-FE-CTP-04`. | **Bagaimana cara refactoring-nya:**<br>Buat sebuah *Custom Hook* terpusat, misalnya `useAuthGuard({ requiredRole: 'student' })` yang:<br>- Membaca dan mem-parsing data sesi di dalam blok `try-catch` yang aman.<br>- Mengembalikan status otentikasi (`isAuthenticated`, `userRole`, `token`).<br>- Menangani pengalihan rute (*redirect*) otomatis ke `/login` atau `/dashboard-teacher` secara konsisten. | Logika otentikasi menjadi terpusat pada satu fungsi, basis kode halaman menjadi lebih ringkas, dan aplikasi terhindar dari *crash* akibat data sesi yang tidak valid. |
| **RF-FE-02** | **Komponen Kartu Status Pengujian**<br>`PassCard.tsx`,<br>`FailCard.tsx`,<br>`MinimalCard.tsx` | **1. Pelanggaran DRY pada Struktur Kartu**:<br>`PassCard`, `FailCard`, dan `MinimalCard` memiliki struktur visual 85% identik (wadah `Card`, judul "Hasil Pengujian", ikon status di kiri, deskripsi persentase di kanan, dan tanggal eksekusi), namun dibuat menjadi 3 file komponen terpisah.<br><br>**2. Pelanggaran OCP (*Open-Closed Principle*)**:<br>Komponen kartu saat ini tertutup untuk perluasan status baru. Menambahkan status pengujian baru (misal *Warning* atau *Running*) memaksa pembuatan file komponen baru dari awal.<br><br>**3. Pelanggaran Naming Consistency**:<br>Di dalam file `MinimalCard.tsx`, nama fungsi komponen tertulis `const PassCard` akibat duplikasi kode (*copy-paste*). | **Kenapa harus diperbaiki:**<br>1. Duplikasi markup dan styling menyebabkan ukuran berkas membesar dan setiap perbaikan desain (seperti margin, ukuran font, atau warna) harus diulang di 3 file terpisah.<br>2. Nilai batas kelulusan pada `MinimalCard` masih ditulis manual (*hardcoded* 80%), bukan bersumber dari data modul yang dinamis. | **Bagaimana cara refactoring-nya:**<br>Gabungkan ketiga kartu menjadi satu komponen modular yang fleksibel, misalnya `<ExecutionResultCard />`, dengan properti polimorfik:<br>- `variant`: `'initial'` \| `'pass'` \| `'fail'`<br>- `coverageScore`: angka persentase cakupan<br>- `minimumCoverage`: batas minimal kelulusan<br>- `executionDate`: tanggal eksekusi<br>- `points`: perolehan poin (opsional untuk status lulus). | Menghapus redundansi 3 komponen menjadi 1 komponen yang mudah dipelihara (*maintainable*), konsistensi antarmuka lebih terjamin, dan penambahan varian status baru di masa depan menjadi sangat mudah. |
| **RF-FE-03** | **Template Tata Letak Halaman Modul**<br>`CreateTestCasePage`,<br>`ExecutionTestCaseFailPage`,<br>`ExecutionTestCasePassPage` | **1. Pelanggaran DRY pada Shell Layout Antarmuka**:<br>Urutan tata letak atas: `Layout` $\rightarrow$ `Menu` $\rightarrow$ `ModuleSpecificationCard` $\rightarrow$ `CodeAndCfgPanels` ditulis berulang 100% pada ketiga berkas halaman.<br><br>**2. Pelanggaran SRP (*Single Responsibility Principle*)**:<br>Komponen halaman memikul beban ganda: mengelola struktur tata letak statis atas sekaligus merender bagian bawah (*Section 3*) yang dinamis. | **Kenapa harus diperbaiki:**<br>Ketiga halaman pada dasarnya merupakan satu alur kerja yang sama (pengerjaan modul), hanya berbeda pada bagian kartu bawah (form input vs hasil gagal vs hasil lulus). Perubahan pada susunan panel atas atau penambahan fitur global (misal breadcrumb modul) mengharuskan pengembang mengedit 3 file halaman secara manual. | **Bagaimana cara refactoring-nya:**<br>Ekstrak struktur tata letak atas menjadi sebuah *Template Component* reusable, misalnya `<ModuleWorkspaceLayout />`:<br>- Mengelola susunan tetap (Header, Menu, Spesifikasi Modul, dan Panel Kode/CFG).<br>- Menerima *slot* konten bawah melalui `children` atau properti `footerSection={<AddTestCaseCard />} / {<ExecutionResultCard />}`. | Mengurangi duplikasi kode hingga lebih dari 60% pada berkas halaman utama, memisahkan tanggung jawab tata letak dari logika halaman, dan menyederhanakan penulisan pengujian unit. |
| **RF-FE-04** | **Logika Pengguliran Layar Otomatis**<br>`ExecutionTestCaseFailPage`,<br>`ExecutionTestCasePassPage` | **1. Pelanggaran Clean Code (*Dead/Duplicate Logic*)**:<br>Pada `ExecutionTestCaseFailPage.tsx`, terdapat dua blok `useEffect` terpisah yang menjalankan fungsi yang sama persis (`bottomRef.current?.scrollIntoView`).<br><br>**2. Pelanggaran Reusability**:<br>Logika referensi DOM `bottomRef` dan efek scroll otomatis disalin ulang pada `ExecutionTestCasePassPage.tsx`. | **Kenapa harus diperbaiki:**<br>Adanya dua blok `useEffect` yang identik dalam satu komponen menandakan kode yang tidak sengaja tertinggal saat proses pengembangan. Hal ini membebani siklus hidup komponen (*component lifecycle*) dan menurunkan keterbacaan kode. | **Bagaimana cara refactoring-nya:**<br>1. Hapus salah satu blok `useEffect` yang terduplikasi pada `FailPage`.<br>2. Bungkus logika pengguliran layar ke dalam satu *hook* sederhana, misalnya `useAutoScrollToBottom()`, atau integrasikan langsung ke dalam *mount lifecycle* dari kartu hasil pengujian. | Siklus *rendering* komponen lebih optimal, kode terbebas dari duplikasi yang tidak perlu, dan alur kerja komponen menjadi lebih bersih. |
| **RF-FE-05** | **Manajemen URL & Parameter Kueri**<br>`ExecutionTestCaseFailPage`,<br>`ExecutionTestCasePassPage` | **1. Pelanggaran Declarative React & Idiomatic React Router**:<br>Pengambilan parameter URL menggunakan instansiasi objek browser langsung: `new URLSearchParams(window.location.search)`, padahal proyek telah mengadopsi pustaka `react-router-dom`.<br><br>**2. Pelanggaran Separation of Concerns**:<br>Komponen React seharusnya memanfaatkan abstraksi *routing* yang disediakan framework daripada berinteraksi langsung dengan objek global browser `window`. | **Kenapa harus diperbaiki:**<br>1. Membaca `window.location.search` secara langsung tidak memicu pembaruan state reaktif jika parameter URL berubah tanpa *reload* halaman.<br>2. Ketergantungan langsung pada objek `window` menyulitkan proses mocking dan isolasi pada pengujian unit (*unit test brittleness*). | **Bagaimana cara refactoring-nya:**<br>Ganti pemanggilan objek global dengan *hook* resmi dari React Router: `useSearchParams()`, contoh:<br>`const [searchParams] = useSearchParams();`<br>`const modulId = searchParams.get('topikModulId');` | Kode lebih reaktif mengikuti paradigma React, mempermudah penulisan unit testing dengan `MemoryRouter`, serta lebih aman dari potensi galat saat pengujian. |
| **RF-FE-06** | **Fungsi Navigasi Laporan Pengujian**<br>`ExecutionTestCaseFailPage`,<br>`ExecutionTestCasePassPage` | **Pelanggaran DRY pada Fungsi Aksi Navigasi**:<br>Fungsi `handleNavigateToTestResult` yang bertugas membentuk URL `/test-result?topikModulId=...` dan menyertakan state `{ modul_id }` ditulis persis sama di berkas `FailPage` dan `PassPage`. | **Kenapa harus diperbaiki:**<br>Jika format URL laporan atau struktur data navigasi yang dibutuhkan diubah di kemudian hari, pengembang berisiko lupa memperbarui salah satu halaman, mengakibatkan rute navigasi yang rusak (*broken link*). | **Bagaimana cara refactoring-nya:**<br>Pindahkan fungsi navigasi ke dalam komponen tombol aksi bersama atau gunakan fungsi pembantu (*navigation helper*), misalnya `navigateToTestResult(navigate, modulId, navigationData)`. | Menjamin konsistensi alur navigasi laporan uji di seluruh halaman hasil eksekusi serta mencegah perbedaan parameter antar halaman. |
| **RF-FE-07** | **Pembersihan Kode Mati & Komentar Usang**<br>`ExecutionTestCasePassPage.tsx`,<br>`FailCard.tsx`, `PassCard.tsx` | **Pelanggaran Clean Code (*Clutter & Dead Code*)**:<br>Terdapat blok kode yang sudah tidak dipakai tetapi tetap ditinggalkan dalam bentuk komentar, seperti:<br>- Blok `useEffect` kosong berisi komentar di baris 106-116 pada `ExecutionTestCasePassPage.tsx`.<br>- Komentar impor `// import { Button }...` dan fungsi yang dinonaktifkan di `FailCard.tsx` dan `PassCard.tsx`.<br>- Variabel lingkungan yang tidak dipakai (`// const modulId = import.meta.env.VITE_MODULE_ID;`). | **Kenapa harus diperbaiki:**<br>Komentar kode usang menambah beban kognitif (*cognitive load*) bagi siapa pun yang membaca kode dan memberi kesan bahwa basis kode belum selesai atau kurang terawat. | **Bagaimana cara refactoring-nya:**<br>Lakukan pembersihan menyeluruh (*clean-up*) dengan menghapus seluruh baris komentar kode lama, variabel tak terpakai (*unused variables*), dan impor pustaka yang tidak digunakan. | Basis kode menjadi jauh lebih bersih, rapi, mudah dibaca, serta mencerminkan standar kode profesional untuk laporan Tugas Akhir. |
| **RF-FE-08** | **Standardisasi Desain & Nilai Statis**<br>`CodeAndCfgPanels.tsx`,<br>`ExecutionTestCasePassPage.tsx`,<br>`FailCard.tsx`, `PassCard.tsx` | **1. Pelanggaran Maintainability & Design Consistency pada Styling**:<br>Penggunaan gaya sebaris (*inline CSS*) dengan nilai statis (*magic values*) seperti `style={{ height: "700px" }}`, `rounded-[10]`, `rounded-[20]`, dan `style={{ fontSize: "14px" }}` yang bercampur dengan kelas utilitas Tailwind.<br><br>**2. Pelanggaran Responsiveness pada Layout**:<br>Penggunaan kelas `w-screen` pada elemen flexbox dalam halaman dapat memicu *horizontal scrollbar overflow* di layar tertentu. | **Kenapa harus diperbaiki:**<br>1. Percampuran *inline styles* dengan Tailwind CSS menyulitkan penyesuaian tema (*theming*) dan melanggar keseragaman sistem desain aplikasi.<br>2. Kelas `w-screen` mengabaikan lebar *scrollbar* peramban sehingga dapat merusak tata letak responsif pada resolusi laptop/desktop tertentu. | **Bagaimana cara refactoring-nya:**<br>1. Ganti seluruh *inline styles* dengan kelas standar Tailwind CSS (misal: `h-[700px]`, `rounded-xl`, `text-sm`, `text-base`).<br>2. Ganti kelas `w-screen` menjadi `w-full max-w-full` agar pas di dalam kontainer `Layout`. | Tampilan antarmuka menjadi sepenuhnya responsif, bebas *glitch* tata letak horizontal, dan konsistensi desain Tailwind terjaga. |

---

## 3. Rincian Analisis Komponen Pembantu (Child Components)

### A. Komponen Penampil Kode Program (`CodeProgramCard.tsx`)
* **Tanggung Jawab**: Merender baris kode Java, nomor baris, dan penyorotan sintaks (*syntax highlighting*).
* **Evaluasi**: Komponen berfungsi dengan baik melalui fungsi pembantu `highlightJavaLine`.
* **Rekomendasi Refactor**: Pastikan logika pemuatan data kode sumber terpisah secara bersih dari komponen antarmuka (*Separation of Presentation and Data*).

### B. Komponen Graf Alir Kontrol (`CFGCard.tsx` & `CodeAndCfgPanels.tsx`)
* **Tanggung Jawab**: Merender graf alir kontrol menggunakan Cytoscape, menampilkan Cyclomatic Complexity, dan sinkronisasi klik node ke baris kode.
* **Evaluasi**: Integrasi interaktif sudah berjalan baik.
* **Rekomendasi Refactor**: Rapikan tombol samping untuk *collapse/expand* panel agar menggunakan kelas Tailwind murni tanpa *inline styles* yang menumpuk.

### C. Komponen Spesifikasi Modul (`ModuleSpecificationCard.tsx`)
* **Tanggung Jawab**: Menyajikan ringkasan modul dan daftar parameter input beserta aturan validasinya (*range*, *enumerasi*, dsb.).
* **Evaluasi**: Fungsi pembantu `parseValidationRule` saat ini diletakkan di dalam berkas komponen.
* **Rekomendasi Refactor**: Ekstrak fungsi `parseValidationRule` ke berkas utilitas terpisah (`src/utils/validationRuleHelper.ts`) agar fungsi tersebut dapat diuji secara mandiri melalui *unit test*.

---

## 4. Ilustrasi Arsitektur: Sebelum vs. Sesudah Refactoring

```
========================================================================================
SEBELUM REFACTORING (Tinggi Duplikasi & Keterikatan Kuat)
========================================================================================

[CreateTestCasePage]
 ├── Salinan Logika Auth (session & redirect) [DUPLIKASI]
 ├── Shell Tata Letak Atas (Layout + Menu + SpecCard + CodeCfgPanels) [DUPLIKASI]
 ├── AddTestCaseCard
 └── MinimalCard (Komponen duplikat dengan hardcoded 80%)

[ExecutionTestCaseFailPage]
 ├── Salinan Logika Auth (session & redirect) [DUPLIKASI]
 ├── Shell Tata Letak Atas (Layout + Menu + SpecCard + CodeCfgPanels) [DUPLIKASI]
 ├── Salinan useAutoScroll (2x useEffect duplikat) [REDUNDAN]
 ├── AddTestCaseCard
 ├── FailCard (Komponen duplikat)
 └── Salinan Fungsi handleNavigateToTestResult [DUPLIKASI]

[ExecutionTestCasePassPage]
 ├── Salinan Logika Auth (session & redirect) [DUPLIKASI]
 ├── Shell Tata Letak Atas (Layout + Menu + SpecCard + CodeCfgPanels) [DUPLIKASI]
 ├── Salinan useAutoScroll [DUPLIKASI]
 ├── AddTestCaseCard
 ├── PassCard (Komponen duplikat)
 └── Salinan Fungsi handleNavigateToTestResult [DUPLIKASI]

========================================================================================
SESUDAH REFACTORING (Modular, Reusable, & Bersih)
========================================================================================

       ┌─────────────────────────────────────────────────────────────┐
       │             Modul & Utilitas Bersama (Shared)               │
       ├─────────────────────────────────────────────────────────────┤
       │ 1. useAuthGuard()          -> Otentikasi & Proteksi Peran   │
       │ 2. ModuleWorkspaceLayout   -> Shell Tata Letak Terpadu      │
       │ 3. ExecutionResultCard     -> Kartu Hasil Bersama (Pass/Fail)│
       │ 4. Navigation Helpers      -> Navigasi Laporan Terpusat     │
       └─────────────────────────────────────────────────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
  [CreateTestCasePage]     [ExecutionTestCaseFailPage]  [ExecutionTestCasePassPage]
  - useAuthGuard()         - useAuthGuard()             - useAuthGuard()
  - ModuleWorkspaceLayout  - ModuleWorkspaceLayout      - ModuleWorkspaceLayout
    - AddTestCaseCard        - ExecutionResultCard        - ExecutionResultCard
    - ExecutionResultCard      (variant="fail")             (variant="pass")
      (variant="initial")
```
