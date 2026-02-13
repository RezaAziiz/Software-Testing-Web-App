import React from "react";
import {
  Card,
  // CardContent,
  // CardFooter,
  // CardHeader,
  CardTitle,
} from "@/components/ui/card";
import "../../index.css";
// import passIcon from "../../assets/logo/pass.png";
// import { Button } from "@/components/ui/button";

const PassCard: React.FC = () => {
  return (
    <div className=" h-full w-full">
      <Card className="pass-card bg-blue-800 text-white">
      <CardTitle className="module-title-white">Hasil Pengujian</CardTitle>
        <div>
          <p
            className="text-base font-semibold"
            style={{ fontSize: "14px" }}
          >
            Minimal Coverage Test Bernilai: {" "}
            <span className="font-bold" style={{ fontSize: "18px" }}>
              80%
            </span>
          </p>
        </div>
      </Card>
    </div>
  );
};

export default PassCard;
