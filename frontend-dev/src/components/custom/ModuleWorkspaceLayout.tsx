import React, { useState } from "react";
import Layout from "@/pages/Layout";
import { Menu } from "@/components/custom/Menu";
import ModuleSpecificationCard from "@/components/custom/ModuleSpecificationCard";
import { CodeAndCfgPanels } from "@/components/custom/CodeAndCfgPanels";

interface ModuleWorkspaceLayoutProps {
  children?: React.ReactNode;
  showCyclomaticComplexity?: boolean;
  showCodeCoverage?: boolean;
  codeCoveragePercentage?: number;
}

export const ModuleWorkspaceLayout: React.FC<ModuleWorkspaceLayoutProps> = ({
  children,
  showCyclomaticComplexity = true,
  showCodeCoverage = false,
  codeCoveragePercentage = 0,
}) => {
  const [highlightedLines, setHighlightedLines] = useState<{ start: number; end: number } | null>(null);

  return (
    <Layout>
      <Menu />
      <div className="flex flex-col w-screen min-h-screen p-4 gap-6">
        {/* Section 1: Spesifikasi Modul dan Daftar Parameter (Full Width) */}
        <div className="w-full">
          <ModuleSpecificationCard />
        </div>

        {/* Section 2: Kode Program (Kiri) dan Struktur Program (Kanan) */}
        <CodeAndCfgPanels
          showCyclomaticComplexity={showCyclomaticComplexity}
          showCodeCoverage={showCodeCoverage}
          codeCoveragePercentage={codeCoveragePercentage}
          highlightedLines={highlightedLines}
          setHighlightedLines={setHighlightedLines}
        />

        {/* Section 3: Test Case, Hasil Pengujian, dan Aksi (Full Width) */}
        {children}
      </div>
    </Layout>
  );
};

export default ModuleWorkspaceLayout;
