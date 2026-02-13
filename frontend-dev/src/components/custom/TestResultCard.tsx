import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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

const TestResultCard: React.FC<TestResultCardProps> = ({
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
      setTestCases(responseData.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    fetchTestCases();
    fetchParameters();
  }, []);
 
  return (
    <Card className="w-full flex flex-col">
    <CardHeader className="flex justify-between">
    {(dataResultTest.totalTestCase > 0 ) && (
      <CardTitle className="text-base module-title m-0">Hasil Pengujian {(dataResultTest.totalPassTestCase/dataResultTest.totalTestCase)*100}% Pass</CardTitle>
    )}
    </CardHeader>
    <CardContent>
      <div className="mb-6 text-sm text-gray-600">
        <p>
          <span className="text-sm">Jumlah Test Case :</span> {dataResultTest.totalTestCase}
        </p>
        <p>
          <span className="text-sm">Jumlah Test Case Pass :</span> {dataResultTest.totalPassTestCase}
        </p>
        <p>
          <span className="text-sm">Jumlah Test Case Not Pass :</span> {dataResultTest.totalFailedTestCase}
        </p>
      </div>

      <Table className="text-sm border-collapse border border-black w-full">
        <TableHeader>
          <TableRow className="bg-blue-800 text-sm text-white py-2 hover:bg-blue-600">
            <TableHead className="border border-black">No</TableHead>
            <TableHead className="border border-black w-52">Objective Testing</TableHead>
            {parameters.map((param) => (
                <TableHead key={`param_${param.ms_id_parameter}`} className="border border-black">
                  {param.ms_nama_parameter}
                </TableHead>
              ))}
            <TableHead className="border border-black w-64">Expected</TableHead>
            <TableHead className="border border-black">Hasil</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {testCases.map((test, index) => (
            <TableRow
              key={test.tr_id_test_case}
              className={`${index % 2 === 0 ? 'bg-blue-100' : 'bg-blue-200'} text-sm leading-tight`}
            >
              <TableCell className="py-2 border border-black">{index + 1}</TableCell>
              <TableCell className="py-2 border border-black w-64 whitespace-nowrap">
                {test.tr_object_pengujian}
              </TableCell>
              {JSON.parse(test.tr_data_test_input).map(
                (paramData: { param_value: string }, i: number) => (
                  <TableCell key={i} className="py-2 border border-black whitespace-nowrap">
                    <div>
                      <span>{paramData.param_value}</span>
                    </div>
                  </TableCell>
                )
              )}
              <TableCell className="py-2 border border-black w-52 whitespace-nowrap">
                {test.tr_expected_result}
              </TableCell>
              <TableCell className="py-2 border border-black w-52 whitespace-nowrap">
                {test.tr_test_result === 'P' ? "Pass" : "Failed"}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </CardContent>
    <CardFooter className="flex justify-between">
      {/* Konten footer card di sini */}
    </CardFooter>
  </Card>
  );
};

export default TestResultCard;
