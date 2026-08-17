import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import CreateTestCasePage from '@/pages/CreateTestCasePage';

// Mocking child components to simplify testing
vi.mock('@/pages/Layout', () => ({ default: ({ children }: any) => <div data-testid="layout">{children}</div> }));
vi.mock('@/components/custom/Menu', () => ({ Menu: () => <div data-testid="menu" /> }));
vi.mock('@/components/custom/ModuleSpecificationCard', () => ({ default: () => <div data-testid="module-spec-card" /> }));
vi.mock('@/components/custom/CodeProgramCard', () => ({ default: () => <div data-testid="code-program-card" /> }));
vi.mock('@/components/custom/CFGCard', () => ({ default: () => <div data-testid="cfg-card" /> }));
vi.mock('@/components/custom/AddTestCaseCard', () => ({ default: () => <div data-testid="add-test-case-card" /> }));
vi.mock('@/components/custom/MinimalCard', () => ({ default: () => <div data-testid="minimal-card" /> }));

describe('CreateTestCasePage', () => {
  beforeEach(() => {
    // Mock local storage session for student
    const mockSession = { login_type: 'student', token: 'fake-token' };
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation((key) => {
      if (key === 'session') return JSON.stringify(mockSession);
      return null;
    });
  });

  it('renders all main components correctly', () => {
    render(
      <BrowserRouter>
        <CreateTestCasePage />
      </BrowserRouter>
    );

    expect(screen.getByTestId('layout')).toBeInTheDocument();
    expect(screen.getByTestId('menu')).toBeInTheDocument();
    expect(screen.getByTestId('module-spec-card')).toBeInTheDocument();
    expect(screen.getAllByTestId('code-program-card').length).toBeGreaterThan(0);
    expect(screen.getAllByTestId('cfg-card').length).toBeGreaterThan(0);
    
    // As a student, these should be rendered
    expect(screen.getByTestId('add-test-case-card')).toBeInTheDocument();
    expect(screen.getByTestId('minimal-card')).toBeInTheDocument();
  });
});
