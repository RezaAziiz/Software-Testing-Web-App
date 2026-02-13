import React from "react";
import { Card, CardTitle } from "@/components/ui/card";
import failIcon from "../../assets/logo/fail.png";
// import { Button } from "@/components/ui/button";

interface FailCardProps {
  percentageCoverage: number;
  minimumCoverage: number;
  statusEksekusi: boolean;
  tanggalEksekusi: string;
  modulId: string; // Added idModul prop
}

const FailCard: React.FC<FailCardProps> = ({
  percentageCoverage,
  minimumCoverage,
  statusEksekusi,
  tanggalEksekusi,
  // modulId, // Added idModul prop
}) => {
  const message = statusEksekusi
    ? `Mohon maaf, belum bisa melanjutkan ke case berikutnya. Minimal coverage test ${minimumCoverage}%.`
    : `Mohon maaf, belum bisa melanjutkan ke case berikutnya. Ubah kembali test case sampai semua hasil test result berstatus PASS.`;

  // const handleReportClick = () => {
  //   const url = `/modul/generateTestUnitClass/${modulId}`;
  //   window.open(url, '_blank');
  // };

  return (
    <div className="h-full w-full">
      <Card className="pass-card bg-red-700 text-white">
        <CardTitle className="module-title-white">Hasil Pengujian</CardTitle>
        <div className="text-center flex flex-col items-center">
          <div className="flex items-start mb-4 justify-start">
            <img
              src={failIcon}
              alt="Blue Card"
              className="mr-4"
              style={{ maxHeight: "150px", width: "150px" }}
            />
            <div className="text-white">
              <p className="font-bold text-medium mb-2 pr-4">
                {statusEksekusi
                  ? `Hasil Coverage Test Case Anda ${percentageCoverage}%`
                  : `Hasil Coverage Test Case Anda tidak dapat dihitung, karena terdapat test case yang berstatus FAILED.`}
              </p>
             
              <p
                className="font-semibold mb-4"
                style={{ fontSize: "14px" }}
              >
                {message}
              </p>
                <p className="font-semibold mb-2" style={{ fontSize: "14px" }}>
                  Tanggal Eksekusi: {tanggalEksekusi}
                </p>
                <div className="button-container-custom mt-4 pr-4" >
            
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default FailCard;
