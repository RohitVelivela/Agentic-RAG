'use client';

import React, { useState, useRef } from 'react';
import { Send, Image, BarChart3, Sparkles, Loader2 } from 'lucide-react';
import ChatMessage from './ChatMessage';
import ChartAnalysis from './ChartAnalysis';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  multimodal?: {
    chart_analysis?: any;
    visual_links?: any[];
    enhanced_context?: boolean;
  };
  timestamp: Date;
}

interface MultiModalChatProps {
  className?: string;
}

const MultiModalChat: React.FC<MultiModalChatProps> = ({ className = '' }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: 'Hello! I can help you analyze documents, charts, and images with advanced multi-modal reasoning. Try asking me about any data visualizations or technical diagrams you\'ve uploaded.',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [useMultiModal, setUseMultiModal] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Choose endpoint based on multi-modal setting
      const endpoint = useMultiModal ? '/multimodal/query' : '/query';

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: input,
          num_results: 5,
          include_web_search: true,
          include_drive_search: true
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.answer,
        multimodal: useMultiModal ? {
          enhanced_context: data.metadata?.multimodal_enhancement || false,
          visual_links: data.metadata?.visual_links || []
        } : undefined,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I encountered an error while processing your request. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQueryFromChart = (fact: string) => {
    setInput(fact);
  };

  const exampleQueries = [
    "What trends do you see in the sales data?",
    "Explain the charts in the uploaded document",
    "Compare the performance metrics across different quarters",
    "What insights can you extract from the technical diagrams?"
  ];

  return (
    <div className={`flex flex-col h-full bg-white ${className}`}>
      {/* Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-500" />
            Multi-Modal AI Assistant
          </h2>

          <div className="flex items-center gap-2">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={useMultiModal}
                onChange={(e) => setUseMultiModal(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-gray-700">Enhanced Multi-Modal</span>
            </label>
          </div>
        </div>

        {useMultiModal && (
          <div className="mt-2 text-sm text-blue-600 bg-blue-50 rounded-lg p-2">
            🚀 Multi-modal reasoning enabled: I can analyze charts, link visuals to text, and provide enhanced insights!
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id}>
            <ChatMessage
              message={message.content}
              isUser={message.type === 'user'}
              timestamp={message.timestamp}
            />

            {/* Multi-modal enhancements */}
            {message.multimodal?.chart_analysis && (
              <div className="mt-3 ml-12">
                <ChartAnalysis
                  analysis={message.multimodal.chart_analysis}
                  onQuery={handleQueryFromChart}
                />
              </div>
            )}

            {message.multimodal?.enhanced_context && (
              <div className="mt-2 ml-12 text-xs text-blue-600 bg-blue-50 rounded px-2 py-1 inline-block">
                ✨ Enhanced with visual context
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center gap-2 text-gray-500">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Analyzing with multi-modal reasoning...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Example Queries */}
      {messages.length === 1 && (
        <div className="px-4 pb-2">
          <div className="text-sm text-gray-600 mb-2">Try these multi-modal queries:</div>
          <div className="flex flex-wrap gap-2">
            {exampleQueries.map((query, index) => (
              <button
                key={index}
                onClick={() => setInput(query)}
                className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded-full transition-colors"
              >
                {query}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="border-t border-gray-200 p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="flex-1 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={useMultiModal
                ? "Ask about charts, images, or any document content..."
                : "Ask a question..."
              }
              className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={isLoading}
            />

            {useMultiModal && (
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex gap-1">
                <BarChart3 className="w-4 h-4 text-blue-400" title="Chart analysis enabled" />
                <Image className="w-4 h-4 text-green-400" title="Image analysis enabled" />
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default MultiModalChat;