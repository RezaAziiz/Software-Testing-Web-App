import React, { useState, useRef } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { FaUpload, FaCloudUploadAlt, FaTrashAlt } from 'react-icons/fa';
import { Button } from '@/components/ui/button';
import { ClipLoader } from "react-spinners";
import apiClient from "@/lib/apiClient";

interface UploadStudentDataProps {
  isDialogOpen: boolean;
  setIsDialogOpen: (open: boolean) => void;
  setInfoMessage: (msg: string) => void;
  setErrorMessage: (msg: string) => void;
  afterUpload: () => void;
}

const UploadStudentDataForm = ({
  isDialogOpen,
  setIsDialogOpen,
  setInfoMessage,
  setErrorMessage,
  afterUpload
}: UploadStudentDataProps) => {
  const apiUrl = import.meta.env.VITE_API_URL;
  const [file, setFile] = useState<File | null>(null);
  const [fileErrorMessage, setFileErrorMessage] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const LoadingOverlay: React.FC = () => (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white p-4 rounded shadow-lg flex items-center">
        <ClipLoader size={35} color={"#123abc"} loading={true} />
        <span className="ml-2">Upload and Saving Data...</span>
      </div>
    </div>
  );

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files ? event.target.files[0] : null;
    if (selectedFile) {
      if (selectedFile.name.endsWith('.xlsx')) {
        setFile(selectedFile);
        setFileErrorMessage("");
      } else {
        setFile(null);
        setFileErrorMessage("File Harus Format .xlsx");
        setTimeout(() => setFileErrorMessage(""), 3000);
      }
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files ? event.dataTransfer.files[0] : null;
    if (droppedFile) {
      if (droppedFile.name.endsWith('.xlsx')) {
        setFile(droppedFile);
        setFileErrorMessage("");
      } else {
        setFile(null);
        setFileErrorMessage("File Harus Format .xlsx");
        setTimeout(() => setFileErrorMessage(""), 3000);
      }
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const handleRemoveFile = () => {
    setFile(null);
    setFileErrorMessage("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleClose = () => {
    setFile(null);
    setFileErrorMessage("");
    setIsDialogOpen(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleUpload = () => {
    if (!file) {
      setFileErrorMessage("File harus diisi sebelum menyimpan!");
      setTimeout(() => setFileErrorMessage(""), 3000);
      return;
    }
    uploadDataSiswa(file);
  };

  const uploadDataSiswa = async (file: File) => {
    try {
      setIsLoading(true);
      let dataUpload = new FormData();
      dataUpload.append('file', file);
      const responseUpload = await apiClient(`${apiUrl}/student/upload`, {
        method: "POST",
        body: dataUpload,
      });
      if (responseUpload.ok) {
        setIsLoading(false);
        setInfoMessage("Data Saved Success");
        setTimeout(() => setInfoMessage(""), 3000);
      } else {
        const data = await responseUpload.json();
        setErrorMessage(data.message);
        setTimeout(() => setErrorMessage(""), 3000);
      }
    } finally {
      setIsLoading(false);
      handleClose();
      afterUpload();
    }
  };

  return (
    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
      <DialogTrigger asChild>
        <Button
          className="flex items-center justify-center text-sm bg-blue-800 text-white py-2 px-3 md:px-4 lg:px-5 rounded hover:bg-blue-700"
        >
          <FaUpload className="mr-0 md:mr-2" />
          <span className="hidden md:inline">Unggah</span>
        </Button>
      </DialogTrigger>
      <DialogContent className="bg-white p-10 rounded-lg shadow-lg max-w-2xl mx-auto">
        <DialogHeader>
          <DialogTitle className="text-lg text-center font-bold mb-4">File Unggah Data Mahasiswa</DialogTitle>
        </DialogHeader>
        <div 
          className="flex flex-col items-center space-y-4" 
          onDrop={handleDrop} 
          onDragOver={handleDragOver}
        >
          {!file && (
            <div className="w-full border-2 border-dashed border-blue-400 rounded-lg p-8 flex flex-col items-center justify-center text-blue-400">
              <FaCloudUploadAlt size={50} />
              <p className="mt-4">Unggah File atau <span className="text-blue-600 cursor-pointer" onClick={() => fileInputRef.current?.click()}>Jelajahi</span></p>
              <input
                type="file"
                className="hidden"
                ref={fileInputRef}
                onChange={handleFileChange}
              />
            </div>
          )}
          {file && (
            <div className="w-full border-2 border-dashed border-blue-400 rounded-lg p-8 flex flex-col items-center justify-center text-blue-400">
              <div className="flex items-center space-x-4">
                <FaUpload size={50} />
                <div className="text-left">
                  <p>{file.name}</p>
                  <p>{(file.size / 1024).toFixed(2)} KB</p>
                </div>
                <button onClick={handleRemoveFile} className="text-red-500 hover:text-red-700" type="button">
                  <FaTrashAlt size={20} />
                </button>
              </div>
            </div>
          )}
          <p className="text-gray-500 text-sm text-center">
            File yang diunggah harus berekstensi .xls dan maksimal 2 MB
          </p>
          {fileErrorMessage && (
            <div className="p-4 mb-4 text-red-500 bg-red-100 rounded-md w-full">
              {fileErrorMessage}
            </div>
          )}
          <div className="flex justify-end space-x-4 w-full mt-6">
            <Button
              type="button"
              className="bg-transparent border border-blue-800 text-blue-800 rounded-full px-4 py-2 hover:bg-blue-100"
              onClick={handleClose}
            >
              Kembali
            </Button>
            <Button
              type="button"
              className="bg-blue-800 text-white rounded-full px-4 py-2 hover:bg-blue-700"
              onClick={handleUpload}
            >
              Simpan
            </Button>
          </div>
        </div>
        {isLoading && <LoadingOverlay />}
      </DialogContent>
    </Dialog>
  );
};

export default UploadStudentDataForm;
