import { useState, useEffect, useRef } from "react";
import { useForm, SubmitHandler } from "react-hook-form";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";


interface EditFormDialogProps {
  isEditFormDialogOpen: boolean;
  setIsEditFormDialogOpen: (open: boolean) => void;
  triggerRefresh: () => void;
  editingTestId: string;
}

interface ParameterModul {
  ms_id_parameter: string;
  ms_id_modul: string;
  ms_nama_parameter: string;
  ms_tipe_data: string;
  ms_rules: string;
  createdby: string;
  created: string;
  updatedby: string;
  updated: string;
}

// interface TestCase {
//   tr_id_test_case: string;
//   object_pengujian: string;
//   expected_result: string;
//   data_test_input: {
//     param_id: string;
//     param_value: string;
//   }[];
// }

// interface TestCaseData {
//   tr_id_test_case: string;
//   tr_object_pengujian: string;
//   tr_expected_result: string;
//   tr_data_test_input: {
//     param_name: string;  
//     param_type: string;  
//     param_value: string;
//   }[];
// }

interface DataResponse {
  message: string;
  data: {
    data_modul: any;
    data_parameter_modul: ParameterModul[];
    data_cfg: {
      nodes: any[];
      edges: any[];
    };
  };
}

interface FormValues {
  objective: string;
  expected: string;
  [key: string]: string;
}

const EditTestCaseFormDialog = ({
  isEditFormDialogOpen,
  setIsEditFormDialogOpen,
  editingTestId,
  triggerRefresh
}: EditFormDialogProps) => {
  const apiUrl = import.meta.env.VITE_API_URL as string;
  let apiKey = import.meta.env.VITE_API_KEY;
  // const modulId = import.meta.env.VITE_MODULE_ID;
  const sessionData = localStorage.getItem('session')
  if (sessionData != null){
      const session = JSON.parse(sessionData);
      apiKey = session.token
  }
  const queryParameters = new URLSearchParams(window.location.search)
  const modulId = queryParameters.get("topikModulId")
  const [parameters, setParameters] = useState<ParameterModul[]>([]);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  const isSubmitted = useRef(false);

  const form = useForm<FormValues>({
    mode: "onBlur",
  });

  const fetchParameters = async () => {
    try {
      const response = await fetch(`${apiUrl}/modul/detailByIdTopikModul/${modulId}`, {
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

      const responseData: DataResponse = await response.json();
      setParameters(responseData.data.data_parameter_modul);
      console.log(responseData);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const fetchTestCaseData = async (id:string) => {
   
      try {
        const response = await fetch(`${apiUrl}/modul/DetailTestCase/${id}`, {
          method: "GET",
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${apiKey}`,
          },
        });
  
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
  
        const responseData = await response.json();
        const testCaseData = responseData.data

        form.setValue("no", testCaseData.tr_no);
        form.setValue("objective", testCaseData.tr_object_pengujian);
        form.setValue("expected", testCaseData.tr_expected_result);
  
        const dataTestInputParsed = JSON.parse(testCaseData.tr_data_test_input);
        console.log(dataTestInputParsed)
        dataTestInputParsed.forEach((input: any) => {
          const param = parameters.find((p) => p.ms_nama_parameter === input.param_name);
          if (param) {
            form.setValue(`param_${param.ms_id_parameter}`, input.param_value);
          }
        });
  
      } catch (error) {
        console.error("Error fetching test case data:", error);
      }
  };
  

  // const getValidationRule = (param: ParameterModul) => {
  //   let rules;
  //   try {
  //     rules = JSON.parse(param.ms_rules as string);
  //   } catch (error) {
  //     console.error("Error parsing JSON rules:", error);
  //     return {
  //       validate: () =>
  //         `Aturan JSON tidak valid untuk parameter ${param.ms_nama_parameter}`,
  //     };
  //   }

  //   switch (rules.nama_rule) {
  //     case "range":
  //       return {
  //         validate: (value: string) => {
  //           const numericValue = parseFloat(value);
  //           if (rules.min_value && numericValue < parseFloat(rules.min_value)) {
  //             return `Masukkan nilai yang lebih besar atau sama dengan ${rules.min_value}`;
  //           }
  //           if (rules.max_value && numericValue > parseFloat(rules.max_value)) {
  //             return `Masukkan nilai yang lebih kecil atau sama dengan ${rules.max_value}`;
  //           }
  //           return true;
  //         },
  //       };
  //     case "condition":
  //       return {
  //         validate: (value: string) => {
  //           const numericValue = parseFloat(value);
  //           const conditionValue = parseFloat(rules.value);
  //           switch (rules.condition) {
  //             case ">":
  //               if (!(numericValue > conditionValue)) {
  //                 return `Masukkan nilai lebih besar dari ${conditionValue}`;
  //               }
  //               break;
  //             case "<":
  //               if (!(numericValue < conditionValue)) {
  //                 return `Masukkan nilai lebih kecil dari ${conditionValue}`;
  //               }
  //               break;
  //             case ">=":
  //               if (!(numericValue >= conditionValue)) {
  //                 return `Masukkan nilai lebih besar dari atau sama dengan ${conditionValue}`;
  //               }
  //               break;
  //             case "<=":
  //               if (!(numericValue <= conditionValue)) {
  //                 return `Masukkan nilai lebih kecil dari atau sama dengan ${conditionValue}`;
  //               }
  //               break;
  //             case "==":
  //               if (!(numericValue === conditionValue)) {
  //                 return `Masukkan nilai sama dengan ${conditionValue}`;
  //               }
  //               break;
  //             case "!=":
  //               if (!(numericValue !== conditionValue)) {
  //                 return `Masukkan nilai tidak sama dengan ${conditionValue}`;
  //               }
  //               break;
  //             default:
  //               return "Kondisi tidak valid";
  //           }
  //           return true;
  //         },
  //       };
  //     case "enumerasi":
  //       return {
  //         validate: (value: string) => {
  //           const allowedValues = rules.value.split(",");
  //           if (!allowedValues.includes(value)) {
  //             return `Masukkan salah satu dari nilai berikut: ${allowedValues.join(
  //               ", "
  //             )}`;
  //           }
  //           return true;
  //         },
  //       };
  //     case "countOfLength":
  //       return {
  //         validate: (value: string) => {
  //           if (value.length !== parseInt(rules.value)) {
  //             return `Nilai harus tepat ${rules.value} karakter`;
  //           }
  //           return true;
  //         },
  //       };
  //     default:
  //       return {};
  //   }
  // };


  const getValidationDataType = (param: ParameterModul) => {
    switch (param.ms_tipe_data) {
      case "int":
        return {
          pattern: {
            value: /^-?[0-9]+$/,
            message: "Masukkan angka",
          },
        };
      case "float":
        return {
          pattern: {
            value: /^-?[0-9]+(\.[0-9]+)?$/,
            message: "Masukkan angka desimal",
          },
        };
      case "string":
        return {
          pattern: {
            value: /^[a-zA-Z0-9\s]+$/,
            message: "Masukkan huruf atau angka",
          },
        };
      default:
        return {};
    }
  }


  useEffect(() => {
      fetchParameters();
      fetchTestCaseData(editingTestId); 
  }, [isEditFormDialogOpen, editingTestId]);
  

  const handleSubmit: SubmitHandler<FormValues> = async (data) => {
    isSubmitted.current = true;
      const formattedData = {
        id_test_case: editingTestId,
        id_topik_modul: modulId,
        no: data.no,
        object_pengujian: data.objective,
        data_test_input: parameters.map((param) => ({
          param_name: param.ms_nama_parameter,
          param_type: param.ms_tipe_data,
          param_value: data[`param_${param.ms_id_parameter}`],
        })),
        expected_result: data.expected,
      };

      try {
        //form.reset(); // Reset form
        const response = await fetch(`${apiUrl}/modul/editTestCase`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${apiKey}`,
          },
          body: JSON.stringify(formattedData),
        });

        if (!response.ok) {
          if (response.status === 403) {
            throw new Error("Forbidden: Access is denied");
          } else {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
        }

        const responseData: DataResponse = await response.json();
        console.log(responseData);
        setShowSuccessMessage(true);
        setTimeout(() => {
          setShowSuccessMessage(false);
          setIsEditFormDialogOpen(false);
          triggerRefresh();
        }, 3000);
      } catch (error) {
        console.error("Error saving data:", error);
      }
  };
  

  return (
    <>
      <Dialog open={isEditFormDialogOpen} onOpenChange={setIsEditFormDialogOpen}>
        <DialogContent className="bg-white rounded-[20] overflow-y-auto max-h-[80vh] p-6">
          <DialogHeader>
          <DialogTitle className="text-lg text-center font-bold mb-4">
              Pengisian Test Case
            </DialogTitle>
            <Form {...form}>
              <form className="space-y-6" onSubmit={form.handleSubmit(handleSubmit)}>
                <FormField
                  control={form.control}
                  name="objective"
                  rules={{ required: "Objektif Pengujian harus terisi",
                            pattern: {
                              value: /^[a-zA-Z0-9\s]+$/,
                              message: "Masukkan huruf atau angka",
                            },
                  }}
                  render={({ field, fieldState: { error } }) => (
                    <FormItem>
                      <FormLabel>Objektif Pengujian</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          className="rounded-md shadow-sm bg-gray-200 focus:ring-0 border-gray-300"
                        />
                      </FormControl>
                      {error && <p className="text-red-600 text-sm">{error.message}</p>}
                    </FormItem>
                  )}
                />
                {parameters &&
                  parameters.length > 0 &&
                  parameters.map((param) => (
                    <FormField
                      key={param.ms_id_parameter}
                      control={form.control}
                      name={`param_${param.ms_id_parameter}`}
                      rules={{
                        required: `${param.ms_nama_parameter} harus terisi`,
                        ...getValidationDataType(param),
                        // ...getValidationRule(param)
                      }}
                      render={({ field, fieldState: { error } }) => (
                        <FormItem>
                          <FormLabel>{param.ms_nama_parameter}</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              className="rounded-md shadow-sm bg-gray-200 focus:ring-0 border-gray-300"
                            />
                          </FormControl>
                          {error && <p className="text-red-600 text-sm">{error.message}</p>}
                        </FormItem>
                      )}
                    />
                  ))}
                <FormField
                  control={form.control}
                  name="expected"
                  rules={{ required: "Expected result harus terisi" }}
                  render={({ field, fieldState: { error } }) => (
                    <FormItem>
                      <FormLabel>Expected</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          className="rounded-md shadow-sm bg-gray-200 focus:ring-0 border-gray-300"
                        />
                      </FormControl>
                      {error && <p className="text-red-600 text-sm">{error.message}</p>}
                    </FormItem>
                  )}
                />
                <div className="flex justify-end gap-4">
                  <Button
                     onClick={(e) => {
                      e.preventDefault();
                      setIsEditFormDialogOpen(false);
                      //form.reset(); // Reset form
                      isSubmitted.current = false; // Set isSubmitted menjadi false
                    }}
                    className="border border-black hover:bg-gray-200"
                  >
                    Kembali
                  </Button>
                  <Button className="bg-blue-800 text-white border border-black hover:bg-gray-200" type="submit">
                    Simpan
                  </Button>
                </div>
              </form>
            </Form>
          </DialogHeader>
          {showSuccessMessage && (
            <div className="absolute inset-x-0 top-0 flex items-center justify-center h-full bg-black bg-opacity-30">
              <div className="bg-white p-4 rounded-lg shadow-lg">
                <p className="text-2140AD font-bold">Test case berhasil diedit!</p>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

export default EditTestCaseFormDialog;
