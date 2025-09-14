'use client';

import React, { useState } from 'react';
import { Link2, Image, FileText, Eye, Search, Filter } from 'lucide-react';

interface VisualTextLink {
  visual_id: string;
  relationship: string;
  confidence: number;
  text_snippets: string[];
}

interface VisualTextLinksProps {
  links: VisualTextLink[];
  onViewVisual?: (visualId: string) => void;
  onSearchText?: (text: string) => void;
  className?: string;
}

const VisualTextLinks: React.FC<VisualTextLinksProps> = ({
  links,
  onViewVisual,
  onSearchText,
  className = ''
}) => {
  const [filter, setFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'confidence' | 'relationship'>('confidence');

  const relationshipTypes = Array.from(new Set(links.map(link => link.relationship)));

  const filteredLinks = links
    .filter(link => filter === 'all' || link.relationship === filter)
    .sort((a, b) => {
      if (sortBy === 'confidence') {
        return b.confidence - a.confidence;
      }
      return a.relationship.localeCompare(b.relationship);
    });

  const getRelationshipColor = (relationship: string) => {
    const colors: { [key: string]: string } = {
      'illustration': 'bg-blue-100 text-blue-800',
      'example': 'bg-green-100 text-green-800',
      'data_visualization': 'bg-purple-100 text-purple-800',
      'reference': 'bg-yellow-100 text-yellow-800',
      'explanation': 'bg-orange-100 text-orange-800',
      'general': 'bg-gray-100 text-gray-800'
    };
    return colors[relationship] || colors.general;
  };

  const getConfidenceBar = (confidence: number) => {
    const percentage = confidence * 100;
    const color = confidence >= 0.8 ? 'bg-green-500' :
                  confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500';

    return (
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full ${color}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    );
  };

  if (links.length === 0) {
    return (
      <div className={`bg-white rounded-lg border p-6 text-center ${className}`}>
        <Link2 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Visual-Text Links</h3>
        <p className="text-gray-500">
          Upload documents with images to see visual-text relationships
        </p>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header and Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Link2 className="w-5 h-5" />
            Visual-Text Links ({filteredLinks.length})
          </h3>
          <p className="text-sm text-gray-600">
            Cross-references between visual elements and text explanations
          </p>
        </div>

        <div className="flex gap-2">
          {/* Relationship Filter */}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Relationships</option>
            {relationshipTypes.map(type => (
              <option key={type} value={type} className="capitalize">
                {type.replace('_', ' ')}
              </option>
            ))}
          </select>

          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'confidence' | 'relationship')}
            className="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="confidence">By Confidence</option>
            <option value="relationship">By Relationship</option>
          </select>
        </div>
      </div>

      {/* Links List */}
      <div className="space-y-3">
        {filteredLinks.map((link, index) => (
          <div
            key={index}
            className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-50 rounded-lg">
                  <Image className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">
                    Visual Element {link.visual_id.split('_').slice(-2).join('_')}
                  </h4>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRelationshipColor(link.relationship)}`}>
                      {link.relationship.replace('_', ' ')}
                    </span>
                    <span className="text-xs text-gray-500">
                      {(link.confidence * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex gap-2">
                {onViewVisual && (
                  <button
                    onClick={() => onViewVisual(link.visual_id)}
                    className="p-2 text-gray-400 hover:text-blue-600 rounded-lg hover:bg-blue-50"
                    title="View visual element"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>

            {/* Confidence Bar */}
            <div className="mb-3">
              <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                <span>Confidence Score</span>
                <span>{(link.confidence * 100).toFixed(0)}%</span>
              </div>
              {getConfidenceBar(link.confidence)}
            </div>

            {/* Text Snippets */}
            <div>
              <h5 className="text-sm font-medium text-gray-900 mb-2 flex items-center gap-1">
                <FileText className="w-4 h-4" />
                Related Text Snippets
              </h5>
              <div className="space-y-2">
                {link.text_snippets.map((snippet, snippetIndex) => (
                  <div
                    key={snippetIndex}
                    className={`
                      p-3 bg-gray-50 rounded text-sm text-gray-700 leading-relaxed
                      ${onSearchText ? 'cursor-pointer hover:bg-gray-100 transition-colors' : ''}
                    `}
                    onClick={() => onSearchText?.(snippet)}
                  >
                    <span>{snippet}</span>
                    {onSearchText && (
                      <button
                        className="ml-2 text-blue-600 hover:text-blue-800"
                        title="Search this text"
                      >
                        <Search className="w-3 h-3 inline" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2">Relationship Summary</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {relationshipTypes.map(type => {
            const count = links.filter(link => link.relationship === type).length;
            const avgConfidence = links
              .filter(link => link.relationship === type)
              .reduce((sum, link) => sum + link.confidence, 0) / count;

            return (
              <div key={type} className="text-center">
                <div className={`px-2 py-1 rounded text-xs font-medium mb-1 ${getRelationshipColor(type)}`}>
                  {type.replace('_', ' ')}
                </div>
                <p className="text-xs text-gray-600">
                  {count} links • {(avgConfidence * 100).toFixed(0)}% avg
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default VisualTextLinks;