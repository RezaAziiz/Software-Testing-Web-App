import Layout from "./Layout";
import { useState, useEffect } from "react";
import { Menu } from "@/components/custom/Menu";
import ModuleSpecificationCard from "@/components/custom/ModuleSpecificationCard";
import CodeProgramCard from "@/components/custom/CodeProgramCard";
import AddTestCaseCard from "@/components/custom/AddTestCaseCard";
import CFGCard from "@/components/custom/CFGCard";
import {
  ResizableHandle,
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
  const sessionData = localStorage.getItem('session')
  let session = null
  if (sessionData != null){
      session = JSON.parse(sessionData);
  }
  useEffect(() => {
    if (session != null){
        if (session.login_type != "student"){
            navigate("/dashboard-teacher")
        }
    }else{
      navigate("/login")
    }
  }, [sessionData]);

  return (
    <Layout>
      <Menu />
      <div className="flex flex-col w-screen min-h-screen p-4 gap-6 bg-slate-50">
        <ResizablePanelGroup direction="horizontal" className="min-h-[calc(100vh-100px)] rounded-lg border border-slate-200">
          
          {/* Left Panel: Specification and Test Cases */}
          <ResizablePanel defaultSize={40} minSize={30} className="overflow-y-auto workspace-scrollbar">
            <div className="flex flex-col gap-6 h-full">
              <ModuleSpecificationCard />
              <AddTestCaseCard />
              <MinimalCard />
            </div>
          </ResizablePanel>

          <ResizableHandle withHandle className="bg-slate-200 w-2 hover:bg-slate-300 transition-colors" />

          {/* Right Panel: Code and CFG */}
          <ResizablePanel defaultSize={60} minSize={30}>
            <ResizablePanelGroup direction="horizontal">
              <ResizablePanel defaultSize={50} minSize={30} className="overflow-y-auto workspace-scrollbar">
                <CodeProgramCard highlightedLines={highlightedLines} />
              </ResizablePanel>

              <ResizableHandle withHandle className="bg-slate-200 w-2 hover:bg-slate-300 transition-colors" />

              <ResizablePanel defaultSize={50} minSize={20} className="overflow-y-auto workspace-scrollbar">
                <CFGCard
                  showCyclomaticComplexity={showCyclomaticComplexity}
                  showCodeCoverage={showCodeCoverage}
                  codeCoveragePercentage={codeCoveragePercentage}
                  onNodeClick={setHighlightedLines}
                  highlightedLines={highlightedLines}
                />
              </ResizablePanel>
            </ResizablePanelGroup>
          </ResizablePanel>

        </ResizablePanelGroup>
      </div>
    </Layout>
  );
};

export default CreateTestCasePage;
