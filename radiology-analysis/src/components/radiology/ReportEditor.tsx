import React from 'react';
import { Button } from '../ui';

interface ReportEditorProps {
  report: string;
  onChange: (report: string) => void;
  onSave: () => void;
}

export const ReportEditor: React.FC<ReportEditorProps> = ({
  report,
  onChange,
  onSave,
}) => {
  return (
    <div className="flex flex-col h-full bg-slate-50 border-t border-slate-200">
      <div className="p-3 border-b border-slate-200 flex justify-between items-center bg-white">
        <h3 className="font-semibold text-slate-900 text-sm">Preliminary Report</h3>
        <Button size="sm" variant="outline" onClick={onSave}>Save Draft</Button>
      </div>
      <div className="flex-1 p-4">
        <textarea
          className="w-full h-full p-4 rounded-lg border border-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm leading-relaxed"
          placeholder="Enter findings and clinical impressions..."
          value={report}
          onChange={(e) => onChange(e.target.value)}
        />
      </div>
    </div>
  );
};
