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

const ModuleList = () => {
  const testData = [
    {
        id: 1,
        moduleName: "Login Page",
        difficulty: "Beginner",
        moduleType: "UI Testing",
    },
    {
        id: 2,
        moduleName: "User Registration",
        difficulty: "Intermediate",
        moduleType: "Functional Testing",
    },
    {
        id: 3,
        moduleName: "Password Reset",
        difficulty: "Advanced",
        moduleType: "Integration Testing",
    },
    {
        id: 4,
        moduleName: "Search Functionality",
        difficulty: "Intermediate",
        moduleType: "UI Testing",
    },
    {
        id: 5,
        moduleName: "Checkout Process",
        difficulty: "Advanced",
        moduleType: "Functional Testing",
    },
    {
        id: 6,
        moduleName: "Payment Gateway Integration",
        difficulty: "Expert",
        moduleType: "Integration Testing",
    },
    {
        id: 7,
        moduleName: "User Profile Management",
        difficulty: "Intermediate",
        moduleType: "Functional Testing",
    },
    {
        id: 8,
        moduleName: "Data Encryption",
        difficulty: "Advanced",
        moduleType: "Security Testing",
    },
    {
        id: 9,
        moduleName: "Product Catalog",
        difficulty: "Intermediate",
        moduleType: "UI Testing",
    },
    {
        id: 10,
        moduleName: "Performance Optimization",
        difficulty: "Expert",
        moduleType: "Load Testing",
    }];

  const handleDelete = () => {};
  const handleEdit = () => {};

  return (
      <Table>
          <TableHeader>
              <TableRow className="bg-blue-800 text-white p-0 hover:text-gray-600">
                  <TableHead style={{ width: "10%" }}>No</TableHead>
                  <TableHead style={{ width: "30%" }}>Nama Modul</TableHead>
                  <TableHead style={{ width: "30%" }}>Tingkat Kesulitan</TableHead>
                  <TableHead style={{ width: "20%" }}>Jenis Modul</TableHead>
                  <TableHead style={{ width: "10%" }}>Aksi</TableHead>
              </TableRow>
          </TableHeader>
          <TableBody>
              {testData.map((module, index) => (
                  <TableRow key={module.id} className={index % 2 === 0 ? "bg-blue-100" : "bg-blue-200"}>
                      <TableCell style={{ width: "10%" }}>{module.id}</TableCell>
                      <TableCell style={{ width: "30%" }} className="whitespace-nowrap">{module.moduleName}</TableCell>
                      <TableCell style={{ width: "20%" }} className="whitespace-nowrap">{module.difficulty}</TableCell>
                      <TableCell style={{ width: "20%" }} className="whitespace-nowrap">{module.moduleType}</TableCell>
                      <TableCell style={{ width: "20%" }} className="flex items-center space-x-2">
                          <Button onClick={() => handleEdit()} className="text-blue-500 p-0 text-sm">
                              <FaEdit />
                          </Button>
                          <Button onClick={() => handleDelete()} className="text-red-500 p-0 text-sm">
                              <FaTrash />
                          </Button>
                      </TableCell>
                  </TableRow>
              ))}
          </TableBody>
      </Table>
  );
};

export default ModuleList;
