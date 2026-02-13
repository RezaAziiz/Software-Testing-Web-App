import AddModuleForm from "@/components/custom/AddModuleForm";
import LayoutForm from "./LayoutForm";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ClipLoader } from "react-spinners";

const ModuleTestPage = () => {
    const navigate = useNavigate();
    const apiUrl = import.meta.env.VITE_API_URL;
    let apiKey = import.meta.env.VITE_API_KEY;
    // const modulId = import.meta.env.VITE_MODULE_ID;
    const sessionData = localStorage.getItem('session')
    let session = null
    if (sessionData != null){
        session = JSON.parse(sessionData);
        apiKey = session.token
    }

    const queryParameters = new URLSearchParams(window.location.search)
    const modulId = queryParameters.get("idModul")

    const LoadingOverlay: React.FC = () => (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white p-4 rounded shadow-lg flex items-center">
            <ClipLoader size={35} color={"#123abc"} loading={true} />
            <span className="ml-2">Saving Data...</span>
          </div>
        </div>
      );
    const [isLoading, setIsLoading] = useState(false); // Add loading state
    const [infoMessage, setInfoMessage] = useState<string | null>(null);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const [screenName, setScreenName] = useState("Tambah Modul Program")
    const [idModul, setIdModul] = useState("0")
    const handleAddModule = (module: any, mode: string, fileSourceCode: any) => {
        addDataModul(module, fileSourceCode)
        console.log("New module added:", module);
        console.log("Mode:", mode);

    };
    const handleEditModule = (module: any, idModul: string, fileSourceCode: any) => {
      editDataModul(idModul, module, fileSourceCode)
    };
    const handleCancel = () => {
        navigate('/list-modules');
    };
    const addDataModul = async (module: any, fileSourceCode:any) => {
        try {
            // prepare param
            setIsLoading(true)
            let paramModul =[]
            for (let i=0; i < module.parameters.length; i++){
                let tempRule = JSON.parse(module.parameters[i].validationRule);
                if (tempRule.nama_rule == "range"){
                  tempRule.min_value = module.parameters[i].ruleValue1;
                  tempRule.max_value = module.parameters[i].ruleValue2;
                }else if (tempRule.nama_rule == "enumerasi"){
                  tempRule.value = module.parameters[i].ruleValue1; 
                }else if (tempRule.nama_rule == "countOfLength"){
                  tempRule.min_value = module.parameters[i].ruleValue1;
                  tempRule.max_value = module.parameters[i].ruleValue2;
                }else if (tempRule.nama_rule == "condition"){
                  tempRule.condition = module.parameters[i].ruleValue1;
                  tempRule.value = module.parameters[i].ruleValue2; 
                }
                paramModul.push({
                    param_name: module.parameters[i].paramName,
                    param_type: module.parameters[i].paramType,
                    param_rules: JSON.stringify(tempRule)
                })
            }
            const paramData = {
                nama_modul: module.moduleName,
                deskripsi_modul: module.moduleDescription,
                jenis_modul: module.moduleType,
                jumlah_param: module.paramCount,
                class_name: module.className,
                function_name: module.functionName,
                return_type: module.returnType,
                parameters: paramModul,
                tingkat_kesulitan: module.complexityLevel
              };
              
              
          const response = await fetch(`${apiUrl}/modul/addModul`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${apiKey}`,
            },
            body: JSON.stringify(paramData),
            });
            
          if (!response.ok) {
            if (response.status === 403) {
              throw new Error("Forbidden: Access is denied");
            } else if (response.status === 422) {
              const data = await response.json();
              console.log(data.message);
              setErrorMessage(data.message);
              setTimeout(() => setErrorMessage(null), 2000);
            }  else {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
          }else{
            const data = await response.json();
            console.log(fileSourceCode.name);
            console.log(data.id_modul);
            let dataUpload = new FormData()
            dataUpload.append('source_code', fileSourceCode)
            const responseUpload = await fetch(`${apiUrl}/modul/uploadSourceCode/${data.id_modul}`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${apiKey}`,
                },
                body: dataUpload,
                });
            if (responseUpload.ok) {
                setIsLoading(false) 
                // navigate('/list-modules?message=addSuccess');
                setInfoMessage("Data Modul Saved Success");
                setTimeout(() => setInfoMessage(null), 2000);
                setTimeout(() => navigate('/list-modules'), 2100);
            }else{
                setErrorMessage("Gagal Upload Source Code Data");
                setTimeout(() => setErrorMessage(null), 2000);
            }
          }
          
        } catch (error) {
          console.error("Error fetching module name:", error);
        } finally{
          setIsLoading(false)    
        }
    };
    const editDataModul = async (idModul:string, module: any, fileSourceCode:any) => {
      try {
          // prepare param
          setIsLoading(true)
          let paramModul =[]
          for (let i=0; i < module.parameters.length; i++){
              let tempRule = JSON.parse(module.parameters[i].validationRule);
              if (tempRule.nama_rule == "range"){
                tempRule.min_value = module.parameters[i].ruleValue1;
                tempRule.max_value = module.parameters[i].ruleValue2;
              }else if (tempRule.nama_rule == "enumerasi"){
                tempRule.value = module.parameters[i].ruleValue1; 
              }else if (tempRule.nama_rule == "countOfLength"){
                tempRule.min_value = module.parameters[i].ruleValue1;
                tempRule.max_value = module.parameters[i].ruleValue2;
              }else if (tempRule.nama_rule == "condition"){
                tempRule.condition = module.parameters[i].ruleValue1;
                tempRule.value = module.parameters[i].ruleValue2; 
              }
              paramModul.push({
                  param_name: module.parameters[i].paramName,
                  param_type: module.parameters[i].paramType,
                  param_rules: JSON.stringify(tempRule)
              })
          }
          const paramData = {
              id_modul: idModul,
              nama_modul: module.moduleName,
              deskripsi_modul: module.moduleDescription,
              jenis_modul: module.moduleType,
              jumlah_param: module.paramCount,
              class_name: module.className,
              function_name: module.functionName,
              return_type: module.returnType,
              parameters: paramModul,
              tingkat_kesulitan: module.complexityLevel
            };
            
            
        const response = await fetch(`${apiUrl}/modul/editModul`, {
          method: "PUT",
          headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${apiKey}`,
          },
          body: JSON.stringify(paramData),
          });
          
        if (!response.ok) {
          if (response.status === 403) {
            throw new Error("Forbidden: Access is denied");
          } else {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
        }else{
          await response.json();
          if (fileSourceCode != null){
            let dataUpload = new FormData()
            dataUpload.append('source_code', fileSourceCode)
            const responseUpload = await fetch(`${apiUrl}/modul/uploadSourceCode/${idModul}`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${apiKey}`,
                },
                body: dataUpload,
                });
            if (responseUpload.ok) {
                setIsLoading(false) 
                // navigate('/list-modules?message=addSuccess');
                setInfoMessage("Data Modul Saved Success");
                setTimeout(() => setInfoMessage(null), 2000);
                setTimeout(() => navigate('/list-modules'), 2100);
            }else{
                setErrorMessage("Gagal Upload Source Code Data");
                setTimeout(() => setErrorMessage(null), 2000);
            }
          }else{
            if (response.ok) {
              setIsLoading(false) 
              // navigate('/list-modules?message=addSuccess');
              setInfoMessage("Data Modul Saved Success");
              setTimeout(() => setInfoMessage(null), 2000);
              setTimeout(() => navigate('/list-modules'), 2100);
            }else{
                setErrorMessage("Gagal Edit Data");
                setTimeout(() => setErrorMessage(null), 2000);
            }
          }
        }
        
      } catch (error) {
        console.error("Error fetching module name:", error);
      } finally{
        setIsLoading(false)    
      }
    };
    useEffect(() => {
      if (session != null){
        if (session.login_type != "teacher"){
            navigate("/dashboard-student")
        }else{
          if (modulId !=  null){
            setScreenName("Edit Modul Program");
            setIdModul(modulId);
           }
        }
      }else{
        navigate("/login")
      }
    }, []);

    return (
        <LayoutForm screenName={screenName}>
            <div className="grid grid-cols-1">
            {infoMessage && (
                <div className="p-4 mb-4 text-green-500 bg-green-100 rounded-md">
                {infoMessage}
                </div>
            )}
            {errorMessage && (
                <div className="p-4 mb-4 text-red-500 bg-red-100 rounded-md">
                {errorMessage}
                </div>
            )}
            </div>
            <div className="min-h-screen w-screen flex items-center justify-center bg-gray-100 p-10">
                <AddModuleForm onAddModule={handleAddModule} onEditModule={handleEditModule} onCancel={handleCancel} idModul={idModul} />
            </div>
            {isLoading && <LoadingOverlay />}
        </LayoutForm>
    );
};

export default ModuleTestPage;
