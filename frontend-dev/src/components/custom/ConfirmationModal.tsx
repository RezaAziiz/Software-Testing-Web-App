import React from 'react';

interface ConfirmationModalProps {
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
  isSidebarOpen?: boolean;
}

const ConfirmationModal: React.FC<ConfirmationModalProps> = ({ message, onConfirm, onCancel,  isSidebarOpen = null }) => {
  return (
    <div
      className={`fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 
        ${isSidebarOpen === true ? "ml-64" : isSidebarOpen === false ? "ml-20" : ""} transition-all duration-300`}
    >
      <div
        className="bg-white p-4 md:p-6 rounded-lg shadow-lg w-11/12 max-w-md md:max-w-lg lg:max-w-xl"
      >
        <h2 className="text-lg font-bold mb-4">Konfirmasi Hapus</h2>
        <p className="mb-4">{message}</p>
        <div className="flex justify-end">
          <button
            className="bg-red-500 text-white px-3 py-2 rounded mr-2 hover:bg-red-600 text-sm md:text-base"
            onClick={onConfirm}
          >
            Hapus
          </button>
          <button
            className="bg-gray-300 text-black px-3 py-2 rounded hover:bg-gray-400 text-sm md:text-base"
            onClick={onCancel}
          >
            Batal
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal;
