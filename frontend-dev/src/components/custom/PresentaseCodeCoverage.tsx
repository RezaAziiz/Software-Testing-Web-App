import React from 'react';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

interface PercentageCircleProps {
  percentage: number;
}

const PercentageCodeCoverage: React.FC<PercentageCircleProps> = ({ percentage }) => {
  return (
    <div style={{ width: '100px', height: '100px' }}>
      <CircularProgressbar
        value={percentage}
        text={`${percentage==0?'-':percentage + "%"}`}
        strokeWidth={14}
        styles={buildStyles({
          textColor: '#000',
          pathColor: '#0000ff',
          trailColor: '#d3d3d3',
          textSize: '18px',
        })}
      />
    </div>
  );
};

export default PercentageCodeCoverage;
