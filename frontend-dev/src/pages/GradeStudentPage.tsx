import React, { useState, useEffect } from 'react';
import { FaSearch, FaDownload } from 'react-icons/fa';
import Sidebar from '../components/custom/Sidebar';
import Pagination from '../components/custom/Pagination';
import GradeStudentTable from '../components/custom/GradeStudentTable';
// import * as XLSX from 'xlsx';
import { useNavigate } from "react-router-dom";

interface grade {
  no: number;
  nim: string;
  nama: string;
  poin: number;
  modul: number;
  program: string;
}
interface combo {
  label: string;
  value: string;
}

// const students = [
//     {
//         no: 1,
//         nim: "16501006",
//         nama: "Asep Sunarya",
//         poin: 750,
//         modul: 5,
//         program: "Ganjil Genap",
//         },
//         {
//         no: 2,
//         nim: "16501007",
//         nama: "Kinara Rengganis",
//         poin: 0,
//         modul: 0,
//         program: "Faktorial",
//         },
//         {
//         no: 3,
//         nim: "16501008",
//         nama: "Kinara Rengganis",
//         poin: 0,
//         modul: 0,
//         program: "Faktorial",
//         },
//         {
//         no: 4,
//         nim: "16501008",
//         nama: "Kinara Rengganis",
//         poin: 0,
//         modul: 0,
//         program: "Faktorial",
//         },
//         {
//         no: 5,
//         nim: "16501009",
//         nama: "Kinara Rengganis",
//         poin: 0,
//         modul: 0,
//         program: "Faktorial",
//         },
//         {
//         no: 6,
//         nim: "16501010",
//         nama: "Asep Sunarya",
//         poin: 750,
//         modul: 5,
//         program: "Ganjil Genap",
//         },
//         {
//         no: 7,
//         nim: "16501012",
//         nama: "Asep Sunarya",
//         poin: 750,
//         modul: 5,
//         program: "Ganjil Genap",
//         },
//         {
//         no: 8,
//         nim: "16501013",
//         nama: "Asep Sunarya",
//         poin: 750,
//         modul: 5,
//         program: "Ganjil Genap",
//         },
//         {
//         no: 10,
//         nim: "16501014",
//         nama: "Kinara Rengganis",
//         poin: 0,
//         modul: 0,
//         program: "Faktorial",
//         },
// ];

// const topics = ["Semua", "Ganjil Genap", "Faktorial", "Pemrograman Dasar", "Struktur Data"];

const GradeStudentPage: React.FC = () => {
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

  const [topics, setTopics] = useState<combo[]>([]);
  const [students, setStudents] = useState<grade[]>([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [selectedTopic, setSelectedTopic] = useState<string>("");
  const [sortColumn, setSortColumn] = useState<'poin' | 'modul' | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [totalPages, setTotalPages] = useState<number>(1);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1); 
    fetchDataGrade(1,e.target.value, selectedTopic)
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    fetchDataGrade(page,searchQuery, selectedTopic)
  };

  const handleTopicChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedTopic(e.target.value);
    setCurrentPage(1); // Reset to first page on topic change
    fetchDataGrade(1,searchQuery, e.target.value)
  };

  const handleSort = (column: 'poin' | 'modul') => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  const itemsPerPage = 10;

  // let filteredStudents = students;
  // if (searchQuery) {
  //   filteredStudents = filteredStudents.filter(
  //     (student) =>
  //       student.nama.toLowerCase().includes(searchQuery.toLowerCase()) ||
  //       student.nim.toLowerCase().includes(searchQuery.toLowerCase())
  //   );
  // }

  // if (selectedTopic !== "semua") {
  //   filteredStudents = filteredStudents.filter(
  //     (student) => student.program.toLowerCase() === selectedTopic
  //   );
  // }

  // if (sortColumn) {
  //   filteredStudents.sort((a, b) => {
  //     if (a[sortColumn] < b[sortColumn]) return sortDirection === 'asc' ? -1 : 1;
  //     if (a[sortColumn] > b[sortColumn]) return sortDirection === 'asc' ? 1 : -1;
  //     return 0;
  //   });
  // }

  // const totalPages = Math.ceil(filteredStudents.length / itemsPerPage);
  // const currentFilteredItems = filteredStudents.slice(
  //   (currentPage - 1) * itemsPerPage,
  //   currentPage * itemsPerPage
  // );

  const handleDownload = () => {
    // const worksheet = XLSX.utils.json_to_sheet(students);
    // const workbook = XLSX.utils.book_new();
    // XLSX.utils.book_append_sheet(workbook, worksheet, "Students");
    // XLSX.writeFile(workbook, "students.xlsx");
    fetchDownloadDataGrade(currentPage, searchQuery, selectedTopic)
  };
  const fetchDownloadDataGrade = async (page:number, keyword:string, id_topik:string) => {
    setCurrentPage(page);
    setSearchQuery(keyword);
    try {
      const response = await fetch(`${apiUrl}/grade/download?keyword=${keyword}&id_topik=${id_topik}&page=${page}&limit=${itemsPerPage}`, {
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
      
      const blob = await response.blob();
     // Create blob link to download
      const url = window.URL.createObjectURL(
        new Blob([blob]),
      );
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute(
        'download',
        `DataGrade.xlsx`,
      );

      // Append to html link element page
      document.body.appendChild(link);

      // Start download
      link.click();

    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };
  const fetchDataGrade = async (page:number, keyword:string, id_topik:string) => {
    setCurrentPage(page);
    setSearchQuery(keyword);
    try {
      const response = await fetch(`${apiUrl}/grade/search?keyword=${keyword}&id_topik=${id_topik}&page=${page}&limit=${itemsPerPage}`, {
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
      let tempGrades = [];
      for (let i = 0; i < data.data.length; i++) {
        tempGrades.push(
            { no: ((page-1)*itemsPerPage)+(i+1), 
              nim: data.data[i].ms_student_nim, 
              nama: data.data[i].ms_student_name, 
              poin: parseInt(data.data[i].JmlPoint), 
              modul: parseInt(data.data[i].JmlModulSelesai), 
              program: data.data[i].lastModulName, 
            }
          )
      }
      setStudents(tempGrades)
      setTotalPages(data.max_page)
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const fetchDataComboTopics = async () => {
    try {
      const response = await fetch(`${apiUrl}/combo/topik`, {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
      });

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error("Forbidden: Access is denied");
        } else {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      }
      const data = await response.json();
      setTopics(data.data);
     } catch (error) {
      console.error("Error fetching module name:", error);
    }
  };
  useEffect(() => {
    if (session != null){
      if (session.login_type != "teacher"){
          navigate("/dashboard-student")
      }else{
        fetchDataComboTopics()
        fetchDataGrade(1,searchQuery, selectedTopic)
      }
    }else{
      navigate("/login")
    }
  },[]);

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
      <div className={`flex-1 ${isSidebarOpen ? "ml-64" : "ml-20"} transition-all duration-300 `}>
        <div className="w-full bg-white p-4 shadow">
          <div className="max-w-screen-xl mx-auto">
          <h1 className="lg:text-2xl text-xl font-bold text-blue-800 mb-6 mt-4">
              Grade Pencapaian Mahasiswa
            </h1>
            <div className="flex flex-row justify-between items-center space-y-0 gap-4">
              <div className="flex items-center w-full md:w-1/2">
                <span className="text-black font-semibold mr-2">Topik:</span>
                <select
                  value={selectedTopic}
                  onChange={handleTopicChange}
                   className="text-sm p-2 border border-gray-300 rounded-md w-full md:w-3/4 lg:w-1/2"
                >
                  <option value="">Semua</option>
                  {topics.map((topic) => (
                    <option key={topic.value} value={topic.value.toLowerCase()}>
                      {topic.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="relative w-full md:w-1/2">
                <input
                  type="text"
                  placeholder="Search or type"
                  value={searchQuery}
                  onChange={handleSearchChange}
                  className="text-sm w-full p-2 pl-10 border border-gray-300 rounded-md"
                />
                <FaSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              </div>
            </div>
          </div>
        </div>
        <button
              className="flex items-center text-sm bg-blue-800 text-white px-4 m-4 rounded hover:bg-blue-600 ml-auto"
              onClick={handleDownload}
            >
              <FaDownload className="mr-0 md:mr-2" />
              <span className="hidden md:inline">Unduh</span>
            </button>
        <div className="min-h-screen px-4">
          <div className="bg-white shadow-md rounded-lg overflow-x-auto">
            <div className="bg-white shadow-md rounded-lg">
              {students.length === 0 ? (
                <div className="p-4 text-center text-red-500">
                  Data tidak ditemukan
                </div>
              ) : (
                <>
                  <GradeStudentTable
                    students={students}
                    onSort={handleSort}
                    sortColumn={sortColumn || undefined}
                    sortDirection={sortDirection}
                  />
                </>
              )}
            </div>
          </div>
          <div className="flex justify-center items-center py-4 text-xs lg:text-sm">
            <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={handlePageChange} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default GradeStudentPage;
