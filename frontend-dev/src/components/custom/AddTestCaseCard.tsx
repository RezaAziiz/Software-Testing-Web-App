import React, { useState, useEffect } from "react";
import TestCaseFormDialog from "./TestCaseFormDialog";
import { useNavigate } from "react-router-dom";
import EditTestCaseFormDialog from "./EditTestCaseFormDialog";
import { ClipLoader } from "react-spinners";
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
import { FaTrash } from "react-icons/fa";
import { Button } from "@/components/ui/button";
import { FaEdit } from "react-icons/fa";

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

const AddTestCaseCard: React.FC = () => {
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [parameters, setParameters] = useState<ParameterModul[]>([]);
  const [isFormDialogOpen, setIsFormDialogOpen] = useState(false);
  const [editingTestId, setEditingTestId] = useState<string>("0");
  const [isEditFormDialogOpen, setIsEditFormDialogOpen] = useState(false);
  const [deletingTestId, setDeletingTestId] = useState<string | null>(null);
  // const [executedTestCase, setExecutedTestCase] = useState(false);
  // const [showMessage, setShowMessage] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [deleteMessage, setDeleteMessage] = useState("");
  // const [minimumCoverage, setMinimumCoverage] = useState<number>(0);
  // const [percentageCoverage, setPercentageCoverage] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState("");
  const [hasUnexecutedChanges, setHasUnexecutedChanges] = useState(false);
  const [isLoading, setIsLoading] = useState(false); // Add loading state
  const [previouslyExecuted, setPreviouslyExecuted] = useState(false);

  type NavigationData = {
    status_eksekusi: boolean;
    tgl_eksekusi: string;
    coverage_score: number;
    minimum_coverage_score: number;
    points: number;
    modul_id: string;
  };

  // const [navigationData, setNavigationData] = useState<NavigationData | null>(
  //   null
  // );
  const navigate = useNavigate();

  const DeleteConfirmationDialog: React.FC<{
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
  }> = ({ isOpen, onClose, onConfirm }) => {
    if (!isOpen) return null;

    return (
      <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
        <div className="bg-white p-4 rounded shadow-lg">
          <h2 className="text-lg">Konfirmasi Penghapusan</h2>
          <p>Apakah kamu yakin akan menghapus test case ini?</p>
          <div className="flex justify-end mt-4">
            <Button onClick={onClose} className="mr-2">
              Cancel
            </Button>
            <Button onClick={onConfirm} className="bg-red-500 text-white">
              Delete
            </Button>
          </div>
        </div>
      </div>
    );
  };

  const LoadingOverlay: React.FC = () => (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white p-4 rounded shadow-lg flex items-center">
        <ClipLoader size={35} color={"#123abc"} loading={true} />
        <span className="ml-2">Loading...</span>
      </div>
    </div>
  );

  const apiUrl = import.meta.env.VITE_API_URL;
  let apiKey = import.meta.env.VITE_API_KEY;
  // const modulId = import.meta.env.VITE_MODULE_ID;
  const sessionData = localStorage.getItem("session");
  let session = null
  if (sessionData == null) {
    navigate("/login");
  } else {
    session = JSON.parse(sessionData);
    apiKey = session.token;
  }
  const queryParameters = new URLSearchParams(window.location.search);
  const modulId = queryParameters.get("topikModulId");

  const fetchParameters = async () => {
    try {
      const response = await fetch(
        `${apiUrl}/modul/detailByIdTopikModul/${modulId}`,
        {
          method: "GET",
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${apiKey}`,
          },
        }
      );

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

  useEffect(() => {
    if (session === null){
       navigate("/login")
    }else if (session.login_type != "student"){
       navigate("/dashboard-teacher")
    }else{
      fetchResultTest();
      fetchParameters();
      fetchTestCases();
  
      // Load previouslyExecuted state from localStorage
      const storedPreviouslyExecuted = localStorage.getItem('previouslyExecuted');
      setPreviouslyExecuted(storedPreviouslyExecuted === 'true');
    }
  }, []);

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

  const fetchResultTest = async () => {
    try {
      const response = await fetch(`${apiUrl}/modul/getResultTest/${modulId}`, {
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
      } else {
        const result = await response.json();
        const dataToPass: NavigationData = {
          status_eksekusi: result.status_eksekusi === "Y",
          tgl_eksekusi: result.executionDate,
          coverage_score: result.coverageScore,
          minimum_coverage_score: result.minimum_coverage_score,
          points: result.point,
          modul_id: result.modul_id,
        };
        console.log(result.coverageScore);
        console.log(result.minimum_coverage_score);
        if (result.status_eksekusi === "Y") {
          if (result.coverageScore < result.minimum_coverage_score) {
            navigate("/fail?topikModulId=" + modulId, { state: dataToPass });
          } else {
            navigate("/pass?topikModulId=" + modulId, { state: dataToPass });
          }
        } else {
          navigate("/fail?topikModulId=" + modulId, { state: dataToPass });
        }
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  // const handleEdit = (id: string) => {
  //   setEditingTestId(id);
  // };

  const handleEdit = (id: string) => {
    setEditingTestId(id);
    setIsEditFormDialogOpen(true);
  };

  const handleDelete = (id: string) => {
    setDeletingTestId(id);
    setIsDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!deletingTestId) return;

    try {
      console.log("Deleting test case with ID:", deletingTestId);

      const response = await fetch(`${apiUrl}/modul/deleteTestCase`, {
        method: "DELETE",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({ id_test_case: deletingTestId }),
      });

      const responseData = await response.json();
      console.log("Response data:", responseData);

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error("Forbidden: Access is denied");
        } else if (response.status === 422) {
          throw new Error(`Unprocessable Entity: ${responseData.detail}`);
        } else {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      }

      setTestCases((prevTestCases) =>
        prevTestCases.filter((test) => test.tr_id_test_case !== deletingTestId)
      );
      setHasUnexecutedChanges(true);
      setDeleteMessage("Test case deleted successfully.");
      const timer = setTimeout(() => {
        setDeleteMessage("");
      }, 5000);
      return () => clearTimeout(timer);
    } catch (error) {
      if (error instanceof Error) {
        console.error("Error deleting test case:", error);
        alert(`Error deleting test case: ${error.message}`);
      } else {
        console.error("Unknown error:", error);
        alert("An unknown error occurred.");
      }
    } finally {
      setIsDeleteDialogOpen(false);
      setDeletingTestId(null);
    }
  };

  const handleExecuteTestCase = async () => {
    if (testCases.length === 0) {
      setErrorMessage("Belum ada test case yang dapat dieksekusi");
      const timer = setTimeout(() => {
        setErrorMessage("");
      }, 5000);
      return () => clearTimeout(timer);
    }

    setIsLoading(true); // Set loading state to true


    try {
      const response = await fetch(`${apiUrl}/modul/run/${modulId}`, {
        method: "POST",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
      });

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error("Forbidden: Access is denied");
        } else {
          setPreviouslyExecuted(true);
          localStorage.setItem('previouslyExecuted', 'true');
     
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
      }


      const result = await response.json();
      console.log("Hasil eksekusi test case:", result);

      setPreviouslyExecuted(true);
      localStorage.setItem('previouslyExecuted', 'true');


      // setPercentageCoverage(result.coverage_score);
      // setMinimumCoverage(result.minimum_coverage_score);

      const dataToPass: NavigationData = {
        status_eksekusi: result.result_test.status_eksekusi,
        tgl_eksekusi: result.result_test.tgl_eksekusi,
        coverage_score: result.coverage_score,
        minimum_coverage_score: result.minimum_coverage_score,
        points: result.point,
        modul_id: result.modul,
      };

      // setNavigationData(dataToPass);
      setHasUnexecutedChanges(false);
      console.log("sebelumnya false");

      if (result.coverage_score < result.minimum_coverage_score) {
        setPreviouslyExecuted(true);
        console.log("previouslyExecuted true");
        navigate("/fail?topikModulId=" + modulId, { state: dataToPass });
      } else {
        setPreviouslyExecuted(true);
        console.log("previouslyExecuted true");
        navigate("/pass?topikModulId=" + modulId, { state: dataToPass });
      }

      // setShowMessage(true);
      // const timer = setTimeout(() => {
      //   setShowMessage(false);
      // }, 5000);
      // return () => clearTimeout(timer);
    } catch (error) {
      console.error("Error executing test case:", error);
    } finally {
      setIsLoading(false); // Set loading state to false
    }
  };

  return (
    <Card className="w-full flex flex-col">
      <CardHeader className="flex justify-between">
        <CardTitle className="text-base module-title m-0">Test Case</CardTitle>
        {hasUnexecutedChanges && previouslyExecuted && (
          <>
            {console.log("executed Changs && previouslyExecuted")}
            <div className="bg-yellow-100 text-yellow-700 p-2 mb-4 m text-sm">
              Test case terbaru belum dieksekusi
            </div>
          </>
        )}
        <div className="flex space-x-2 items-center justify-end">
          <Button
            variant="outline"
            className="bg-white text-blue-800 border-2 border-blue-800 rounded-[10] hover:bg-blue-800 hover:text-white"
            style={{ fontSize: "14px" }}
            onClick={handleExecuteTestCase}
          >
            Eksekusi Test Case
          </Button>
          <TestCaseFormDialog
            isDialogOpen={isFormDialogOpen}
            setIsDialogOpen={setIsFormDialogOpen}
            triggerRefresh={fetchTestCases}
            onSuccess={() => {
              console.log(
                "Test case added, setting hasUnexecutedChanges to true"
              );
              setHasUnexecutedChanges(true);
            }}
          />
          <EditTestCaseFormDialog
                      editingTestId={editingTestId}
                      isEditFormDialogOpen={isEditFormDialogOpen}
                      setIsEditFormDialogOpen={setIsEditFormDialogOpen}
                      triggerRefresh={fetchTestCases}
                    />
        </div>
      </CardHeader>

      {deleteMessage && (
        <div className="bg-blue-800 text-white font-bold p-2 pt-4 mb-4 pb-4 text-sm">
          {deleteMessage}
        </div>
      )}

      {errorMessage && (
        <div className="bg-red-100 text-red-700 p-2 mb-4 text-sm">
          {errorMessage}
        </div>
      )}

      <CardContent className="flex-grow overflow-y-auto">
        <Table className="text-sm border-collapse border border-black w-full">
          <TableHeader>
            <TableRow className="bg-blue-800 text-sm text-white py-2 hover:bg-blue-600">
              <TableHead className="border border-black">No</TableHead>
              <TableHead className="border border-black w-52">
                Objektif Pengujian
              </TableHead>
              {parameters.map((param) => (
                <TableHead
                  key={`param_${param.ms_id_parameter}`}
                  className="border border-black"
                >
                  {param.ms_nama_parameter}
                </TableHead>
              ))}
              <TableHead className="border border-black w-64">
                Ekspektasi
              </TableHead>
              <TableHead className="border border-black">Aksi</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {testCases.map((test, index) => (
              <TableRow
                key={test.tr_id_test_case}
                className={`${
                  index % 2 === 0 ? "bg-blue-100" : "bg-blue-200"
                } text-sm leading-tight`}
              >
                <TableCell className="py-2 border border-black">
                  {index + 1}
                </TableCell>
                <TableCell className="py-2 border border-black w-64 whitespace-nowrap">
                  {test.tr_object_pengujian}
                </TableCell>
                {JSON.parse(test.tr_data_test_input).map(
                  (paramData: { param_value: string }, i: number) => (
                    <TableCell
                      key={i}
                      className="py-2 border border-black whitespace-nowrap"
                    >
                      <div>
                        <span>{paramData.param_value}</span>
                      </div>
                    </TableCell>
                  )
                )}
                <TableCell className="py-2 border border-black w-52 whitespace-nowrap">
                  {test.tr_expected_result}
                </TableCell>
                <TableCell className="py-2 flex items-center justify-between px-2">
                  <Button
                    onClick={() => handleEdit(test.tr_id_test_case)}
                    className="text-blue-500 text-base p-1"
                  >
                    <FaEdit />
                  </Button>
                  <Button
                    onClick={() => handleDelete(test.tr_id_test_case)}
                    className="text-red-500 text-base p-1"
                  >
                    <FaTrash />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>

      <CardFooter className="flex justify-between">
        {/* Konten footer card di sini */}
      </CardFooter>

      <DeleteConfirmationDialog
        isOpen={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        onConfirm={confirmDelete}
      />
      {isLoading && <LoadingOverlay />}
    </Card>
  );
};

export default AddTestCaseCard;
