import Layout from "./Layout";
import { useState, useEffect, useRef } from "react";
import { Menu } from "@/components/custom/Menu";
import ModuleCoverage from "@/components/custom/ModuleCoverage";
import CFGCard from "@/components/custom/CFGCard";
import {
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { ImperativePanelHandle, PanelResizeHandle } from "react-resizable-panels";
import TestResultCard from "@/components/custom/TestResultCard";
import { Button } from "@/components/ui/button";
//import PercentageCodeCoverage from "@/components/custom/PresentaseCodeCoverage";
import { useNavigate } from "react-router-dom";

interface DataResultTest {
  coverageScore: number;
  point: number;
  totalTestCase: number;
  totalPassTestCase: number;
  totalFailedTestCase: number;
  executionDate: string;
  linkReportTesting: string;
  linkReportCoverage: string;
  linkSourceCoverage: string;
  data_cfg: {
    nodes: any[];
    edges: any[];
    unexecutedPaths?: string[];
  };
}

const TestResultPage = () => {
  const navigate = useNavigate();
  const apiUrl = import.meta.env.VITE_API_URL;
  let apiKey = import.meta.env.VITE_API_KEY;
  // const modulId = import.meta.env.VITE_MODULE_ID;
  const sessionData = localStorage.getItem("session");
  let session = null;
  if (sessionData != null) {
    session = JSON.parse(sessionData);
    apiKey = session.token;
  }

  const queryParameters = new URLSearchParams(window.location.search);
  const modulId = queryParameters.get("topikModulId");
  const defaultData: DataResultTest = {
    coverageScore: 0,
    point: 0,
    totalTestCase: 0,
    totalPassTestCase: 0,
    totalFailedTestCase: 0,
    executionDate: "",
    linkReportTesting: "",
    linkReportCoverage: "",
    linkSourceCoverage: "",
    data_cfg: {
      nodes: [],
      edges: [],
      unexecutedPaths: [],
    },
  };
  const [showCyclomaticComplexity] = useState(false);
  const [showCodeCoverage] = useState(true);
  const [dataTestResult, setDataTestResult] =
    useState<DataResultTest>(defaultData);
  const [error, setError] = useState<string | null>(null);
  const [highlightedLines, setHighlightedLines] = useState<{ start: number; end: number } | null>(null);

  const [isCodeCollapsed, setIsCodeCollapsed] = useState(false);
  const [isCfgCollapsed, setIsCfgCollapsed] = useState(false);
  const codePanelRef = useRef<ImperativePanelHandle>(null);
  const cfgPanelRef = useRef<ImperativePanelHandle>(null);
  const fetchDataTestResult = async () => {
    try {
      const response = await fetch(`${apiUrl}/modul/getResultTest/${modulId}`, {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
      });

      if (!response.ok) {
        if (response.status === 403) {
          // throw new Error('Forbidden: Access is denied');
          navigate("/error");
        } else if (response.status !== 404) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      } else {
        const data = await response.json();
        setDataTestResult(data || null);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
      setError((error as Error).message);
    }
  };
  const handleCoverageTestReport = async () => {
    const url = apiUrl + "/" + dataTestResult?.linkReportCoverage;
    const win = window.open(url, "_blank");
    win?.focus();
  };
  const handleTestReport = async () => {
    const url = apiUrl + "/" + dataTestResult?.linkReportTesting;
    const win = window.open(url, "_blank");
    win?.focus();
  };

  useEffect(() => {
    if (session === null) {
      navigate("/login");
    } else if (session.login_type != "student") {
      navigate("/dashboard-teacher");
    } else {
      fetchDataTestResult();
    }
  }, []);

  if (error) {
    return (
      <div className="p-4 bg-white rounded-lg shadow-md h-screen">
        Error: {error}
      </div>
    );
  }

  return (
    <Layout>
      <Menu />
      <div className="flex flex-col w-screen min-h-[calc(100vh-100px)] p-4 bg-slate-50 relative">
        <ResizablePanelGroup direction="horizontal" className="min-h-full rounded-lg border border-slate-200">
          <ResizablePanel 
            ref={codePanelRef}
            collapsible={true}
            collapsedSize={0}
            defaultSize={50} 
            minSize={15} 
            className="flex flex-col bg-white"
            onCollapse={() => setIsCodeCollapsed(true)}
            onExpand={() => setIsCodeCollapsed(false)}
          >
            <div className="overflow-y-auto p-4 workspace-scrollbar w-full h-full">
              <ModuleCoverage dataResultTest={dataTestResult} />
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
            className="flex flex-col bg-white"
            onCollapse={() => setIsCfgCollapsed(true)}
            onExpand={() => setIsCfgCollapsed(false)}
          >
            <div className="overflow-y-auto p-4 workspace-scrollbar w-full h-full flex flex-col gap-6">
              <CFGCard
                showCyclomaticComplexity={showCyclomaticComplexity}
                showCodeCoverage={showCodeCoverage}
                codeCoveragePercentage={dataTestResult.coverageScore}
                nodesWithStatus={dataTestResult.data_cfg?.nodes}
                edgesWithStatus={dataTestResult.data_cfg?.edges}
                unexecutedPaths={dataTestResult.data_cfg?.unexecutedPaths}
                onNodeClick={setHighlightedLines}
                highlightedLines={highlightedLines}
                jacocoUrl={
                  dataTestResult.linkSourceCoverage
                    ? `${apiUrl}/${dataTestResult.linkSourceCoverage}`
                    : null
                }
              />
              <TestResultCard dataResultTest={dataTestResult} />
              <div className="flex justify-end space-x-2 items-center p-4">
                {dataTestResult.totalFailedTestCase == 0 &&
                  dataTestResult.executionDate !== "" && (
                    <Button
                      variant="outline"
                      className="bg-white text-sm text-blue-800 border-2 border-blue-800 rounded-[10px] hover:bg-blue-800 hover:text-white"
                      onClick={handleCoverageTestReport}
                    >
                      Coverage Test
                    </Button>
                  )}
                {dataTestResult.executionDate !== "" && (
                  <Button
                    className="bg-blue-800 text-sm text-white border-2 border-blue-800 rounded-[10px] pt-0 pb-0"
                    onClick={handleTestReport}
                  >
                    Test Report
                  </Button>
                )}
              </div>
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>

        {isCodeCollapsed && (
          <button
            onClick={() => codePanelRef.current?.expand()}
            className="absolute left-4 top-1/2 -translate-y-1/2 bg-blue-50 hover:bg-blue-100 border border-blue-200 border-l-0 rounded-r-md px-1.5 py-4 shadow-sm transition-colors z-20 flex flex-col items-center justify-center cursor-pointer group"
            title="Tampilkan Code Coverage"
          >
            <div style={{ writingMode: 'vertical-rl', transform: 'rotate(180deg)' }} className="text-xs font-semibold text-blue-700 tracking-wider group-hover:scale-105 transition-transform">
              Code Coverage
            </div>
          </button>
        )}

        {isCfgCollapsed && (
          <button
            onClick={() => cfgPanelRef.current?.expand()}
            className="absolute right-4 top-1/2 -translate-y-1/2 bg-blue-50 hover:bg-blue-100 border border-blue-200 border-r-0 rounded-l-md px-1.5 py-4 shadow-sm transition-colors z-20 flex flex-col items-center justify-center cursor-pointer group"
            title="Tampilkan Struktur Program & Hasil"
          >
            <div style={{ writingMode: 'vertical-rl', transform: 'rotate(180deg)' }} className="text-xs font-semibold text-blue-700 tracking-wider group-hover:scale-105 transition-transform">
              Struktur & Hasil
            </div>
          </button>
        )}
      </div>
    </Layout>
  );
};

export default TestResultPage;