import { useState, useEffect } from 'react';
import "../../index.css";
import { Skeleton } from "@/components/ui/skeleton";
// import { CopyBlock, dracula } from 'react-code-blocks';



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
interface DataResultTest {
  coverageScore: number;
  point: number;
  totalTestCase: number;
  totalPassTestCase: number;
  totalFailedTestCase: number;
  executionDate: string;
  linkReportTesting: string;
  linkReportCoverage: string;
  linkSourceCoverage: string;
  data_cfg: {
    nodes: any[];
    edges: any[];
  };
}

type ModuleCoverageProps = {
  dataResultTest: DataResultTest;
};


const ModuleCoverage: React.FC<ModuleCoverageProps> = ({
  dataResultTest
}) => {
  const apiUrl = import.meta.env.VITE_API_URL;
  let apiKey = import.meta.env.VITE_API_KEY;
  // const modulId = import.meta.env.VITE_MODULE_ID;
  const sessionData = localStorage.getItem('session')
  if (sessionData != null){
      const session = JSON.parse(sessionData);
      apiKey = session.token
  }
  // const modulId = import.meta.env.VITE_MODULE_ID;
  const queryParameters = new URLSearchParams(window.location.search)
  const modulId = queryParameters.get("topikModulId")
  const [dataModule, setDataModule] = useState<Data | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  //const [sourceCode, setSourceCode] = useState<string | null>(null);
  const linkReportSourceCoverage = apiUrl+"/"+dataResultTest.linkSourceCoverage
  
  useEffect(() => {
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
            throw new Error('Forbidden: Access is denied');
          } else {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
        }

        const data = await response.json();
        console.log(data);
        setDataModule(data.data || null);

        // if (data.data) {
          // fetchSourceCodeText(data.data.data_modul.ms_id_modul);
        // }
      } catch (error) {
        console.error('Error fetching data:', error);
        setError((error as Error).message);
      } finally {
        setLoading(false);
      }
    };

    // const fetchSourceCodeText = async (modulId: string) => {
    //   try {
    //     const response = await fetch(`${apiUrl}/modul/getSourceCodeText/${modulId}`, {
    //       method: 'GET',
    //       headers: {
    //         'Accept': 'application/json',
    //         'Authorization': `Bearer ${apiKey}`
    //       }
    //     });

    //     if (!response.ok) {
    //       throw new Error(`HTTP error! status: ${response.status}`);
    //     }

    //     const data = await response.json();
    //     setSourceCode(data.data);
    //   } catch (error) {
    //     console.error('Error fetching source code text:', error);
    //     setError((error as Error).message);
    //   }
    // };

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

        {/* Kotak Code Coverage */}
        <div className="bg-gray-100 p-4 rounded-lg">
          <Skeleton className="h-5 w-32 mb-4 bg-gray-200" />
          <Skeleton className="h-5 w-full mb-4 bg-gray-200" />
          <Skeleton className="h-5 w-full mb-4 bg-gray-200" />
          <Skeleton className="h-5 w-full mb-4 bg-gray-200" />
        </div>
      </div>

    );
  }

  if (dataResultTest.totalTestCase == 0){
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
              <h4 className="text-base font-bold mb-1 text-gray-800">Code Coverage</h4>
              <div className="text-sm p-2 rounded-lg">
                {/* <CopyBlock
                  language="java"
                  text={sourceCode || 'Loading source code...'}
                  showLineNumbers={true}
                  theme={dracula}
                  codeBlock
                /> */}
              </div>
              <p className="mb-6 text-sm  text-red-600">Code Coverage Tidak Terbentuk, karena belum ada test case </p>
            </>
          )}
        </div>
      </div>
    );
  }else if (dataResultTest.totalTestCase == dataResultTest.totalPassTestCase){
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
              <h4 className="text-base font-bold mb-1 text-gray-800">Code Coverage</h4>
              <div className="text-sm p-4 rounded-lg">
                <iframe src={linkReportSourceCoverage} width={1000} height={500}>
                </iframe>
              </div>
            </>
          )}
        </div>
        <div className="mt-2">
              <h4 className="text-base font-bold mb-2 text-gray-800">Legend</h4>
              <div className="flex items-center mb-2">
                <span className="inline-block w-4 h-4 bg-green-500 mr-2"></span>
                <span className="text-sm text-gray-600">: Statement program telah dieksekusi</span>
              </div>
              <div className="flex items-center mb-2">
                <span className="inline-block w-4 h-4 bg-yellow-500 mr-2"></span>
                <span className="text-sm text-gray-600">: Statement program dieksekusi sebagian</span>
              </div>
              <div className="flex items-center">
                <span className="inline-block w-4 h-4 bg-red-500 mr-2"></span>
                <span className="text-sm text-gray-600">: Statement program belum dieksekusi</span>
              </div>
        </div>
      </div>
    );
  }else{
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
              <h4 className="text-base font-bold mb-1 text-gray-800">Code Coverage</h4>
              <div className="text-sm p-2 rounded-lg">
                {/* <CopyBlock
                  language="java"
                  text={sourceCode || 'Loading source code...'}
                  showLineNumbers={true}
                  theme={dracula}
                  codeBlock
                /> */}
              </div>
              <p className="mb-6 text-sm  text-red-600">Code Coverage Gagal Terbentuk, karena terdapat test case dengan status Fail</p>
            </>
          )}
        </div>
      </div>
    );
  }
  
};

export default ModuleCoverage;
