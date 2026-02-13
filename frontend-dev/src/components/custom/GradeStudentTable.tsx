import React from 'react';
import { FaSortUp, FaSortDown } from 'react-icons/fa';

interface Student {
  no: number;
  nim: string;
  nama: string;
  poin: number;
  modul: number;
  program: string;
}

interface StudentTableProps {
  students: Student[];
  onSort: (column: 'poin' | 'modul') => void;
  sortColumn?: 'poin' | 'modul';
  sortDirection?: 'asc' | 'desc';
}

const GradeStudentTable: React.FC<StudentTableProps> = ({ students, onSort, sortColumn, sortDirection }) => {
  const renderSortIcon = (column: 'poin' | 'modul') => {
    if (sortColumn === column) {
      return sortDirection === 'asc' ? <FaSortUp /> : <FaSortDown />;
    }
    return (
      <span className="text-gray-400 flex flex-col">
        <FaSortUp />
        <FaSortDown />
      </span>
    );
  };

  return (
    <div className="bg-white shadow-md rounded-lg overflow-x-auto">
      <table className="min-w-full">
        <thead className="bg-blue-800 text-white text-xs lg:text-sm">
          <tr>
            <th className="py-3 px-2 md:px-6 text-left border-b border-r">No</th>
            <th className="py-3 px-2 md:px-6 text-left border-b border-r">Nim</th>
            <th className="py-3 px-2 md:px-6 text-left border-b border-r">Nama</th>
            <th
              className="py-3 px-2 md:px-6 text-left border-b border-r cursor-pointer"
              onClick={() => onSort('poin')}
            >
              <div className="flex items-center">
                Jumlah Poin {renderSortIcon('poin')}
              </div>
            </th>
            <th
              className="py-3 px-2 md:px-6 text-left border-b border-r cursor-pointer"
              onClick={() => onSort('modul')}
            >
              <div className="flex items-center">
                Jumlah Modul Terselesaikan {renderSortIcon('modul')}
              </div>
            </th>
            <th className="py-3 px-2 md:px-6 text-left border-b">Modul Program Terakhir</th>
          </tr>
        </thead>
        <tbody className="text-xs lg:text-sm">
          {students.map((student, index) => (
            <tr key={student.no} className={`border-b ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
              <td className="py-3 px-2 md:px-6 border-r">{student.no}</td>
              <td className="py-3 px-2 md:px-6 border-r">{student.nim}</td>
              <td className="py-3 px-2 md:px-6 border-r">{student.nama}</td>
              <td className="py-3 px-2 md:px-6 border-r">{student.poin}</td>
              <td className="py-3 px-2 md:px-6 border-r">{student.modul}</td>
              <td className="py-3 px-2 md:px-6">{student.program}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default GradeStudentTable;
