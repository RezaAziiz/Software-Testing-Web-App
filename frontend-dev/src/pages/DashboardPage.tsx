import React, { useState, useEffect } from "react";
import Sidebar from "../components/custom/Sidebar";
import "../index.css";
import { useNavigate } from "react-router-dom";

const DashboardPage: React.FC = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const navigate = useNavigate();
  // Dummy account
  let accountName = "Asri Maspupah";
  const sessionData = localStorage.getItem("session");
  let session = null;
  if (sessionData != null) {
    session = JSON.parse(sessionData);
    accountName = session.name;
  }
  useEffect(() => {
    if (session != null) {
      if (session.login_type !== "teacher") {
        navigate("/dashboard-student");
      }
    } else {
      navigate("/login");
    }
  }, [sessionData]);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  useEffect(() => {
    const mediaQuery = window.matchMedia("(min-width: 768px)");
    const handleMediaQueryChange = (event: MediaQueryListEvent) => {
      setIsSidebarOpen(event.matches);
    };

    setIsSidebarOpen(mediaQuery.matches);

    mediaQuery.addEventListener("change", handleMediaQueryChange);
    return () => {
      mediaQuery.removeEventListener("change", handleMediaQueryChange);
    };
  }, []);


  return (
    <div className="flex h-screen">
      <Sidebar isOpen={isSidebarOpen} toggleSidebar={toggleSidebar} />
      <div
        className={`flex-1 transition-all duration-300 flex items-center justify-center ${
          isSidebarOpen ? "ml-64 lg:ml-64" : "ml-10 lg:ml-20"
        }`}
      >
        <h1
          className={`ml-10 text-3xl md:text-5xl lg:text-7xl font-bold text-blue-800 justify-center animate-fade-in ${
            isSidebarOpen ? "hidden md:block" : "ml-20"
          }`}
        >
          Selamat Datang <br />
          {accountName}
        </h1>
      </div>
    </div>
  );
};

export default DashboardPage;
