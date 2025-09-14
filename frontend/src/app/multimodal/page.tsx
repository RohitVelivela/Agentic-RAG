'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Sparkles,
  BarChart3,
  Image,
  FileText,
  Upload,
  Search,
  Eye,
  Layers
} from 'lucide-react';

import MultiModalChat from '@/components/MultiModalChat';
import MultiModalUpload from '@/components/MultiModalUpload';
import ChartAnalysis from '@/components/ChartAnalysis';
import VisualTextLinks from '@/components/VisualTextLinks';

export default function MultiModalPage() {
  const [activeTab, setActiveTab] = useState<'chat' | 'upload' | 'analysis' | 'links'>('chat');
  const [chartAnalysis, setChartAnalysis] = useState<any>(null);
  const [visualLinks, setVisualLinks] = useState<any[]>([]);

  const handleFileUpload = async (file: File, type: 'document' | 'chart' | 'image') => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      let endpoint = '/upload';
      if (type === 'chart') {
        endpoint = '/analyze/chart';
      } else if (type === 'image') {
        endpoint = '/analyze/image';
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();

      // Handle chart analysis results
      if (type === 'chart' && result.success) {
        setChartAnalysis(result);
        setActiveTab('analysis');
      }

      return result;
    } catch (error) {
      console.error('Upload failed:', error);
      throw error;
    }
  };

  const handleQueryFromChart = (fact: string) => {
    setActiveTab('chat');
    // The chat component will handle this
  };

  const tabs = [
    {
      id: 'chat',
      label: 'AI Chat',
      icon: Sparkles,
      description: 'Multi-modal conversation with enhanced reasoning'
    },
    {
      id: 'upload',
      label: 'Upload & Analyze',
      icon: Upload,
      description: 'Upload documents, charts, and images for analysis'
    },
    {
      id: 'analysis',
      label: 'Chart Analysis',
      icon: BarChart3,
      description: 'View detailed chart and graph insights'
    },
    {
      id: 'links',
      label: 'Visual Links',
      icon: Layers,
      description: 'Explore visual-text relationships'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Multi-Modal RAG
                </h1>
                <p className="text-sm text-gray-500">
                  Advanced visual-text reasoning system
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Multi-modal AI</span>
                </div>
                <div className="flex items-center space-x-1">
                  <BarChart3 className="w-4 h-4 text-blue-500" />
                  <span>Chart Analysis</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Eye className="w-4 h-4 text-purple-500" />
                  <span>Visual-Text Links</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`
                  flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <tab.icon className="w-5 h-5" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'chat' && (
            <div className="bg-white rounded-lg shadow-sm border h-[600px]">
              <MultiModalChat />
            </div>
          )}

          {activeTab === 'upload' && (
            <div className="space-y-6">
              {/* Upload Component */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="mb-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-2">
                    Upload Multi-Modal Content
                  </h2>
                  <p className="text-gray-600">
                    Upload PDFs, charts, and images to enable advanced multi-modal analysis and search.
                  </p>
                </div>

                <MultiModalUpload
                  onUpload={handleFileUpload}
                />
              </div>

              {/* Feature Showcase */}
              <div className="grid md:grid-cols-3 gap-6">
                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                    <BarChart3 className="w-6 h-6 text-blue-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Chart-to-Text Intelligence
                  </h3>
                  <p className="text-gray-600 text-sm">
                    Convert complex charts and graphs into queryable insights with extracted data points, trends, and key statistics.
                  </p>
                </div>

                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                    <Layers className="w-6 h-6 text-green-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Visual-Text Cross-Reference
                  </h3>
                  <p className="text-gray-600 text-sm">
                    Link visual elements in documents to their text explanations for comprehensive understanding.
                  </p>
                </div>

                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                    <Image className="w-6 h-6 text-purple-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Smart Image Captioning
                  </h3>
                  <p className="text-gray-600 text-sm">
                    Generate detailed, searchable descriptions of technical diagrams and images.
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'analysis' && (
            <div className="space-y-6">
              {chartAnalysis ? (
                <ChartAnalysis
                  analysis={chartAnalysis}
                  onQuery={handleQueryFromChart}
                />
              ) : (
                <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
                  <BarChart3 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    No Chart Analysis Available
                  </h3>
                  <p className="text-gray-600 mb-6">
                    Upload a chart or graph in the Upload tab to see detailed analysis here.
                  </p>
                  <button
                    onClick={() => setActiveTab('upload')}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Upload Chart
                  </button>
                </div>
              )}
            </div>
          )}

          {activeTab === 'links' && (
            <div className="space-y-6">
              <VisualTextLinks
                links={visualLinks}
                onViewVisual={(visualId) => {
                  console.log('View visual:', visualId);
                  // Implement visual viewing
                }}
                onSearchText={(text) => {
                  setActiveTab('chat');
                  // The chat component will handle this
                }}
              />
            </div>
          )}
        </motion.div>
      </div>

      {/* Features Summary */}
      <div className="bg-gray-50 border-t border-gray-200 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Why Multi-Modal RAG is Unique
            </h2>
            <p className="text-gray-600 max-w-3xl mx-auto">
              Most RAG systems only handle text. Our multi-modal approach excels at reasoning across
              charts, diagrams, and visual data - addressing the real enterprise challenge where most
              business data is visual.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Chart Intelligence</h3>
              <p className="text-sm text-gray-600">
                Convert charts into searchable insights with data extraction and trend analysis
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Search className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Multi-Modal Search</h3>
              <p className="text-sm text-gray-600">
                Search across text, images, tables, and charts simultaneously
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Layers className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Visual-Text Links</h3>
              <p className="text-sm text-gray-600">
                Connect visual elements to explanatory text for deeper understanding
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Eye className="w-8 h-8 text-orange-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Smart Captioning</h3>
              <p className="text-sm text-gray-600">
                Generate detailed descriptions of technical diagrams and images
              </p>
            </div>
          </div>

          <div className="mt-12 text-center">
            <div className="inline-flex items-center space-x-2 bg-white rounded-full px-6 py-3 shadow-sm border">
              <span className="text-sm font-medium text-gray-900">Enterprise Ready:</span>
              <span className="text-sm text-gray-600">Handles dashboards, presentations, and business data</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}