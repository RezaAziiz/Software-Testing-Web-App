import React, { useState, useEffect } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";


import "../../index.css";

interface ParameterModul {
  ms_id_parameter: string;
  ms_id_modul: string;
  ms_nama_parameter: string;
  ms_tipe_data: string;
  ms_rules: string;
  createdby: string;
  created: string;
  updatedby: string;
  updated: string;
}

interface TestCase {
  tr_id_test_case: string;
  tr_id_modul: string;
  tr_student_id: string;
  tr_no: number;
  tr_object_pengujian: string;
  tr_data_test_input: string;
  tr_expected_result: string;
  tr_test_result: string | null;
  createdby: string;
  created: string;
  updatedby: string;
  updated: string;
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
type TestResultCardProps = {
  dataResultTest: DataResultTest;
};

const TestResultCard: React.FC<TestResultCardProps> = () => {
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
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [parameters, setParameters] = useState<ParameterModul[]>([]);
  const fetchParameters = async () => {
    try {
      const response = await fetch(`${apiUrl}/modul/detailByIdTopikModul/${modulId}`, {
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

      const responseData: {
        data: { data_parameter_modul: ParameterModul[] };
      } = await response.json();
      setParameters(responseData.data.data_parameter_modul);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const fetchTestCases = async () => {
    try {
      const response = await fetch(`${apiUrl}/modul/TestCase/${modulId}`, {
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

      const responseData: { data: TestCase[] } = await response.json();
      const executedTestCases = responseData.data.filter(test => test.tr_test_result !== null);
      setTestCases(executedTestCases);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    fetchTestCases();
    fetchParameters();
  }, []);

  return (
    <div className="w-full flex flex-col">
      <p className="text-sm text-slate-500 mb-4">
        Test case pass menunjukkan output sesuai expected, tetapi belum tentu semua jalur kode telah diuji.
      </p>

      <div className="rounded-xl overflow-hidden border border-slate-200">
        <Table className="text-sm w-full">
          <TableHeader>
            <TableRow className="bg-blue-800 text-sm py-2 hover:bg-blue-700">
              <TableHead className="font-semibold text-center w-[5%] text-white">No</TableHead>
              <TableHead className="font-semibold w-[25%] text-white">Objective Testing</TableHead>
              {parameters.map((param) => (
                <TableHead key={`param_${param.ms_id_parameter}`} className="font-semibold text-white">
                  Input {param.ms_nama_parameter}
                </TableHead>
              ))}
              <TableHead className="font-semibold w-[15%] text-white">Expected</TableHead>
              <TableHead className="font-semibold w-[15%] text-center text-white">Hasil</TableHead>
              <TableHead className="font-semibold w-[10%] text-center text-white">Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {testCases.map((test, index) => (
              <TableRow
                key={test.tr_id_test_case}
                className="text-sm leading-tight border-b border-slate-200 hover:bg-slate-50 transition-colors"
              >
                <TableCell className="py-2 text-center">{index + 1}</TableCell>
                <TableCell className="py-2 whitespace-nowrap font-medium text-slate-800">
                  {test.tr_object_pengujian}
                </TableCell>
                {JSON.parse(test.tr_data_test_input).map(
                  (paramData: { param_value: string }, i: number) => (
                    <TableCell key={i} className="py-2 whitespace-nowrap text-slate-600 font-mono text-xs">
                      <div>
                        <span>{paramData.param_value}</span>
                      </div>
                    </TableCell>
                  )
                )}
                <TableCell className="py-2 whitespace-nowrap text-slate-600">
                  {test.tr_expected_result}
                </TableCell>
                <TableCell className="py-2 whitespace-nowrap text-center text-slate-600">
                  {test.tr_test_result === 'P' ? test.tr_expected_result : '—'}
                </TableCell>
                <TableCell className="py-2 whitespace-nowrap text-center font-medium">
                  {test.tr_test_result === 'P' ? (
                    <span className="text-green-600 bg-green-100 px-2 py-1 rounded-md text-xs font-semibold">Pass</span>
                  ) : (
                    <span className="text-red-600 bg-red-100 px-2 py-1 rounded-md text-xs font-semibold">Failed</span>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};

export default TestResultCard;
