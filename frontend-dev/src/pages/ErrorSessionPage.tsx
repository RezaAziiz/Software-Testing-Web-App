//import React from 'react';
import { useNavigate } from 'react-router-dom';
import logo_polban from "../assets/logo/polban.png";
import logo_error from "../assets/logo/error.png";
const ErrorSessionPage = () => {
  const navigate = useNavigate();

  const handleLoginClick = () => {
    navigate('/login');
  };


  return (
    <div className="min-h-screen w-screen bg-red-700 text-white flex flex-col">
      <header className="flex items-center w-full p-5">
        {/* Logo */}
        <img
          // src="./src/assets/logo/polban.png"
          src={logo_polban}
          alt="Polban Logo"
          className="w-20 h-20 mr-4"
        />
        <div className="text-2xl font-bold">Coverage Test</div>
      </header>
      <main className="flex flex-grow w-full px-10">
        <div className="flex flex-[2] flex-col items-start justify-start mt-8">
          <h1 className="text-4xl font-bold mb-4">Sesi Anda Telah Habis</h1>
          <p className="mb-6">Silahkan Login Kembali Untuk Mengakses Website Ini</p>
          <button
            onClick={handleLoginClick}
            className="bg-white text-bold text-red-700 px-4 py-2 rounded-20"
          >
            LOGIN
          </button>
        </div>
        <div className="flex flex-[3] justify-center items-start">
          <img
            src={logo_error}
            alt="Illustration"
            style={{ width: '450px', height: 'auto' }}
          />
        </div>
      </main>
    </div>
  );
};

export default ErrorSessionPage;
