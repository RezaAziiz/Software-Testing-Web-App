import pytest
from unittest.mock import MagicMock
from infrastructure.cfg_coverage_sync import CfgCoverageSync

class DummyNode:
    def __init__(self, node_id, node_type, line_start=None, line_end=None, line_number=None):
        self.ms_id_node = node_id
        self.ms_node_type = node_type
        self.ms_line_start = line_start
        self.ms_line_end = line_end
        self.ms_line_number = line_number

class DummyEdge:
    def __init__(self, edge_id, start_node, finish_node):
        self.ms_id_edge = edge_id
        self.ms_id_start_node = start_node
        self.ms_id_finish_node = finish_node

class TestCfgCoverageSync:
    def test_synchronize_method_not_executed(self):
        """
        Test Case Name: Sinkronisasi CFG - Metode Tidak Pernah Dieksekusi
        Precondition: XML dari JaCoCo mengindikasikan seluruh baris method memiliki status 'N'.
        Step to Execute: 
            1. Siapkan mock `CfgRepository` berisi node dan edge master.
            2. Inisialisasi objek `CfgCoverageSync`.
            3. Panggil `synchronize()` dengan `line_statuses` yang hanya memuat status 'N'.
            4. Lakukan pengecekan pada parameter yang dipassing ke metode mock saat insert.
        Test Data: 
            - Nodes: n1 (START), n2 (STATEMENT), n3 (END)
            - Edges: n1->n2, n2->n3
            - Status Baris: 1->N, 2->N, 3->N
        Expected Result: 
            - reset_tr_nodes dan reset_tr_edges dipanggil.
            - Seluruh tr_nodes dan tr_edges yang akan disimpan di Database memiliki `tr_status` = 'N'.
        """
        mock_repo = MagicMock()
        mock_repo.get_master_nodes.return_value = [
            DummyNode('n1', 'START', line_number=1),
            DummyNode('n2', 'STATEMENT', line_number=2),
            DummyNode('n3', 'END', line_number=3)
        ]
        mock_repo.get_master_edges.return_value = [
            DummyEdge('e1', 'n1', 'n2'),
            DummyEdge('e2', 'n2', 'n3')
        ]
        
        sync = CfgCoverageSync(mock_repo)
        
        line_statuses = [
            {'line_number': 1, 'status': 'N'},
            {'line_number': 2, 'status': 'N'},
            {'line_number': 3, 'status': 'N'}
        ]
        
        sync.synchronize("topik1", "student1", "modul1", line_statuses)
        
        mock_repo.reset_tr_nodes.assert_called_once_with("topik1", "student1")
        mock_repo.reset_tr_edges.assert_called_once_with("topik1", "student1")
        
        # Verify node insert
        nodes_args = mock_repo.bulk_insert_tr_nodes.call_args[0][0]
        assert len(nodes_args) == 3
        for node in nodes_args:
            assert node['tr_status'] == 'N'
            
        # Verify edge insert
        edges_args = mock_repo.bulk_insert_tr_edges.call_args[0][0]
        assert len(edges_args) == 2
        for edge in edges_args:
            assert edge['tr_status'] == 'N'

    def test_synchronize_method_executed_with_propagation(self):
        """
        Test Case Name: Sinkronisasi CFG - Eksekusi Method dengan Propagasi Maju
        Precondition: Method dieksekusi secara nyata, setidaknya sebagian baris status 'Y' atau 'S'.
        Step to Execute: 
            1. Siapkan mock `CfgRepository` dengan Nodes dan Edges majemuk (serial).
            2. Node n2 di-map ke multiple baris dengan `line_start` & `line_end`.
            3. Panggil `synchronize()` dan lewatkan line_statuses dengan campuran 'Y' dan 'S'.
            4. Periksa node args yang di-*insert*.
        Test Data: 
            - Status Baris: n1->Y (via START logic), n2->Y (dari mapping line 2), n3->S (dari mapping line 3). 
            - n4 tidak diberikan status sehingga 'N', tetapi forward propagation akan mengubahnya.
        Expected Result: 
            - Node START dan END otomatis menjadi 'Y'.
            - Node n4 otomatis menjadi 'Y' karena menerima propagasi dari parent-nya n3 yang memiliki status 'S'.
        """
        mock_repo = MagicMock()
        mock_repo.get_master_nodes.return_value = [
            DummyNode('n1', 'START', line_number=1),
            DummyNode('n2', 'STATEMENT', line_start=2, line_end=2),
            DummyNode('n3', 'STATEMENT', line_number=3),
            DummyNode('n4', 'STATEMENT', line_number=4),
            DummyNode('n5', 'END', line_number=5)
        ]
        mock_repo.get_master_edges.return_value = [
            DummyEdge('e1', 'n1', 'n2'),
            DummyEdge('e2', 'n2', 'n3'),
            DummyEdge('e3', 'n3', 'n4'),
            DummyEdge('e4', 'n4', 'n5')
        ]
        
        sync = CfgCoverageSync(mock_repo)
        
        line_statuses = [
            {'line_number': 1, 'status': 'Y'}, 
            {'line_number': 2, 'status': 'Y'},
            {'line_number': 3, 'status': 'S'},
        ]
        
        sync.synchronize("topik1", "student1", "modul1", line_statuses)
        
        # Verify nodes
        nodes_args = mock_repo.bulk_insert_tr_nodes.call_args[0][0]
        status_map = {n['tr_id_node']: n['tr_status'] for n in nodes_args}
        
        assert status_map['n1'] == 'Y' 
        assert status_map['n2'] == 'Y' 
        assert status_map['n3'] == 'S' 
        assert status_map['n4'] == 'Y' 
        assert status_map['n5'] == 'Y' 
        
        # Verify edges
        edges_args = mock_repo.bulk_insert_tr_edges.call_args[0][0]
        edge_status_map = {e['tr_id_edge']: e['tr_status'] for e in edges_args}
        
        assert edge_status_map['e1'] == 'Y'
        assert edge_status_map['e2'] == 'Y' 
        assert edge_status_map['e3'] == 'Y' 
        assert edge_status_map['e4'] == 'Y' 
        
    def test_synchronize_backward_propagation(self):
        """
        Test Case Name: Sinkronisasi CFG - Pengujian Backward Propagation Spesifik
        Precondition: Sebuah Node dieksekusi ('Y') namun Node parent-nya ('N') tidak ditandai (karena misal mapping line luput).
        Step to Execute: 
            1. Buat graph linier: n1 -> n2 -> n3.
            2. Panggil synchronize() hanya dengan `status` 'Y' di n3.
            3. Amati perubahan di n2.
        Test Data: 
            - n3 baris ke-3 berstatus 'Y'. n2 tidak ada di line_statuses (default 'N').
        Expected Result: 
            - n3 (status Y) akan menularkan status Y-nya ke atas/mundur ke parent n2 (status N) sehingga n2 menjadi Y.
        """
        mock_repo = MagicMock()
        mock_repo.get_master_nodes.return_value = [
            DummyNode('n1', 'START', line_number=1),
            DummyNode('n2', 'STATEMENT', line_number=2),
            DummyNode('n3', 'STATEMENT', line_number=3)
        ]
        mock_repo.get_master_edges.return_value = [
            DummyEdge('e1', 'n1', 'n2'),
            DummyEdge('e2', 'n2', 'n3')
        ]
        
        sync = CfgCoverageSync(mock_repo)
        
        line_statuses = [
            {'line_number': 3, 'status': 'Y'}
        ]
        
        sync.synchronize("topik1", "student1", "modul1", line_statuses)
        
        nodes_args = mock_repo.bulk_insert_tr_nodes.call_args[0][0]
        status_map = {n['tr_id_node']: n['tr_status'] for n in nodes_args}
        
        assert status_map['n2'] == 'Y'

    def test_synchronize_forward_propagation(self):
        """
        Test Case Name: Sinkronisasi CFG - Pengujian Forward Propagation Spesifik
        Precondition: Sebuah Node dieksekusi ('Y') dengan child ('N'), dan child tersebut bukan endpoint yang termutasi Backward Propagation.
        Step to Execute: 
            1. Buat graph dengan percabangan untuk memblokir Backward Propagation dari END.
            2. Panggil synchronize() dengan 'Y' hanya di n1.
        Test Data: 
            - n1 (START) ke n2. n2 ke n3 dan n4. n1 = Y.
        Expected Result: 
            - n1 (status Y) menularkan 'Y' ke bawah (Forward) ke anak tunggalnya (n2), membuat n2 menjadi 'Y'. 
        """
        mock_repo = MagicMock()
        mock_repo.get_master_nodes.return_value = [
            DummyNode('n1', 'START', line_number=1),
            DummyNode('n2', 'STATEMENT', line_number=2),
            DummyNode('n3', 'STATEMENT', line_number=3),
            DummyNode('n4', 'STATEMENT', line_number=4)
        ]
        mock_repo.get_master_edges.return_value = [
            DummyEdge('e1', 'n1', 'n2'),
            DummyEdge('e2', 'n2', 'n3'),
            DummyEdge('e3', 'n2', 'n4')
        ]
        
        sync = CfgCoverageSync(mock_repo)
        
        line_statuses = [
            {'line_number': 1, 'status': 'Y'}
        ]
        
        sync.synchronize("topik1", "student1", "modul1", line_statuses)
        
        nodes_args = mock_repo.bulk_insert_tr_nodes.call_args[0][0]
        status_map = {n['tr_id_node']: n['tr_status'] for n in nodes_args}
        
        assert status_map['n2'] == 'Y'

    def test_synchronize_edge_not_executed(self):
        """
        Test Case Name: Sinkronisasi CFG - Edge Belum Terlalui (Not Executed)
        Precondition: Edge menghubungkan dua Node. Salah satu node berstatus 'N'.
        Step to Execute: 
            1. Buat percabangan n2 -> n3 dan n2 -> n4.
            2. Panggil synchronize() dengan n2='Y' dan n4='Y', tanpa n3.
            3. Analisis status masing-masing Edge.
        Test Data: 
            - n2 (status Y) dan n3 (status N).
        Expected Result: 
            - Edge 'e2' yang menghubungkan n2 ke n3 harus berstatus 'N' karena n3 tidak terlalui.
        """
        mock_repo = MagicMock()
        mock_repo.get_master_nodes.return_value = [
            DummyNode('n1', 'START', line_number=1),
            DummyNode('n2', 'STATEMENT', line_number=2), 
            DummyNode('n3', 'STATEMENT', line_number=3),
            DummyNode('n4', 'STATEMENT', line_number=4)
        ]
        mock_repo.get_master_edges.return_value = [
            DummyEdge('e1', 'n1', 'n2'),
            DummyEdge('e2', 'n2', 'n3'),
            DummyEdge('e3', 'n2', 'n4')
        ]
        
        sync = CfgCoverageSync(mock_repo)
        
        line_statuses = [
            {'line_number': 2, 'status': 'S'},
            {'line_number': 4, 'status': 'Y'}
        ]
        
        sync.synchronize("topik1", "student1", "modul1", line_statuses)
        
        edges_args = mock_repo.bulk_insert_tr_edges.call_args[0][0]
        edge_status_map = {e['tr_id_edge']: e['tr_status'] for e in edges_args}
        
        assert edge_status_map['e1'] == 'Y' 
        assert edge_status_map['e2'] == 'N' 
        assert edge_status_map['e3'] == 'Y' 

    def test_synchronize_edge_executed(self):
        """
        Test Case Name: Sinkronisasi CFG - Edge Terlalui (Executed)
        Precondition: Edge menghubungkan dua Node yang sama-sama tereksekusi.
        Step to Execute: 
            1. Buat koneksi n1 -> n2 -> n3.
            2. Berikan status 'Y' pada seluruh node melalui data XML baris.
            3. Amati status setiap Edge yang ter-insert.
        Test Data: 
            - n2 (status Y) dan n3 (status Y).
        Expected Result: 
            - Edge 'e2' (n2->n3) bernilai 'Y'. Seluruh Edge lainnya juga 'Y'.
        """
        mock_repo = MagicMock()
        mock_repo.get_master_nodes.return_value = [
            DummyNode('n1', 'START', line_number=1),
            DummyNode('n2', 'STATEMENT', line_number=2), 
            DummyNode('n3', 'END', line_number=3)
        ]
        mock_repo.get_master_edges.return_value = [
            DummyEdge('e1', 'n1', 'n2'),
            DummyEdge('e2', 'n2', 'n3')
        ]
        
        sync = CfgCoverageSync(mock_repo)
        
        line_statuses = [
            {'line_number': 2, 'status': 'Y'},
            {'line_number': 3, 'status': 'Y'}
        ]
        
        sync.synchronize("topik1", "student1", "modul1", line_statuses)
        
        edges_args = mock_repo.bulk_insert_tr_edges.call_args[0][0]
        edge_status_map = {e['tr_id_edge']: e['tr_status'] for e in edges_args}
        
        assert edge_status_map['e1'] == 'Y' 
        assert edge_status_map['e2'] == 'Y' 

    def test_synchronize_block_node_partial_execution(self):
        """
        Test Case Name: Sinkronisasi CFG - Node Blok Baris Tereksekusi Sebagian
        Precondition: Sebuah node merangkum rentang baris (line_start hingga line_end). 
        Step to Execute: 
            1. Buat Node dengan line_start=2 dan line_end=4.
            2. Beri status eksekusi hanya pada line_number=3 (di dalam rentang).
            3. Panggil synchronize() dan amati status Node tersebut.
        Test Data: n2 memiliki range baris 2 s.d 4. line_statuses = [{'line_number': 3, 'status': 'Y'}].
        Expected Result: n2 otomatis mendapat status 'Y' karena line 3 tercakup di dalamnya.
        """
        mock_repo = MagicMock()
        mock_repo.get_master_nodes.return_value = [
            DummyNode('n1', 'START', line_number=1),
            DummyNode('n2', 'STATEMENT', line_start=2, line_end=4), 
            DummyNode('n3', 'END', line_number=5)
        ]
        mock_repo.get_master_edges.return_value = [
            DummyEdge('e1', 'n1', 'n2'),
            DummyEdge('e2', 'n2', 'n3')
        ]
        
        sync = CfgCoverageSync(mock_repo)
        
        line_statuses = [
            {'line_number': 3, 'status': 'Y'}
        ]
        
        sync.synchronize("topik1", "student1", "modul1", line_statuses)
        
        nodes_args = mock_repo.bulk_insert_tr_nodes.call_args[0][0]
        status_map = {n['tr_id_node']: n['tr_status'] for n in nodes_args}
        
        assert status_map['n2'] == 'Y' 

