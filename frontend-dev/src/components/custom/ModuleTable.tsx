import { FaEdit, FaTrash } from "react-icons/fa";

// Define the Module interface directly here
interface Module {
  id: string;
  name: string;
  type: string;
  difficulty: number; // 1: Sangat Mudah, 2: Mudah, 3: Sedang, 4: Sulit
}

const getDifficultyString = (difficulty: number): string => {
  switch (difficulty) {
    case 1:
      return "Sangat Mudah";
    case 2:
      return "Mudah";
    case 3:
      return "Sedang";
    case 4:
      return "Sulit";
    default:
      return "";
  }
};

const ModulesTable = ({
  modules,
  onDelete,
  onEdit,
}: {
  modules: Module[];
  onDelete: (module: Module) => void;
  onEdit: (module: Module) => void;
}) => {
  return (
    <table className="min-w-full">
      <thead className="bg-blue-800 text-white text-xs lg:text-sm">
        <tr>
          <th className="py-3 px-2 md:px-6 text-left border-b border-r">Nama Modul</th>
          <th className="py-3 px-2 md:px-6 text-left border-b border-r">Jenis Modul</th>
          <th className="py-3 px-2 md:px-6 text-left border-b border-r">Tingkat Kesulitan</th>
          <th className="py-3 px-2 md:px-6 text-left border-b">Action</th>
        </tr>
      </thead>
      <tbody className="text-xs lg:text-sm">
        {modules.map((module, index) => (
          <tr key={module.id} className={`border-b ${index % 2 === 0 ? "bg-white" : "bg-gray-50"}`}>
            <td className="py-3 px-2 md:px-6 border-r">{module.name}</td>
            <td className="py-3 px-2 md:px-6 border-r">{module.type}</td>
            <td className="py-3 px-2 md:px-6 border-r">
              <span
                className={`px-2 py-1 rounded ${
                  module.difficulty === 1
                    ? "bg-blue-100 text-blue-600"
                    : module.difficulty === 2
                    ? "bg-green-100 text-green-600"
                    : module.difficulty === 3
                    ? "bg-yellow-100 text-yellow-600"
                    : "bg-red-100 text-red-600"
                }`}
              >
                {getDifficultyString(module.difficulty)}
              </span>
            </td>
            <td className="py-3 px-2 md:px-6 flex items-center space-x-2">
              <FaEdit className="cursor-pointer text-blue-500" onClick={() => onEdit(module)} />
              <FaTrash className="cursor-pointer text-red-500" onClick={() => onDelete(module)} />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default ModulesTable;
