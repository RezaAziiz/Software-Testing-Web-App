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


  // const handleFileChange = (e:any, field:any) => {
  //   field.onChange(e.target.files?.[0]?.name || '')
  //   if (e.target.files != null){
  //     setFileSourceCode(e.target.files[0])
  //   }
  // };

  const handleFileChange = (e: any, field: any) => {
    const file = e.target.files?.[0];
    let errors = [];
    if (file) {
      if (file.size > 2097152) {
        errors.push("Ukuran maksimal file adalah 2 MB!");
      }
      if (!file.name.endsWith('.java')) {
        errors.push("File Source Code tidak sesuai");
      }
      if (errors.length === 0) {
        setFileSourceCode(file);
        setFileErrors([]);
        field.onChange(file.name);
      } else {
        setFileSourceCode(null);
        setFileErrors(errors);
        field.onChange('');
      }
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
                                className="border rounded p-2 w-32 bg-gray-50"
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
                      <Input {...field} className="border rounded p-2 w-full bg-white" />
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
                      <Select onValueChange={(e) => handleDataTypeChange(e, index)} defaultValue={field.value}>
                        <SelectTrigger className="w-full bg-white">
                          <SelectValue placeholder="Pilih" />
                        </SelectTrigger>
                        <SelectContent className="bg-white">
                          <SelectGroup>
                            {comboDataType.map((dataCombo) => (
                              <SelectItem value={dataCombo.value}>{dataCombo.label}</SelectItem>
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
                <FormLabel className="w-full sm:w-1/3">
                    Source Code
                    {!editMode && (<span className="text-red-500">*</span>)}
                    :
                 </FormLabel>
                <FormControl className="flex-1">
                    <div>
                        <Input
                            type="file"
                            onChange={(e) => handleFileChange(e, field)}
                            className="border rounded p-2 w-full bg-gray-50"
                        />
                        {fileName && (
                          <FormLabel className="w-1/3">
                              {fileName}
                          </FormLabel>
                        )}
                        
                        <FormDescription className="text-xs text-gray-500 mt-1">File harus berekstensi .java dan memiliki ukuran maksimal 2MB</FormDescription>
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
                        <Input {...field} className="border rounded p-2 w-full bg-gray-50" />
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
                        <Input {...field} className="border rounded p-2 w-full bg-gray-50" />
                        <FormDescription className="text-xs text-gray-500 mt-1">*Nama Fungsi harus sama dengan yang ada pada source code & mengikuti standar coding convention</FormDescription>
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
    </Form>
  );
};

export default AddModuleForm;
