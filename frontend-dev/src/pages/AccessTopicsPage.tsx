import React, { useState, useEffect  } from "react";
import Sidebar from "../components/custom/SidebarStudent";
import { FaSearch } from "react-icons/fa";
import OngoingTopics from "../components/custom/OngoingTopics";
import LearningTopics from "../components/custom/LearningTopics";
import CompletedTopics from "../components/custom/CompletedTopics";
import { useNavigate } from "react-router-dom";

// const ongoingTopics = [
//   { id: 1, title: "Pemula", progress: 40, remaining: 8, xp: 600 },
//   { id: 2, title: "Pemula", progress: 10, remaining: 9, xp: 90 },
// ];

// const learningTopics = [
//   {
//     id: 1,
//     title: "Topik 1",
//     description: "Pembuatan Test Case level menengah",
//     challenges: 20,
//     xp: 2400,
//   },
//   {
//     id: 2,
//     title: "Topik 2",
//     description: "Pembuatan Test Case level Pemula",
//     challenges: 10,
//     xp: 1600,
//   },
//   {
//     id: 3,
//     title: "Topik 3",
//     description: "Pembuatan Test Case level Mahir",
//     challenges: 30,
//     xp: 4600,
//   },
//   {
//     id: 4,
//     title: "Topik 4",
//     description: "Pembuatan Test Case level Pemula",
//     challenges: 40,
//     xp: 6000,
//   },
//   {
//     id: 5,
//     title: "Topik 1",
//     description: "Pembuatan Test Case level menengah",
//     challenges: 20,
//     xp: 2400,
//   },
//   {
//     id: 6,
//     title: "Topik 2",
//     description: "Pembuatan Test Case level Pemula",
//     challenges: 10,
//     xp: 1600,
//   },
//   {
//     id: 7,
//     title: "Topik 3",
//     description: "Pembuatan Test Case level Mahir",
//     challenges: 30,
//     xp: 4600,
//   },
// ];

// const completedTopics = [
//   { id: 1, title: "Topik X", xp: 550 },
//   { id: 2, title: "Topik Y", xp: 900 },
//   { id: 3, title: "Topik Z", xp: 780 },
//   { id: 4, title: "Topik X", xp: 550 },
//   { id: 5, title: "Topik Y", xp: 900 },
//   { id: 6, title: "Topik Z", xp: 780 },
// ];
interface DataOnGoing {
  id: string;
  title: string;
  progress: number; 
  remaining: number;
  xp: number;
}
interface DataCompleted {
  id: string;
  title: string;
  xp: number;
}
interface DataLearning {
  id: string;
  title: string;
  description: string;
  challenges: number;
  xp: number;
}
const TopicPage: React.FC = () => {
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
  useEffect(() => {
    if (session != null){
        if (session.login_type != "student"){
            navigate("/dashboard-teacher")
        }
    }else{
      navigate("/login")
    }
  }, []);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [filterOption, setFilterOption] = useState<string>("all");
  const [ongoingTopics, setOngoingTopics] = useState<DataOnGoing[]>([]);
  const [learningTopics, setLearningTopics] = useState<DataLearning[]>([]);
  const [completedTopics, setCompletedTopics] = useState<DataCompleted[]>([]);
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleCompletedTopicClick = (id: string) => {
    // console.log(`Clicked on topic id: ${id}`);
    navigate("/list-challanges?idTopik="+id);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilterOption(e.target.value);
  };

  const fetchDataOngoingChallenge = async () => {
    try {
      const response = await fetch(`${apiUrl}/topik/challenge?status=ongoing`, {
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
      let tempOngoing = [];
      for (let i = 0; i < data.data.length; i++) {
        tempOngoing.push(
            { id: data.data[i].ms_id_topik, 
              title: data.data[i].ms_nama_topik, 
              progress: (data.data[i].jml_completed_modul/data.data[i].jml_modul)*100, 
              remaining: (data.data[i].jml_modul - data.data[i].jml_completed_modul), 
              xp: data.data[i].jml_ongoing_point },
          )
      }
      setOngoingTopics(tempOngoing);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };
  const fetchDataLearningChallenge = async () => {
    try {
      const response = await fetch(`${apiUrl}/topik/challenge?status=learning`, {
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
      let tempLearning = [];
      for (let i = 0; i < data.data.length; i++) {
        tempLearning.push(
            { id: data.data[i].ms_id_topik, 
              title: data.data[i].ms_nama_topik, 
              description: data.data[i].ms_deskripsi_topik, 
              challenges: (data.data[i].jml_modul), 
              xp: data.data[i].jml_point }
          )
      }
      setLearningTopics(tempLearning);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const fetchDataCompletedChallenge = async () => {
    try {
      const response = await fetch(`${apiUrl}/topik/challenge?status=completed`, {
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
      let tempCompleted = [];
      for (let i = 0; i < data.data.length; i++) {
        tempCompleted.push(
            { id: data.data[i].ms_id_topik, 
              title: data.data[i].ms_nama_topik, 
              xp: data.data[i].jml_ongoing_point }
          )
      }
      setCompletedTopics(tempCompleted);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };
  useEffect(() => {
    fetchDataOngoingChallenge();
    fetchDataLearningChallenge();
    fetchDataCompletedChallenge();
  }, []);

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
  
  return (
    <div className="flex flex-col lg:flex-row w-screen lg:w-screen">
      <Sidebar isOpen={isSidebarOpen} toggleSidebar={toggleSidebar} />
      <div className={`flex-1 ${isSidebarOpen ? "ml-64" : "ml-20"} transition-all duration-300`}>
        <div className="w-full bg-white p-4 shadow mb-6">
          <div className="max-w-screen-xl mx-auto">
            <h1 className="text-xl lg:text-2xl font-bold text-blue-800 mb-6 mt-4">
              Belajar Kemampuan Pembuatan Test Case Unit
            </h1>
            <div className="flex flex-row justify-between items-center space-y-0 gap-4">
              <div className="relative w-full md:w-1/2">
                <input
                  type="text"
                  placeholder="Search or type"
                  value={searchQuery}
                  onChange={handleSearchChange}
                  className="w-full p-2 text-sm pl-10 border border-gray-300 rounded-md"
                />
                <FaSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              </div>
              <div className="flex items-center space-x-4 mr-4">
                <select
                  value={filterOption}
                  onChange={handleFilterChange}
                  className="p-2 border border-gray-300 rounded-md text-sm"
                >
                  <option value="all">Semua</option>
                  <option value="ongoing">Sedang Berjalan</option>
                  <option value="learning">Topik Belajar</option>
                  <option value="completed">Sudah Dipelajari</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <div className="min-h-screen p-4 md:p-6">
          <div className="bg-white shadow-md rounded-lg overflow-hidden">
            {filterOption === "all" || filterOption === "ongoing" ? (
              <OngoingTopics topics={ongoingTopics} searchQuery={searchQuery} />
            ) : null}

            {filterOption === "all" || filterOption === "learning" ? (
              <LearningTopics topics={learningTopics} searchQuery={searchQuery} />
            ) : null}

            {filterOption === "all" || filterOption === "completed" ? (
              <CompletedTopics
                topics={completedTopics}
                searchQuery={searchQuery}
                onTopicClick={handleCompletedTopicClick}
              />
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TopicPage;
