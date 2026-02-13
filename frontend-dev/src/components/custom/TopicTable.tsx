import React from 'react';
import { FaEdit, FaTrash, FaCloudUploadAlt, FaCloudDownloadAlt, FaSortUp, FaSortDown } from 'react-icons/fa';

interface Topic {
  id: string;
  name: string;
  description: string;
  moduleCount: number;
  status: 'P' | 'D';
  studentAccess: number | string;
}

interface TopicTableProps {
  topics: Topic[];
  orderBy: string;
  order: 'asc' | 'desc';
  onSort: (property: string) => void;
  onTogglePublish: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit: (id: string) => void;
}

const getStatusStyle = (status: 'P' | 'D'): string => {
  switch (status) {
    case 'P':
      return 'bg-green-100 text-green-600';
    case 'D':
      return 'bg-yellow-100 text-yellow-600';
    default:
      return '';
  }
};

const getStatusLabel = (status: 'P' | 'D'): string => {
  switch (status) {
    case 'P':
      return 'Published';
    case 'D':
      return 'Draft';
    default:
      return '';
  }
};

// Fungsi untuk memformat tampilan jumlah mahasiswa
const formatStudentAccess = (access: number | string) => {
  return access === 0 ? '-' : access;
};

const TopicTable: React.FC<TopicTableProps> = ({ topics, orderBy, order, onSort, onTogglePublish, onDelete, onEdit }) => {
  return (
    <table className="min-w-full">
      <thead className="bg-blue-800 text-white text-xs lg:text-sm">
        <tr>
          <th className="py-3 px-2 md:px-6 text-left border-b border-r">Nama Topik</th>
          <th className="py-3 px-2 md:px-6 text-left border-b border-r">Deskripsi</th>
          <th className="py-3 px-2 md:px-6 text-left border-b border-r cursor-pointer" onClick={() => onSort('jml_modul')}>
            <div className="flex items-center">
              Jumlah Modul Program
              {orderBy === 'jml_modul' ? (
                order === 'asc' ? <FaSortUp className="ml-2 text-white" /> : <FaSortDown className="ml-2 text-white" />
              ) : (
                <FaSortDown className="ml-2 text-white opacity-50" />
              )}
            </div>
          </th>
          <th className="py-3 px-6 text-left border-b border-r">Status Tayang</th>
          <th className="py-3 px-6 text-left border-b border-r cursor-pointer" onClick={() => onSort('jml_student')}>
            <div className="flex items-center">
              Jumlah Mahasiswa Mengakses
              {orderBy === 'jml_student' ? (
                order === 'asc' ? <FaSortUp className="ml-2 text-white" /> : <FaSortDown className="ml-2 text-white" />
              ) : (
                <FaSortDown className="ml-2 text-white opacity-50" />
              )}
            </div>
          </th>
          <th className="py-3 px-6 text-left border-b">Action</th>
        </tr>
      </thead>
      <tbody className="text-xs lg:text-sm">
        {topics.map((topic, index) => (
          <tr key={topic.id} className={`border-b ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
            <td className="py-3 px-2 md:px-6 border-r">{topic.name}</td>
            <td className="py-3 px-2 md:px-6 border-r">{topic.description}</td>
            <td className="py-3 px-2 md:px-6 border-r">{topic.moduleCount}</td>
            <td className="py-3 px-2 md:px-6 border-r">
              <span className={`px-2 py-1 rounded ${getStatusStyle(topic.status)}`}>{getStatusLabel(topic.status)}</span>
            </td>
            <td className="py-3 px-6 border-r">{formatStudentAccess(topic.studentAccess)}</td>
            <td className="py-3 px-6 flex items-center space-x-2">
              <FaEdit className={`cursor-pointer ${topic.status === 'P' ? 'text-gray-300 cursor-not-allowed' : 'text-blue-500'}`} onClick={() => topic.status !== 'P' && onEdit(topic.id)} />
              <FaTrash className={`cursor-pointer ${topic.status === 'P' ? 'text-gray-300 cursor-not-allowed' : 'text-red-500'}`} onClick={() => topic.status !== 'P' && onDelete(topic.id)} />
              {topic.status === 'D' ? (
                <FaCloudUploadAlt className="cursor-pointer text-green-500" onClick={() => onTogglePublish(topic.id)} />
              ) : topic.status === 'P' && topic.studentAccess === 0 ? (
                <FaCloudDownloadAlt className="cursor-pointer text-gray-500" onClick={() => onTogglePublish(topic.id)} />
              ) : (
                <FaCloudDownloadAlt className="cursor-not-allowed text-gray-300" />
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default TopicTable;
