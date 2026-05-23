import React from 'react';
import { Button } from '../ui';

interface ViewerControlsProps {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onReset: () => void;
}

export const ViewerControls: React.FC<ViewerControlsProps> = ({
  onZoomIn,
  onZoomOut,
  onReset,
}) => {
  return (
    <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-slate-900/80 backdrop-blur-sm rounded-full px-4 py-2 flex items-center gap-2 shadow-lg z-10">
      <Button variant="ghost" size="sm" onClick={onZoomOut} className="text-white hover:bg-slate-700 hover:text-white" title="Zoom Out">
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" /></svg>
      </Button>
      <Button variant="ghost" size="sm" onClick={onReset} className="text-white hover:bg-slate-700 hover:text-white" title="Reset View">
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
      </Button>
      <Button variant="ghost" size="sm" onClick={onZoomIn} className="text-white hover:bg-slate-700 hover:text-white" title="Zoom In">
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" /></svg>
      </Button>
      
      <div className="w-px h-6 bg-slate-600 mx-2"></div>
      
      <Button variant="ghost" size="sm" className="text-white hover:bg-slate-700 hover:text-white text-xs font-semibold px-3" title="Window Level">W/L</Button>
      <Button variant="ghost" size="sm" className="text-white hover:bg-slate-700 hover:text-white" title="Pan">
         <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 11.5V14m0-2.5v-6a1.5 1.5 0 113 0m-3 6a1.5 1.5 0 00-3 0v2a7.5 7.5 0 0015 0v-5a1.5 1.5 0 00-3 0m-6-3V11m0-5.5v-1a1.5 1.5 0 013 0v1m0 0V11m0-5.5a1.5 1.5 0 013 0v3m0 0V11" /></svg>
      </Button>
    </div>
  );
};
