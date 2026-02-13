import React, { useState, useEffect } from "react";
import { FaSearch} from "react-icons/fa";
import Pagination from "@/components/custom/Pagination";
import StudentTable from "../components/custom/StudentTable";
import ConfirmationModal from "../components/custom/ConfirmationModal";
import Sidebar from "@/components/custom/Sidebar";
import AddStudentDataForm from "@/components/custom/AddStudentDataForm";
import UploadStudentDataForm from "@/components/custom/UploadStudentDataForm";
import { useNavigate } from "react-router-dom";

interface Student {
  id: string;
  nim: string;
  name: string;
  class: string;
  program: string;
}

const initialStudents: Student[] = [
    // {
    //   id: "1",
    //   nim: "16501006",
    //   name: "Asep Sunarya",
    //   class: "A",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "2",
    //   nim: "16501007",
    //   name: "Kinara Rengganis",
    //   class: "B",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "3",
    //   nim: "16501008",
    //   name: "Rizky Pratama",
    //   class: "A",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "4",
    //   nim: "16501009",
    //   name: "Siti Nurhaliza",
    //   class: "B",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "5",
    //   nim: "16501010",
    //   name: "Ahmad Fauzi",
    //   class: "C",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "6",
    //   nim: "16501011",
    //   name: "Dewi Sartika",
    //   class: "A",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "7",
    //   nim: "16501012",
    //   name: "Budi Setiawan",
    //   class: "B",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "8",
    //   nim: "16501013",
    //   name: "Tini Rahmawati",
    //   class: "C",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "9",
    //   nim: "16501014",
    //   name: "Andi Kurniawan",
    //   class: "A",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "10",
    //   nim: "16501015",
    //   name: "Sri Mulyani",
    //   class: "B",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "11",
    //   nim: "16501016",
    //   name: "Fajar Nugraha",
    //   class: "C",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "12",
    //   nim: "16501017",
    //   name: "Intan Permatasari",
    //   class: "A",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "13",
    //   nim: "16501018",
    //   name: "Eko Susanto",
    //   class: "B",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "14",
    //   nim: "16501019",
    //   name: "Lina Marlina",
    //   class: "C",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "15",
    //   nim: "16501020",
    //   name: "Gilang Ramadhan",
    //   class: "A",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "16",
    //   nim: "16501021",
    //   name: "Rina Andriani",
    //   class: "B",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "17",
    //   nim: "16501022",
    //   name: "Hendra Saputra",
    //   class: "C",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "18",
    //   nim: "16501023",
    //   name: "Putri Ayu",
    //   class: "A",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "19",
    //   nim: "16501024",
    //   name: "Agus Supriyadi",
    //   class: "B",
    //   program: "D4 Teknik Informatika",
    // },
    // {
    //   id: "20",
    //   nim: "16501025",
    //   name: "Nurul Hidayati",
    //   class: "C",
    //   program: "D4 Teknik Informatika",
    // }
  ];

const StudentPage: React.FC = () => {
  const apiUrl = import.meta.env.VITE_API_URL;
  let apiKey = import.meta.env.VITE_API_KEY;
  // const modulId = import.meta.env.VITE_MODULE_ID;
  const sessionData = localStorage.getItem('session')
  let session = null
  if (sessionData != null){
      session = JSON.parse(sessionData);
      apiKey = session.token
  }
  const navigate = useNavigate();

  const [students, setStudents] = useState<Student[]>(initialStudents);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [showConfirmation, setShowConfirmation] = useState<boolean>(false);
  const [studentToDelete, setStudentToDelete] = useState<string | null>(null);
  const [studentToUpdate, setStudentToUpdate] = useState<string>("0");
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);
  const [infoMessage, setInfoMessage] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [isAddStudentFormOpen, setIsAddStudentFormOpen] = useState(false);
  const [isUploadStudentFormOpen, setIsUploadStudentFormOpen] = useState(false);
  const [totalPages,setTotalPages]= useState<number>(1);
  const itemsPerPage = 10;

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    fetchDataStudent(page, searchQuery);
  };

  const handleEdit = (id:string) => {
    // Handle edit logic here
    setStudentToUpdate(id)
    setIsAddStudentFormOpen(true)
  };

  const handleDelete = (id: string) => {
    setShowConfirmation(true);
    setStudentToDelete(id);
  };

  const confirmDelete = () => {
    if (studentToDelete !== null) {
      deleteDataStudent(studentToDelete)
    }
  };

  const cancelDelete = () => {
    setShowConfirmation(false);
    setStudentToDelete(null);
  };
  const handleAfterSave = () => {
    fetchDataStudent(currentPage, searchQuery);
  };
  const handleAfterUpload = () => {
    fetchDataStudent(currentPage, searchQuery);
  };

  // const filteredStudents = students.filter(
  //   (student) =>
  //     student.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
  //     student.nim.toLowerCase().includes(searchQuery.toLowerCase()) ||
  //     student.class.toLowerCase().includes(searchQuery.toLowerCase()) ||
  //     student.program.toLowerCase().includes(searchQuery.toLowerCase())
  // );

  // const currentFilteredItems = filteredStudents.slice(
  //   (currentPage - 1) * itemsPerPage,
  //   currentPage * itemsPerPage
  // );
  const deleteDataStudent = async (id:string) => {
    try {
      const response = await fetch(`${apiUrl}/student/${id}`, {
        method: 'DELETE',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        }
      });

      if (!response.ok) {
        if (response.status === 403) {
          // throw new Error('Forbidden: Access is denied');
          navigate('/error');
        } else if (response.status === 500) {
          const data = await response.json();
          setErrorMessage(`${data.message}`);
          setTimeout(() => setErrorMessage(""), 2000);
        } else {
          setErrorMessage(`HTTP error! status: ${response.status}`);
          setTimeout(() => setErrorMessage(""), 2000);
        }
      }else{
        setInfoMessage("Mahasiswa berhasil dihapus");
        setTimeout(() => setInfoMessage(""), 3000);
        fetchDataStudent(currentPage, searchQuery);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally{
      setShowConfirmation(false);
      setStudentToDelete(null);
    }
  };

  const fetchDataStudent = async (page:number, keyword:string) => {
    setCurrentPage(page);
    setSearchQuery(keyword);
    let url = `${apiUrl}/student/search?keyword=${keyword}&page=${page}&limit=${itemsPerPage}`
   
    try {
      const response = await fetch(url, {
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
      let tempStudents = [];
      for (let i = 0; i < data.data.length; i++) {
        tempStudents.push(
            { id: data.data[i].ms_student_id,
              nim: data.data[i].ms_student_nim,
              name: data.data[i].ms_student_name,
              class: data.data[i].ms_student_kelas,
              program: data.data[i].ms_student_prodi,
            }
        )
      }
      
      // setStudents(tempStudents)
      // setTotalPages(data.max_page)

      if (tempStudents.length === 0 && page > 1) {
        setCurrentPage(page - 1); // Go to the previous page if no data in the current page
        fetchDataStudent(page - 1, keyword);
      } else {
        setStudents(tempStudents);
        setTotalPages(data.max_page);
      }
    } catch (error) {
      setErrorMessage("Error fetching data");
      setTimeout(() => setErrorMessage(""), 3000);
      console.error('Error fetching data:', error);
    }
  };

  useEffect(() => {
    if (session != null){
      if (session.login_type != "teacher"){
          navigate("/dashboard-student")
      }else{
        fetchDataStudent(1,searchQuery)
      }
    }else{
      navigate("/login")
    }
    
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
      <div
        className={`flex-1 ${
          isSidebarOpen ? "ml-64" : "ml-20"
        } transition-all duration-300`}
      >
        <div className="w-full bg-white p-4 shadow mb-6">
          <div className="max-w-screen-xl mx-auto">
            <h1 className="lg:text-2xl text-xl font-bold text-blue-800 mb-6 mt-4">
              Kelola Data Mahasiswa
            </h1>
            <div className="flex flex-row justify-between items-center space-y-0 gap-4">
              <div className="relative w-full md:w-1/2">
                <input
                  type="text"
                  placeholder="Search or type"
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setCurrentPage(1); // Reset to first page on search
                    fetchDataStudent(1,e.target.value);
                  }}
                  className="w-full p-2 pl-10 border text-sm border-gray-300 rounded-md"
                />
                <FaSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              </div>
              <div className="flex space-x-4">
                <UploadStudentDataForm
                  isDialogOpen={isUploadStudentFormOpen}
                  setIsDialogOpen={setIsUploadStudentFormOpen}
                  setInfoMessage={setInfoMessage}
                  setErrorMessage={setErrorMessage}
                  afterUpload={handleAfterUpload}
                />
                <AddStudentDataForm 
                  isDialogOpen={isAddStudentFormOpen}
                  setIsDialogOpen={setIsAddStudentFormOpen}
                  idStudent={studentToUpdate}
                  setIdStudent={setStudentToUpdate}
                  afterSave={handleAfterSave}
                />
              </div>
            </div>
          </div>
        </div>
        <div className="min-h-screen p-4 md:p-6">
          <div className="bg-white shadow-md rounded-lg overflow-x-auto">
          {infoMessage && (
            <div className="p-4 mb-4 text-green-500 bg-green-100 rounded-md">
              {infoMessage}
            </div>
          )}
          {errorMessage && (
              <div className="p-4 mb-4 text-red-500 bg-red-100 rounded-md">
                {errorMessage}
              </div>
          )}
          {students.length === 0 ? (
            <div className="p-4 text-center text-red-500">
              Data tidak ditemukan
            </div>
          ) : (
            <>
              <StudentTable
                students={students}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            </>
          )}
          </div>
          <div className="flex justify-center items-center py-4 text-xs lg:text-sm">
            <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={handlePageChange} />
          </div>
        </div>
      </div>
      {showConfirmation && (
        <ConfirmationModal
          message="Are you sure you want to delete this student?"
          onConfirm={confirmDelete}
          onCancel={cancelDelete}
          isSidebarOpen={isSidebarOpen}
        />
      )}
    </div>
  );
};

export default StudentPage;
