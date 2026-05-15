import Layout from "./Layout";
import React, { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom"; // Import hooks
import { Menu } from "@/components/custom/Menu";
import ModuleSpecificationCard from "@/components/custom/ModuleSpecificationCard";
import CodeProgramCard from "@/components/custom/CodeProgramCard";
import AddTestCaseCard from "@/components/custom/AddTestCaseCard";
import CFGCard from "@/components/custom/CFGCard";
import { Button } from "@/components/ui/button";
// import {
//   ResizableHandle,
//   ResizablePanel,
//   ResizablePanelGroup,
// } from "@/components/ui/resizable";
// import { ScrollArea } from "@/components/ui/scroll-area";
import FailCard from "@/components/custom/FailCard";

const ExecutionTestCaseFailPage: React.FC = () => {
  const [showCyclomaticComplexity] =useState(true);
  const [showCodeCoverage] = useState(false);
  const [codeCoveragePercentage] = useState(0);

  const bottomRef = useRef<HTMLDivElement>(null);
  const location = useLocation();
  const { state: navigationData } = location;
  // const { idModul } = useParams<{ idModul: string }>(); // Dapatkan ID modul dari URL
  const queryParameters = new URLSearchParams(window.location.search)
  const modulId = queryParameters.get("topikModulId")

  type NavigationDataModul = {
    modul_id: string;
  };

  // const [dataIdModul, SetDataIdModul] = useState<NavigationDataModul | null>(
  //   null
  // );

  const navigate = useNavigate(); // Gunakan useNavigate hook

  // const [failCardData, setFailCardData] = useState<{
  //   percentageCoverage: number;
  //   minimumCoverage: number;
  //   statusEksekusi: boolean;
  //   tanggalEksekusi: string;
  //   poin: number;
  //   modulId: string;
  // }>({
  //   percentageCoverage: 0,
  //   minimumCoverage: 0,
  //   statusEksekusi: false,
  //   tanggalEksekusi: "",
  //   poin: 0,
  //   modulId: ""
  // });

  useEffect(() => {
    // Scroll ke bagian paling bawah saat komponen dimount
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  // Fungsi untuk menavigasi ke halaman /test-result dengan ID modul sebagai parameter
  const handleNavigateToTestResult = () => {
    const dataToPass: NavigationDataModul = {
      modul_id: navigationData?.modul_id,
      };

      // SetDataIdModul(dataToPass);
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
          <div className="flex flex-col md:flex-row gap-6 w-full">
            <div className="w-full md:w-1/2 flex flex-col" style={{ maxHeight: "600px" }}>
              <CodeProgramCard />
            </div>
            <div className="w-full md:w-1/2 flex flex-col" style={{ maxHeight: "600px" }}>
              <CFGCard
                showCyclomaticComplexity={showCyclomaticComplexity}
                showCodeCoverage={showCodeCoverage}
                codeCoveragePercentage={codeCoveragePercentage}
              />
            </div>
          </div>

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
