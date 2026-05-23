import React from 'react';
import { Finding } from '../../types/radiology';
import { Button } from '../ui';

interface AIAnalysisPanelProps {
  isAnalyzing: boolean;
  findings: Finding[];
  onAnalyze: () => void;
}

export const AIAnalysisPanel: React.FC<AIAnalysisPanelProps> = ({
  isAnalyzing,
  findings,
  onAnalyze,
}) => {
  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-slate-100 flex justify-between items-center">
        <h3 className="font-semibold text-slate-900">AI Analysis</h3>
        <Button 
          size="sm" 
          onClick={onAnalyze} 
          disabled={isAnalyzing}
          className={isAnalyzing ? 'animate-pulse' : ''}
        >
          {isAnalyzing ? 'Analyzing...' : 'Run Analysis'}
        </Button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {findings.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-sm text-slate-500 italic">
              {isAnalyzing ? 'AI is processing the image...' : 'No findings yet. Run AI analysis to begin.'}
            </p>
          </div>
        ) : (
          findings.map((finding) => (
            <div 
              key={finding.id} 
              className="p-3 rounded-lg border border-slate-200 bg-slate-50 hover:bg-blue-50 hover:border-blue-200 transition-colors cursor-pointer"
            >
              <div className="flex justify-between items-start mb-1">
                <span className="font-medium text-slate-900 text-sm">{finding.label}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                  finding.confidence > 0.8 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {Math.round(finding.confidence * 100)}%
                </span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">{finding.description}</p>
              {finding.location && (
                <div className="mt-2 text-[10px] uppercase tracking-wider font-semibold text-slate-400">
                  Location: {finding.location}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
