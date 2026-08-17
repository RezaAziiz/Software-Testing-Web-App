import React from "react";
import { Card, CardTitle } from "@/components/ui/card";
import "../../index.css";

interface MinimalCardProps {
  minimumCoverage?: number;
}

const MinimalCard: React.FC<MinimalCardProps> = ({ minimumCoverage = 80 }) => {
  return (
    <div className="h-full w-full">
      <Card className="pass-card bg-blue-800 text-white">
        <CardTitle className="module-title-white">Hasil Pengujian</CardTitle>
        <div>
          <p className="text-base font-semibold" style={{ fontSize: "14px" }}>
            Minimal Coverage Test Bernilai:{" "}
            <span className="font-bold" style={{ fontSize: "18px" }}>
              {minimumCoverage}%
            </span>
          </p>
        </div>
      </Card>
    </div>
  );
};

export default MinimalCard;
