import Layout from "./Layout";
import { useState, useEffect } from "react";
import { Menu } from "@/components/custom/Menu";
import ModuleCoverage from "@/components/custom/ModuleCoverage";
import CFGCard from "@/components/custom/CFGCard";
// import {
// //   ResizableHandle,
//   ResizablePanel,
//   ResizablePanelGroup,
// } from "@/components/ui/resizable";
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
    };
  }

const TestResultPage = () => {
    const navigate = useNavigate();
    const apiUrl = import.meta.env.VITE_API_URL;
    let apiKey = import.meta.env.VITE_API_KEY;
    // const modulId = import.meta.env.VITE_MODULE_ID;
    const sessionData = localStorage.getItem('session')
    let session = null
    if (sessionData != null){
        session = JSON.parse(sessionData);
        apiKey = session.token
    }

    const queryParameters = new URLSearchParams(window.location.search)
    const modulId = queryParameters.get("topikModulId")
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
          edges: []
        }
    };
    const [showCyclomaticComplexity] = useState(false);
    const [showCodeCoverage] = useState(true);
    const [dataTestResult, setDataTestResult] = useState<DataResultTest>(defaultData);
    const [error, setError] = useState<string | null>(null);
    const fetchDataTestResult = async () => {
        
        try {
          const response = await fetch(`${apiUrl}/modul/getResultTest/${modulId}`, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
              'Authorization': `Bearer ${apiKey}`
            }
          });
    
          if (!response.ok) {
            if (response.status === 403) {
              // throw new Error('Forbidden: Access is denied');
              navigate("/error")
            } else if (response.status !== 404) {
              throw new Error(`HTTP error! status: ${response.status}`);
            } 
          }else{
            const data = await response.json();
            setDataTestResult(data || null);
          }
        } catch (error) {
          console.error('Error fetching data:', error);
          setError((error as Error).message);
        }
    };
    const handleCoverageTestReport = async () => {
        const url = apiUrl +"/"+ dataTestResult?.linkReportCoverage;
        const win = window.open(url, '_blank');
        win?.focus();
    };
    const handleTestReport = async () => {
        const url = apiUrl +"/"+ dataTestResult?.linkReportTesting;
        const win = window.open(url, '_blank');
        win?.focus();
    };
    
    useEffect(() => {
      if (session === null){
        navigate("/login")
      }else if (session.login_type != "student"){
          navigate("/dashboard-teacher")
      }else{
          fetchDataTestResult();
      }
    }, []);

    if (error) {
        return <div className="p-4 bg-white rounded-lg shadow-md h-screen">Error: {error}</div>;
    }
    
    return (
        <Layout>
        <Menu />
        <div className="flex flex-col md:flex-row w-screen min-h-screen">
          <div className="flex flex-col w-full md:w-1/2">
            <ModuleCoverage dataResultTest = {dataTestResult}/>
          </div>
          <div
            className="flex flex-col w-full md:w-1/2 items-center md:pl-4 md:pr-4 md:gap-4"
            style={{ overflowY: "auto" }}
          >
             <CFGCard 
                showCyclomaticComplexity={showCyclomaticComplexity}
                showCodeCoverage={showCodeCoverage}
                codeCoveragePercentage={dataTestResult.coverageScore}
              />
              <TestResultCard dataResultTest = {dataTestResult}/>
                  <div className="flex justify-end space-x-2 items-center p-4">
                      {(dataTestResult.totalFailedTestCase == 0 && dataTestResult.executionDate !== "") && (
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
        </div>
        </Layout>
    );
};

export default TestResultPage;
