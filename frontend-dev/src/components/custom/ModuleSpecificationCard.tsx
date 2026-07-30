import { useState, useEffect } from 'react';
import "../../index.css";
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

const parseValidationRule = (ruleString: string) => {
  try {
    const rule = JSON.parse(ruleString);
    if (rule.nama_rule === "range") {
      return `Range: ${rule.min_value} - ${rule.max_value}`;
    } else if (rule.nama_rule === "enumerasi") {
      return `Enumerasi: ${rule.value}`;
    } else if (rule.nama_rule === "countOfLength") {
      return `Length: ${rule.min_value} - ${rule.max_value}`;
    } else if (rule.nama_rule === "condition") {
      return `Kondisi: ${rule.condition} ${rule.value}`;
    }
    return rule.nama_rule || ruleString;
  } catch (e) {
    return ruleString;
  }
};

const ModuleSpecificationCard = () => {
  const navigate = useNavigate();
  const apiUrl = import.meta.env.VITE_API_URL;
  let apiKey = import.meta.env.VITE_API_KEY;
  // const modulId = import.meta.env.VITE_MODULE_ID;
  const sessionData = localStorage.getItem('session')
  if (sessionData != null) {
    const session = JSON.parse(sessionData);
    apiKey = session.token
  }

  const queryParameters = new URLSearchParams(window.location.search)
  const modulId = queryParameters.get("topikModulId")

  const [dataModule, setDataModule] = useState<Data | null>(null);
  const [error, setError] = useState<string | null>(null);
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
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError((error as Error).message);
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
              <p className="mb-4 text-sm text-gray-600">Modul : {dataModule.data_modul.ms_nama_modul}</p>
              <p className="mb-4 text-sm text-gray-600">{dataModule.data_modul.ms_deskripsi_modul}</p>
            </div>

            <div className="rounded-lg mb-6 overflow-hidden border border-slate-200">
              <h4 className="text-base font-semibold mb-3 text-gray-700 bg-white p-2 border-b border-slate-200">Daftar Parameter</h4>
              <Table className="text-sm w-full">
                <TableHeader>
                  <TableRow className="bg-blue-800 text-sm text-white py-2 hover:bg-blue-700">
                    <TableHead className="w-10 text-center font-semibold text-white">No</TableHead>
                    <TableHead className="font-semibold text-white">Nama Parameter</TableHead>
                    <TableHead className="font-semibold text-white">Tipe Data</TableHead>
                    <TableHead className="w-full text-center pr-4 font-semibold text-white">Aturan Validasi</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {dataModule.data_parameter_modul.map((parameter, index) => (
                    <TableRow key={parameter.ms_id_parameter} className="text-sm leading-tight border-b border-slate-200 hover:bg-slate-50 transition-colors">
                      <TableCell className="py-2 w-10 text-center">{index + 1}</TableCell>
                      <TableCell className="py-2 font-medium text-slate-800">{parameter.ms_nama_parameter}</TableCell>
                      <TableCell className="py-2 text-slate-600 font-mono text-xs">{parameter.ms_tipe_data}</TableCell>
                      <TableCell className="py-2 w-full pr-4">{parseValidationRule(parameter.ms_rules)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ModuleSpecificationCard;
