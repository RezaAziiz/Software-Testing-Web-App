import React from "react";
import {
  Card,
  // CardContent,
  CardFooter,
  // CardHeader,
  CardTitle,
} from "@/components/ui/card";
import "../../index.css";
import passIcon from "../../assets/logo/pass.png";
// import { Button } from "@/components/ui/button";

interface PassCardProps {
  percentageCoverage: number;
  minimumCoverage: number;
  statusEksekusi: boolean;
  tanggalEksekusi: string;
  poin: number;
  modulId: string;
}

const PassCard: React.FC<PassCardProps> = ({
  percentageCoverage,
  minimumCoverage,
  // statusEksekusi,
  tanggalEksekusi,
  // modulId,
  poin,
}) => {
  // Mendapatkan tanggal saat ini
  // const currentDate = new Date();
  // const formattedDate = currentDate.toLocaleDateString();

  return (
    <div className=" w-full">
      <Card className="pass-card bg-blue-800 text-white">
        <CardTitle className="module-title-white">Hasil Pengujian</CardTitle>
        <div className="text-center flex flex-col items-center">
          <div className="flex items-start mb-4 justify-start">
          <img
              src={passIcon}
              alt="Blue Card"
              className="mr-4"
              style={{ width: "180px" }}
            />
            <div className="text-white">
              <p className="font-bold text-medium mb-2 pr-4">
                Hasil Coverage Test Case Anda {percentageCoverage}%
              </p>
            
              <p
                className="font-semibold text-base mb-2"
                style={{ fontSize: "14px" }}
              >
                Selamat! Anda sudah berhasil melewati batas minimal coverage
                test, yaitu {minimumCoverage}%
              </p>
              <p
              className="text-base mb-2 font-semibold"
              style={{ fontSize: "16px" }}
            >
              Poin yang didapat :{" "}
              <span className="font-bold" style={{ fontSize: "16px" }}>
                {poin} Poin
              </span>
            </p>
            <p
              className="text-base mb-4 font-semibold "
              style={{ fontSize: "14px" }}
            >
              Tanggal Eksekusi: {tanggalEksekusi}
            </p>
            </div>
          </div>
        </div>
        <CardFooter className="card-footer flex justify-end items-center">

</CardFooter>

      </Card>
    </div>
  );
};

export default PassCard;
