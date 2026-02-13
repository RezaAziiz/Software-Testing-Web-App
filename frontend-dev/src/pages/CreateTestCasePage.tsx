import Layout from "./Layout";
import { useState, useEffect } from "react";
import { Menu } from "@/components/custom/Menu";
import ModuleSpecificationCard from "@/components/custom/ModuleSpecificationCard";
import AddTestCaseCard from "@/components/custom/AddTestCaseCard";
import CFGCard from "@/components/custom/CFGCard";
// import {
//   ResizableHandle,
//   ResizablePanel,
//   ResizablePanelGroup,
// } from "@/components/ui/resizable";
import MinimalCard from "@/components/custom/MinimalCard";
import { useNavigate } from "react-router-dom";

const CreateTestCasePage: React.FC = () => {
  const navigate = useNavigate();
  const [showCyclomaticComplexity] = useState(true);
  const [showCodeCoverage] = useState(false);
  const codeCoveragePercentage = 0;
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
      <div className="flex flex-col md:flex-row w-screen min-h-screen">
        <div className="flex flex-col w-full md:w-1/2">
          <ModuleSpecificationCard />
        </div>
        <div
          className="flex flex-col w-full md:w-1/2 items-center md:pl-4 md:pr-4 md:gap-4"
          style={{ overflowY: "auto" }}
        >
          <CFGCard
            showCyclomaticComplexity={showCyclomaticComplexity}
            showCodeCoverage={showCodeCoverage}
            codeCoveragePercentage={codeCoveragePercentage}
          />
          <AddTestCaseCard />
          <MinimalCard />
        </div>
      </div>
    </Layout>
  );
};

export default CreateTestCasePage;
