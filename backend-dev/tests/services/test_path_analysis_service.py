import pytest
from unittest.mock import patch
from core.types import NodeType
from services.path_analysis_service import (
    NodeAdapter,
    _path_vector,
    _adds_rank,
    _rank,
    _shortest_node_path,
    _path_covering_edge,
    _format_path,
    generate_independent_paths,
    PathAnalysisService
)

class TestPathAnalysisServiceFunctions:
    def test_node_adapter(self):
        """
        Test Case Name: Konversi Data Node menjadi Objek NodeAdapter
        Precondition: Terdapat data mentah berupa dictionary dari database yang berisi informasi node (ID, tipe, dan urutan).
        Step to Execute: 
            1. Masukkan data dictionary yang lengkap ke dalam NodeAdapter.
            2. Masukkan data dictionary yang tipe node-nya salah (invalid).
            3. Masukkan data dictionary yang sama sekali tidak memiliki kolom tipe node.
        Test Data: 
            - Node 1: tipe "START"
            - Node 2: tipe "INVALID_TYPE"
            - Node 3: tanpa kolom tipe
        Expected Result: Data berhasil diubah menjadi objek NodeAdapter. Jika tipe node tidak valid atau kosong, sistem akan secara otomatis memberinya tipe bawaan (fallback) yaitu "DECISION".
        """
        adapter = NodeAdapter({"id_node": "1", "node_type": "START", "execution_order": 1})
        assert adapter.id_node == "1"
        assert adapter.node_type == NodeType.START
        assert adapter.execution_order == 1

        adapter2 = NodeAdapter({"ms_id_node": "2", "node_type": "INVALID_TYPE"})
        assert adapter2.node_type == NodeType.DECISION

        adapter3 = NodeAdapter({"ms_id_node": "3"})
        assert adapter3.node_type == NodeType.DECISION
        
    def test_path_vector(self):
        """
        Test Case Name: Perhitungan Representasi Biner dari Jalur (Path Vector)
        Precondition: Setiap garis penghubung (edge) dalam graf memiliki nomor indeks yang unik.
        Step to Execute: 
            1. Definisikan pemetaan edge ke indeks (A->B adalah 0, B->C adalah 1).
            2. Berikan sebuah jalur yang melewati node A, lalu B, lalu C.
            3. Hitung nilai vektor jalurnya.
        Test Data: Jalur = [A, B, C]. Indeks edge yang dilewati adalah 0 dan 1.
        Expected Result: Fungsi mengembalikan nilai angka 3. Angka ini adalah representasi biner yang menandakan edge 0 dan 1 telah dilewati secara unik.
        """
        edge_index = {("A", "B", ""): 0, ("B", "C", ""): 1, ("A", "C", ""): 2}
        path = ["A", "B", "C"]
        vector = _path_vector(path, edge_index)
        assert vector == 3

    def test_rank_and_adds_rank(self):
        """
        Test Case Name: Pengecekan Keunikan Kombinasi Jalur (Linear Independence)
        Precondition: Terdapat sekumpulan nilai vektor dari jalur-jalur yang sudah dipilih sebelumnya.
        Step to Execute: 
            1. Masukkan vektor baru ke dalam kumpulan vektor lama.
            2. Cek apakah vektor baru ini memberikan variasi edge yang benar-benar baru, atau hanya kombinasi dari jalur-jalur lama.
        Test Data: Vektor lama = [1, 2]. Vektor baru yang diuji = 3 (gabungan 1 dan 2) dan 4 (jalur baru).
        Expected Result: Vektor 3 ditolak (False) karena hanya perulangan dari jalur yang sudah ada. Vektor 4 diterima (True) karena merupakan jalur yang benar-benar unik.
        """
        assert _rank([1, 2]) == 2
        assert _rank([1, 2, 3]) == 2
        assert _adds_rank([1, 2], 3) is False
        assert _adds_rank([1, 2], 4) is True

    def test_shortest_node_path(self):
        """
        Test Case Name: Pencarian Rute Terpendek Antar Node (Shortest Path)
        Precondition: Tersedia struktur peta yang menghubungkan antar node (Adjacency List).
        Step to Execute: 
            1. Cari rute dari node A menuju node D.
            2. Cari rute dari node B menuju titik akhir mana pun (Terminal Node).
            3. Cari rute dari node A menuju node E yang tidak terhubung.
        Test Data: Peta hubungan node: A terhubung ke B. B terhubung ke C dan D. C kembali ke A. D adalah jalan buntu.
        Expected Result: 
            - Rute A ke D menghasilkan [A, B, D].
            - Rute B ke titik akhir (D) menghasilkan [B, D].
            - Rute A ke E menghasilkan None (karena jalan tidak ada).
        """
        adjacency = {
            "A": [{"id_finish_node": "B"}],
            "B": [{"id_finish_node": "C"}, {"id_finish_node": "D"}],
            "C": [{"id_finish_node": "A"}],
            "D": []
        }
        path = _shortest_node_path(["A"], "D", adjacency)
        assert path == ["A", "B", "D"]

        path2 = _shortest_node_path(["B"], None, adjacency, terminal_nodes=["D"])
        assert path2 == ["B", "D"]

        path3 = _shortest_node_path(["A"], "E", adjacency)
        assert path3 is None

    def test_path_covering_edge(self):
        """
        Test Case Name: Pembuatan Jalur yang Melewati Garis Tertentu (Edge Covering)
        Precondition: Terdapat sebuah target garis penghubung (edge) yang wajib dilalui oleh jalur uji.
        Step to Execute: 
            1. Minta fungsi untuk membuat rute utuh dari Start menuju End, tapi WAJIB melewati garis A->B.
            2. Minta fungsi untuk melewati garis X->Y yang sebenarnya tidak ada.
        Test Data: Titik awal = A, Titik akhir = C. Target garis yang harus dilewati = A->B.
        Expected Result: 
            - Mengembalikan jalur [A, B, C] karena berhasil menyusun awalan (A->A) dan akhiran (B->C).
            - Mengembalikan None jika garis target tidak bisa dijangkau.
        """
        adjacency = {
            "A": [{"id_finish_node": "B"}, {"id_finish_node": "C"}],
            "B": [{"id_finish_node": "D"}],
            "C": [{"id_finish_node": "D"}],
            "D": []
        }
        target_edge = {"id_start_node": "A", "id_finish_node": "B"}
        path = _path_covering_edge(target_edge, ["A"], ["D"], adjacency)
        assert path == ["A", "B", "D"]

        bad_edge = {"id_start_node": "X", "id_finish_node": "Y"}
        path2 = _path_covering_edge(bad_edge, ["A"], ["D"], adjacency)
        assert path2 is None

    def test_format_path(self):
        """
        Test Case Name: Pemformatan Jalur Menjadi Teks yang Mudah Dibaca
        Precondition: Terdapat urutan ID Node yang menyusun sebuah jalur.
        Step to Execute: 
            1. Berikan daftar ID Node beserta tipe dan urutan eksekusinya.
            2. Ubah daftar ID tersebut menjadi teks panah.
        Test Data: ID [1, 2, 3, 4, 5] yang mewakili tipe [START, MERGE, NORMAL (urutan 3), DECISION, END].
        Expected Result: Node tipe MERGE akan disembunyikan. Node lainnya diubah sesuai nama/urutannya menjadi teks berformat: "Start→3→4→End".
        """
        class DummyNode:
            def __init__(self, t, e):
                self.node_type = t
                self.execution_order = e
        
        node_by_id = {
            "1": DummyNode(NodeType.START, None),
            "2": DummyNode(NodeType.MERGE, None),
            "3": DummyNode(NodeType.NORMAL, 3),
            "4": DummyNode(NodeType.DECISION, None),
            "5": DummyNode(NodeType.END, None)
        }
        
        path = ["1", "2", "3", "4", "5"]
        result = _format_path(path, node_by_id)
        assert result["ids"] == ["1", "3", "4", "5"]
        assert result["nodes"] == ["Start", "3", "4", "End"]
        assert result["path"] == "Start→3→4→End"
        
        # Test default fallback when node_type and execution_order is none
        node_by_id_2 = {"1": DummyNode(None, None)}
        res2 = _format_path(["1"], node_by_id_2)
        assert res2["nodes"] == ["1"] # Fallback label

    def test_generate_independent_paths(self):
        """
        Test Case Name: Pembuatan Basis Jalur Pengujian Utama (Basis Path Generation)
        Precondition: Terdapat data Node dan Edge yang menyusun algoritma diagram alir (Control Flow Graph).
        Step to Execute: 
            1. Berikan graf lurus sederhana (A->B->C).
            2. Berikan graf melingkar (siklus tanpa ujung).
            3. Berikan simulasi kondisi khusus di mana algoritma terpaksa mencari sisa jalur (fase fallback) agar target jumlah jalur terpenuhi.
        Test Data: Nodes: START, NORMAL, END. Edges yang menghubungkan ketiganya.
        Expected Result: 
            - Graf lurus menghasilkan tepat 1 jalur valid: "Start→1→End".
            - Kondisi memutar dan batas-batas anomali bisa ditangani dengan aman tanpa membuat program crash atau macet.
        """
        assert generate_independent_paths([], []) == []

        nodes = [
            NodeAdapter({"id_node": "A", "node_type": "START"}),
            NodeAdapter({"id_node": "B", "node_type": "NORMAL", "execution_order": 1}),
            NodeAdapter({"id_node": "C", "node_type": "END"})
        ]
        edges = [
            {"id_start_node": "A", "id_finish_node": "B", "branch_type": ""},
            {"id_start_node": "B", "id_finish_node": "C", "branch_type": ""}
        ]
        paths = generate_independent_paths(nodes, edges)
        assert len(paths) == 1
        assert paths[0]["path"] == "Start→1→End"

        # Force line 160: start_nodes empty (pure cycle)
        nodes_cycle = [
            NodeAdapter({"id_node": "A", "node_type": "NORMAL"}),
            NodeAdapter({"id_node": "B", "node_type": "NORMAL"})
        ]
        edges_cycle = [
            {"id_start_node": "A", "id_finish_node": "B", "branch_type": ""},
            {"id_start_node": "B", "id_finish_node": "A", "branch_type": ""}
        ]
        paths_cycle = generate_independent_paths(nodes_cycle, edges_cycle)
        assert paths_cycle == []

        # Force line 206: vector == 0
        with patch('services.path_analysis_service._path_vector', return_value=0):
            assert generate_independent_paths(nodes, edges) == []

        # Force line 216-225: Fallback phase using mocked _adds_rank to simulate independent edges missing from cycles
        with patch('services.path_analysis_service._adds_rank', side_effect=[True, True, True, True, True]):
            paths_mocked = generate_independent_paths(nodes, edges, target_count=3)
            # Should reach max_paths (3) because the mocked adds_rank returns True for the fallback edges
            assert len(paths_mocked) == 3

    def test_path_analysis_service_normalize(self):
        """
        Test Case Name: Normalisasi Objek Data Node menjadi Dictionary
        Precondition: Modul ini sering menerima data node dalam bentuk yang bermacam-macam dari ORM Database.
        Step to Execute: 
            1. Berikan data node berupa objek class murni.
            2. Berikan data node berupa dictionary biasa.
            3. Berikan data berupa tipe sembarangan (seperti string).
        Test Data: Objek murni `DummyObj`, dict `{"a": 1}`, dan teks `"string"`.
        Expected Result: Semua tipe data valid akan diseragamkan menjadi format dictionary Python `{}`. Jika tipe sembarangan, akan dikembalikan sebagai dictionary kosong agar tidak error.
        """
        service = PathAnalysisService()
        
        class DummyObj:
            def __init__(self):
                self.id_node = "1"
        
        obj = DummyObj()
        norm1 = service._normalize_node(obj)
        assert norm1["id_node"] == "1"
        
        norm2 = service._normalize_node({"a": 1})
        assert norm2["a"] == 1
        
        norm3 = service._normalize_node("string")
        assert norm3 == {}

    def test_path_analysis_service_get_node_label(self):
        """
        Test Case Name: Penentuan Label Tampilan Sebuah Node
        Precondition: Data mentah sebuah node siap untuk direpresentasikan ke layar.
        Step to Execute: Panggil fungsi untuk mengambil label dari node berdasarkan tipe-nya.
        Test Data: Node bertipe START, END, MERGE, dan Node dengan urutan eksekusi ke-5.
        Expected Result: Menghasilkan teks baku: "Start" untuk START, "End" untuk END, teks kosong "" untuk MERGE, dan angka "5" untuk urutan eksekusi kelima.
        """
        service = PathAnalysisService()
        assert service._get_node_label({"node_type": "START"}, 1) == "Start"
        assert service._get_node_label({"node_type": "END"}, 1) == "End"
        assert service._get_node_label({"node_type": "MERGE"}, 1) == ""
        assert service._get_node_label({"execution_order": 5}, 1) == "5"
        assert service._get_node_label({}, 99) == "99"

    def test_build_unexecuted_paths(self):
        """
        Test Case Name: Penyaringan Jalur yang Belum Dieksekusi (Unexecuted Paths)
        Precondition: Sudah ada sekumpulan jalur uji, dan beberapa node sudah ditandai statusnya (Y = sudah dieksekusi, N = belum).
        Step to Execute: 
            1. Buat graf dengan 2 jalur alternatif. 
            2. Jalur pertama melewati node yang statusnya 'N'. Jalur kedua melewati node yang statusnya 'Y'.
            3. Saring jalur tersebut untuk mencari mana yang masih butuh diuji.
        Test Data: Jalur 1 melewati Node 2 (status N). Jalur 2 melewati Node 3 (status Y).
        Expected Result: Fungsi HANYA mengembalikan jalur pertama ("Start→1→End") karena jalur tersebut memuat blok baris yang belum ter-eksekusi (status N). Jalur yang isinya Y semua akan dibuang.
        """
        service = PathAnalysisService()
        assert service.build_unexecuted_paths([], []) == []

        nodes = [
            {"id_node": "1", "node_type": "START", "tr_status": "Y"},
            {"id_node": "2", "node_type": "NORMAL", "execution_order": 1, "tr_status": "N"},
            {"id_node": "3", "node_type": "NORMAL", "execution_order": 2, "tr_status": "Y"},
            {"id_node": "4", "node_type": "END", "tr_status": "Y"} 
        ]
        edges = [
            {"id_start_node": "1", "id_finish_node": "2"},
            {"id_start_node": "2", "id_finish_node": "4"},
            {"id_start_node": "1", "id_finish_node": "3"},
            {"id_start_node": "3", "id_finish_node": "4"}
        ]
        
        paths = service.build_unexecuted_paths(nodes, edges)
        assert len(paths) == 1
        assert paths[0] == "Start→1→End"

    def test_build_unexecuted_paths_exceptions(self):
        """
        Test Case Name: Penanganan Error Saat Menyaring Jalur
        Precondition: Terdapat data masukan graf yang rusak atau tidak lengkap.
        Step to Execute: Masukkan data garis (edge) yang titik awalnya kosong, titik awalnya tidak dikenali, atau fungsi utama di-mock agar memicu error sistem.
        Test Data: Edge dengan id_start_node = None atau id_start_node = "9" (tidak ada di daftar node).
        Expected Result: Sistem tidak akan crash. Error akan ditangkap diam-diam dan sistem mengembalikan list kosong [].
        """
        service = PathAnalysisService()
        nodes = [{"id_node": "1"}]
        edges = [{"id_start_node": None}]
        assert service.build_unexecuted_paths(nodes, edges) == []
        
        edges2 = [{"id_start_node": "9", "id_finish_node": "8"}]
        assert service.build_unexecuted_paths(nodes, edges2) == []
        
        with patch("services.path_analysis_service.generate_independent_paths", side_effect=Exception("Test Error")):
            edges3 = [{"id_start_node": "1", "id_finish_node": "1"}]
            assert service.build_unexecuted_paths(nodes, edges3) == []

    def test_build_unexecuted_paths_sort(self):
        """
        Test Case Name: Pengurutan Daftar Jalur Secara Numerik (Bukan Alfabet)
        
        [INCIDENT REPORT]
        Bug Title: Path Sorting Logic Silently Fails and Returns 0.0 for All Paths
        Description: Fungsi pengurutan `parse_path_for_sorting` mencoba mengonversi seluruh elemen teks (termasuk kata "Start" dan "End") menjadi angka float secara langsung menggunakan List Comprehension `[float(x) for x in path.split("→")]`. Hal ini memicu `ValueError`, yang kemudian ditangkap oleh outer `except Exception` block dan mereturn nilai default `[0.0]`. Akibatnya, semua jalur mendapat bobot pengurutan yang sama (0.0) dan urutan numerik gagal bekerja sama sekali.
        Attachment Evidence Bug: [SENTRY-LOG-9284] Traceback ValueError: could not convert string to float: 'Start'. Serta lampiran [SCREENSHOT_UI_SORTING_BUG.png] yang menunjukkan urutan jalur di layar berantakan dan tidak terurut secara numerik (10 muncul sebelum 2).
        
        Precondition: Daftar jalur dihasilkan dengan susunan angka yang acak.
        Step to Execute: Minta sistem mengurutkan daftar jalur yang telah selesai dibuat.
        Test Data: Terdapat 2 jalur: "Start→10→End" dan "Start→2→End".
        Expected Result: Array diurutkan berdasarkan logika angka murni, sehingga hasilnya adalah ["Start→2→End", "Start→10→End"]. Fungsi yang telah diperbaiki kini hanya akan mengekstrak elemen numerik dan mengabaikan teks.
        """
        service = PathAnalysisService()
        nodes = [
            {"id_node": "1", "node_type": "START", "tr_status": "Y"},
            {"id_node": "2", "node_type": "NORMAL", "execution_order": 10, "tr_status": "N"},
            {"id_node": "3", "node_type": "NORMAL", "execution_order": 2, "tr_status": "N"},
            {"id_node": "4", "node_type": "END", "tr_status": "N"}
        ]
        edges = [
            {"id_start_node": "1", "id_finish_node": "2"},
            {"id_start_node": "2", "id_finish_node": "4"},
            {"id_start_node": "1", "id_finish_node": "3"},
            {"id_start_node": "3", "id_finish_node": "4"}
        ]
        paths = service.build_unexecuted_paths(nodes, edges)
        
        # Urutan ascending secara float 
        assert paths == ["Start→2→End", "Start→10→End"]

    def test_build_unexecuted_paths_sort_outer_exception(self):
        """
        Test Case Name: Penanganan Error Saat Pengurutan Daftar Jalur
        Precondition: Data jalur yang dihasilkan cacat (misalnya bukan teks / string, melainkan None).
        Step to Execute: Panggil sistem penyaringan namun paksa sistem agar mengembalikan jalur bernilai None.
        Test Data: Nilai kembalian jalur dipaksa menjadi `[None]`.
        Expected Result: Ketika sistem pengurutan mencoba memecah teks (split) pada `None`, error akan ditangkap dengan aman. Data cacat tersebut diurutkan dengan bobot angka default 0.0 tanpa menghentikan aplikasi.
        """
        service = PathAnalysisService()
        nodes = [{"id_node": "1", "node_type": "NORMAL", "tr_status": "N"}]
        edges = [{"id_start_node": "1", "id_finish_node": "1"}]
        
        with patch('services.path_analysis_service.generate_independent_paths', return_value=[{"ids": ["1"], "path": None}]):
            paths = service.build_unexecuted_paths(nodes, edges)
            assert paths == [None]
