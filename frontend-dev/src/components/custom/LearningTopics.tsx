import React from 'react';
import logo_berpikir from "../../assets/logo/berpikir.png";
import logo_skor from "../../assets/logo/skor.png";
import { useNavigate } from "react-router-dom";

interface LearningTopic {
  id: string;
  title: string;
  description: string;
  challenges: number;
  xp: number;
}

interface LearningTopicsProps {
  topics: LearningTopic[];
  searchQuery: string;
}

const LearningTopics: React.FC<LearningTopicsProps> = ({ topics, searchQuery }) => {
  const navigate = useNavigate();
  const filterTopics = (topics: LearningTopic[], query: string) => {
    if (!query) return topics;
    return topics.filter((topic) =>
      topic.title.toLowerCase().includes(query.toLowerCase())
    );
  };

  const filteredLearningTopics = filterTopics(topics, searchQuery);
  const onLearn = (id: string) => {
    navigate("/list-challanges?idTopik="+id);
  };
  return (
    <>
      {filteredLearningTopics.length > 0 && (
      <div className="m-2 lg:m-4">
        <h2 className="text-base lg:text-xl font-bold text-blue-800 mb-4">Topik Belajar</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 m-2 animate-fade-in">
          {filteredLearningTopics.map((topic) => (
            <div
              key={topic.id}
              className="bg-blue-50 text-black p-6 rounded-lg shadow-lg border-2 border-blue-800"
            >
              <div className="flex justify-between items-start mb-2 text-blue-800">
                <h3 className="text-base lg:text-lg font-bold">{topic.title}</h3>
                <img src={logo_berpikir} alt="Logo" className="w-20" />
              </div>
              <p className="text-sm lg:text-base font-semibold text-blue-800 mb-2">
                {topic.description}
              </p>
              <p className="text-xs lg:text-sm font-bold text-blue-800 mb-2">
                {topic.challenges} Tantangan
              </p>
              <div className="flex justify-between items-center mt-4">
                <div className="flex items-center">
                  <img src={logo_skor} alt="Logo" className="w-10 mr-2" />
                  <p className="font-semibold text-xs lg:text-sm">{topic.xp} XP</p>
                </div>
                <button onClick={() => onLearn(topic.id)} className="text-xs lg:text-sm bg-blue-800 hover:bg-blue-500 text-white px-4 py-2 rounded">
                  Pelajari
                </button>
              </div>
            </div>
          ))}
        </div>
        <hr className="border-blue-800 my-6" />
      </div>
      )}
    </>
  );
};

export default LearningTopics;
