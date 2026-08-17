import Layout from "./Layout";
import React, { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom"; // Import hooks
import { Menu } from "@/components/custom/Menu";
import { Button } from "@/components/ui/button";
import ModuleSpecificationCard from "@/components/custom/ModuleSpecificationCard";
import AddTestCaseCard from "@/components/custom/AddTestCaseCard";
import { CodeAndCfgPanels } from "@/components/custom/CodeAndCfgPanels";
import FailCard from "@/components/custom/FailCard";

const ExecutionTestCaseFailPage: React.FC = () => {
  const apiUrl = import.meta.env.VITE_API_URL;
  let apiKey = import.meta.env.VITE_API_KEY;
  // const modulId = import.meta.env.VITE_MODULE_ID;
  const sessionData = localStorage.getItem("session");
  let session = null;
  if (sessionData != null) {
    session = JSON.parse(sessionData);
    apiKey = session.token;
  }

  const navigate = useNavigate(); // Gunakan useNavigate hook

  useEffect(() => {
    if (session != null) {
      if (session.login_type != "student") {
        navigate("/dashboard-teacher");
      }
    } else {
      navigate("/login");
    }
    // Scroll ke bagian paling bawah saat komponen dimount
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  const [showCyclomaticComplexity] = useState(true);
  const [showCodeCoverage] = useState(false);
  const [codeCoveragePercentage] = useState(0);
  const [highlightedLines, setHighlightedLines] = useState<{ start: number; end: number } | null>(null);

  const bottomRef = useRef<HTMLDivElement>(null);
  const location = useLocation();
  const { state: navigationData } = location;
  const queryParameters = new URLSearchParams(window.location.search)
  const modulId = queryParameters.get("topikModulId")

  type NavigationDataModul = {
    modul_id: string;
  };


  useEffect(() => {
    // Scroll ke bagian paling bawah saat komponen dimount
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  // Fungsi untuk menavigasi ke halaman /test-result dengan ID modul sebagai parameter
  const handleNavigateToTestResult = () => {
    const dataToPass: NavigationDataModul = {
      modul_id: navigationData?.modul_id,
      };

      navigate("/test-result?topikModulId="+modulId, { state: dataToPass });

  };

  return (
    <>
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

          {/* Section 3: Test Case, Hasil Pengujian, dan Tombol (Full Width) */}
          <div className="w-full flex flex-col gap-6 pb-6">
            <AddTestCaseCard />
            <div className="w-full">
              <FailCard
                percentageCoverage={navigationData?.coverage_score || 0}
                minimumCoverage={navigationData?.minimum_coverage_score || 0}
                statusEksekusi={navigationData?.status_eksekusi || false}
                tanggalEksekusi={navigationData?.tgl_eksekusi || ""}
                modulId={navigationData?.modul_id || ""}
              />
            </div>
            <Button
              className="text-sm bg-white rounded-lg font-bold text-red-700 border border-red-700 hover:bg-red-700 hover:text-white button-custom"
              onClick={handleNavigateToTestResult}
            >
              Laporan Pengujian
            </Button>
            <div ref={bottomRef}></div>
          </div>
        </div>
      </Layout>
    </>
  );
};

export default ExecutionTestCaseFailPage;
