import { useState, useEffect } from 'react';
import { CopyBlock, dracula } from 'react-code-blocks';
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";
import "../../index.css";

const CodeProgramCard = () => {
  const apiUrl = import.meta.env.VITE_API_URL;
  let apiKey = import.meta.env.VITE_API_KEY;

  const navigate = useNavigate();

  const sessionData = localStorage.getItem('session');
  if (sessionData != null) {
    const session = JSON.parse(sessionData);
    apiKey = session.token;
  }

  const queryParameters = new URLSearchParams(window.location.search);
  const modulId = queryParameters.get("topikModulId");

  const [sourceCode, setSourceCode] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDataModule = async () => {
    try {
      const response = await fetch(`${apiUrl}/modul/detailByIdTopikModul/${modulId}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        }
      });

      if (!response.ok) {
        if (response.status === 403) {
          // throw new Error('Forbidden: Access is denied');
          navigate('/error');
        } else {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      }

      const data = await response.json();
      console.log(data);

      if (data.data) {
        fetchSourceCodeText(data.data.data_modul.ms_id_modul);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      setError((error as Error).message);
    }
  };

  const fetchSourceCodeText = async (modulId: string) => {
    try {
      const response = await fetch(`${apiUrl}/modul/getSourceCodeText/${modulId}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setSourceCode(data.data || '');
    } catch (error) {
      console.error('Error fetching source code:', error);
      setError((error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (modulId) {
      fetchDataModule();
    } else {
      setLoading(false);
    }
  }, [modulId]);

  if (error) {
    return (
      <Card className="w-full h-full">
        <CardHeader>
          <CardTitle className="text-base font-bold">Kode Program</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-red-600">Error: {error}</div>
        </CardContent>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card className="w-full h-full">
        <CardHeader>
          <CardTitle className="text-base font-bold">Kode Program</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full h-full flex flex-col">
      <CardHeader className="pb-0">
        <CardTitle className="text-base font-bold">Kode Program</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden p-0">
        <div className="text-sm p-4">
            <CopyBlock
                language="java"
                text={sourceCode || 'Loading source code...'}
                showLineNumbers={true}
                theme={dracula}
                codeBlock
                customStyle={{
                    height: '450px',
                    overflowY: 'scroll',
                    borderRadius: '5px',
                    boxShadow: '1px 2px 10px rgba(0,0,0,0.2)',
                    fontSize: 'small',
                }}
            />
        </div>
      </CardContent>
    </Card>
  );
};

export default CodeProgramCard;
