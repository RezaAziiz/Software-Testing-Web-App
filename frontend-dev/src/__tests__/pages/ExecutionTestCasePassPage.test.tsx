import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import ExecutionTestCasePassPage from '@/pages/ExecutionTestCasePassPage';

// Mock react-router-dom navigate
const mockNavigate = vi.fn();
let mockLocationState: any = null;
let mockSearch = '?topikModulId=MOD-100';

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({
      state: mockLocationState,
      search: mockSearch,
      pathname: '/execution-pass',
    }),
  };
});

// Mock child components
vi.mock('@/pages/Layout', () => ({
  default: ({ children }: any) => <div data-testid="layout">{children}</div>,
}));
vi.mock('@/components/custom/Menu', () => ({
  Menu: () => <div data-testid="menu">Menu Component</div>,
}));
vi.mock('@/components/custom/ModuleSpecificationCard', () => ({
  default: () => <div data-testid="module-spec-card">Module Specification</div>,
}));
vi.mock('@/components/custom/AddTestCaseCard', () => ({
  default: () => <div data-testid="add-test-case-card">Add Test Case</div>,
}));
vi.mock('@/components/custom/CodeAndCfgPanels', () => ({
  CodeAndCfgPanels: () => (
    <div data-testid="code-and-cfg-panels">
      <div data-testid="code-program-card">Java Code Panel</div>
      <div data-testid="cfg-card">CFG Panel</div>
    </div>
  ),
}));
vi.mock('@/components/custom/PassCard', () => ({
  default: ({ percentageCoverage, minimumCoverage, statusEksekusi, tanggalEksekusi, modulId, poin }: any) => (
    <div data-testid="pass-card">
      <span data-testid="pass-card-coverage">{percentageCoverage}</span>
      <span data-testid="pass-card-min-coverage">{minimumCoverage}</span>
      <span data-testid="pass-card-status">{statusEksekusi ? 'PASS' : 'FAIL'}</span>
      <span data-testid="pass-card-date">{tanggalEksekusi}</span>
      <span data-testid="pass-card-modul-id">{modulId}</span>
      <span data-testid="pass-card-poin">{poin}</span>
    </div>
  ),
}));

describe('ExecutionTestCasePassPage - Unit Test', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockLocationState = null;
    mockSearch = '?topikModulId=MOD-100';
    // Reset global fetch mock
    global.fetch = vi.fn();
  });

  afterEach(() => {
    localStorage.clear();
  });

  // TC-FE-ETCP-01: Statement Render Komponen Utama
  it('TC-FE-ETCP-01: renders all main page components, PassCard, and navigation buttons', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student', token: 'token-pass' }));
    mockLocationState = {
      coverage_score: 100,
      minimum_coverage_score: 80,
      status_eksekusi: true,
      tgl_eksekusi: '2026-08-17',
      modul_id: 'MOD-100',
      points: 50,
    };

    render(
      <MemoryRouter>
        <ExecutionTestCasePassPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('layout')).toBeInTheDocument();
    expect(screen.getByTestId('menu')).toBeInTheDocument();
    expect(screen.getByTestId('module-spec-card')).toBeInTheDocument();
    expect(screen.getByTestId('code-and-cfg-panels')).toBeInTheDocument();
    expect(screen.getByTestId('add-test-case-card')).toBeInTheDocument();
    expect(screen.getByTestId('pass-card')).toBeInTheDocument();
    expect(screen.getByText('Hasil Pengujian')).toBeInTheDocument();
    expect(screen.getByText('Kasus Selanjutnya')).toBeInTheDocument();
  });

  // TC-FE-ETCP-02: Validasi Status Login (session != null - False)
  it('TC-FE-ETCP-02: redirects to /login when user has no session', () => {
    localStorage.removeItem('session');

    render(
      <MemoryRouter>
        <ExecutionTestCasePassPage />
      </MemoryRouter>
    );

    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  // TC-FE-ETCP-03: Proteksi Peran Pengguna (login_type != "student" - True)
  it('TC-FE-ETCP-03: redirects to /dashboard-teacher when user is a teacher', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'teacher' }));

    render(
      <MemoryRouter>
        <ExecutionTestCasePassPage />
      </MemoryRouter>
    );

    expect(mockNavigate).toHaveBeenCalledWith('/dashboard-teacher');
  });

  // TC-FE-ETCP-04: Proteksi Peran Pengguna (login_type != "student" - False)
  it('TC-FE-ETCP-04: allows access when user is a student', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));

    render(
      <MemoryRouter>
        <ExecutionTestCasePassPage />
      </MemoryRouter>
    );

    expect(mockNavigate).not.toHaveBeenCalledWith('/login');
    expect(mockNavigate).not.toHaveBeenCalledWith('/dashboard-teacher');
  });

  // TC-FE-ETCP-05: Penyajian Metrik Kelulusan pada PassCard
  it('TC-FE-ETCP-05: passes passed execution metrics and points to PassCard correctly', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));
    mockLocationState = {
      coverage_score: 95,
      minimum_coverage_score: 70,
      status_eksekusi: true,
      tgl_eksekusi: '2026-08-17 11:00',
      modul_id: 'MOD-888',
      points: 100,
    };

    render(
      <MemoryRouter>
        <ExecutionTestCasePassPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('pass-card-coverage')).toHaveTextContent('95');
    expect(screen.getByTestId('pass-card-min-coverage')).toHaveTextContent('70');
    expect(screen.getByTestId('pass-card-status')).toHaveTextContent('PASS');
    expect(screen.getByTestId('pass-card-date')).toHaveTextContent('2026-08-17 11:00');
    expect(screen.getByTestId('pass-card-modul-id')).toHaveTextContent('MOD-888');
    expect(screen.getByTestId('pass-card-poin')).toHaveTextContent('100');
  });

  // TC-FE-ETCP-06: Penanganan Akses Langsung (navigationData kosong)
  it('TC-FE-ETCP-06: handles undefined navigationData with default fallbacks safely', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));
    mockLocationState = undefined;

    render(
      <MemoryRouter>
        <ExecutionTestCasePassPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('pass-card-coverage')).toHaveTextContent('0');
    expect(screen.getByTestId('pass-card-min-coverage')).toHaveTextContent('0');
    expect(screen.getByTestId('pass-card-status')).toHaveTextContent('FAIL');
    expect(screen.getByTestId('pass-card-date')).toHaveTextContent('');
    expect(screen.getByTestId('pass-card-modul-id')).toHaveTextContent('');
    expect(screen.getByTestId('pass-card-poin')).toHaveTextContent('0');
  });

  // TC-FE-ETCP-07: Aksi Tombol "Hasil Pengujian"
  it('TC-FE-ETCP-07: navigates to /test-result with state when Hasil Pengujian button is clicked', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));
    mockLocationState = { modul_id: 'MOD-100' };

    render(
      <MemoryRouter>
        <ExecutionTestCasePassPage />
      </MemoryRouter>
    );

    const resultBtn = screen.getByText('Hasil Pengujian');
    fireEvent.click(resultBtn);

    expect(mockNavigate).toHaveBeenCalledWith(
      expect.stringContaining('/test-result'),
      expect.objectContaining({ state: { modul_id: 'MOD-100' } })
    );
  });

  // TC-FE-ETCP-08: Navigasi Tantangan: Respon Akses Ditolak (403 Forbidden)
  it('TC-FE-ETCP-08: navigates to /error when nextChallenge API responds with 403 Forbidden', async () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student', token: 'fake-token' }));
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 403,
    });

    render(
      <MemoryRouter>
        <ExecutionTestCasePassPage />
      </MemoryRouter>
    );

    const nextBtn = screen.getByText('Kasus Selanjutnya');
    fireEvent.click(nextBtn);

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/error');
    });
  });

  // TC-FE-ETCP-09: Navigasi Tantangan: Gangguan Server API (500 Server Error)
  it('TC-FE-ETCP-09: handles 500 Server Error from nextChallenge gracefully in catch block', async () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student', token: 'fake-token' }));
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    render(
      <MemoryRouter>
        <ExecutionTestCasePassPage />
      </MemoryRouter>
    );

    const nextBtn = screen.getByText('Kasus Selanjutnya');
    fireEvent.click(nextBtn);

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled();
    });
    consoleSpy.mockRestore();
  });

  // TC-FE-ETCP-10: Navigasi Tantangan: Gangguan Jaringan (Network Error)
  it('TC-FE-ETCP-10: handles network connection failure during nextChallenge fetch gracefully', async () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student', token: 'fake-token' }));
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    (global.fetch as any).mockRejectedValueOnce(new Error('Network disconnected'));

    render(
      <MemoryRouter>
        <ExecutionTestCasePassPage />
      </MemoryRouter>
    );

    const nextBtn = screen.getByText('Kasus Selanjutnya');
    fireEvent.click(nextBtn);

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Error fetching data:', expect.any(Error));
    });
    consoleSpy.mockRestore();
  });

  // TC-FE-ETCP-11: Navigasi Tantangan: Modul Selanjutnya Tersedia
  it('TC-FE-ETCP-11: navigates to /topikModul when nextTopikModulId is returned', async () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student', token: 'fake-token' }));
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        data: { ms_id_topik_modul: 'MOD-02' },
      }),
    });

    render(
      <MemoryRouter>
        <ExecutionTestCasePassPage />
      </MemoryRouter>
    );

    const nextBtn = screen.getByText('Kasus Selanjutnya');
    fireEvent.click(nextBtn);

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith({
        pathname: '/topikModul',
        search: '?topikModulId=MOD-02',
      });
    });
  });

  // TC-FE-ETCP-12: Navigasi Tantangan: Modul Selesai, Topik Tersedia
  it('TC-FE-ETCP-12: navigates to /list-challanges when only currentTopikId is returned', async () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student', token: 'fake-token' }));
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        data: null,
        data_current: { ms_id_topik: 'TOP-01' },
      }),
    });

    render(
      <MemoryRouter>
        <ExecutionTestCasePassPage />
      </MemoryRouter>
    );

    const nextBtn = screen.getByText('Kasus Selanjutnya');
    fireEvent.click(nextBtn);

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith({
        pathname: '/list-challanges',
        search: '?idTopik=TOP-01',
      });
    });
  });

  // TC-FE-ETCP-13: Navigasi Tantangan: Seluruh Topik Selesai
  it('TC-FE-ETCP-13: navigates to /list-topics when neither module nor topic id is returned', async () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student', token: 'fake-token' }));
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        data: null,
        data_current: null,
      }),
    });

    render(
      <MemoryRouter>
        <ExecutionTestCasePassPage />
      </MemoryRouter>
    );

    const nextBtn = screen.getByText('Kasus Selanjutnya');
    fireEvent.click(nextBtn);

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/list-topics');
    });
  });

  // TC-FE-ETCP-14: Render Kode & Graf Pendukung
  it('TC-FE-ETCP-14: renders CodeAndCfgPanels alongside PassCard', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));

    render(
      <MemoryRouter>
        <ExecutionTestCasePassPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('code-and-cfg-panels')).toBeInTheDocument();
    expect(screen.getByTestId('code-program-card')).toBeInTheDocument();
    expect(screen.getByTestId('cfg-card')).toBeInTheDocument();
  });

  // TC-FE-ETCP-15: Perilaku Pengguliran Layar Otomatis
  it('TC-FE-ETCP-15: triggers scrollIntoView on bottom ref element when mounted', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));

    render(
      <MemoryRouter>
        <ExecutionTestCasePassPage />
      </MemoryRouter>
    );

    expect(window.HTMLElement.prototype.scrollIntoView).toHaveBeenCalled();
  });
});
