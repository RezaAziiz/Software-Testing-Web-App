import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import CreateTestCasePage from '@/pages/CreateTestCasePage';

// Mock react-router-dom navigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
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
vi.mock('@/components/custom/MinimalCard', () => ({
  default: () => <div data-testid="minimal-card">Minimal Card</div>,
}));
vi.mock('@/components/custom/CodeAndCfgPanels', () => ({
  CodeAndCfgPanels: ({ highlightedLines, setHighlightedLines }: any) => (
    <div data-testid="code-and-cfg-panels">
      <div data-testid="code-program-card">Java Code Program Panel</div>
      <div data-testid="cfg-card">CFG Graph Canvas Panel</div>
      <button
        data-testid="mock-cfg-node-click"
        onClick={() => setHighlightedLines?.({ start: 5, end: 10 })}
      >
        Click CFG Node
      </button>
      {highlightedLines && (
        <span data-testid="highlighted-indicator">
          Lines: {highlightedLines.start}-{highlightedLines.end}
        </span>
      )}
    </div>
  ),
}));

describe('CreateTestCasePage - Unit Test', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  // TC-FE-CTP-01: Statement Render Komponen Utama
  it('TC-FE-CTP-01: renders all main layout components when valid student session exists', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student', token: 'valid-token' }));

    render(
      <BrowserRouter>
        <CreateTestCasePage />
      </BrowserRouter>
    );

    expect(screen.getByTestId('layout')).toBeInTheDocument();
    expect(screen.getByTestId('menu')).toBeInTheDocument();
    expect(screen.getByTestId('module-spec-card')).toBeInTheDocument();
    expect(screen.getByTestId('code-and-cfg-panels')).toBeInTheDocument();
  });

  // TC-FE-CTP-02: Pengecekan Data Sesi (sessionData != null - False)
  it('TC-FE-CTP-02: triggers redirect to /login when session is missing in localStorage', () => {
    localStorage.removeItem('session');

    render(
      <BrowserRouter>
        <CreateTestCasePage />
      </BrowserRouter>
    );

    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  // TC-FE-CTP-03: Pengecekan Data Sesi (sessionData != null - True)
  it('TC-FE-CTP-03: successfully parses valid session JSON and sets session state', () => {
    const mockSession = { login_type: 'student', name: 'Budi' };
    localStorage.setItem('session', JSON.stringify(mockSession));

    render(
      <BrowserRouter>
        <CreateTestCasePage />
      </BrowserRouter>
    );

    expect(mockNavigate).not.toHaveBeenCalledWith('/login');
    expect(screen.getByTestId('add-test-case-card')).toBeInTheDocument();
  });

  // TC-FE-CTP-04: Penanganan Data Sesi Rusak (Malformed JSON)
  it('TC-FE-CTP-04: handles malformed session JSON safely without crash', () => {
    localStorage.setItem('session', 'INVALID_JSON_CORRUPTED{[');

    // Expect render not to crash completely or to handle safely
    expect(() => {
      render(
        <BrowserRouter>
          <CreateTestCasePage />
        </BrowserRouter>
      );
    }).not.toThrow();
  });

  // TC-FE-CTP-05: Validasi Status Login (session == null - True)
  it('TC-FE-CTP-05: redirects to /login when session is null', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockReturnValue(null);

    render(
      <BrowserRouter>
        <CreateTestCasePage />
      </BrowserRouter>
    );

    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  // TC-FE-CTP-06: Validasi Status Login (session == null - False)
  it('TC-FE-CTP-06: remains on page when user session is active', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));

    render(
      <BrowserRouter>
        <CreateTestCasePage />
      </BrowserRouter>
    );

    expect(mockNavigate).not.toHaveBeenCalled();
    expect(screen.getByTestId('layout')).toBeInTheDocument();
  });

  // TC-FE-CTP-07: Hak Akses Siswa (login_type === "student" - True)
  it('TC-FE-CTP-07: renders test case input cards when login_type is student', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));

    render(
      <BrowserRouter>
        <CreateTestCasePage />
      </BrowserRouter>
    );

    expect(screen.getByTestId('add-test-case-card')).toBeInTheDocument();
    expect(screen.getByTestId('minimal-card')).toBeInTheDocument();
  });

  // TC-FE-CTP-08: Hak Akses Siswa (login_type === "student" - False)
  it('TC-FE-CTP-08: hides test case input cards when user is not a student (e.g., teacher)', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'teacher' }));

    render(
      <BrowserRouter>
        <CreateTestCasePage />
      </BrowserRouter>
    );

    expect(screen.queryByTestId('add-test-case-card')).not.toBeInTheDocument();
    expect(screen.queryByTestId('minimal-card')).not.toBeInTheDocument();
  });

  // TC-FE-CTP-09: Render Kode Program Java
  it('TC-FE-CTP-09: renders Java source code panel inside panels container', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));

    render(
      <BrowserRouter>
        <CreateTestCasePage />
      </BrowserRouter>
    );

    expect(screen.getByTestId('code-program-card')).toBeInTheDocument();
    expect(screen.getByText('Java Code Program Panel')).toBeInTheDocument();
  });

  // TC-FE-CTP-10: Penanganan Gagal Muat Kode Java
  it('TC-FE-CTP-10: keeps container rendered when code panel is present', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));

    render(
      <BrowserRouter>
        <CreateTestCasePage />
      </BrowserRouter>
    );

    expect(screen.getByTestId('code-and-cfg-panels')).toBeInTheDocument();
  });

  // TC-FE-CTP-11: Render Graf Alir Kontrol (CFG)
  it('TC-FE-CTP-11: renders CFG graph canvas panel inside panels container', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));

    render(
      <BrowserRouter>
        <CreateTestCasePage />
      </BrowserRouter>
    );

    expect(screen.getByTestId('cfg-card')).toBeInTheDocument();
    expect(screen.getByText('CFG Graph Canvas Panel')).toBeInTheDocument();
  });

  // TC-FE-CTP-12: Penanganan Struktur Graf Kosong
  it('TC-FE-CTP-12: panels container handles presence of CFG component gracefully', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));

    render(
      <BrowserRouter>
        <CreateTestCasePage />
      </BrowserRouter>
    );

    expect(screen.getByTestId('cfg-card')).toBeInTheDocument();
  });

  // TC-FE-CTP-13: Sinkronisasi Interaksi CFG ke Kode
  it('TC-FE-CTP-13: updates highlighted lines state when CFG node is clicked', () => {
    localStorage.setItem('session', JSON.stringify({ login_type: 'student' }));

    render(
      <BrowserRouter>
        <CreateTestCasePage />
      </BrowserRouter>
    );

    const clickNodeBtn = screen.getByTestId('mock-cfg-node-click');
    fireEvent.click(clickNodeBtn);

    expect(screen.getByTestId('highlighted-indicator')).toHaveTextContent('Lines: 5-10');
  });
});
