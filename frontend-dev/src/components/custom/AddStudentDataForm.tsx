import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { 
    Dialog, 
    DialogContent, 
    DialogHeader, 
    DialogTitle, 
    DialogTrigger 
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { FaPlus } from 'react-icons/fa';
import { 
    Form, 
    FormField, 
    FormItem, 
    FormLabel, 
    FormControl,
} from '@/components/ui/form';
import { useNavigate } from "react-router-dom";

interface FormData {
  nim: string;
  nama: string;
  kelas: string;
  prodi: string;
}

interface AddStudentFormProps {
  isDialogOpen: boolean;
  setIsDialogOpen: (open: boolean) => void;
  idStudent: string;
  setIdStudent: (id: string) => void;
  afterSave: () => void;
}

const AddStudentDataForm = ({
  isDialogOpen,
  setIsDialogOpen,
  idStudent,
  setIdStudent,
  afterSave
}: AddStudentFormProps) => {
    const navigate = useNavigate();
    const apiUrl = import.meta.env.VITE_API_URL;
    let apiKey = import.meta.env.VITE_API_KEY;
    const sessionData = localStorage.getItem('session')
    if (sessionData != null){
        const session = JSON.parse(sessionData);
        apiKey = session.token
    }

    const [showSuccessMessage, setShowSuccessMessage] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const [formTitle, setFormTitle] = useState("Form Tambah Data Mahasiswa");

    const form = useForm<FormData>({
        mode: "onBlur",
    });

    const onSubmit = (data: FormData) => {
        // console.log(data.kelas);
        handleSave(data)
    };
    const handleSave = (data: FormData) => {
        const dataStudent = {
          ms_student_nim: data.nim,
          ms_student_name: data.nama,
          ms_student_kelas: data.kelas,
          ms_student_prodi: data.prodi
        }
        console.log(idStudent)
        if (idStudent != "0"){
          editDataStudent(idStudent, dataStudent)
        }else{
          addDataStudent(dataStudent)
        }
      };
    const addDataStudent = async (student: any) => {
    try {
            // prepare param
            // setIsLoading(true)
            const response = await fetch(`${apiUrl}/student`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${apiKey}`,
            },
            body: JSON.stringify(student),
            });

            const data = await response.json();

            if (!response.ok) {
                if (response.status === 403) {
                    navigate("/error")
                } else if (response.status == 400){
                    setErrorMessage(data.message);
                    setTimeout(() => setErrorMessage(""), 2000);
                } else {
                    setErrorMessage(`HTTP error! status: ${response.status}`);
                    setTimeout(() => setErrorMessage(""), 2000);
                }
            }else{
                setShowSuccessMessage(true);
                setTimeout(() => {
                    setShowSuccessMessage(false);
                    setIsDialogOpen(false);
                }, 2000); // Hide the message after 2 seconds
                afterSave();
            }
            
        } catch (error) {
            console.error("Error fetching module name:", error);
        } 
    };
      const editDataStudent = async (id:string, student: any) => {
        try {
            // prepare param
            // setIsLoading(true)
            const response = await fetch(`${apiUrl}/student/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${apiKey}`,
            },
            body: JSON.stringify(student),
            });

            const data = await response.json();
            
          if (!response.ok) {
            if (response.status === 403) {
              navigate("/error")
            } else if (response.status == 400){
                setErrorMessage(data.message);
                setTimeout(() => setErrorMessage(""), 2000);
            } else {
                setErrorMessage(`HTTP error! status: ${response.status}`);
                setTimeout(() => setErrorMessage(""), 2000);
            }
          }else{
            setShowSuccessMessage(true);
            setTimeout(() => {
                setShowSuccessMessage(false);
                setIsDialogOpen(false);
            }, 2000); // Hide the message after 2 seconds
            afterSave();
          }
        } catch (error) {
          console.error("Error fetching module name:", error);
        }
      };
      const fetchDataStudent = async (id:string) => {
        try {
          const response = await fetch(`${apiUrl}/student/${id}`, {
            method: "GET",
            headers: {
              Accept: "application/json",
              Authorization: `Bearer ${apiKey}`,
            },
          });
    
          if (!response.ok) {
            if (response.status === 403) {
              navigate("/error")
            } else {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
          }
          const data = await response.json();
          form.setValue("nim", data.data.ms_student_nim);
          form.setValue("nama", data.data.ms_student_name);
          form.setValue("kelas", data.data.ms_student_kelas);
          form.setValue("prodi", data.data.ms_student_prodi);
        } catch (error) {
          console.error("Error fetching module name:", error);
        }
      };
    useEffect(() => {
        if (!isDialogOpen) {
            form.reset();
            setShowSuccessMessage(false);
            setErrorMessage("");
        }
        if (idStudent != "0"){
            form.reset();
            fetchDataStudent(idStudent);
            setFormTitle("Form Edit Data Mahasiswa");
        }else{
            form.reset();
            setFormTitle("Form Tambah Data Mahasiswa");
        }
    }, [isDialogOpen, form, idStudent]);

    return (
        <>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogTrigger asChild>
                    <Button
                        className="flex items-center justify-center text-sm bg-blue-800 text-white py-2 px-3 md:px-4 lg:px-5 rounded hover:bg-blue-700"
                        onClick={() =>setIdStudent("0")}
                    >
                       <FaPlus className="mr-0 md:mr-2" />
                       <span className="hidden md:inline">Tambah</span>
                    </Button>
                </DialogTrigger>
                <DialogContent className="bg-white p-10 rounded-lg shadow-lg max-w-2xl mx-auto">
                    <DialogHeader>
                        <DialogTitle className="text-lg text-center font-bold mb-4">{formTitle}</DialogTitle>
                        <Form {...form}>
                            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                                <FormField
                                    control={form.control}
                                    name="nim"
                                    rules={{
                                        required: "NIM harus diisi!",
                                        pattern: {
                                            value: /^[0-9]{9}$/,
                                            message: "Format NIM tidak sesuai!"
                                        }
                                    }}
                                    render={({ field, fieldState: { error } }) => (
                                        <FormItem>
                                            <div className="flex items-center">
                                                <FormLabel className="w-1/6 flex items-center space-x-2">
                                                    <span>Nim</span> 
                                                    <span className="text-red-500">*</span>
                                                    <span>:</span>
                                                </FormLabel>
                                                <FormControl>
                                                    <Input {...field} className="mt-1 block w-full rounded border-gray-300 bg-gray-50 shadow-sm" />
                                                </FormControl>
                                            </div>
                                            {error && (
                                                <p className="text-red-600 pl-20 text-sm mt-1">
                                                    {error.message}
                                                </p>
                                            )}
                                        </FormItem>
                                    )}
                                />
                                <FormField
                                    control={form.control}
                                    name="nama"
                                    rules={{
                                        required: "Nama harus diisi!",
                                        pattern: {
                                            value: /^[a-zA-Z\s]{1,50}$/,
                                            message: "Nama tidak sesuai!"
                                        }
                                    }}
                                    render={({ field, fieldState: { error } }) => (
                                        <FormItem>
                                            <div className="flex items-center">
                                                <FormLabel className="w-1/6 flex items-center space-x-2">
                                                    <span>Nama</span> 
                                                    <span className="text-red-500">*</span>
                                                    <span>:</span>
                                                </FormLabel>
                                                <FormControl>
                                                    <Input {...field} className="mt-1 block w-full rounded border-gray-300 bg-gray-50 shadow-sm" />
                                                </FormControl>
                                            </div>
                                            {error && (
                                                <p className="text-red-600 pl-20 text-sm mt-1">
                                                    {error.message}
                                                </p>
                                            )}
                                        </FormItem>
                                    )}
                                />
                                <FormField
                                    control={form.control}
                                    name="kelas"
                                    rules={{
                                        required: "Kelas harus diisi!",
                                        pattern: {
                                            value: /^[A-Z]$/,
                                            message: "Kelas tidak sesuai!"
                                        }
                                    }}
                                    render={({ field, fieldState: { error } }) => (
                                        <FormItem>
                                            <div className='flex items-center'>
                                                <FormLabel className="w-1/6 flex items-center space-x-2">
                                                    <span>Kelas</span> 
                                                    <span className="text-red-500">*</span>
                                                    <span>:</span>
                                                </FormLabel>
                                                <FormControl>
                                                    <Input {...field} className="mt-1 block w-full rounded border-gray-300 bg-gray-50 shadow-sm" />
                                                </FormControl>
                                            </div>
                                            {error && (
                                                <p className="text-red-600 pl-20 text-sm mt-1">
                                                    {error.message}
                                                </p>
                                            )}
                                        </FormItem>
                                    )}
                                />
                                <FormField
                                    control={form.control}
                                    name="prodi"
                                    rules={{ required: "Prodi harus diisi!" }}
                                    render={({ field, fieldState: { error } }) => (
                                        <FormItem>
                                            <div className='flex items-center'>
                                                <FormLabel className="w-1/6 flex items-center space-x-2">
                                                    <span>Prodi</span> 
                                                    <span className="text-red-500">*</span>
                                                    <span>:</span>
                                                </FormLabel>
                                                <FormControl>
                                                    <Input {...field} className="mt-1 block w-full rounded border-gray-300 bg-gray-50 shadow-sm" />
                                                </FormControl>
                                            </div>
                                            {error && (
                                                <p className="text-red-600 pl-20 text-sm mt-1">
                                                    {error.message}
                                                </p>
                                            )}
                                        </FormItem>
                                    )}
                                />
                                {errorMessage && (
                                    <div className="p-4 mb-4 text-red-500 bg-red-100 rounded-md">
                                    {errorMessage}
                                    </div>
                                )}
                                <div className="flex justify-end gap-4">
                                    <Button
                                        type="button"
                                        className="bg-transparent border border-blue-800 text-blue-800 rounded-full px-4 py-2 hover:bg-blue-100"
                                        onClick={() => setIsDialogOpen(false)}
                                    >
                                        Kembali
                                    </Button>
                                    <Button
                                        type="submit"
                                        className="bg-blue-800 text-white rounded-full px-4 py-2 hover:bg-blue-700"
                                    >
                                        Simpan
                                    </Button>
                                </div>
                            </form>
                        </Form>
                    </DialogHeader>
                    {showSuccessMessage && (
                        <div className="absolute inset-x-0 top-0 flex items-center justify-center h-full bg-black bg-opacity-30">
                            <div className="bg-blue-800 p-4 rounded-lg shadow-lg">
                                <p className="text-white font-bold">
                                    Data Mahasiswa Berhasil Disimpan!
                                </p>
                            </div>
                        </div>
                    )}
                </DialogContent>
            </Dialog>
        </>
    );
};

export default AddStudentDataForm;
