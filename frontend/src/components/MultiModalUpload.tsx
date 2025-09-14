'use client';

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Image, BarChart3, FileText, Loader2, CheckCircle, XCircle } from 'lucide-react';

interface MultiModalUploadProps {
  onUpload: (file: File, type: 'document' | 'chart' | 'image') => Promise<void>;
  className?: string;
}

interface UploadResult {
  success: boolean;
  type: 'document' | 'chart' | 'image';
  filename: string;
  result?: any;
  error?: string;
}

const MultiModalUpload: React.FC<MultiModalUploadProps> = ({ onUpload, className = '' }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadResults, setUploadResults] = useState<UploadResult[]>([]);

  const detectFileType = (file: File): 'document' | 'chart' | 'image' => {
    if (file.type === 'application/pdf') {
      return 'document';
    }
    if (file.type.startsWith('image/')) {
      // Basic heuristic - in production, you might use ML to detect charts
      if (file.name.toLowerCase().includes('chart') ||
          file.name.toLowerCase().includes('graph') ||
          file.name.toLowerCase().includes('plot')) {
        return 'chart';
      }
      return 'image';
    }
    return 'document';
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true);
    const results: UploadResult[] = [];

    for (const file of acceptedFiles) {
      try {
        const fileType = detectFileType(file);
        await onUpload(file, fileType);

        results.push({
          success: true,
          type: fileType,
          filename: file.name
        });
      } catch (error) {
        results.push({
          success: false,
          type: detectFileType(file),
          filename: file.name,
          error: error instanceof Error ? error.message : 'Upload failed'
        });
      }
    }

    setUploadResults(prev => [...prev, ...results]);
    setUploading(false);
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.svg'],
      'text/*': ['.txt', '.md']
    },
    multiple: true
  });

  const getFileTypeIcon = (type: 'document' | 'chart' | 'image') => {
    switch (type) {
      case 'chart':
        return <BarChart3 className="w-5 h-5 text-blue-500" />;
      case 'image':
        return <Image className="w-5 h-5 text-green-500" />;
      default:
        return <FileText className="w-5 h-5 text-gray-500" />;
    }
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
          }
          ${uploading ? 'pointer-events-none opacity-50' : ''}
        `}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center space-y-4">
          {uploading ? (
            <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
          ) : (
            <Upload className="w-12 h-12 text-gray-400" />
          )}

          <div>
            <p className="text-lg font-medium text-gray-900">
              {uploading ? 'Processing files...' : 'Upload multi-modal content'}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              {isDragActive
                ? 'Drop the files here...'
                : 'Drag & drop PDFs, images, or charts here, or click to select'
              }
            </p>
          </div>

          {/* File Type Examples */}
          <div className="flex flex-wrap justify-center gap-4 text-xs text-gray-500">
            <div className="flex items-center gap-1">
              <FileText className="w-4 h-4" />
              <span>PDFs with images</span>
            </div>
            <div className="flex items-center gap-1">
              <BarChart3 className="w-4 h-4" />
              <span>Charts & Graphs</span>
            </div>
            <div className="flex items-center gap-1">
              <Image className="w-4 h-4" />
              <span>Technical Diagrams</span>
            </div>
          </div>
        </div>
      </div>

      {/* Upload Results */}
      {uploadResults.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-900">Upload Results</h3>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {uploadResults.map((result, index) => (
              <div
                key={index}
                className={`
                  flex items-center gap-3 p-3 rounded-lg border
                  ${result.success
                    ? 'bg-green-50 border-green-200'
                    : 'bg-red-50 border-red-200'
                  }
                `}
              >
                {result.success ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-600" />
                )}

                {getFileTypeIcon(result.type)}

                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {result.filename}
                  </p>
                  <p className="text-xs text-gray-500 capitalize">
                    {result.type} • {result.success ? 'Processed successfully' : result.error}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {uploadResults.length > 3 && (
            <button
              onClick={() => setUploadResults([])}
              className="text-xs text-gray-500 hover:text-gray-700"
            >
              Clear results
            </button>
          )}
        </div>
      )}

      {/* Feature Highlights */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2">
          Enhanced Multi-Modal Features
        </h4>
        <ul className="text-xs text-gray-600 space-y-1">
          <li>• Charts converted to searchable insights</li>
          <li>• Visual elements linked to text explanations</li>
          <li>• Smart image captioning for technical diagrams</li>
          <li>• Search across text, images, and data visualizations</li>
        </ul>
      </div>
    </div>
  );
};

export default MultiModalUpload;