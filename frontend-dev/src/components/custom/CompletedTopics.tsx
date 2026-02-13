import React from 'react';
import logo_skor from "../../assets/logo/skor.png";

interface CompletedTopic {
  id: string;
  title: string;
  xp: number;
}

interface CompletedTopicsProps {
  topics: CompletedTopic[];
  searchQuery: string;
  onTopicClick: (title: string) => void;
}

const CompletedTopics: React.FC<CompletedTopicsProps> = ({ topics, searchQuery, onTopicClick }) => {
  const filterTopics = (topics: CompletedTopic[], query: string) => {
    if (!query) return topics;
    return topics.filter((topic) =>
      topic.title.toLowerCase().includes(query.toLowerCase())
    );
  };

  const filteredCompletedTopics = filterTopics(topics, searchQuery);

  return (
    <>
      {filteredCompletedTopics.length > 0 && (
        <div className="m-2 lg:m-4">
          <h2 className="text-base lg:text-xl font-bold text-blue-800 mb-4">Sudah Dipelajari</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 m-2">
            {filteredCompletedTopics.map((topic) => (
              <div
                key={topic.id}
                onClick={() => onTopicClick(topic.id)}
                className="bg-blue-50 text-black p-4 rounded-lg shadow-lg border-2 border-blue-800 cursor-pointer transition-transform transform hover:scale-105"
              >
                <div className="flex justify-between items-center">
                  <h3 className="text-base lg:text-lg font-bold text-blue-800">{topic.title}</h3>
                  <div className="flex items-center">
                    <img src={logo_skor} alt="Logo" className="w-8 h-8 mr-2" />
                    <p className="text-xs lg:text-sm font-semibold">{topic.xp} XP</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
};

export default CompletedTopics;
