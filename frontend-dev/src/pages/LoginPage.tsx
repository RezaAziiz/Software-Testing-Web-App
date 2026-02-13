import React, { useState } from "react";
import { FaEyeSlash, FaEye, FaPhoneAlt } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import logo_polban from "../assets/logo/polban.png";
import logo_login from "../assets/logo/login.png";
import logo_default from "../assets/logo/default.png";


const LoginPage = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({ username: "", password: "" });
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();

  const apiUrl = import.meta.env.VITE_API_URL;

  const login =  async (username:string, password:string) => {
    const dataLogin = {
      nis_or_nip: username,
      password: password
    };
    try {
        const response = await fetch(`${apiUrl}/login`, {
          method: "POST",
          headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
          },
          body: JSON.stringify(dataLogin),
        });

        let result = await response.json();
        result.status = response.status
        return result
      } catch (error) {
        console.error("login:", error);
      }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    let formIsValid = true;
    let errors = { username: "", password: "" };

    if (!username) {
      errors.username = "Username harus diisi";
      formIsValid = false;
    }

    if (!password) {
      errors.password = "Password harus diisi";
      formIsValid = false;
    }

    if (formIsValid) {
      // call api auth
      let result_login = await login(username, password);
      console.log(result_login)
      if (result_login.status == 200){
        localStorage.setItem('session',JSON.stringify(result_login.data));
        console.log(result_login.data.login_type)
        if (result_login.data.login_type == 'student'){
          navigate("/dashboard-student")
        }else{
          navigate("/dashboard-teacher")
        }
        
      } else if (result_login.status === 400) {
        if (result_login.message.includes("NIP")) {
          errors.username = "Username tidak sesuai! Masukkan NIM atau NIP!";
        }
        if (result_login.message.includes("password")) {
          errors.password = "Password yang dimasukkan tidak sesuai!";
        }
        formIsValid = false;
      }
    

      // // Check if the provided username and password match the hardcoded credentials
      // if (username === "07501030" && password === "admin123!!") {
      //   console.log("Login successful");
      //   // Navigate to CreateTestCasePage
      //   navigate("/");
      // } else if (username === "KO067N" && password === "admin123!!") {
      //   console.log("Login successful");
      //   // Navigate to CreateTestCasePage
      //   navigate("/");
      // } else {
      //   if (username !== "07501030" && username !== "KO067N") {
      //     errors.username = "Username tidak valid";
      //   }
      //   if (password !== "admin123!!") {
      //     errors.password = "Password tidak valid";
      //   }
      //   formIsValid = false;
      // }
    }

    setErrors(errors);
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const handleForgotPassword = () => {
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
  };

  return (
    <div className="min-h-screen w-screen flex flex-col md:flex-row overflow-hidden">
      <div className="w-full md:w-1/2 bg-white text-black p-8 flex flex-col justify-start items-center">
        <div className="flex items-center mb-4">
          <img
            src={logo_polban}
            alt="Logo"
            className="w-28 mr-2"
          />
          <img
            src={logo_default}
            alt="Logo"
            className="w-24 mr-2"
          />
        </div>
        <h2 className="text-2xl font-bold mb-6">Selamat Datang Kembali</h2>
        <h3 className="text-xl font-medium text-gray-700 mb-6">
          Harap Masuk ke Akun Anda
        </h3>
        <form className="w-full" onSubmit={handleSubmit}>
          <div className="mb-4">
            <label
              className="block text-gray-700 text-sm font-bold mb-2"
              htmlFor="username"
            >
              Username
            </label>
            <input
              className={`w-full px-3 py-2 border rounded-md text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-400 ${
                errors.username ? "border-red-500" : ""
              }`}
              id="username"
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => {
                setUsername(e.target.value);
                if (errors.username) setErrors({ ...errors, username: "" });
              }}
            />
            {errors.username && (
              <p className="text-red-500 text-xs italic mt-2">
                {errors.username}
              </p>
            )}
          </div>
          <div className="mb-4 relative">
            <label
              className="block text-gray-700 text-sm font-bold mb-2"
              htmlFor="password"
            >
              Password
            </label>
            <div className="relative">
              <input
                className={`w-full px-3 py-2 border rounded-md text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-400 ${
                  errors.password ? "border-red-500" : ""
                }`}
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="Password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (errors.password) setErrors({ ...errors, password: "" });
                }}
              />
              <button
                type="button"
                className="absolute right-2 top-1/2 bg-white transform -translate-y-1/2 text-gray-500 focus:outline-none"
                onClick={togglePasswordVisibility}
              >
                {showPassword ? <FaEyeSlash /> : <FaEye />}
              </button>
            </div>
            {errors.password && (
              <p className="text-red-500 text-xs italic mt-2">
                {errors.password}
              </p>
            )}
          </div>
          <div className="flex items-center justify-between mb-4">
            <label className="inline-flex items-center">
              <input
                type="checkbox"
                className="form-checkbox h-4 w-4 text-indigo-600"
              />
              <span className="ml-2 text-gray-700 text-sm">Remember Me</span>
            </label>
            <a
              href="#"
              className="text-sm text-blue-600 hover:text-blue-800"
              onClick={handleForgotPassword}
            >
              Forgot Password?
            </a>
          </div>
          <button
            type="submit"
            className="w-full bg-blue-800 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:ring-2 focus:ring-indigo-400"
          >
            Login
          </button>
          <p className="mt-4 text-sm text-gray-600">
            * Gunakan NIM atau NIP untuk masuk ke dalam sini
          </p>
        </form>
      </div>
      <div className="hidden md:flex md:w-1/2 bg-blue-800 text-white p-8 items-center justify-center">
        <div className="flex flex-col items-center justify-center">
          <h3 className="text-3xl font-bold mb-2 text-center">
            Test Flow Kit Learning
          </h3>
          <p className="mb-4 text-xl mt-4 text-center">
            Anda Bisa Belajar Banyak Hal Tentang Pembuatan Test Case dengan Path
            Testing
          </p>
          <img
            src={logo_login}
            alt="Illustration"
            className="w-auto max-h-96"
          />
        </div>
      </div>
      {/* Modal */}
      {showModal && (
        <>
          <div className="fixed inset-0 bg-black bg-opacity-50 z-10"></div>
          <div className="fixed z-20 inset-0 overflow-y-auto">
            <div className="flex items-center justify-center min-h-screen">
              <div className="bg-white rounded-lg shadow-lg p-6 max-w-sm mx-auto">
                <h2 className="text-xl font-bold mb-4 text-center">Forgot your password?</h2>
                <p className="text-gray-800 mb-4 text-center">
                  Silakan hubungi administrator untuk melakukan perubahan password
                </p>
                <div className="flex items-center justify-center mb-4">
                  <FaPhoneAlt className="mr-2" />
                  <span className="text-lg font-semibold">088776654321</span>
                </div>
                <div className="flex justify-center">
                  <button
                    className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                    onClick={closeModal}
                  >
                    Ok
                  </button>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default LoginPage;
