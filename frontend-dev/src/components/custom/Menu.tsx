import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import PoinIcon from "/src/assets/logo/poin.png";

interface ModuleData {
  ms_tingkat_kesulitan: string;
}


export function Menu() {
  const apiUrl = import.meta.env.VITE_API_URL;
  let apiKey = import.meta.env.VITE_API_KEY;
  // const modulId = import.meta.env.VITE_MODULE_ID;
  const sessionData = localStorage.getItem('session')
  if (sessionData != null){
      const session = JSON.parse(sessionData);
      apiKey = session.token
  }
  const queryParameters = new URLSearchParams(window.location.search)
  const modulId = queryParameters.get("topikModulId")
  const location = useLocation();
  const [moduleData, setModuleData] = useState<ModuleData | null>(null);

  useEffect(() => {
    const fetchModuleData = async () => {
      try {
        const response = await fetch(`${apiUrl}/modul/detailByIdTopikModul/${modulId}`, {
          method: "GET",
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${apiKey}`,
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const responseData = await response.json();
        setModuleData(responseData.data.data_modul);
        // Tampilkan tingkat kesulitan yang terambil dari respons
        console.log("Tingkat Kesulitan:", responseData.data.data_modul.ms_tingkat_kesulitan);
      } catch (error) {
        console.error("Error fetching module data:", error);
      }
    };

    fetchModuleData();
  }, []);

  // Simulasi nilai difficultyLevel dari database
  const difficultyLevel: string = moduleData?.ms_tingkat_kesulitan || "";
  const levels: { [key: string]: string } = {
    "1": "Sangat Mudah",
    "2": "Mudah",
    "3": "Sedang",
    "4": "Sulit",
  };

  // Fungsi untuk menghitung poin maksimal
  const calculateMaxPoint = (level: number, difficulty: string): number => {
    switch (difficulty) {
      case "4":
        return level * 4;
      case "3":
        return level * 3;
      case "2":
        return level * 2;
      case "1":
        return level * 1;
      default:
        return 0;
    }
  };

  const maxPoint: number = calculateMaxPoint(100, difficultyLevel); // Misalnya level kesulitan adalah 100
  const linkPembuatanTestCase = "/topikModul?topikModulId="+modulId
  const linkTestResult = "/test-result?topikModulId="+modulId
  return (
    <div className="menu"
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        maxWidth: "100%",
        marginRight: "20px",
      }}
    >
      <div className="buttons text-sm lg:text-base" style={{ display: "flex" }}>
        <Link
          to={linkPembuatanTestCase}
          className={
            location.pathname === "/topikModul" ||
            location.pathname === "/pass" ||
            location.pathname === "/fail"
              ? "buttonMenu activeButton"
              : "buttonMenu inactiveButton"
          }
        >
          Pembuatan Test Case
        </Link>
        <Link
          to={linkTestResult}
          className={
            location.pathname === "/test-result"
              ? "buttonMenu activeButton"
              : "buttonMenu inactiveButton"
          }
        >
          Hasil Pengujian
        </Link>
      </div>

      <div
        className="poin mr-6"
        style={{ display: "flex", alignItems: "center" }}
      >
        <img
          src={PoinIcon}
          alt="Poin Icon"
          className="w-5 h-5 lg:w-6 lg:h-6 mr-2"
        />
        <div>
          <p className='text-xs lg:text-sm font-bold mt-1'>
            Poin Maksimal: {maxPoint}
          </p>
          <p className="text-xs mb-1">
            {levels[difficultyLevel]}
          </p>
        </div>
      </div>
    </div>
  );
}
