import React, { useState } from 'react';
import { ChevronRight, ChevronLeft, BarChart3 } from 'lucide-react';
import { DiagnosticQuestion, DiagnosticResponse } from '../types';
import { diagnosticQuestions } from '../data/diagnosticQuestions';

interface DiagnosticQuizProps {
  onComplete: (responses: DiagnosticResponse[]) => void;
}

const DiagnosticQuiz: React.FC<DiagnosticQuizProps> = ({ onComplete }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [responses, setResponses] = useState<DiagnosticResponse[]>([]);
  
  const currentQuestion = diagnosticQuestions[currentIndex];
  const progress = ((currentIndex + 1) / diagnosticQuestions.length) * 100;

  const handleResponse = (value: number) => {
    const newResponse: DiagnosticResponse = {
      questionId: currentQuestion.id,
      value
    };

    const updatedResponses = responses.filter(r => r.questionId !== currentQuestion.id);
    updatedResponses.push(newResponse);
    setResponses(updatedResponses);

    if (currentIndex < diagnosticQuestions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      onComplete(updatedResponses);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const getCurrentResponse = () => {
    return responses.find(r => r.questionId === currentQuestion.id)?.value || 0;
  };

  const getScaleLabel = (value: number) => {
    const labels = ['Pas du tout', 'Peu', 'Modérément', 'Beaucoup', 'Énormément'];
    return labels[value - 1] || '';
  };

  const getCategoryInfo = (category: string) => {
    if (category === 'bigfive') {
      return {
        title: 'Personnalité',
        description: 'Ces questions évaluent vos traits de personnalité fondamentaux',
        color: 'from-blue-500 to-purple-500'
      };
    }
    return {
      title: 'Intérêts professionnels',
      description: 'Ces questions identifient vos préférences d\'environnement de travail',
      color: 'from-green-500 to-teal-500'
    };
  };

  const categoryInfo = getCategoryInfo(currentQuestion.category);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className={`inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r ${categoryInfo.color} rounded-2xl mb-4`}>
            <BarChart3 className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Diagnostic Phoenix Aube</h1>
          <p className="text-gray-600">{categoryInfo.description}</p>
        </div>

        {/* Progress */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>{categoryInfo.title}</span>
            <span>{currentIndex + 1} / {diagnosticQuestions.length}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`bg-gradient-to-r ${categoryInfo.color} h-2 rounded-full transition-all duration-300`}
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border border-gray-100">
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 leading-relaxed">
              {currentQuestion.question}
            </h2>
            
            {currentQuestion.category === 'riasec' && (
              <p className="text-gray-600 text-sm">
                Dans quelle mesure appréciez-vous cette activité ?
              </p>
            )}
          </div>

          {/* Scale Response */}
          <div className="space-y-4">
            <div className="grid grid-cols-5 gap-3">
              {[1, 2, 3, 4, 5].map((value) => (
                <button
                  key={value}
                  onClick={() => handleResponse(value)}
                  className={`p-4 rounded-xl border-2 transition-all duration-200 ${
                    getCurrentResponse() === value
                      ? `border-orange-500 bg-orange-50 shadow-md`
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="text-center">
                    <div className={`w-8 h-8 rounded-full mx-auto mb-2 flex items-center justify-center font-bold ${
                      getCurrentResponse() === value
                        ? 'bg-orange-500 text-white'
                        : 'bg-gray-200 text-gray-600'
                    }`}>
                      {value}
                    </div>
                    <div className="text-xs font-medium text-gray-700">
                      {getScaleLabel(value)}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-between">
          <button
            onClick={handlePrevious}
            disabled={currentIndex === 0}
            className="flex items-center px-6 py-3 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="h-5 w-5 mr-2" />
            Précédent
          </button>
          
          <div className="text-sm text-gray-500 flex items-center">
            Appuyez sur un chiffre ou cliquez pour continuer
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiagnosticQuiz;