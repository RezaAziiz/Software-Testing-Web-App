// import { useState } from "react";
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
import { FaEdit, FaTrash } from "react-icons/fa";
import { Button } from "@/components/ui/button";

import "../../index.css";

const AddTestCaseCard = () => {
  // Dummy data untuk tabel (boleh diganti dengan data yang sesuai)
  const testData = [
    {
      id: 1,
      objective:
        "Objective 1 kakakakakak kakakakak lllllllllllllllllllllllllllllllllllll",
      parameters: ["Param 1", "Param 2"],
      expected: "Expected1",
    },
    {
      id: 2,
      objective: "Objective 2",
      parameters: ["Param 1", "Param 2"],
      expected: "Expected2 jkjkjkjk",
    },
  ];

  // State untuk menyimpan ID tes yang sedang diedit atau dihapus
  // const [editingTestId, setEditingTestId] = useState(null);
  // const [deletingTestId, setDeletingTestId] = useState(null);

  // Handle edit test case
  const handleEdit = () => {
    // Lakukan logika atau tindakan sesuai kebutuhan untuk mengedit test case
  };

  // Handle hapus test case
  const handleDelete = () => {
    // Lakukan logika atau tindakan sesuai kebutuhan untuk menghapus test case
  };

  return (
    <Card className="h-[30vh] w-full overflow-auto">
      <CardHeader className="p-6">
        <CardTitle className="module-title ">Test Case</CardTitle>
      </CardHeader>

      <CardContent>
        <Table>
          <TableHeader>
            <TableRow
              className="bg-blue-800 text-white p-0"
              style={{ fontSize: "12px" }}
            >
              <TableHead>No</TableHead>
              <TableHead style={{ width: "250px" }}>
                Objective Testing
              </TableHead>
              {testData.length > 0 &&
                testData[0].parameters.map((param, index) => (
                  <TableHead key={param}>Parameter {index + 1}</TableHead>
                ))}
              <TableHead style={{ width: "250px" }}>Expected</TableHead>
              <TableHead>Aksi</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {testData.map((test, index) => (
              <TableRow
                key={test.id}
                className={index % 2 === 0 ? "bg-blue-100" : "bg-blue-200"}
                style={{ fontSize: "12px" }}
              >
                <TableCell>{test.id}</TableCell>
                <TableCell style={{ width: "250px", whiteSpace: "nowrap" }}>
                  {test.objective}
                </TableCell>
                {test.parameters.map((param, index) => (
                  <TableCell key={index} style={{ whiteSpace: "nowrap" }}>
                    {param}
                  </TableCell>
                ))}
                <TableCell style={{ width: "250px", whiteSpace: "nowrap" }}>
                  {test.expected}
                </TableCell>
                <TableCell className="flex items-center space-x-2">
                  <Button
                    onClick={() => handleEdit()}
                    className="text-blue-500 p-0"
                    style={{ fontSize: "12px" }}
                  >
                    <FaEdit />
                  </Button>
                  <Button
                    onClick={() => handleDelete()}
                    className="text-red-500 p-0"
                    style={{ fontSize: "12px" }}
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
    </Card>
  );
};

export default AddTestCaseCard;
