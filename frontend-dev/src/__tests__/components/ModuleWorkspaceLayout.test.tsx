import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import ModuleWorkspaceLayout from '@/components/custom/ModuleWorkspaceLayout';

// Mock child components
vi.mock('@/pages/Layout', () => ({
  default: ({ children }: any) => <div data-testid="mock-layout">{children}</div>,
}));
vi.mock('@/components/custom/Menu', () => ({
  Menu: () => <div data-testid="mock-menu">Menu Component</div>,
}));
vi.mock('@/components/custom/ModuleSpecificationCard', () => ({
  default: () => <div data-testid="mock-module-spec-card">Module Spec Card</div>,
}));
vi.mock('@/components/custom/CodeAndCfgPanels', () => ({
  CodeAndCfgPanels: ({ showCyclomaticComplexity, codeCoveragePercentage }: any) => (
    <div data-testid="mock-code-and-cfg-panels">
      <span data-testid="mock-panel-cc">{String(showCyclomaticComplexity)}</span>
      <span data-testid="mock-panel-coverage">{codeCoveragePercentage}</span>
    </div>
  ),
}));

describe('ModuleWorkspaceLayout - Unit Test', () => {
  // TC-FE-MWL-01: Render Struktur Layout Bersama
  it('TC-FE-MWL-01: renders Layout, Menu, ModuleSpecificationCard, CodeAndCfgPanels, and children slot', () => {
    render(
      <BrowserRouter>
        <ModuleWorkspaceLayout>
          <div data-testid="mock-child-content">Child Footer Slot Content</div>
        </ModuleWorkspaceLayout>
      </BrowserRouter>
    );

    expect(screen.getByTestId('mock-layout')).toBeInTheDocument();
    expect(screen.getByTestId('mock-menu')).toBeInTheDocument();
    expect(screen.getByTestId('mock-module-spec-card')).toBeInTheDocument();
    expect(screen.getByTestId('mock-code-and-cfg-panels')).toBeInTheDocument();
    expect(screen.getByTestId('mock-child-content')).toBeInTheDocument();
  });

  // TC-FE-MWL-02: Penerusan Konfigurasi Panel CFG
  it('TC-FE-MWL-02: passes showCyclomaticComplexity and codeCoveragePercentage props to CodeAndCfgPanels', () => {
    render(
      <BrowserRouter>
        <ModuleWorkspaceLayout
          showCyclomaticComplexity={false}
          codeCoveragePercentage={85}
        >
          <div>Footer Slot</div>
        </ModuleWorkspaceLayout>
      </BrowserRouter>
    );

    expect(screen.getByTestId('mock-panel-cc')).toHaveTextContent('false');
    expect(screen.getByTestId('mock-panel-coverage')).toHaveTextContent('85');
  });
});
