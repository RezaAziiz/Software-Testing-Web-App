import React, { useState } from 'react';
import { FaTrophy } from 'react-icons/fa';
import { Card, CardContent } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";
import Modal from '../custom/Modal';

interface ChallengeCardProps {
  idTopikModul: string;
  title: string;
  level: string;
  currentPoints: number;
  maxPoints: number;
  status: string;
}

const ChallengeCard: React.FC<ChallengeCardProps> = ({ idTopikModul, title, level, currentPoints, maxPoints, status }) => {
  const navigate = useNavigate();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [modalMessage, setModalMessage] = useState('');
  const apiUrl = import.meta.env.VITE_API_URL;
  let apiKey = import.meta.env.VITE_API_KEY;
  // const modulId = import.meta.env.VITE_MODULE_ID;
  const sessionData = localStorage.getItem('session')
  if (sessionData != null){
      const session = JSON.parse(sessionData);
      apiKey = session.token
  }
  const getLevelColor = (level: string) => {
    switch (level) {
      case 'Mudah':
        return 'text-[#04B200]';
      case 'Sangat Mudah':
        return 'text-[#5087F2]';
      case 'Sedang':
        return 'text-[#A0640A]';
      case 'Sulit':
        return 'text-[#FF0000]';
      default:
        return 'text-black';
    }
  };

  const getButtonStyle = (status: string) => {
    switch (status) {
      case 'N':
        return 'bg-green-600 text-white';
      case 'Y':
        return 'bg-blue-600 text-white';
      case 'B':
        return 'border border-blue-600 bg-white text-blue-600';
      default:
        return 'border border-blue-600 bg-white text-blue-600';
    }
  };

  const getButtonLabel = (status: string) => {
    switch (status) {
      case 'N':
        return 'Lanjutkan';
      case 'B':
        return 'Selesaikan';
      case 'Y':
        return 'Selesai';
      default:
        return 'Selesaikan';
    }
  };

  const goToTestCasePage = async () => {
    try {
        const response = await fetch(`${apiUrl}/topik/checkChallenge?idTopikModul=${idTopikModul}`, {
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
      console.log(data.data_allowed)
      if (data.data_allowed){
          navigate({
            pathname: '/topikModul',
            search: '?topikModulId='+idTopikModul,
          });
      }else{
          setModalMessage("Anda belum bisa mengerjakan modul ini, silahkan selesaikan dahulu modul sebelumnya");
          setIsModalVisible(true);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };
  return (
    <Card className="mb-4 border border-blue-800 rounded">
      <CardContent className="lg:p-4 p-2">
        <div className="flex justify-between items-center mb-2">
          <h3 className="lg:text-lg md:text-base text-sm font-bold text-blue-600">{title}</h3>
          <div className="lg:text-base md:text-sm text-xs text-blue-600 flex items-center">
            <FaTrophy className="mr-1" />
            <span>{currentPoints === 0 ? '---' : currentPoints}/{maxPoints} XP</span>
          </div>
        </div>
        <div className="flex justify-between items-center">
          <div className="lg:text-base md:text-sm text-xs font-semibold">
            <span className={getLevelColor(level)}>{level}</span>, Max Points : {maxPoints} XP
          </div>
          <button
            onClick={goToTestCasePage}
            className={`font-bold rounded lg:text-base md:text-sm text-xs lg:py-2 lg:px-4 py-1 px-2 ${getButtonStyle(status)}`}
          >
            {getButtonLabel(status)}
          </button>
        </div>
      </CardContent>
      <Modal
        isVisible={isModalVisible}
        onClose={() => setIsModalVisible(false)}
        message={modalMessage}
      />
    </Card>
  );
};

export default ChallengeCard;
