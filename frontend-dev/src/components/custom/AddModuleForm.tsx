import React, {useEffect, useState} from 'react';
import { useForm, useFieldArray } from "react-hook-form";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormDescription,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useNavigate } from "react-router-dom";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { UploadCloud, FileCode, AlertTriangle, Loader2 } from "lucide-react";

interface AddModuleFormProps {
  onAddModule: (module: any, mode: string, fileSourceCode:any) => void;
  onEditModule: (module: any, idModul: string, fileSourceCode:any) => void;
  onCancel: () => void;
  idModul:string
}
interface ComboData {
  label: string;
  value: string;
}
const AddModuleForm: React.FC<AddModuleFormProps> = ({ onAddModule, onEditModule, onCancel, idModul}) => {
  const navigate = useNavigate();
  const apiUrl = import.meta.env.VITE_API_URL;
  let apiKey = import.meta.env.VITE_API_KEY;
  // const modulId = import.meta.env.VITE_MODULE_ID;
  const sessionData = localStorage.getItem('session')
  if (sessionData != null){
      const session = JSON.parse(sessionData);
      apiKey = session.token
  }
  const defaultCombo = [{value:"pilih", label:"pilih"}];
  const [paramRules, setParamRules] = useState<any[]>([]);
  const [fileSourceCode, setFileSourceCode] = useState(null);
  const [fileErrors, setFileErrors] = useState<string[]>([]);
  const [comboDataType, setComboDataType] = useState<ComboData[]>(defaultCombo);
  const [comboValidationType, setComboValidationType] = useState<ComboData[]>(defaultCombo);
  const [comboModuleType, setComboModuleType] = useState<ComboData[]>(defaultCombo);
  const [comboLevel, setComboLevel] = useState<ComboData[]>(defaultCombo);
  const [comboCondition, setComboCondition] = useState<ComboData[]>(defaultCombo);
  const [defaultValueJenisModul, setDefaultValueJenisModul] = useState('');
  const [defaultValueLevel, setDefaultValueLevel] = useState('');
  const [defaultValueReturnType, setDefaultValueReturnType] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [selectedDataType, setSelectedDataType] = useState('');
  const [fileName, setFileName] = useState('');

  const [parsedMetadata, setParsedMetadata] = useState<any>(null);
  const [parsedMethods, setParsedMethods] = useState<any[]>([]);
  const [selectedMethodName, setSelectedMethodName] = useState<string>('');
  const [isSourceCodeUploaded, setIsSourceCodeUploaded] = useState<boolean>(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);


  // const handleFileChange = (e:any, field:any) => {
  //   field.onChange(e.target.files?.[0]?.name || '')
  //   if (e.target.files != null){
  //     setFileSourceCode(e.target.files[0])
  //   }
  // };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      await parseFileMetadata(file);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      await parseFileMetadata(file);
    }
  };

  const handlingLevelChange = (e:any) =>{
    form.setValue(`complexityLevel`, e);
    setDefaultValueLevel(e);
  }
  const handlingReturnTypeChange = (e:any) =>{
    form.setValue(`returnType`, e);
    setDefaultValueReturnType(e);
  }
  const handlingModulTypeChange = (e:any) =>{
    form.setValue(`moduleType`, e);
    setDefaultValueJenisModul(e);
  }
  const handleDataTypeChange = (e: any, index: number) => {
    form.setValue(`parameters.${index}.paramType`, e);
    setSelectedDataType(e);
    fetchDataComboValidationType(e);
    fetchDataComboConditionType(e);
  };
  const handlingRuleChange = (e:any, index:number) =>{
    form.setValue(`parameters.${index}.validationRule`, e);
    let data = JSON.parse(e);
    let newArr = [...paramRules]
    newArr[index].jmlParam = parseInt(data.jml_param)
    newArr[index].isCondition = data.nama_rule === "condition";
    if (data.nama_rule == "range"){
      newArr[index].nameParam1 = "Min" 
      newArr[index].nameParam2 = "Max"
    }else if (data.nama_rule == "enumerasi"){
      newArr[index].nameParam1 = "Enum" 
    }else if (data.nama_rule == "countOfLength"){
      newArr[index].nameParam1 = "Min" 
      newArr[index].nameParam2 = "Max"
    }else if (data.nama_rule == "condition"){
      newArr[index].nameParam1 = "Condition"
      newArr[index].nameParam2 = "Value" 
    }
    setParamRules(newArr);
  }
  const fetchDataModule = async () => {
        try {
          const response = await fetch(`${apiUrl}/modul/detail/${idModul}`, {
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
          form.setValue("moduleName", data.data.data_modul.ms_nama_modul);
          form.setValue("moduleType", data.data.data_modul.ms_jenis_modul);
          setDefaultValueJenisModul(data.data.data_modul.ms_jenis_modul);
          form.setValue("paramCount", data.data.data_modul.ms_jml_parameter);
          form.setValue("moduleDescription", data.data.data_modul.ms_deskripsi_modul);
          form.setValue("returnType", data.data.data_modul.ms_return_type);
          setDefaultValueReturnType(data.data.data_modul.ms_return_type);
          form.setValue("functionName", data.data.data_modul.ms_function_name);
          form.setValue("className", data.data.data_modul.ms_class_name);
          form.setValue(`complexityLevel`, data.data.data_modul.ms_tingkat_kesulitan);
          setDefaultValueLevel(data.data.data_modul.ms_tingkat_kesulitan);
          form.setValue("sourceCode", data.data.data_modul.ms_source_code);
          let data_params = data.data.data_parameter_modul;
          let tempParamRules = []
          for(let i=0; i<data_params.length; i++){
            tempParamRules.push({jmlParam: 0, nameParam1: "",  nameParam2: ""});
            form.setValue(`parameters.${i}.paramName`, data_params[i].ms_nama_parameter);
            form.setValue(`parameters.${i}.paramType`, data_params[i].ms_tipe_data);
            let dataRule = JSON.parse(data_params[i].ms_rules)
            tempParamRules[i].jmlParam = parseInt(dataRule.jml_param)
            
            if (dataRule.nama_rule == "range"){
              tempParamRules[i].nameParam1 = "Min";
              tempParamRules[i].nameParam2 = "Max";
              form.setValue(`parameters.${i}.ruleValue1`, dataRule.min_value);
              form.setValue(`parameters.${i}.ruleValue2`, dataRule.max_value);
              dataRule.min_value = "";
              dataRule.max_value = "";  
            }else if (dataRule.nama_rule == "enumerasi"){
              tempParamRules[i].nameParam1 = "Enum";
              form.setValue(`parameters.${i}.ruleValue1`, dataRule.value);
              dataRule.value="";
            }else if (dataRule.nama_rule == "countOfLength"){
              tempParamRules[i].nameParam1 = "Min";
              tempParamRules[i].nameParam2 = "Max";
              form.setValue(`parameters.${i}.ruleValue1`, dataRule.min_value);
              form.setValue(`parameters.${i}.ruleValue2`, dataRule.max_value);
              dataRule.min_value = "";
              dataRule.max_value = "";  
            }else if (dataRule.nama_rule == "condition"){
              tempParamRules[i].nameParam1 = "Condition";
              tempParamRules[i].nameParam2 = "Value";
              form.setValue(`parameters.${i}.ruleValue1`, dataRule.condition);
              form.setValue(`parameters.${i}.ruleValue2`, dataRule.value);
              dataRule.value="";
              dataRule.condition="";
            }
            form.setValue(`parameters.${i}.validationRule`, JSON.stringify(dataRule));
          }
          setParamRules(tempParamRules);
          setFileName(data.data.data_modul.ms_source_code);
          if (data.data.data_modul.ms_source_code) {
            setIsSourceCodeUploaded(true);
          }
        } catch (error) {
          console.error("Error fetching module name:", error);
        }
  };

  const fetchDataComboDataType = async () => {
    try {
      const response = await fetch(`${apiUrl}/combo/data_type`, {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
      });

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error("Forbidden: Access is denied");
        } else {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      }
      const data = await response.json();
      setComboDataType(data.data);
     } catch (error) {
      console.error("Error fetching module name:", error);
    }
  };
  const fetchDataComboValidationType = async (dataType: string) => {
    try {
      const response = await fetch(`${apiUrl}/combo/validasi_parameter?data_type=${dataType}`, {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
      });

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error("Forbidden: Access is denied");
        } else {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      }
      const data = await response.json();
      setComboValidationType(data.data);
     } catch (error) {
      console.error("Error fetching module name:", error);
    }
  };
  const fetchDataComboConditionType = async (dataType: string) => {
    try {
      const response = await fetch(`${apiUrl}/combo/condition?data_type=${dataType}`, {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
      });

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error("Forbidden: Access is denied");
        } else {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      }
      const data = await response.json();
      setComboCondition(data.data);
     } catch (error) {
      console.error("Error fetching module name:", error);
    }
  };
  const fetchDataComboModuleType = async () => {
    try {
      const response = await fetch(`${apiUrl}/combo/module_type`, {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
      });

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error("Forbidden: Access is denied");
        } else {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      }
      const data = await response.json();
      setComboModuleType(data.data);
     } catch (error) {
      console.error("Error fetching module name:", error);
    }
  };
  const fetchDataComboLevel = async () => {
    try {
      const response = await fetch(`${apiUrl}/combo/tingkat_kesulitan`, {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
      });

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error("Forbidden: Access is denied");
        } else {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      }
      const data = await response.json();
      setComboLevel(data.data);
     } catch (error) {
      console.error("Error fetching module name:", error);
    }
  };

  const form = useForm({
    mode: "onBlur",
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "parameters",
  });

  const autoFillMetadata = (metadata: any, methodName: string) => {
    if (!metadata) return;
    form.setValue("className", metadata.class_name);
    const method = metadata.methods.find((m: any) => m.method_name === methodName);
    if (!method) return;
    form.setValue("functionName", method.method_name);
    form.setValue("returnType", method.return_type);
    setDefaultValueReturnType(method.return_type);
    const count = method.parameters.length;
    form.setValue("paramCount", count);
    setTimeout(() => {
      method.parameters.forEach((p: any, idx: number) => {
        form.setValue(`parameters.${idx}.paramName`, p.param_name);
        form.setValue(`parameters.${idx}.paramType`, p.param_type);
      });
    }, 50);
  };

  const parseFileMetadata = async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.java')) {
      setModalError("File yang diunggah harus berekstensi .java (tidak mendukung PDF, Word, Excel, Gambar, dll).");
      return;
    }
    setModalLoading(true);
    setModalError(null);
    setFileErrors([]);
    try {
      const formData = new FormData();
      formData.append('source_code', file);
      const response = await fetch(`${apiUrl}/modul/parse-metadata`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiKey}`,
        },
        body: formData,
      });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.message || "Gagal memproses file source code");
      }
      const resData = await response.json();
      setParsedMetadata(resData);
      setParsedMethods(resData.methods || []);
      setIsSourceCodeUploaded(true);
      setFileSourceCode(file as any);
      setFileName(file.name);
      
      if (resData.methods && resData.methods.length > 0) {
        const defaultMethod = resData.methods[0].method_name;
        setSelectedMethodName(defaultMethod);
        
        // Auto fill form
        form.setValue("className", resData.class_name);
        const method = resData.methods.find((m: any) => m.method_name === defaultMethod) || resData.methods[0];
        form.setValue("functionName", method.method_name);
        form.setValue("returnType", method.return_type);
        setDefaultValueReturnType(method.return_type);
        const count = method.parameters.length;
        form.setValue("paramCount", count);
        
        // Auto-fill extracted description!
        if (resData.description) {
          form.setValue("moduleDescription", resData.description);
        }
        
        setTimeout(() => {
          method.parameters.forEach((p: any, idx: number) => {
            form.setValue(`parameters.${idx}.paramName`, p.param_name);
            form.setValue(`parameters.${idx}.paramType`, p.param_type);
          });
        }, 50);
        
        // Set form value for react-hook-form validation
        form.setValue("sourceCode", file.name, { shouldValidate: true });
        
        // Close modal on success!
        setIsUploadModalOpen(false);
      } else {
        throw new Error("Tidak ada method/fungsi publik ditemukan dalam source code.");
      }
    } catch (err: any) {
      console.error(err);
      setFileSourceCode(null);
      setFileErrors([err.message || "Gagal memproses file source code"]);
      form.setValue('sourceCode', '');
      setIsSourceCodeUploaded(false);
      setParsedMetadata(null);
      setParsedMethods([]);
      setSelectedMethodName('');
      setModalError(err.message || "Gagal memproses file source code");
    } finally {
      setModalLoading(false);
    }
  };

  const paramCount = form.watch("paramCount");

  useEffect(() => {
    let temp=[...paramRules]
    if (paramCount > fields.length) {
      for (let i = fields.length; i < paramCount; i++) {
        append({ paramName: "", paramType: "", validationRule: "" });
        temp.push({jmlParam: 0, nameParam1: "",  nameParam2: ""})
      }
    } else if (paramCount < fields.length) {
      for (let i = fields.length; i > paramCount; i--) {
        remove(i - 1);
        temp.slice(0,-1);
      }
    }
    setParamRules(temp)
    fetchDataComboDataType()
    fetchDataComboModuleType()
    fetchDataComboLevel()
    fetchDataComboValidationType(selectedDataType)
    fetchDataComboConditionType(selectedDataType)
  }, [paramCount, fields.length, append, remove]);
  useEffect(() => {
    if (idModul != "0"){  
      setEditMode(true)
      fetchDataModule()
    }
  },[idModul]);

  // Auto open upload modal in Create Mode if no source code is uploaded yet
  useEffect(() => {
    if (!editMode && !isSourceCodeUploaded) {
      setIsUploadModalOpen(true);
    }
  }, [editMode, isSourceCodeUploaded]);
  const onSubmit = (data: any) => {
    let mode = "add";
    if (idModul != "0"){  
      mode = "edit"
      onEditModule(data, idModul, fileSourceCode);
    }else{
      onAddModule(data, mode, fileSourceCode);
    }
  };

  //Combo untuk condition validation sementara
  // const conditionType = [
  //   {
  //     "label": "!=",
  //     "value": "!="
  //   },
  //   {
  //     "label": "<",
  //     "value": "<"
  //   },
  //   {
  //     "label": "<=",
  //     "value": "<="
  //   },
  //   {
  //     "label": "=",
  //     "value": "="
  //   },
  //   {
  //     "label": ">",
  //     "value": ">"
  //   },
  //   {
  //     "label": ">=",
  //     "value": ">="
  //   }
  // ];
  

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 p-4 sm:p-6 md:p-10 w-full mx-auto bg-white shadow-md rounded-md">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-10 pb-10 md:pb-14">
            <div>
                <FormField
                    control={form.control}
                    name="moduleName"
                    rules={{
                      required: "Nama Modul harus diisi!",
                      maxLength: { value: 50, message: "Nama Modul tidak sesuai!" }
                    }}
                    render={({ field, fieldState: { error } }) => (
                        <FormItem>
                            <FormLabel>
                                Nama Modul
                                <span className="text-red-500">*</span>
                            </FormLabel>
                            <FormControl>
                                <Input {...field} className="border rounded p-2 w-full bg-gray-50" />
                            </FormControl>
                            <FormDescription className="text-xs text-gray-500 mt-1">*Nama modul harus unik, belum pernah dibuat sebelumnya</FormDescription>
                            {error && (
                              <p className="text-red-600 text-sm mt-1">
                                {error.message}
                                  </p>
                            )}
                        </FormItem>
                    )}
                />
                <FormField
                    control={form.control}
                    name="moduleType"
                    rules={{ required: "Jenis modul harus dipilih!" }}
                    render={({ field,  fieldState: { error } }) => (
                    <FormItem>
                      <div  className="flex items-center mt-4 w-full">
                        <FormLabel className="w-1/3">Jenis Modul :</FormLabel>
                        <FormControl className="flex-1">
                        <Select onValueChange={(e) => handlingModulTypeChange(e)} defaultValue={field.value} value={defaultValueJenisModul}>
                          <SelectTrigger className="w-full bg-white">
                            <SelectValue placeholder="Pilih" />
                          </SelectTrigger>
                          <SelectContent className="bg-white">
                            <SelectGroup>
                            {comboModuleType.map((dataCombo) => (
                              <SelectItem key={dataCombo.value} value={dataCombo.value}>{dataCombo.label}</SelectItem>
                            ))}
                            </SelectGroup>
                          </SelectContent>
                        </Select>
                        </FormControl>
                        </div>
                        {error && (
                          <p className="text-red-600 text-sm pl-36 mt-1">
                            {error.message}
                          </p>
                        )}
                    </FormItem>
                    )}
                />
                <FormField
                    control={form.control}
                    name="paramCount"
                    rules={{
                      required: "Jumlah Parameter harus diisi!",
                      pattern: { value: /^[0-9]+$/, message: "Jumlah Parameter tidak sesuai!" }
                    }}
                    render={({ field, fieldState: { error } }) => (
                    <FormItem className="flex items-center mt-4">
                        <FormLabel className="w-1/3">
                            Jumlah Parameter 
                            <span className="text-red-500">*</span>
                            :
                         </FormLabel>
                        <FormControl className="flex-1">
                        <div>
                            <Input
                                type="number"
                                {...field}
                                readOnly={isSourceCodeUploaded || editMode}
                                className={`border rounded p-2 w-32 ${(isSourceCodeUploaded || editMode) ? 'bg-gray-100 cursor-not-allowed' : 'bg-gray-50'}`}
                            />
                            <FormDescription className="text-xs text-gray-500 mt-1">*Jumlah parameter minimal 1</FormDescription>
                            {error && (
                              <p className="text-red-600 text-sm mt-1">
                                {error.message}
                              </p>
                            )}
                        </div>
                        </FormControl>
                    </FormItem>
                    )}
                />
            </div>
            <div className="flex flex-col h-full sm:pb-1">
                <FormField
                    control={form.control}
                    name="moduleDescription"
                    rules={{
                      required: "Deskripsi Modul harus diisi!"
                    }}
                    render={({ field, fieldState: { error } }) => (
                        <FormItem className="flex-grow">
                            <FormLabel>Deskripsi Modul</FormLabel>
                            <FormControl className="h-full">
                                <textarea {...field} className="border rounded p-2 w-full h-full bg-gray-50 border-black" />
                            </FormControl>
                            {error && (
                              <p className="text-red-600 text-sm mt-1">
                                {error.message}
                              </p>
                            )}
                        </FormItem>
                    )}
                />
            </div>
        </div>
        <div>
        {fields.map((field, index) => (
          <div key={field.id} className="flex flex-col md:flex-row gap-4 bg-blue-50 rounded p-4">
            <FormField
                control={form.control}
                name={`parameters.${index}.paramName`}
                rules={{
                  required: "Nama Parameter harus diisi!",
                  pattern: {
                    value: /^[a-zA-Z_][a-zA-Z0-9_]*$/,
                    message: "Nama Parameter tidak sesuai!"
                  }
                }}
                render={({ field, fieldState: { error } }) => (
                  <FormItem className="w-full col-span-1">
                    <FormLabel>
                      Nama Parameter
                      <span className="text-red-500">*</span>
                    </FormLabel>
                    <FormControl>
                      <Input 
                        {...field} 
                        readOnly={isSourceCodeUploaded || editMode}
                        className={`border rounded p-2 w-full ${(isSourceCodeUploaded || editMode) ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}`} 
                      />
                    </FormControl>
                    {error && (
                      <p className="text-red-600 text-sm mt-1">
                        {error.message}
                      </p>
                    )}
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name={`parameters.${index}.paramType`}
                rules={{ required: "Tipe data parameter harus dipilih!" }}
                render={({ field, fieldState: { error } }) => (
                  <FormItem className="w-full col-span-1">
                    <FormLabel>
                      Tipe Data
                      <span className="text-red-500">*</span>
                    </FormLabel>
                    <FormControl>
                      {isSourceCodeUploaded || editMode ? (
                        <Input 
                          readOnly 
                          value={field.value} 
                          className="border rounded p-2 w-full bg-gray-100 cursor-not-allowed" 
                        />
                      ) : (
                        <Select onValueChange={(e) => handleDataTypeChange(e, index)} defaultValue={field.value}>
                          <SelectTrigger className="w-full bg-white">
                            <SelectValue placeholder="Pilih" />
                          </SelectTrigger>
                          <SelectContent className="bg-white">
                            <SelectGroup>
                              {comboDataType.map((dataCombo) => (
                                <SelectItem key={dataCombo.value} value={dataCombo.value}>{dataCombo.label}</SelectItem>
                              ))}
                            </SelectGroup>
                          </SelectContent>
                        </Select>
                      )}
                    </FormControl>
                    {error && (
                      <p className="text-red-600 text-sm mt-1">
                        {error.message}
                      </p>
                    )}
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name={`parameters.${index}.validationRule`}
                rules={{ required: "Aturan validasi harus dipilih!" }}
                render={({ field, fieldState: { error } }) => (
                  <FormItem className="w-full col-span-1">
                    <FormLabel>Aturan Validasi</FormLabel>
                    <FormControl>
                      <Select onValueChange={(e) => handlingRuleChange(e, index)} defaultValue={field.value}>
                        <SelectTrigger className="w-full bg-white">
                          <SelectValue placeholder="Pilih" />
                        </SelectTrigger>
                        <SelectContent className="bg-white">
                          <SelectGroup>
                            {comboValidationType.map((dataCombo) => (
                              <SelectItem key={dataCombo.value} value={dataCombo.value}>{dataCombo.label}</SelectItem>
                            ))}
                          </SelectGroup>
                        </SelectContent>
                      </Select>
                    </FormControl>
                    {error && (
                      <p className="text-red-600 text-sm mt-1">
                        {error.message}
                      </p>
                    )}
                  </FormItem>
                )}
              />
              {paramRules[index].jmlParam >= 1 && (
                paramRules[index].isCondition ? (
                  //FormField untuk condition validation
                  <FormField
                    control={form.control}
                    name={`parameters.${index}.ruleValue1`}
                    render={({ field }) => (
                      <FormItem className="w-full col-span-1">
                        <FormLabel>
                          {paramRules[index].nameParam1}
                          <span className="text-red-500">*</span>
                        </FormLabel>
                        <FormControl>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <SelectTrigger className="w-full bg-white">
                              <SelectValue placeholder="Pilih" />
                            </SelectTrigger>
                            <SelectContent className="bg-white">
                              <SelectGroup>
                                {comboCondition.map((dataCombo) => (
                                  <SelectItem value={dataCombo.value}>{dataCombo.label}</SelectItem>
                                ))}
                              </SelectGroup>
                            </SelectContent>
                          </Select>
                        </FormControl>
                      </FormItem>
                    )}
                  />
                ) : (
                  <FormField
                    control={form.control}
                    name={`parameters.${index}.ruleValue1`}
                    render={({ field }) => (
                      <FormItem className="w-full col-span-1">
                        <FormLabel>
                          {paramRules[index].nameParam1}
                          <span className="text-red-500">*</span>
                        </FormLabel>
                        <FormControl>
                          <Input {...field} className="border rounded p-2 w-full bg-white" />
                        </FormControl>
                      </FormItem>
                    )}
                  />
                )
              )}
              {paramRules[index].jmlParam === 2 && (
                <FormField
                  control={form.control}
                  name={`parameters.${index}.ruleValue2`}
                  render={({ field }) => (
                    <FormItem className="w-full col-span-1">
                      <FormLabel>
                        {paramRules[index].nameParam2}
                        <span className="text-red-500">*</span>
                      </FormLabel>
                      <FormControl>
                        <Input {...field} className="border rounded p-2 w-full bg-white" />
                      </FormControl>
                    </FormItem>
                  )}
                />
              )}
            </div>
          ))}
          <FormDescription className="text-xs text-gray-500 mt-2 pl-5">*Urutan parameter dan tipe data harus sama dengan source code</FormDescription>
        </div>
    
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-10 pb-8">
        <div className="flex flex-col space-y-4">
            <FormField
            control={form.control}
            name="returnType"
            rules={{ required: "Tipe data kembalian harus dipilih!" }}
            render={({ field, fieldState: { error } }) => (
                <FormItem>
                <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
                <FormLabel className="w-full sm:w-1/3">
                    Tipe Data Kembalian
                    <span className="text-red-500">*</span>
                    :
                 </FormLabel>
                <FormControl className="w-auto flex-1">
                    {isSourceCodeUploaded || editMode ? (
                      <Input 
                        readOnly 
                        value={field.value || defaultValueReturnType} 
                        className="border rounded p-2 w-32 bg-gray-100 cursor-not-allowed" 
                      />
                    ) : (
                      <Select onValueChange={(e) => handlingReturnTypeChange(e)} defaultValue={field.value} value={defaultValueReturnType}>
                      <SelectTrigger className="w-32 bg-gray-50"> 
                          <SelectValue placeholder="Pilih" />
                      </SelectTrigger>
                      <SelectContent className="bg-white">
                          <SelectGroup>
                          {comboDataType.map((dataCombo) => (
                            <SelectItem key={dataCombo.value} value={dataCombo.value}>{dataCombo.label}</SelectItem>
                          ))}
                          </SelectGroup>
                      </SelectContent>
                      </Select>
                    )}
                </FormControl>
                </div>
                {error && (
                    <p className="text-red-600 text-sm pl-48 mt-1">
                        {error.message}
                    </p>
                  )}
                </FormItem>
            )}
            />
            <FormField
            control={form.control}
            name="sourceCode"
            rules={{
              required: !editMode ? "Source code harus diunggah!" : undefined,
            }}
            render={({ field, fieldState:{error} }) => (
                <FormItem>
                <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
                <FormLabel className="w-full sm:w-1/3 flex items-center gap-1">
                    Source Code
                    {!editMode && (<span className="text-red-500">*</span>)}
                    :
                 </FormLabel>
                <FormControl className="flex-1">
                    <div>
                        {isSourceCodeUploaded && fileName ? (
                          <div className="flex flex-wrap items-center gap-3 p-3 bg-blue-50/50 border border-blue-200 rounded-xl max-w-md">
                            <div className="p-2 rounded-lg bg-blue-100 text-blue-600">
                              <FileCode className="h-5 w-5" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-semibold text-gray-800 truncate">{fileName}</p>
                              <p className="text-xs text-green-600 flex items-center gap-1 mt-0.5">
                                <span className="inline-block w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                                Teranalisis & Siap
                              </p>
                            </div>
                            <Button 
                              type="button" 
                              variant="outline" 
                              size="sm"
                              onClick={() => {
                                setModalError(null);
                                setModalLoading(false);
                                setIsUploadModalOpen(true);
                              }}
                              className="rounded-lg text-xs h-8"
                            >
                              Ganti File
                            </Button>
                          </div>
                        ) : (
                          <Button 
                            type="button" 
                            onClick={() => {
                              setModalError(null);
                              setModalLoading(false);
                              setIsUploadModalOpen(true);
                            }}
                            className="bg-blue-600 text-white rounded-xl hover:bg-blue-700 font-semibold px-4 py-2 flex items-center gap-2"
                          >
                            <UploadCloud className="h-4 w-4" />
                            Unggah Source Code
                          </Button>
                        )}
                        
                        <input type="hidden" name={field.name} value={fileName} />
                    </div>
                </FormControl>
                </div>
                {fileErrors.map((err, idx) => (
                    <p key={idx} className="text-red-600 text-sm pl-48 mt-1">
                      {err}
                    </p>
                  ))}
                  {error && (
                    <p className="text-red-600 text-sm pl-48 mt-1">
                      {error.message}
                    </p>
                  )}
                </FormItem>
            )}
            />
            <FormField
            control={form.control}
            name="complexityLevel"
            rules={{ required: "Tingkat kesulitan harus dipilih!" }}
            render={({ field, fieldState: {error} }) => (
                <FormItem>
                 <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
                 <FormLabel className="w-full sm:w-1/3">
                    Tingkat Kesulitan
                    <span className="text-red-500">*</span>
                    :
                 </FormLabel>
                <FormControl className="flex-1">
                    <Select onValueChange={(e) => handlingLevelChange(e)} defaultValue={field.value} value={defaultValueLevel}>
                    <SelectTrigger className="w-32 bg-gray-50">
                        <SelectValue placeholder="Pilih" />
                    </SelectTrigger>
                    <SelectContent className="bg-white">
                        <SelectGroup>
                        {comboLevel.map((dataCombo) => (
                          <SelectItem key={dataCombo.value} value={dataCombo.value}>{dataCombo.label}</SelectItem>
                        ))}
                        </SelectGroup>
                    </SelectContent>
                    </Select>
                </FormControl>
                </div> 
                {error && (
                    <p className="text-red-600 text-sm pl-48 mt-1">
                        {error.message}
                    </p>
                  )}
                </FormItem>
            )}
            />
        </div>
        <div className="flex flex-col space-y-4">
            <FormField
            control={form.control}
            name="className"
            rules={{
              required: "Nama Class harus diisi!",
              pattern: {
                value: /^[a-zA-Z_][a-zA-Z0-9_]*$/,
                message: "Nama Class Tidak sesuai!"
              }
            }}
            render={({ field, fieldState: {error} }) => (
                <FormItem>
                <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
                <FormLabel className="w-full sm:w-1/3">
                    Nama Class
                    <span className="text-red-500">*</span>
                    :
                 </FormLabel>
                <FormControl className="flex-1">
                    <div>
                        <Input 
                          {...field} 
                          readOnly={isSourceCodeUploaded || editMode}
                          className={`border rounded p-2 w-full ${(isSourceCodeUploaded || editMode) ? 'bg-gray-100 cursor-not-allowed' : 'bg-gray-50'}`} 
                        />
                        <FormDescription className="text-xs text-gray-500 mt-1">*Nama Class harus sama dengan yang ada pada source code & mengikuti standar coding convention</FormDescription>
                        {error && (
                          <p className="text-red-600 text-sm mt-1">
                              {error.message}
                          </p>
                        )}
                    </div>
                </FormControl>
                </div>
                </FormItem>
            )}
            />
            <FormField
            control={form.control}
            name="functionName"
            rules={{
              required: "Nama fungsi harus diisi!",
              pattern: {
                value: /^[a-zA-Z_][a-zA-Z0-9_]*$/,
                message: "Nama fungsi Tidak sesuai!"
              }
            }}
            render={({ field, fieldState:{error} }) => (
                <FormItem>
                <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
                <FormLabel className="w-full sm:w-1/3">
                    Nama Fungsi
                    <span className="text-red-500">*</span>
                    :
                 </FormLabel>
                <FormControl className="flex-1">
                    <div>
                        {parsedMethods.length > 0 ? (
                            <Select 
                              onValueChange={(val) => {
                                field.onChange(val);
                                setSelectedMethodName(val);
                                autoFillMetadata(parsedMetadata, val);
                              }} 
                              value={field.value || selectedMethodName}
                            >
                              <SelectTrigger className="w-full bg-white border border-blue-500">
                                <SelectValue placeholder="Pilih Fungsi/Method" />
                              </SelectTrigger>
                              <SelectContent className="bg-white">
                                <SelectGroup>
                                  {parsedMethods.map((m: any) => (
                                    <SelectItem key={m.method_name} value={m.method_name}>{m.method_name}</SelectItem>
                                  ))}
                                </SelectGroup>
                              </SelectContent>
                            </Select>
                        ) : (
                            <Input 
                              {...field} 
                              readOnly={isSourceCodeUploaded || editMode}
                              className={`border rounded p-2 w-full ${(isSourceCodeUploaded || editMode) ? 'bg-gray-100 cursor-not-allowed' : 'bg-gray-50'}`} 
                            />
                        )}
                        <FormDescription className="text-xs text-gray-500 mt-1">
                          {parsedMethods.length > 0 
                            ? "*Pilih method dari source code yang akan dijadikan objek pengujian"
                            : "*Nama Fungsi harus sama dengan yang ada pada source code & mengikuti standar coding convention"
                          }
                        </FormDescription>
                        {error && (
                          <p className="text-red-600 text-sm mt-1">
                              {error.message}
                          </p>
                        )}
                    </div>
                </FormControl>
                </div>
                </FormItem>
            )}
            />
        </div>
        </div>

        <div className="flex justify-end space-x-4">
            <Button onClick={onCancel} type="reset" className="bg-blue-50 text-blue-700 border-2 border-blue-700 py-2 px-4 rounded-full hover:bg-blue-700 hover:text-white">Batal</Button>
            <Button type="submit" className="bg-blue-50 text-blue-700 border-2 border-blue-700 py-2 px-4 rounded-full hover:bg-blue-700 hover:text-white">Simpan</Button>
        </div>
      </form>

      {/* Upload Source Code Modal overlay */}
      <Dialog open={isUploadModalOpen} onOpenChange={(open) => {
        if (modalLoading) return;
        setIsUploadModalOpen(open);
        if (!open) {
          setModalError(null);
        }
      }}>
        <DialogContent className="sm:max-w-[500px] bg-white border border-gray-200 shadow-2xl rounded-xl p-6">
          <DialogHeader className="space-y-1">
            <DialogTitle className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <FileCode className="h-6 w-6 text-blue-600" />
              Unggah Source Code Program
            </DialogTitle>
            <DialogDescription className="text-sm text-gray-500">
              Unggah file Java (`.java`) untuk menganalisis class, fungsi, parameter, return type, dan deskripsi secara otomatis.
            </DialogDescription>
          </DialogHeader>

          <div className="mt-4 space-y-4">
            <div
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              onClick={() => document.getElementById("file-upload-input")?.click()}
              className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center gap-4 cursor-pointer transition-all duration-200 min-h-[220px] ${
                dragActive
                  ? "border-blue-500 bg-blue-50/50 scale-[0.99]"
                  : "border-gray-300 hover:border-blue-400 hover:bg-gray-50/50"
              }`}
            >
              <input
                id="file-upload-input"
                type="file"
                className="hidden"
                accept=".java"
                onChange={handleFileSelect}
                disabled={modalLoading}
              />
              
              {modalLoading ? (
                <div className="flex flex-col items-center gap-2">
                  <Loader2 className="h-12 w-12 text-blue-600 animate-spin" />
                  <p className="text-sm font-semibold text-gray-700 mt-2">Menganalisis file source code...</p>
                  <p className="text-xs text-gray-400">Menjalankan parser dan validasi Gradle</p>
                </div>
              ) : (
                <>
                  <div className="p-4 rounded-full bg-blue-50 text-blue-600">
                    <UploadCloud className="h-10 w-10" />
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-semibold text-gray-800">
                      Tarik & lepas file Java di sini, atau klik untuk memilih
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Hanya mendukung file .java dengan ukuran maksimal 2MB
                    </p>
                  </div>
                </>
              )}
            </div>

            {modalError && (
              <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
                <AlertTriangle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-semibold text-red-800">Gagal Memproses File</p>
                  <p className="text-xs mt-1 text-red-700/90 leading-relaxed">{modalError}</p>
                </div>
              </div>
            )}

            <div className="flex justify-end gap-3 pt-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsUploadModalOpen(false)}
                disabled={modalLoading}
                className="rounded-full"
              >
                Batal
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </Form>
  );
};

export default AddModuleForm;
