import React, { useCallback, useState } from 'react';
import { ImageMetadata } from '../../types/radiology';

interface ImageUploaderProps {
  onUpload: (metadata: ImageMetadata) => void;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({ onUpload }) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      // Simulate file processing
      const metadata: ImageMetadata = {
        id: Math.random().toString(36).substr(2, 9),
        url: URL.createObjectURL(file),
        type: file.name.endsWith('.dcm') ? 'DICOM' : (file.type.includes('png') ? 'PNG' : 'JPG'),
        fileName: file.name,
        uploadDate: new Date().toISOString(),
      };
      onUpload(metadata);
    }
  }, [onUpload]);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      const metadata: ImageMetadata = {
        id: Math.random().toString(36).substr(2, 9),
        url: URL.createObjectURL(file),
        type: file.name.endsWith('.dcm') ? 'DICOM' : (file.type.includes('png') ? 'PNG' : 'JPG'),
        fileName: file.name,
        uploadDate: new Date().toISOString(),
      };
      onUpload(metadata);
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer
        ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-slate-300 hover:border-blue-400'}`}
    >
      <input
        type="file"
        id="file-upload"
        className="hidden"
        accept=".dcm,.png,.jpg,.jpeg"
        onChange={handleFileInput}
      />
      <label htmlFor="file-upload" className="cursor-pointer">
        <div className="flex flex-col items-center">
          <svg className="w-12 h-12 text-slate-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p className="text-lg font-medium text-slate-700">Click or drag and drop to upload</p>
          <p className="text-sm text-slate-500 mt-1">DICOM, PNG, or JPG (max. 50MB)</p>
        </div>
      </label>
    </div>
  );
};
