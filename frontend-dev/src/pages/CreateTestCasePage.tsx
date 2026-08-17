import Layout from "./Layout";
import { useState, useEffect } from "react";
import { Menu } from "@/components/custom/Menu";
import ModuleSpecificationCard from "@/components/custom/ModuleSpecificationCard";
import AddTestCaseCard from "@/components/custom/AddTestCaseCard";
import MinimalCard from "@/components/custom/MinimalCard";
import { useNavigate } from "react-router-dom";
import { CodeAndCfgPanels } from "@/components/custom/CodeAndCfgPanels";

const CreateTestCasePage: React.FC = () => {
  const navigate = useNavigate();
  const [showCyclomaticComplexity] = useState(true);
  const [showCodeCoverage] = useState(false);
  const codeCoveragePercentage = 0;
  const [highlightedLines, setHighlightedLines] = useState<{ start: number; end: number } | null>(null);
  const sessionData = localStorage.getItem('session')
  let session = null
  if (sessionData != null){
      session = JSON.parse(sessionData);
  }
  useEffect(() => {
    if (session == null){
      navigate("/login")
    }
  }, [sessionData]);

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

        {/* Section 3: Test Case dan Hasil Pengujian (Full Width) */}
        {session?.login_type === "student" && (
          <div className="w-full flex flex-col gap-6 pb-6">
            <AddTestCaseCard />
            <MinimalCard />
          </div>
        )}
      </div>
    </Layout>
  );
};

export default CreateTestCasePage;
