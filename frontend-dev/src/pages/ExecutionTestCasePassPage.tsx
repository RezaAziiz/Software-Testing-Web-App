import Layout from "./Layout";
import React, { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Menu } from "@/components/custom/Menu";
import ModuleSpecificationCard from "@/components/custom/ModuleSpecificationCard";
import AddTestCaseCard from "@/components/custom/AddTestCaseCard";
import CFGCard from "@/components/custom/CFGCard";
// import {
//   ResizableHandle,
//   ResizablePanel,
//   ResizablePanelGroup,
// } from "@/components/ui/resizable";
// import { ScrollArea } from "@/components/ui/scroll-area";
import PassCard from "@/components/custom/PassCard";

const ExecutionTestCasePassPage: React.FC = () => {
  const apiUrl = import.meta.env.VITE_API_URL;
  let apiKey = import.meta.env.VITE_API_KEY;
  // const modulId = import.meta.env.VITE_MODULE_ID;
  const sessionData = localStorage.getItem('session')
  let session = null
  if (sessionData != null){
      session = JSON.parse(sessionData);
      apiKey = session.token
  }
  useEffect(() => {
    if (session != null){
        if (session.login_type != "student"){
            navigate("/dashboard-teacher")
        }
    }else{
      navigate("/login")
    }
  }, []);

  const [showCyclomaticComplexity] = useState(true);
  const [showCodeCoverage] = useState(false);
  // const [percentageCoverage, setPercentageCoverage] = useState<number>(0);
  // const [minimumCoverage, setMinimumCoverage] = useState<number>(0);
  // const [points, setPoints] = useState<number>(0);
  const [codeCoveragePercentage] = useState(0);

  const bottomRef = useRef<HTMLDivElement>(null);

  const location = useLocation();
  const { state: navigationData } = location;
  type NavigationDataModul = {
    modul_id: string;
  };

  // const [dataIdModul, SetDataIdModul] = useState<NavigationDataModul | null>(
  //   null
  // );
  const queryParameters = new URLSearchParams(window.location.search)
  const modulId = queryParameters.get("topikModulId")

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
      navigate("/test-result?topikModulId="+modulId, { state: dataToPass });
    } 
    
    const handleNavigateNextChallenge = async() => {
      try {
        const response = await fetch(`${apiUrl}/topik/nextChallenge?idTopikModul=${modulId}`, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Authorization': `Bearer ${apiKey}`
          }
        });
  
        if (!response.ok) {
          if (response.status === 403) {
            // throw new Error('Forbidden: Access is denied');
            navigate('/error');
          } else {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
        }
        
        const data = await response.json();
        if (data.data){
          navigate({
            pathname: '/topikModul',
            search: '?topikModulId='+data.data.ms_id_topik_modul,
          });
        } else{
          navigate({
            pathname: '/list-challanges',
            search: '?idTopik='+data.data_current.ms_id_topik,
          });
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
     } 

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
              <div className="mt-6 h-full w-full">
                <PassCard
                  percentageCoverage={navigationData?.coverage_score || 0}
                  minimumCoverage={navigationData?.minimum_coverage_score || 0}
                  statusEksekusi={navigationData?.status_eksekusi || false}
                  tanggalEksekusi={navigationData?.tgl_eksekusi || ""}
                  modulId={navigationData?.modul_id||""}
                  poin={navigationData?.points||0}

                />
              </div>
              {/* Penanda untuk scroll ke bagian paling bawah */}
              <div ref={bottomRef}></div>
              <div className="space-x-2 items-center p-4 justify-end">
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
