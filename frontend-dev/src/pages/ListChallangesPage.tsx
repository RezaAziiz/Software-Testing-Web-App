// src/pages/ListChallengesPage.tsx
import React, { useState, useEffect } from "react";
import SidebarStudent from "../components/custom/SidebarStudent";
import ChallengeCard from "../components/custom/ChallengeCard";
import logo_berpikir from "../assets/logo/berpikir.png";
import { useNavigate } from "react-router-dom";

interface DataChallenges {
  id: string;
  title: string;
  level: string;
  currentPoints: number;
  maxPoints: number;
  status: string;
}

const ListChallengesPage: React.FC = () => {
  const navigate = useNavigate();
  const apiUrl = import.meta.env.VITE_API_URL;
  let apiKey = import.meta.env.VITE_API_KEY;
  // const modulId = import.meta.env.VITE_MODULE_ID;
  const sessionData = localStorage.getItem("session");
  if (sessionData != null) {
    const session = JSON.parse(sessionData);
    apiKey = session.token;
  }
  const queryParameters = new URLSearchParams(window.location.search);
  const topikId = queryParameters.get("idTopik") ?? "";

  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isInvalidTopik, setIsInvalidTopik] = useState(false);
  // const [statusFilter, setStatusFilter] = useState<string[]>([]); // 'All', 'Selesai', 'Belum Selesai'
  const [isSelesaiChecked, setIsSelesaiChecked] = useState(false);
  const [isBlmSelesaiChecked, setIsBlmSelesaiChecked] = useState(false);
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };
  const handleSelesaiChecked = (e: any) => {
    setIsSelesaiChecked(e.target.checked);
    if (e.target.checked) {
      fetchDataListChallenge("Y");
    } else {
      fetchDataListChallenge("All");
    }
  };
  const handleBlmSelesaiChecked = (e: any) => {
    setIsBlmSelesaiChecked(e.target.checked);
    if (e.target.checked) {
      fetchDataListChallenge("N");
    } else {
      fetchDataListChallenge("All");
    }
  };

  const [challenges, setChallenges] = useState<DataChallenges[]>([]);
  const [namaModul, setNamaModul] = useState<string>("");
  const [currentXP, setCurrentXP] = useState<number>(0);
  const [maxXP, setMaxXP] = useState<number>(0); // Set the total XP to 2700 as per the design
  const [completedChallenges, setCompletedChallenges] = useState<number>(0);
  const [totalChallenges, setTotalChallenges] = useState<number>(0);
  const [progressPercentage, setProgressPrecentage] = useState<number>(0);

  const fetchDataListChallenge = async (status: string) => {
    if (!topikId) {
      setIsInvalidTopik(true);
      return;
    }

    try {
      const response = await fetch(
        `${apiUrl}/topik/listChallenge?idTopik=${topikId}&status=${status}`,
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
      console.log(data);
      const challengesData = Array.isArray(data.data_challenge)
        ? data.data_challenge
        : [];
      const dataTopik = data.data_topik ?? {
        ms_nama_topik: "",
        jml_ongoing_point: 0,
        jml_point: 0,
        jml_completed_modul: 0,
        jml_modul: 0,
      };

      let tempChallanges = [];
      for (let i = 0; i < challengesData.length; i++) {
        let statusTemp = challengesData[i].status;
        if (statusTemp === "B") {
          if (challengesData[i].status_test_case != "Kosong") {
            statusTemp = "N";
          }
        }
        tempChallanges.push({
          id: challengesData[i].ms_id_topik_modul,
          title: challengesData[i].ms_nama_modul,
          level: challengesData[i].tingkat_kesulitan,
          currentPoints: challengesData[i].ongoing_point,
          maxPoints: parseInt(challengesData[i].ms_tingkat_kesulitan) * 100,
          // status: getStatusString(challengesData[i].status),
          status: statusTemp,
          ms_tingkat_kesulitan: challengesData[i].ms_tingkat_kesulitan,
        });
      }
      // Urutkan tantangan berdasarkan ms_tingkat_kesulitan
      // tempChallanges.sort((a: any, b:any) => parseInt(a.ms_tingkat_kesulitan) - parseInt(b.ms_tingkat_kesulitan)); // sort dilakukan di BE
      setChallenges(tempChallanges);
      setNamaModul(dataTopik.ms_nama_topik);
      setCurrentXP(dataTopik.jml_ongoing_point);
      setMaxXP(dataTopik.jml_point);
      setCompletedChallenges(dataTopik.jml_completed_modul);
      setTotalChallenges(dataTopik.jml_modul);
      setProgressPrecentage(
        dataTopik.jml_modul > 0
          ? (dataTopik.jml_completed_modul / dataTopik.jml_modul) * 100
          : 0,
      );
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };
  // const getStatusString = (status: string): string => {
  //   switch (status) {
  //     case "N":
  //       return "Ongoing";
  //     case "B":
  //       return "Not Started";
  //     case "Y":
  //       return "Completed";
  //     default:
  //       return "Not Started";
  //   }
  // };
  useEffect(() => {
    if (!topikId) {
      setIsInvalidTopik(true);
      return;
    }
    fetchDataListChallenge("All");
  }, [topikId]);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(min-width: 768px)");
    const handleMediaQueryChange = (event: MediaQueryListEvent) => {
      setIsSidebarOpen(event.matches);
    };

    setIsSidebarOpen(mediaQuery.matches);

    mediaQuery.addEventListener("change", handleMediaQueryChange);
    return () => {
      mediaQuery.removeEventListener("change", handleMediaQueryChange);
    };
  }, []);

  if (isInvalidTopik) {
    return (
      <div className="flex flex-col lg:flex-row w-screen lg:w-screen min-h-screen bg-slate-100">
        <SidebarStudent isOpen={isSidebarOpen} toggleSidebar={toggleSidebar} />
        <div
          className={`flex-1 transition-all duration-300 ${isSidebarOpen ? "ml-64" : "ml-20"}`}
        >
          <div className="flex justify-center items-center h-screen px-6">
            <div className="max-w-xl w-full bg-white rounded-xl shadow-lg p-8 text-center">
              <h2 className="text-2xl font-bold text-blue-800 mb-4">
                Topik tidak tersedia
              </h2>
              <p className="text-sm text-gray-600 mb-6">
                Halaman ini membutuhkan parameter idTopik. Silakan kembali ke
                daftar topik dan pilih topik terlebih dahulu.
              </p>
              <button
                onClick={() => navigate("/list-topics")}
                className="rounded-lg bg-blue-800 text-white px-4 py-2 hover:bg-blue-700"
              >
                Kembali ke Daftar Topik
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col lg:flex-row w-screen lg:w-screen min-h-screen bg-slate-100">
      <SidebarStudent isOpen={isSidebarOpen} toggleSidebar={toggleSidebar} />
      <div
        className={`flex-1 transition-all duration-300 ${isSidebarOpen ? "ml-64" : "ml-20"}`}
      >
        <div className="flex justify-between bg-white items-center m-5 p-4">
          <h1 className="lg:text-xl md:text-lg text-base font-bold text-blue-800">
            Belajar Kemampuan Pembuatan Test Case Unit
          </h1>
        </div>
        <div className="lg:px-20 md:px-2  shadow h-full overflow-auto bg-slate-100">
          <div className="sticky top-0 bg-white z-10">
            <div className="flex flex-col lg:flex-row bg-white p-4 mx-8">
              <div className="flex flex-col lg:w-1/2">
                <h2 className="lg:text-xl md:text-lg text-base font-bold text-blue-800">
                  {namaModul}
                </h2>
                <div className="text-green-600 lg:text-lg md:text-base text-sm font-bold">
                  {currentXP} / {maxXP} XP
                </div>
              </div>
              <div className="flex lg:w-1/2 gap-4">
                <div className="flex flex-col flex-grow gap-4">
                  <div className="text-blue-800 lg:text-sm md:text-xs text-xs">
                    {totalChallenges - completedChallenges} tantangan lagi
                  </div>
                  <div className="w-full lg:mt-2">
                    <div className="w-full bg-gray-200 rounded-full">
                      <div
                        className="bg-blue-600 lg:h-4 md:h-3 h-2 rounded-full"
                        style={{ width: `${progressPercentage}%` }}
                      ></div>
                    </div>
                  </div>
                  <span className="lg:text-sm md:text-xs text-xs">
                    {progressPercentage.toFixed(1)}% : {completedChallenges} /{" "}
                    {totalChallenges}
                  </span>
                </div>
                <div className="flex justify-end items-center">
                  <img
                    src={logo_berpikir}
                    alt="Logo"
                    className="lg:w-40 md:w-30 w-20"
                  />
                </div>
              </div>
            </div>
            <div className="border border-gray-300 lg:mx-10 md:mx-5 mx-4" />
            <div className="flex flex-row gap-4 lg:mx-10 lg:mt-10 md:mx-6 md:mt-6 mx-4 mt-4 ">
              <div className="flex-1 overflow-y-auto">
                <div className="grid grid-cols-1 lg:gap-4 md:gap-2 gap-1">
                  {challenges.length > 0 ? (
                    challenges.map((challenge, index) => (
                      <ChallengeCard
                        key={index}
                        idTopikModul={challenge.id}
                        title={challenge.title}
                        level={challenge.level}
                        currentPoints={challenge.currentPoints}
                        maxPoints={challenge.maxPoints}
                        status={challenge.status}
                      />
                    ))
                  ) : (
                    <div className="text-center text-gray-500">
                      No challenges found
                    </div>
                  )}
                </div>
              </div>
              <div className="w-1/4 bg-white h-full overflow-auto mx-auto">
                <h2 className="lg:text-lg md:text-base text-sm font-bold text-blue-800 mb-4 lg:mx-6 md:mx-4 mx-2">
                  Status
                </h2>
                <div className="lg:mx-6 md:mx-4 mx-2">
                  <input
                    type="checkbox"
                    id="selesai"
                    checked={isSelesaiChecked}
                    onChange={(e) => handleSelesaiChecked(e)}
                  />
                  <label
                    htmlFor="selesai"
                    className="ml-2 lg:text-base md:text-sm text-xs font-medium text-blue-800"
                  >
                    Selesai
                  </label>
                </div>
                <div className="lg:mx-6 md:mx-4 mx-2">
                  <input
                    type="checkbox"
                    id="belumSelesai"
                    checked={isBlmSelesaiChecked}
                    onChange={(e) => handleBlmSelesaiChecked(e)}
                  />
                  <label
                    htmlFor="belumSelesai"
                    className="ml-2 lg:text-base md:text-sm text-xs font-medium text-blue-800"
                  >
                    Belum Selesai
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ListChallengesPage;
