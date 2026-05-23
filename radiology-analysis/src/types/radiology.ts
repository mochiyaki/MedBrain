export interface Finding {
  id: string;
  label: string;
  confidence: number;
  location?: string;
  description: string;
}

export interface Report {
  id: string;
  patientId: string;
  findings: Finding[];
  preliminaryReport: string;
  createdAt: string;
  status: 'draft' | 'final';
}

export interface ImageMetadata {
  id: string;
  url: string;
  type: 'DICOM' | 'PNG' | 'JPG';
  fileName: string;
  uploadDate: string;
}

export interface Annotation {
  id: string;
  type: 'roi' | 'measure' | 'mark';
  data: any; // Simplified for initial prototype
}

export interface RadiologySession {
  activeImage?: ImageMetadata;
  comparisonImage?: ImageMetadata;
  isAnalyzing: boolean;
  findings: Finding[];
  report: string;
}
