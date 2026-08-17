import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import ExecutionTestCaseFailPage from '@/pages/ExecutionTestCaseFailPage';

// Mock react-router-dom navigate
const mockNavigate = vi.fn();
let mockLocationState: any = null;
let mockSearch = '?topikModulId=MOD-123';

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({
      state: mockLocationState,
      search: mockSearch,
      pathname: '/execution-fail',
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
vi.mock('@/components/custom/FailCard', () => ({
  default: ({ percentageCoverage, minimumCoverage, statusEksekusi, tanggalEksekusi, modulId }: any) => (
    <div data-testid="fail-card">
      <span data-testid="fail-card-coverage">{percentageCoverage}</span>
      <span data-testid="fail-card-min-coverage">{minimumCoverage}</span>
      <span data-testid="fail-card-status">{statusEksekusi ? 'PASS' : 'FAIL'}</span>
      <span data-testid="fail-card-date">{tanggalEksekusi}</span>
      <span data-testid="fail-card-modul-id">{modulId}</span>
    </div>
  ),
}));

describe('ExecutionTestCaseFailPage - Unit Test', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockLocationState = null;
    mockSearch = '?topikModulId=MOD-123';
  });

  afterEach(() => {
    localStorage.clear();
  });

  // TC-FE-ETCF-01: Statement Render Komponen Utama
  it('TC-FE-ETCF-01: renders all main page components, FailCard, and Laporan Pengujian button', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student', token: 'token-123' }));
    mockLocationState = {
      coverage_score: 50,
      minimum_coverage_score: 80,
      status_eksekusi: false,
      tgl_eksekusi: '2026-08-17',
      modul_id: 'MOD-123',
    };

    render(
      <MemoryRouter>
        <ExecutionTestCaseFailPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('layout')).toBeInTheDocument();
    expect(screen.getByTestId('menu')).toBeInTheDocument();
    expect(screen.getByTestId('module-spec-card')).toBeInTheDocument();
    expect(screen.getByTestId('code-and-cfg-panels')).toBeInTheDocument();
    expect(screen.getByTestId('add-test-case-card')).toBeInTheDocument();
    expect(screen.getByTestId('fail-card')).toBeInTheDocument();
    expect(screen.getByText('Laporan Pengujian')).toBeInTheDocument();
  });

  // TC-FE-ETCF-02: Validasi Status Login (session != null - False)
  it('TC-FE-ETCF-02: redirects to /login when user has no session in localStorage', () => {
    localStorage.removeItem('session');

    render(
      <MemoryRouter>
        <ExecutionTestCaseFailPage />
      </MemoryRouter>
    );

    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  // TC-FE-ETCF-03: Proteksi Peran Pengguna (login_type != "student" - True)
  it('TC-FE-ETCF-03: redirects to /dashboard-teacher when user is logged in as teacher', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'teacher', token: 'token-teach' }));

    render(
      <MemoryRouter>
        <ExecutionTestCaseFailPage />
      </MemoryRouter>
    );

    expect(mockNavigate).toHaveBeenCalledWith('/dashboard-teacher');
  });

  // TC-FE-ETCF-04: Proteksi Peran Pengguna (login_type != "student" - False)
  it('TC-FE-ETCF-04: allows access and does not redirect when user is a student', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student', token: 'token-stud' }));

    render(
      <MemoryRouter>
        <ExecutionTestCaseFailPage />
      </MemoryRouter>
    );

    expect(mockNavigate).not.toHaveBeenCalledWith('/login');
    expect(mockNavigate).not.toHaveBeenCalledWith('/dashboard-teacher');
  });

  // TC-FE-ETCF-05: Penyajian Metrik Pengujian pada FailCard
  it('TC-FE-ETCF-05: passes coverage metrics and failure status to FailCard correctly', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));
    mockLocationState = {
      coverage_score: 45,
      minimum_coverage_score: 75,
      status_eksekusi: false,
      tgl_eksekusi: '2026-08-17 10:00',
      modul_id: 'MOD-999',
    };

    render(
      <MemoryRouter>
        <ExecutionTestCaseFailPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('fail-card-coverage')).toHaveTextContent('45');
    expect(screen.getByTestId('fail-card-min-coverage')).toHaveTextContent('75');
    expect(screen.getByTestId('fail-card-status')).toHaveTextContent('FAIL');
    expect(screen.getByTestId('fail-card-date')).toHaveTextContent('2026-08-17 10:00');
    expect(screen.getByTestId('fail-card-modul-id')).toHaveTextContent('MOD-999');
  });

  // TC-FE-ETCF-06: Penanganan Akses Langsung (navigationData kosong)
  it('TC-FE-ETCF-06: applies default fallback values when navigationData is undefined', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));
    mockLocationState = undefined;

    render(
      <MemoryRouter>
        <ExecutionTestCaseFailPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('fail-card-coverage')).toHaveTextContent('0');
    expect(screen.getByTestId('fail-card-min-coverage')).toHaveTextContent('0');
    expect(screen.getByTestId('fail-card-status')).toHaveTextContent('FAIL');
    expect(screen.getByTestId('fail-card-date')).toHaveTextContent('');
    expect(screen.getByTestId('fail-card-modul-id')).toHaveTextContent('');
  });

  // TC-FE-ETCF-07: Aksi Tombol "Laporan Pengujian"
  it('TC-FE-ETCF-07: navigates to /test-result with state when Laporan Pengujian is clicked', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));
    mockLocationState = { modul_id: 'MOD-555' };

    render(
      <MemoryRouter>
        <ExecutionTestCaseFailPage />
      </MemoryRouter>
    );

    const reportButton = screen.getByText('Laporan Pengujian');
    fireEvent.click(reportButton);

    expect(mockNavigate).toHaveBeenCalledWith(
      expect.stringContaining('/test-result'),
      expect.objectContaining({ state: { modul_id: 'MOD-555' } })
    );
  });

  // TC-FE-ETCF-08: Aksi Tombol "Laporan Pengujian" (Tanpa Modul)
  it('TC-FE-ETCF-08: navigates safely when navigationData has undefined modul_id', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));
    mockLocationState = null;

    render(
      <MemoryRouter>
        <ExecutionTestCaseFailPage />
      </MemoryRouter>
    );

    const reportButton = screen.getByText('Laporan Pengujian');
    fireEvent.click(reportButton);

    expect(mockNavigate).toHaveBeenCalledWith(
      expect.stringContaining('/test-result'),
      expect.objectContaining({ state: { modul_id: undefined } })
    );
  });

  // TC-FE-ETCF-09: Render Kode & Graf Pendukung
  it('TC-FE-ETCF-09: renders CodeAndCfgPanels alongside FailCard', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));

    render(
      <MemoryRouter>
        <ExecutionTestCaseFailPage />
      </MemoryRouter>
    );

    expect(screen.getByTestId('code-and-cfg-panels')).toBeInTheDocument();
    expect(screen.getByTestId('code-program-card')).toBeInTheDocument();
    expect(screen.getByTestId('cfg-card')).toBeInTheDocument();
  });

  // TC-FE-ETCF-10: Perilaku Pengguliran Layar Otomatis
  it('TC-FE-ETCF-10: triggers scrollIntoView on bottom ref element when mounted', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));

    render(
      <MemoryRouter>
        <ExecutionTestCaseFailPage />
      </MemoryRouter>
    );

    expect(window.HTMLElement.prototype.scrollIntoView).toHaveBeenCalled();
  });
});
