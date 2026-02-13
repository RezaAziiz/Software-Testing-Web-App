import { useState, useEffect } from 'react';
import "../../index.css";
import { CopyBlock, dracula } from 'react-code-blocks';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { useNavigate } from "react-router-dom";


interface DataModul {
  ms_id_modul: string;
  ms_jenis_modul: string;
  ms_nama_modul: string;
  ms_deskripsi_modul: string;
  ms_source_code: string | null;
  ms_class_name: string;
  ms_function_name: string;
  ms_return_type: string;
  ms_jml_parameter: number;
  ms_tingkat_kesulitan: string;
  ms_cc: string | null;
}

interface ParameterData {
  ms_id_parameter: string;
  ms_id_modul: string;
  ms_nama_parameter: string;
  ms_tipe_data: string;
  ms_rules: string;
}

interface Data {
  data_modul: DataModul;
  data_parameter_modul: ParameterData[];
  data_cfg: {
    nodes: any[];
    edges: any[];
  };
}

const ModuleSpecificationCard = () => {
  const navigate = useNavigate();
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
  
  const [dataModule, setDataModule] = useState<Data | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sourceCode, setSourceCode] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchDataModule = async () => {
    try {
      const response = await fetch(`${apiUrl}/modul/detailByIdTopikModul/${modulId}`, {
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
      console.log(data);
      setDataModule(data.data || null);

      if (data.data) {
        fetchSourceCodeText(data.data.data_modul.ms_id_modul);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      setError((error as Error).message);
    }
  };

  const fetchSourceCodeText = async (modulId: string) => {
    try {
      const response = await fetch(`${apiUrl}/modul/getSourceCodeText/${modulId}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setSourceCode(data.data);
    } catch (error) {
      console.error('Error fetching source code text:', error);
      setError((error as Error).message);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchDataModule();
  }, []);

  if (error) {
    return <div className="p-4 bg-white rounded-lg shadow-md h-screen">Error: {error}</div>;
  }
  
  if (loading) {
    return (
      <div className="p-6 bg-white rounded-lg shadow-lg h-full space-y-6">
        {/* Kotak Spesifikasi Modul */}
        <div className="bg-gray-100 p-4 rounded-lg">
          <Skeleton className="h-5 w-32 mb-4 bg-gray-200" />
          <Skeleton className="h-5 w-full mb-4 bg-gray-200" />
          <Skeleton className="h-5 w-full mb-4 bg-gray-200" />
        </div>

        {/* Kotak Tabel Parameter */}
        <div className="bg-gray-100 p-4 rounded-lg">
          <Skeleton className="h-5 w-32 mb-4 bg-gray-200" />
          <Skeleton className="h-5 w-full mb-4 bg-gray-200" />
          <Skeleton className="h-5 w-full mb-4 bg-gray-200" />
          <Skeleton className="h-5 w-full mb-4 bg-gray-200" />
        </div>

        {/* Kotak Kode Program */}
        <div className="bg-gray-100 p-4 rounded-lg">
          <Skeleton className="h-5 w-32 mb-4 bg-gray-200" />
          <Skeleton className="h-5 w-full mb-4 bg-gray-200" />
          <Skeleton className="h-5 w-full mb-4 bg-gray-200" />
          <Skeleton className="h-5 w-full mb-4 bg-gray-200" />
        </div>
      </div>

    );
  }

  
  return (
    <div className="p-6 bg-white rounded-lg shadow-lg h-full">
      <div className="overflow-y-auto">
        {dataModule && dataModule.data_modul && dataModule.data_parameter_modul && (
          <>
            <h3 className="text-base font-bold mb-4 text-gray-800">Spesifikasi Modul</h3>
            <div className='border border-black p-2 mb-6 bg-slate-50'>
              <p className="mb-4 text-sm  text-gray-600">Modul : {dataModule.data_modul.ms_nama_modul}</p>
              <p className="mb-4 text-sm  text-gray-600">{dataModule.data_modul.ms_deskripsi_modul}</p>
            </div>
            
            <div className="rounded-lg mb-6">
              <h4 className="text-base font-semibold mb-3 text-gray-700">Daftar Parameter</h4>
              <Table className="text-sm border-collapse border border-black">
                <TableHeader>
                  <TableRow className="bg-blue-800 text-sm text-white py-2 hover:bg-blue-600">
                    <TableHead className="border border-black w-10">No</TableHead>
                    <TableHead className="border border-black">Nama Parameter</TableHead>
                    <TableHead className="border border-black">Tipe Data</TableHead>
                    <TableHead className="border border-black w-full text-center pr-4">Aturan Validasi</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {dataModule.data_parameter_modul.map((parameter, index) => (
                    <TableRow key={parameter.ms_id_parameter} className={`${index % 2 === 0 ? "bg-blue-100" : "bg-blue-200"} text-sm leading-tight`}>
                      <TableCell className="py-2 border border-black w-10 text-center">{index + 1}</TableCell>
                      <TableCell className="py-2 border border-black">{parameter.ms_nama_parameter}</TableCell>
                      <TableCell className="py-2 border border-black">{parameter.ms_tipe_data}</TableCell>
                      <TableCell className="py-2 border border-black w-full pr-4">{parameter.ms_rules}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
            
            <h4 className="text-base font-bold mb-1 text-gray-800">Kode Program</h4>
            <div className="text-sm p-4 rounded-lg">
              <CopyBlock
                language="java"
                text={sourceCode || 'Loading source code...'}
                showLineNumbers={true}
                theme={dracula}
                codeBlock
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ModuleSpecificationCard;
