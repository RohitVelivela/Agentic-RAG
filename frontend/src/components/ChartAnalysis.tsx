'use client';

import React, { useState } from 'react';
import { BarChart3, TrendingUp, Database, Eye, Download, Share } from 'lucide-react';

interface ChartAnalysisProps {
  analysis: {
    chart_type: string;
    text_description: string;
    data_insights: {
      data_points: Array<{
        category: string;
        value: number;
        series?: string;
      }>;
      trends: string[];
      key_statistics: {
        highest?: { category: string; value: number };
        lowest?: { category: string; value: number };
        average?: number;
        total?: number;
      };
      insights: string[];
    };
    queryable_facts: string[];
    confidence: number;
  };
  onQuery?: (fact: string) => void;
  className?: string;
}

const ChartAnalysis: React.FC<ChartAnalysisProps> = ({
  analysis,
  onQuery,
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'data' | 'insights' | 'facts'>('overview');

  const getChartTypeIcon = (type: string) => {
    return <BarChart3 className="w-5 h-5" />;
  };

  const formatValue = (value: number) => {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    }
    if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K`;
    }
    return value.toString();
  };

  const confidenceColor = analysis.confidence >= 0.8 ? 'text-green-600' :
                         analysis.confidence >= 0.6 ? 'text-yellow-600' : 'text-red-600';

  return (
    <div className={`bg-white rounded-lg border shadow-sm ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-3">
          {getChartTypeIcon(analysis.chart_type)}
          <div>
            <h3 className="font-semibold text-gray-900 capitalize">
              {analysis.chart_type.replace('_', ' ')} Analysis
            </h3>
            <p className={`text-sm ${confidenceColor}`}>
              Confidence: {(analysis.confidence * 100).toFixed(0)}%
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
            <Download className="w-4 h-4" />
          </button>
          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
            <Share className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b">
        {[
          { id: 'overview', label: 'Overview', icon: Eye },
          { id: 'data', label: 'Data', icon: Database },
          { id: 'insights', label: 'Insights', icon: TrendingUp },
          { id: 'facts', label: 'Queryable Facts', icon: BarChart3 }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`
              flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors
              ${activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
              }
            `}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="p-4">
        {activeTab === 'overview' && (
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Description</h4>
              <p className="text-gray-700 text-sm leading-relaxed">
                {analysis.text_description}
              </p>
            </div>

            {analysis.data_insights.key_statistics && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Key Statistics</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {analysis.data_insights.key_statistics.highest && (
                    <div className="bg-green-50 p-3 rounded-lg">
                      <p className="text-xs text-green-600 font-medium">Highest</p>
                      <p className="text-lg font-bold text-green-900">
                        {formatValue(analysis.data_insights.key_statistics.highest.value)}
                      </p>
                      <p className="text-xs text-green-700">
                        {analysis.data_insights.key_statistics.highest.category}
                      </p>
                    </div>
                  )}

                  {analysis.data_insights.key_statistics.lowest && (
                    <div className="bg-red-50 p-3 rounded-lg">
                      <p className="text-xs text-red-600 font-medium">Lowest</p>
                      <p className="text-lg font-bold text-red-900">
                        {formatValue(analysis.data_insights.key_statistics.lowest.value)}
                      </p>
                      <p className="text-xs text-red-700">
                        {analysis.data_insights.key_statistics.lowest.category}
                      </p>
                    </div>
                  )}

                  {analysis.data_insights.key_statistics.average && (
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <p className="text-xs text-blue-600 font-medium">Average</p>
                      <p className="text-lg font-bold text-blue-900">
                        {formatValue(analysis.data_insights.key_statistics.average)}
                      </p>
                    </div>
                  )}

                  {analysis.data_insights.key_statistics.total && (
                    <div className="bg-purple-50 p-3 rounded-lg">
                      <p className="text-xs text-purple-600 font-medium">Total</p>
                      <p className="text-lg font-bold text-purple-900">
                        {formatValue(analysis.data_insights.key_statistics.total)}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'data' && (
          <div className="space-y-4">
            {analysis.data_insights.data_points.length > 0 ? (
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Data Points</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-2 font-medium text-gray-900">Category</th>
                        <th className="text-right py-2 font-medium text-gray-900">Value</th>
                        {analysis.data_insights.data_points.some(p => p.series) && (
                          <th className="text-left py-2 font-medium text-gray-900">Series</th>
                        )}
                      </tr>
                    </thead>
                    <tbody>
                      {analysis.data_insights.data_points.slice(0, 10).map((point, index) => (
                        <tr key={index} className="border-b border-gray-100">
                          <td className="py-2 text-gray-900">{point.category}</td>
                          <td className="py-2 text-right font-mono text-gray-900">
                            {formatValue(point.value)}
                          </td>
                          {analysis.data_insights.data_points.some(p => p.series) && (
                            <td className="py-2 text-gray-600">{point.series || '-'}</td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {analysis.data_insights.data_points.length > 10 && (
                    <p className="text-xs text-gray-500 mt-2">
                      Showing first 10 of {analysis.data_insights.data_points.length} data points
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No specific data points extracted</p>
            )}
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="space-y-4">
            {analysis.data_insights.trends.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Trends</h4>
                <ul className="space-y-2">
                  {analysis.data_insights.trends.map((trend, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <TrendingUp className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{trend}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {analysis.data_insights.insights.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Key Insights</h4>
                <ul className="space-y-2">
                  {analysis.data_insights.insights.map((insight, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <Eye className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{insight}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {analysis.data_insights.trends.length === 0 && analysis.data_insights.insights.length === 0 && (
              <p className="text-gray-500 text-sm">No specific insights extracted</p>
            )}
          </div>
        )}

        {activeTab === 'facts' && (
          <div className="space-y-3">
            <h4 className="font-medium text-gray-900">Searchable Facts</h4>
            {analysis.queryable_facts.length > 0 ? (
              <div className="space-y-2">
                {analysis.queryable_facts.map((fact, index) => (
                  <div
                    key={index}
                    className={`
                      p-3 bg-gray-50 rounded-lg text-sm
                      ${onQuery ? 'cursor-pointer hover:bg-gray-100 transition-colors' : ''}
                    `}
                    onClick={() => onQuery?.(fact)}
                  >
                    <span className="text-gray-900">{fact}</span>
                    {onQuery && (
                      <span className="text-blue-600 text-xs ml-2">(click to search)</span>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No queryable facts extracted</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChartAnalysis;