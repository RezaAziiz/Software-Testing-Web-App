import React, { useRef, useState } from "react";
import { ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable";
import { ImperativePanelHandle, PanelResizeHandle } from "react-resizable-panels";
import CodeProgramCard from "@/components/custom/CodeProgramCard";
import CFGCard from "@/components/custom/CFGCard";

interface CodeAndCfgPanelsProps {
  showCyclomaticComplexity?: boolean;
  showCodeCoverage?: boolean;
  codeCoveragePercentage?: number;
  highlightedLines: { start: number; end: number } | null;
  setHighlightedLines: React.Dispatch<React.SetStateAction<{ start: number; end: number } | null>>;
}

export const CodeAndCfgPanels: React.FC<CodeAndCfgPanelsProps> = ({
  showCyclomaticComplexity = true,
  showCodeCoverage = false,
  codeCoveragePercentage = 0,
  highlightedLines,
  setHighlightedLines,
}) => {
  const [isCodeCollapsed, setIsCodeCollapsed] = useState(false);
  const [isCfgCollapsed, setIsCfgCollapsed] = useState(false);
  const codePanelRef = useRef<ImperativePanelHandle>(null);
  const cfgPanelRef = useRef<ImperativePanelHandle>(null);

  return (
    <>
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
              style={{
                position: "absolute",
                zIndex: 10,
                display: "flex",
                height: 56,
                width: 24,
                alignItems: "center",
                justifyContent: "center",
                borderRadius: 12,
                border: "1px solid rgba(255,255,255,0.15)",
                boxShadow: "0 4px 10px -4px rgba(0,0,0,0.4)",
                flexDirection: "column",
                gap: 4,
              }}
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
            <div
              style={{ writingMode: "vertical-rl", transform: "rotate(180deg)" }}
              className="text-xs font-semibold text-blue-700 tracking-wider group-hover:scale-105 transition-transform"
            >
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
            <div
              style={{ writingMode: "vertical-rl", transform: "rotate(180deg)" }}
              className="text-xs font-semibold text-blue-700 tracking-wider group-hover:scale-105 transition-transform"
            >
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
    </>
  );
};
