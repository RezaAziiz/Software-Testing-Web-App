import React from 'react';
// import { FaSortUp, FaSortDown } from 'react-icons/fa';

interface Student {
  no: number;
  nim: string;
  nama: string;
  score: Score[];
}

interface Score {
  score: number;
}

interface Topik {
  namaTopik: string;
}

interface ProgressStudentTableProps {
  students: Student[];
  topiks: Topik[];
  onSort: (column: 'poin' | 'modul') => void;
  sortColumn?: 'poin' | 'modul';
  sortDirection?: 'asc' | 'desc';
}

// const ProgressStudentTable: React.FC<ProgressStudentTableProps> = ({ students, topiks,  onSort, sortColumn, sortDirection }) => {
const ProgressStudentTable: React.FC<ProgressStudentTableProps> = ({ students, topiks }) => {
  //   const renderSortIcon = (column: 'poin' | 'modul') => {
  //   if (sortColumn === column) {
  //     return sortDirection === 'asc' ? <FaSortUp /> : <FaSortDown />;
  //   }
  //   return (
  //     <span className="text-gray-400 flex flex-col">
  //       <FaSortUp />
  //       <FaSortDown />
  //     </span>
  //   );
  // };

  return (
    <div className="bg-white shadow-md rounded-lg overflow-x-auto">
      <table className="min-w-full">
        <thead className="bg-blue-800 text-white text-xs lg:text-sm">
          <tr>
            <th className="py-3 px-2 md:px-6 text-left border-b border-r">No</th>
            <th className="py-3 px-2 md:px-6 text-left border-b border-r">Nim</th>
            <th className="py-3 px-2 md:px-6 text-left border-b border-r">Nama</th>
            {topiks.map((topic) => (
              <th className="py-3 px-2 md:px-6 text-left border-b border-r">{topic.namaTopik}</th>
            ))}  
          </tr>
        </thead>
        <tbody className="text-xs lg:text-sm">
          {students.map((student, index) => (
            <tr key={student.no} className={`border-b ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
              <td className="py-3 px-2 md:px-6 border-r">{student.no}</td>
              <td className="py-3 px-2 md:px-6 border-r">{student.nim}</td>
              <td className="py-3 px-2 md:px-6 border-r">{student.nama}</td>
              {student.score.map((score) => (
                <td className="py-3 px-2 md:px-6 border-r" align='center'>{score.score == -1?'-':score.score}</td>
              ))}  
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ProgressStudentTable;
