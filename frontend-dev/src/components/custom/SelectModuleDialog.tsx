import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import Pagination from '@/components/custom/Pagination';
import { useNavigate } from "react-router-dom";

interface Module {
  id: string;
  name: string;
  description: string;
  difficulty: string;
}

interface SelectModuleDialogProps {
  isDialogOpen: boolean;
  setIsDialogOpen: (open: boolean) => void;
  onAddModules: (modules: Module[]) => void;
  selectedModules: Module[];
  topicName: string;
}

const SelectModuleDialog: React.FC<SelectModuleDialogProps> = ({ isDialogOpen, setIsDialogOpen, onAddModules, selectedModules, topicName }) => {
  const navigate = useNavigate();
  const apiUrl = import.meta.env.VITE_API_URL;
  let apiKey = import.meta.env.VITE_API_KEY;
  // const modulId = import.meta.env.VITE_MODULE_ID;
  const sessionData = localStorage.getItem('session')
  if (sessionData != null){
      const session = JSON.parse(sessionData);
      apiKey = session.token
  }
  const [totalPages, setTotalPages] = useState<number>(1);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [modules, setModules] = useState<Module[]>([]);
  const itemsPerPage = 8; // Number of items per page
  const [tempSelectedModules, setTempSelectedModules] = useState<Module[]>(selectedModules);

  // const allModules: Module[] = [
  //   { id: '1', name: 'Perkalian', description: 'Modul mengalikan dua buah bilangan', difficulty: 'Sangat Mudah' },
  //   { id: '2', name: 'Penambahan', description: 'Modul menambahkan dua buah bilangan', difficulty: 'Mudah' },
  //   { id: '3', name: 'Pembagian', description: 'Modul pembagian dua bilangan', difficulty: 'Sedang' },
  //   { id: '4', name: 'Pengurangan', description: 'Modul pengurangan dua buah bilangan', difficulty: 'Sulit' },
  //   { id: '5', name: 'Modul 5', description: 'Deskripsi Modul 5', difficulty: 'Mudah' },
  //   { id: '6', name: 'Modul 6', description: 'Deskripsi Modul 6', difficulty: 'Sulit' },
  //   { id: '7', name: 'Modul 7', description: 'Deskripsi Modul 7', difficulty: 'Sedang' },
  //   { id: '8', name: 'Modul 8', description: 'Deskripsi Modul 8', difficulty: 'Sangat Mudah' },
  //   { id: '9', name: 'Modul 9', description: 'Deskripsi Modul 9', difficulty: 'Mudah' },
  //   { id: '10', name: 'Modul 10', description: 'Deskripsi Modul 10', difficulty: 'Sulit' },
  //   { id: '11', name: 'Modul 11', description: 'Deskripsi Modul 11', difficulty: 'Sedang' },
  //   { id: '12', name: 'Modul 12', description: 'Deskripsi Modul 12', difficulty: 'Sangat Mudah' },
  //   { id: '13', name: 'Modul 13', description: 'Deskripsi Modul 13', difficulty: 'Mudah' },
  //   { id: '14', name: 'Modul 14', description: 'Deskripsi Modul 14', difficulty: 'Sulit' },
  //   { id: '15', name: 'Modul 15', description: 'Deskripsi Modul 15', difficulty: 'Sedang' },
  //   { id: '16', name: 'Modul 16', description: 'Deskripsi Modul 16', difficulty: 'Sangat Mudah' },
  //   { id: '17', name: 'Modul 17', description: 'Deskripsi Modul 17', difficulty: 'Mudah' },
  //   { id: '18', name: 'Modul 18', description: 'Deskripsi Modul 18', difficulty: 'Sulit' },
  //   { id: '19', name: 'Modul 19', description: 'Deskripsi Modul 19', difficulty: 'Sedang' },
  //   { id: '20', name: 'Modul 20', description: 'Deskripsi Modul 20', difficulty: 'Sangat Mudah' },
  // ];

  useEffect(() => {
    fetchModules(currentPage);
  }, [currentPage]);

  useEffect(() => {
    setTempSelectedModules(selectedModules);
  }, [isDialogOpen]);

  const fetchModules = async (page: number) => {
    // Simulate fetching modules from an API or data source
    // setModules(allModules.slice((page - 1) * itemsPerPage, page * itemsPerPage));
    setCurrentPage(page);
    try {
      const response = await fetch(`${apiUrl}/modul/search?page=${page}&limit=${itemsPerPage}`, {
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
              description: data.data[i].ms_deskripsi_modul, 
              difficulty: data.data[i].tingkat_kesulitan, 
            }     
          )
      }
      setModules(tempModules)
      setTotalPages(data.max_page)
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const toggleModuleSelection = (moduleId: string) => {
    const selectedModule = modules.find(m => m.id === moduleId);
    if (selectedModule) {
      if (tempSelectedModules.some(m => m.id === moduleId)) {
        setTempSelectedModules(tempSelectedModules.filter(m => m.id !== moduleId));
      } else {
        setTempSelectedModules([...tempSelectedModules, selectedModule]);
      }
    }
  };

  const isSelected = (moduleId: string) => tempSelectedModules.some(m => m.id === moduleId);


  // const totalPages = Math.ceil(allModules.length / itemsPerPage);

  const getDifficultyStyle = (difficulty: string) => {
    switch (difficulty) {
      case 'Sangat Mudah':
        return 'bg-blue-100 text-blue-700';
      case 'Mudah':
        return 'bg-green-100 text-green-700';
      case 'Sedang':
        return 'bg-yellow-100 text-yellow-700';
      case 'Sulit':
        return 'bg-red-100 text-red-700';
      default:
        return '';
    }
  };

  const handleCancel = () => {
    setTempSelectedModules(selectedModules); // Reset to original selected modules
    setIsDialogOpen(false);
  };

  const handleAdd = () => {
    onAddModules(tempSelectedModules); // Keep the changes
    setIsDialogOpen(false);
  };


  return (
    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
      <DialogContent className="bg-white p-4 md:p-10 rounded-lg shadow-lg max-w-4xl mx-auto max-h-screen overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-lg text-center font-bold mb-2">
            Tambahkan Tantangan Pada Topik {topicName}
          </DialogTitle>
        </DialogHeader>
        <div className="overflow-x-auto text-xs lg:text-sm">
          <table className="min-w-full bg-white border rounded-lg shadow-md">
            <thead>
              <tr className="bg-blue-800 text-white">
                <th className="py-2 px-4 border">No</th>
                <th className="py-2 px-4 border">Select</th>
                <th className="py-2 px-4 border">Nama Modul Program</th>
                <th className="py-2 px-4 border">Deskripsi</th>
                <th className="py-2 px-4 border">Tingkat Kesulitan</th>
              </tr>
            </thead>
            <tbody>
              {modules.map((module, index) => (
                <tr key={module.id} className={`text-center ${index % 2 === 0 ? 'bg-blue-50' : 'bg-white'}`}>
                  <td className="py-2 px-4 border">{(currentPage - 1) * itemsPerPage + index + 1}</td>
                  <td className="py-2 px-4 border">
                    <input
                      type="checkbox"
                      checked={isSelected(module.id)}
                      onChange={() => toggleModuleSelection(module.id)}
                    />
                  </td>
                  <td className="py-2 px-4 border">{module.name}</td>
                  <td className="py-2 px-4 border">{module.description}</td>
                  <td className="py-2 px-4 border">
                    <span className={`inline-block w-32 px-2 py-1 rounded-full ${getDifficultyStyle(module.difficulty)}`}>
                      {module.difficulty}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="flex justify-center mt-2">
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={(page) => setCurrentPage(page)}
            />
          </div>
          <div className="flex flex-col md:flex-row justify-end space-y-4 md:space-y-0 md:space-x-4 w-full flex-wrap">
            <Button className="bg-transparent border border-blue-800 text-blue-800 rounded-full px-4 py-2 hover:bg-blue-100 sm:px-2 sm:py-1 sm:text-xs" onClick={handleCancel}>
              Kembali
            </Button>
            <Button className="bg-blue-800 text-white rounded-full px-4 py-2 hover:bg-blue-700 sm:px-2 sm:py-1 sm:text-xs" onClick={handleAdd}>
              Tambahkan
            </Button>
          </div>
      </DialogContent>
    </Dialog>
  );
};

export default SelectModuleDialog;
