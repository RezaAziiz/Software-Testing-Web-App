import React, { useState, useEffect } from "react";
import { FaPlus, FaSearch } from "react-icons/fa";
import Sidebar from "../components/custom/Sidebar";
import Pagination from "@/components/custom/Pagination";
import ModulesTable from "../components/custom/ModuleTable";
import ConfirmationModal from "../components/custom/ConfirmationModal";
import { useNavigate } from "react-router-dom";

// Interface for module object
export interface Module {
  id: string;
  name: string;
  type: string;
  difficulty: number; // 1: Sangat Mudah, 2: Mudah, 3: Sedang, 4: Sulit
}

// Array of modules
const initialModules: Module[] = [
  // { id: '1', name: "Pengurangan", type: "Fungsi", difficulty: 1 },
  // { id: '2', name: "Penambahan", type: "Fungsi", difficulty: 2 },
  // { id: '3', name: "Perkalian", type: "Fungsi", difficulty: 3 },
  // { id: '4', name: "Pembagian", type: "Fungsi", difficulty: 4 },
  // { id: '5', name: "Pengurangan", type: "Fungsi", difficulty: 1 },
  // { id: '6', name: "Penambahan", type: "Fungsi", difficulty: 2 },
  // { id: '7', name: "Perkalian", type: "Fungsi", difficulty: 3 },
  // { id: '8', name: "Pembagian", type: "Fungsi", difficulty: 4 },
  // { id: '9', name: "Pengurangan", type: "Fungsi", difficulty: 1 },
  // { id: '10', name: "Penambahan", type: "Fungsi", difficulty: 2 },
  // { id: '11', name: "Perkalian", type: "Fungsi", difficulty: 3 },
];

const ListModulesPage = () => {
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
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10; // Number of items per page
  const [modules, setModules] = useState(initialModules);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [moduleToDelete, setModuleToDelete] = useState<Module | null>(null);
  const [deleteMessage, setDeleteMessage] = useState<string | null>(null);
  const [deleteErrorMessage, setDeleteErrorMessage] = useState<string | null>(null);
  const [totalPages, setTotalPages] = useState<number>(1);

 
  const fetchDataModul = async (page:number, keyword:string) => {
    setCurrentPage(page);
    setSearchTerm(keyword);
    try {
      const response = await fetch(`${apiUrl}/modul/search?keyword=${keyword}&page=${page}&limit=${itemsPerPage}`, {
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
      let tempModules = [];
      for (let i = 0; i < data.data.length; i++) {
        tempModules.push(
            { id: data.data[i].ms_id_modul, 
              name: data.data[i].ms_nama_modul, 
              type: data.data[i].jenis_modul, 
              difficulty: parseInt(data.data[i].ms_tingkat_kesulitan), 
            }
          )
      }
      setModules(tempModules)
      setTotalPages(data.max_page)
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };
  const deleteDataModul = async (id:string) => {
    try {
      let param = {
        id_modul: id
      }
      const response = await fetch(`${apiUrl}/modul/delete`, {
        method: 'DELETE',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body:JSON.stringify(param)
      });

      if (!response.ok) {
        if (response.status === 403) {
          // throw new Error('Forbidden: Access is denied');
          navigate('/error');
        } else if (response.status === 500) {
          const data = await response.json();
          setDeleteErrorMessage(`${data.message}`);
          setTimeout(() => setDeleteErrorMessage(null), 2000);
        } else {
          setDeleteErrorMessage(`HTTP error! status: ${response.status}`);
          setTimeout(() => setDeleteErrorMessage(null), 2000);
        }
      }else{
        setDeleteMessage("Modul berhasil dihapus.");
        setTimeout(() => setDeleteMessage(null), 2000);
        fetchDataModul(1, searchTerm); 
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const handlePageChange = (pageNumber: number) => {
    // setCurrentPage(pageNumber);
    fetchDataModul(pageNumber, searchTerm)
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleDelete = (id: string) => {
    deleteDataModul(id)
    closeModal();
  };

  const openModal = (module: Module) => {
    setModuleToDelete(module);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setModuleToDelete(null);
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    fetchDataModul(1,e.target.value);
  };

  // const filteredModules = modules.filter(
  //   (module) =>
  //     module.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
  //     module.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
  //     getDifficultyString(module.difficulty)
  //       .toLowerCase()
  //       .includes(searchTerm.toLowerCase())
  // );

  // const indexOfLastItem = currentPage * itemsPerPage;
  // const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  // const currentItems = filteredModules.slice(indexOfFirstItem, indexOfLastItem);
  useEffect(() => {
    if (session != null){
      if (session.login_type != "teacher"){
          navigate("/dashboard-student")
      }else{
        fetchDataModul(1,searchTerm)
      }
    }else{
      navigate("/login")
    }
    
  }, []);

  const addModul = () => {
    navigate("/module")
  };
  const editModul = (module: Module) => {
    navigate("/module?idModul="+module.id)
  };

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
            <h1 className="lg:text-2xl text-xl font-bold text-blue-800 mb-6 mt-4">
              Kelola Data Modul Program
            </h1>
            <div className="flex flex-row justify-between items-center space-y-0 gap-4">
              <div className="relative w-full md:w-1/2">
                <input
                  type="text"
                  placeholder="Search or type"
                  className="w-full p-2 pl-10 border text-sm border-gray-300 rounded-md"
                  value={searchTerm}
                  onChange={handleSearch}
                />
                <FaSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              </div>
              <button
                className="flex items-center justify-center text-sm bg-blue-800 text-white py-2 px-3 md:px-4 lg:px-5 rounded hover:bg-blue-700"
                onClick={addModul}
              >
                <FaPlus className="mr-0 md:mr-2" />
                <span className="hidden md:inline">Tambah Modul Program</span>
              </button>
            </div>
          </div>
        </div>
        <div className="min-h-screen p-4 md:p-6">
          <div className="bg-white shadow-md rounded-lg overflow-x-auto">
            {deleteMessage && (
              <div className="p-4 mb-4 text-green-500 bg-green-100 rounded-md">
                {deleteMessage}
              </div>
            )}
            {deleteErrorMessage && (
              <div className="p-4 mb-4 text-red-500 bg-red-100 rounded-md">
                {deleteErrorMessage}
              </div>
            )}
            {modules.length === 0 ? (
              <div className="p-4 text-center text-red-500">
                Data tidak ditemukan
              </div>
            ) : (
              <>
                <ModulesTable modules={modules} onDelete={openModal} onEdit={editModul} />
              </>
            )}
          </div>
          <div className="flex justify-center items-center py-4 text-xs lg:text-sm">
                  <Pagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={handlePageChange}
                  />
          </div>
        </div>
      </div>
      {isModalOpen && moduleToDelete && (
        <ConfirmationModal
          message="Apakah kamu benar-benar ingin menghapus modul ini? Modul akan dihapus secara permanen."
          onConfirm={() => handleDelete(moduleToDelete.id)}
          onCancel={closeModal}
          isSidebarOpen={isSidebarOpen}
        />
      )}
    </div>
  );
};

// const getDifficultyString = (difficulty: number): string => {
//   switch (difficulty) {
//     case 1:
//       return "Sangat Mudah";
//     case 2:
//       return "Mudah";
//     case 3:
//       return "Sedang";
//     case 4:
//       return "Sulit";
//     default:
//       return "";
//   }
// };

export default ListModulesPage;
