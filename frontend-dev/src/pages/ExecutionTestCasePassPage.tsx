import React, { useEffect, useRef } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import AddTestCaseCard from "@/components/custom/AddTestCaseCard";
import PassCard from "@/components/custom/PassCard";
import ModuleWorkspaceLayout from "@/components/custom/ModuleWorkspaceLayout";
import { useAuthGuard } from "@/hooks/useAuthGuard";

const ExecutionTestCasePassPage: React.FC = () => {
  const { token } = useAuthGuard({ requiredRole: "student" });

  const apiUrl = import.meta.env.VITE_API_URL;
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const bottomRef = useRef<HTMLDivElement>(null);

  const { state: navigationData } = location;
  const modulId = searchParams.get("topikModulId");

  // Scroll otomatis ke bagian bawah saat halaman selesai dimuat
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  // Navigasi ke halaman laporan hasil pengujian lengkap
  const handleNavigateToTestResult = () => {
    navigate("/test-result?topikModulId=" + modulId, {
      state: {
        modul_id: navigationData?.modul_id,
      },
    });
  };

  // Navigasi ke tantangan kasus uji berikutnya
  const handleNavigateNextChallenge = async () => {
    try {
      const response = await fetch(
        `${apiUrl}/topik/nextChallenge?idTopikModul=${modulId}`,
        {
          method: "GET",
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (!response.ok) {
        if (response.status === 403) {
          navigate("/error");
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const nextTopikModulId = data?.data?.ms_id_topik_modul;
      const currentTopikId = data?.data_current?.ms_id_topik;

      if (nextTopikModulId) {
        navigate({
          pathname: "/topikModul",
          search: "?topikModulId=" + nextTopikModulId,
        });
      } else if (currentTopikId) {
        navigate({
          pathname: "/list-challanges",
          search: "?idTopik=" + currentTopikId,
        });
      } else {
        navigate("/list-topics");
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  return (
    <ModuleWorkspaceLayout>
      {/* Section 3: Test Case, Hasil Pengujian, dan Tombol (Full Width) */}
      <div className="w-full flex flex-col gap-6">
        <AddTestCaseCard />
        <div className="w-full">
          <PassCard
            percentageCoverage={navigationData?.coverage_score || 0}
            minimumCoverage={navigationData?.minimum_coverage_score || 0}
            statusEksekusi={navigationData?.status_eksekusi || false}
            tanggalEksekusi={navigationData?.tgl_eksekusi || ""}
            modulId={navigationData?.modul_id || ""}
            poin={navigationData?.points || 0}
          />
        </div>

        {/* Penanda untuk scroll ke bagian paling bawah */}
        <div ref={bottomRef}></div>

        <div className="flex space-x-2 items-center p-4 justify-center">
          <Button
            variant="outline"
            className="bg-white text-sm text-blue-800 border-2 border-blue-800 rounded-[10] hover:bg-blue-800 hover:text-white"
            onClick={handleNavigateToTestResult}
          >
            Hasil Pengujian
          </Button>
          <Button
            className="bg-blue-800 text-sm text-white border-2 border-blue-800 rounded-[20] pt-0 pb-0"
            onClick={handleNavigateNextChallenge}
          >
            Kasus Selanjutnya
          </Button>
        </div>
      </div>
    </ModuleWorkspaceLayout>
  );
};

export default ExecutionTestCasePassPage;
