import React from 'react';
import { FaEdit, FaTrash } from 'react-icons/fa';

interface Student {
  id: string;
  nim: string;
  name: string;
  class: string;
  program: string;
}

interface StudentTableProps {
  students: Student[];
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

const StudentTable: React.FC<StudentTableProps> = ({ students, onEdit, onDelete }) => {
  return (
    <table className="min-w-full">
      <thead className="bg-blue-800 text-white text-xs lg:text-sm">
        <tr>
        <th className="py-3 px-2 md:px-6 text-left border-b border-r">No</th>
        <th className="py-3 px-2 md:px-6 text-left border-b border-r">Nim</th>
        <th className="py-3 px-2 md:px-6 text-left border-b border-r">Nama</th>
        <th className="py-3 px-2 md:px-6 text-left border-b border-r">Kelas</th>
        <th className="py-3 px-2 md:px-6 text-left border-b border-r">Prodi</th>
        <th className="py-3 px-2 md:px-6 text-left border-b border-r">Action</th>
        </tr>
      </thead>
      <tbody className="text-xs lg:text-sm">
        {students.map((student, index) => (
          <tr key={student.id} className={`border-b ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
             <td className="py-3 px-2 md:px-6 border-r">{index + 1}</td>
             <td className="py-3 px-2 md:px-6 border-r">{student.nim}</td>
             <td className="py-3 px-2 md:px-6 border-r">{student.name}</td>
             <td className="py-3 px-2 md:px-6 border-r">{student.class}</td>
             <td className="py-3 px-2 md:px-6 border-r">{student.program}</td>
             <td className="py-3 px-2 md:px-6 flex items-center space-x-2">
                <FaEdit className="cursor-pointer text-blue-500" onClick={() => onEdit(student.id)} />
                <FaTrash className="cursor-pointer text-red-500" onClick={() => onDelete(student.id)} />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default StudentTable;
