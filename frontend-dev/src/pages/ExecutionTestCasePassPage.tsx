import Layout from "./Layout";
import React, { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Menu } from "@/components/custom/Menu";
import ModuleSpecificationCard from "@/components/custom/ModuleSpecificationCard";
import CodeProgramCard from "@/components/custom/CodeProgramCard";
import AddTestCaseCard from "@/components/custom/AddTestCaseCard";
import CFGCard from "@/components/custom/CFGCard";
import {
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { ImperativePanelHandle, PanelResizeHandle } from "react-resizable-panels";
import PassCard from "@/components/custom/PassCard";

const ExecutionTestCasePassPage: React.FC = () => {
  const apiUrl = import.meta.env.VITE_API_URL;
  let apiKey = import.meta.env.VITE_API_KEY;
  // const modulId = import.meta.env.VITE_MODULE_ID;
  const sessionData = localStorage.getItem("session");
  let session = null;
  if (sessionData != null) {
    session = JSON.parse(sessionData);
    apiKey = session.token;
  }
  useEffect(() => {
    if (session != null) {
      if (session.login_type != "student") {
        navigate("/dashboard-teacher");
      }
    } else {
      navigate("/login");
    }
  }, []);

  const [showCyclomaticComplexity] = useState(true);
  const [showCodeCoverage] = useState(false);
  const [codeCoveragePercentage] = useState(0);
  const [highlightedLines, setHighlightedLines] = useState<{ start: number; end: number } | null>(null);

  const [isCodeCollapsed, setIsCodeCollapsed] = useState(false);
  const [isCfgCollapsed, setIsCfgCollapsed] = useState(false);
  const codePanelRef = useRef<ImperativePanelHandle>(null);
  const cfgPanelRef = useRef<ImperativePanelHandle>(null);

  const bottomRef = useRef<HTMLDivElement>(null);

  const location = useLocation();
  const { state: navigationData } = location;
  type NavigationDataModul = {
    modul_id: string;
  };

  // const [dataIdModul, SetDataIdModul] = useState<NavigationDataModul | null>(
  //   null
  // );
  const queryParameters = new URLSearchParams(window.location.search);
  const modulId = queryParameters.get("topikModulId");

  const navigate = useNavigate();

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
    navigate("/test-result?topikModulId=" + modulId, { state: dataToPass });
  };

  const handleNavigateNextChallenge = async () => {
    try {
      const response = await fetch(
        `${apiUrl}/topik/nextChallenge?idTopikModul=${modulId}`,
        {
          method: "GET",
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${apiKey}`,
          },
        },
      );

      if (!response.ok) {
        if (response.status === 403) {
          // throw new Error('Forbidden: Access is denied');
          navigate("/error");
        } else {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      }

      const data = await response.json();
      const nextTopikModulId = data?.data?.ms_id_topik_modul;
      const currentTopikId = data?.data_current?.ms_id_topik;

      if (nextTopikModulId) {
        navigate({
          pathname: "/topikModul",
          search: "?topikModulId=" + nextTopikModulId,
        });
      } else if (currentTopikId) {
        navigate({
          pathname: "/list-challanges",
          search: "?idTopik=" + currentTopikId,
        });
      } else {
        navigate("/list-topics");
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    // Mendapatkan nilai percentageCoverage, minimumCoverage, dan points dari URL query params
    // const searchParams = new URLSearchParams(location.search);
    // const percentage = Number(searchParams.get("percentageCoverage"));
    // const minimum = Number(searchParams.get("minimumCoverage"));
    // const pointsValue = Number(searchParams.get("points"));
    // Set nilai percentageCoverage, minimumCoverage, dan points
    // setPercentageCoverage(percentage);
    // setMinimumCoverage(minimum);
    // setPoints(pointsValue);
  }, []);

  return (
    <Layout>
      <Menu />
      <div className="flex flex-col w-screen min-h-screen p-4 gap-6">
        {/* Section 1: Spesifikasi Modul dan Daftar Parameter (Full Width) */}
        <div className="w-full">
          <ModuleSpecificationCard />
        </div>

        {/* Section 2: Kode Program (Kiri) dan Struktur Program (Kanan) */}
        <div className="w-full hidden md:flex relative" style={{ height: "700px" }}>
          <ResizablePanelGroup direction="horizontal" className="w-full h-full">
            <ResizablePanel 
              ref={codePanelRef}
              collapsible={true} 
              collapsedSize={0} 
              defaultSize={50} 
              minSize={15} 
              className="flex flex-col"
              onCollapse={() => setIsCodeCollapsed(true)}
              onExpand={() => setIsCodeCollapsed(false)}
            >
              <div className="w-full h-full pr-3 overflow-hidden">
                <CodeProgramCard highlightedLines={highlightedLines} onLineClick={setHighlightedLines} />
              </div>
            </ResizablePanel>
            
          <PanelResizeHandle 
            className="bg-transparent w-4 relative flex items-center justify-center cursor-col-resize group" 
            style={{ position: "relative", display: "flex", alignItems: "center", justifyContent: "center" }}
          >
              <div 
                className="bg-slate-300 group-hover:bg-[#0b6af0] group-active:bg-blue-700 transition-colors"
                style={{ position: "absolute", top: 0, bottom: 0, width: 2, zIndex: 0 }} 
              />
              <div 
                className="bg-slate-300 group-hover:bg-[#0b6af0] group-active:bg-blue-700 transition-all group-hover:scale-105"
                style={{ position: "absolute", zIndex: 10, display: "flex", height: 56, width: 24, alignItems: "center", justifyContent: "center", borderRadius: 12, border: "1px solid rgba(255,255,255,0.15)", boxShadow: "0 4px 10px -4px rgba(0,0,0,0.4)", flexDirection: "column", gap: 4 }} 
              >
                <div style={{ width: 2, height: 16, backgroundColor: "rgba(255,255,255,0.5)", borderRadius: 1 }} />
                <div style={{ width: 2, height: 16, backgroundColor: "rgba(255,255,255,0.5)", borderRadius: 1 }} />
              </div>
          </PanelResizeHandle>

            <ResizablePanel 
              ref={cfgPanelRef}
              collapsible={true} 
              collapsedSize={0} 
              defaultSize={50} 
              minSize={15} 
              className="flex flex-col"
              onCollapse={() => setIsCfgCollapsed(true)}
              onExpand={() => setIsCfgCollapsed(false)}
            >
              <div className="w-full h-full pl-3 overflow-hidden">
              <CFGCard
                showCyclomaticComplexity={showCyclomaticComplexity}
                showCodeCoverage={showCodeCoverage}
                codeCoveragePercentage={codeCoveragePercentage}
                onNodeClick={setHighlightedLines}
                highlightedLines={highlightedLines}
              />
              </div>
            </ResizablePanel>
          </ResizablePanelGroup>

          {isCodeCollapsed && (
            <button
              onClick={() => codePanelRef.current?.expand()}
              className="absolute left-0 top-1/2 -translate-y-1/2 bg-blue-50 hover:bg-blue-100 border border-blue-200 border-l-0 rounded-r-md px-1.5 py-4 shadow-sm transition-colors z-20 flex flex-col items-center justify-center cursor-pointer group"
              title="Tampilkan Kode Program"
            >
              <div style={{ writingMode: 'vertical-rl', transform: 'rotate(180deg)' }} className="text-xs font-semibold text-blue-700 tracking-wider group-hover:scale-105 transition-transform">
                Kode Program
              </div>
            </button>
          )}

          {isCfgCollapsed && (
            <button
              onClick={() => cfgPanelRef.current?.expand()}
              className="absolute right-0 top-1/2 -translate-y-1/2 bg-blue-50 hover:bg-blue-100 border border-blue-200 border-r-0 rounded-l-md px-1.5 py-4 shadow-sm transition-colors z-20 flex flex-col items-center justify-center cursor-pointer group"
              title="Tampilkan Struktur Program"
            >
              <div style={{ writingMode: 'vertical-rl', transform: 'rotate(180deg)' }} className="text-xs font-semibold text-blue-700 tracking-wider group-hover:scale-105 transition-transform">
                Struktur Program
              </div>
            </button>
          )}
        </div>

        {/* Mobile View */}
        <div className="flex flex-col md:hidden gap-6 w-full">
          <div className="w-full flex flex-col" style={{ height: "700px" }}>
            <CodeProgramCard highlightedLines={highlightedLines} onLineClick={setHighlightedLines} />
          </div>
          <div className="w-full flex flex-col" style={{ height: "700px" }}>
            <CFGCard
              showCyclomaticComplexity={showCyclomaticComplexity}
              showCodeCoverage={showCodeCoverage}
              codeCoveragePercentage={codeCoveragePercentage}
              onNodeClick={setHighlightedLines}
              highlightedLines={highlightedLines}
            />
          </div>
        </div>

        {/* Section 3: Test Case, Hasil Pengujian, dan Tombol (Full Width) */}
        <div className="w-full flex flex-col gap-6">
          <AddTestCaseCard />
          <div className="w-full">
            <PassCard
              percentageCoverage={navigationData?.coverage_score || 0}
              minimumCoverage={navigationData?.minimum_coverage_score || 0}
              statusEksekusi={navigationData?.status_eksekusi || false}
              tanggalEksekusi={navigationData?.tgl_eksekusi || ""}
              modulId={navigationData?.modul_id || ""}
              poin={navigationData?.points || 0}
            />
          </div>
          {/* Penanda untuk scroll ke bagian paling bawah */}
          <div ref={bottomRef}></div>
          <div className="flex space-x-2 items-center p-4 justify-center">
            <Button
              variant="outline"
              className="bg-white text-sm text-blue-800 border-2 border-blue-800 rounded-[10] hover:bg-blue-800 hover:text-white"
              onClick={handleNavigateToTestResult}
            >
              Hasil Pengujian
            </Button>
            <Button
              className="bg-blue-800 text-sm text-white border-2 border-blue-800 rounded-[20] pt-0 pb-0"
              onClick={handleNavigateNextChallenge}
            >
              Kasus Selanjutnya
            </Button>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ExecutionTestCasePassPage;
