import Layout from "./Layout";
import { useState, useEffect, useRef } from "react";
import { ImperativePanelHandle, PanelResizeHandle } from "react-resizable-panels";
import { Menu } from "@/components/custom/Menu";
import ModuleSpecificationCard from "@/components/custom/ModuleSpecificationCard";
import CodeProgramCard from "@/components/custom/CodeProgramCard";
import AddTestCaseCard from "@/components/custom/AddTestCaseCard";
import CFGCard from "@/components/custom/CFGCard";
import {
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import MinimalCard from "@/components/custom/MinimalCard";
import { useNavigate } from "react-router-dom";

const CreateTestCasePage: React.FC = () => {
  const navigate = useNavigate();
  const [showCyclomaticComplexity] = useState(true);
  const [showCodeCoverage] = useState(false);
  const codeCoveragePercentage = 0;
  const [highlightedLines, setHighlightedLines] = useState<{ start: number; end: number } | null>(null);
  const [isCodeCollapsed, setIsCodeCollapsed] = useState(false);
  const [isCfgCollapsed, setIsCfgCollapsed] = useState(false);
  const codePanelRef = useRef<ImperativePanelHandle>(null);
  const cfgPanelRef = useRef<ImperativePanelHandle>(null);
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
        <div className="w-full hidden md:flex relative" style={{ height: "600px" }}>
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
                <CodeProgramCard highlightedLines={highlightedLines} />
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
          <div className="w-full flex flex-col" style={{ height: "600px" }}>
            <CodeProgramCard highlightedLines={highlightedLines} />
          </div>
          <div className="w-full flex flex-col" style={{ height: "600px" }}>
            <CFGCard
              showCyclomaticComplexity={showCyclomaticComplexity}
              showCodeCoverage={showCodeCoverage}
              codeCoveragePercentage={codeCoveragePercentage}
              onNodeClick={setHighlightedLines}
              highlightedLines={highlightedLines}
            />
          </div>
        </div>

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
