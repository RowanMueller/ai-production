import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  Loader2,
  MessageSquare,
  Sparkles,
  RefreshCw,
  CornerDownLeft,
  BrainCircuit
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import apiClient from '../api';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  const quickSuggestions = [
    "Tell me about AAPL stock",
    "Predict TSLA price for next week",
    "Analyze MSFT performance",
    "What's the market sentiment?",
    "Get portfolio recommendations"
  ];

  useEffect(() => {
    initializeSession();
  }, []);

  useEffect(() => {
    scrollToBottom();
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeSession = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.post('/chat/start');
      setSessionId(response.data.session_id);
      setMessages([{ 
        role: 'assistant', 
        content: 'Hello! How can I assist you with your financial questions today?' 
      }]);
    } catch (error) {
      console.error('Failed to initialize session:', error);
      toast.error('Could not start a new chat session.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (message = inputMessage) => {
    if (!message.trim() || isLoading) return;

    const userMessage = { role: 'user', content: message };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await apiClient.post('/chat/send', {
        session_id: sessionId,
        message: message,
      });

      const aiResponse = { role: 'assistant', content: response.data.response };
      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const generateAIResponse = (message) => {
    const lowerMessage = message.toLowerCase();
    
    // Simple response logic
    if (lowerMessage.includes('aapl') || lowerMessage.includes('apple')) {
      return {
        content: "Apple (AAPL) is currently trading at $175.50. The stock has shown strong performance with a 5.2% increase over the past week. Technical indicators suggest a bullish trend with RSI at 65.4. Would you like me to provide a price prediction or detailed analysis?",
        confidence: 0.92,
        suggestions: [
          "Get AAPL price prediction",
          "Analyze AAPL technical indicators",
          "Check AAPL market sentiment"
        ]
      };
    } else if (lowerMessage.includes('tsla') || lowerMessage.includes('tesla')) {
      return {
        content: "Tesla (TSLA) is currently at $245.30. The stock has been volatile recently with mixed signals. Our AI models suggest a potential upward movement in the next week, but with moderate confidence. Would you like a detailed prediction analysis?",
        confidence: 0.78,
        suggestions: [
          "Predict TSLA price for next week",
          "Get TSLA technical analysis",
          "Compare TSLA with other EV stocks"
        ]
      };
    } else if (lowerMessage.includes('predict') || lowerMessage.includes('forecast')) {
      return {
        content: "I can provide stock price predictions using our advanced AI models. Which stock would you like me to predict? I can analyze historical data, technical indicators, and market sentiment to give you accurate forecasts.",
        confidence: 0.85,
        suggestions: [
          "Predict AAPL price",
          "Forecast TSLA movement",
          "Get MSFT prediction"
        ]
      };
    } else if (lowerMessage.includes('market') || lowerMessage.includes('sentiment')) {
      return {
        content: "Current market sentiment is moderately bullish. Major indices are showing positive momentum, with technology stocks leading the gains. However, there's some volatility due to economic uncertainty. Would you like specific stock analysis?",
        confidence: 0.88,
        suggestions: [
          "Get market overview",
          "Check specific stock sentiment",
          "View top performing stocks"
        ]
      };
    } else {
      return {
        content: "I'm here to help with your stock market questions! I can provide price predictions, technical analysis, market sentiment, and investment recommendations. What specific stock or topic would you like to know about?",
        confidence: 0.75,
        suggestions: [
          "Ask about a specific stock",
          "Get price predictions",
          "Request market analysis"
        ]
      };
    }
  };

  const handleSuggestionClick = (suggestion) => {
    handleSendMessage(suggestion);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: Date.now(),
        type: 'bot',
        content: "Chat cleared! How can I help you with your stock market questions?",
        timestamp: new Date(),
        suggestions: quickSuggestions.slice(0, 3)
      }
    ]);
    setSuggestions([]);
  };

  const Message = ({ role, content }) => {
    const isUser = role === 'user';
    const Icon = isUser ? User : BrainCircuit;

    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`flex items-start gap-3 my-4 ${isUser ? 'justify-end' : ''}`}
      >
        {!isUser && (
          <div className="flex-shrink-0 h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white">
            <Icon size={20} />
          </div>
        )}
        <div
          className={`px-4 py-3 rounded-xl max-w-lg ${
            isUser
              ? 'bg-blue-600 text-white rounded-br-none'
              : 'bg-gray-200 text-gray-800 rounded-bl-none'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap">{content}</p>
        </div>
        {isUser && (
          <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center text-gray-600">
            <Icon size={20} />
          </div>
        )}
      </motion.div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-md">
      {/* Header */}
      <div className="p-4 border-b">
        <h1 className="text-xl font-bold text-gray-900">AI Financial Chatbot</h1>
        <p className="text-sm text-gray-500">Your personal finance assistant</p>
      </div>
      
      {/* Chat Messages */}
      <div ref={chatContainerRef} className="flex-1 p-6 overflow-y-auto">
        <AnimatePresence>
          {messages.map((msg, index) => (
            <Message key={index} role={msg.role} content={msg.content} />
          ))}
          {isLoading && messages.length > 0 && messages[messages.length - 1].role === 'user' && (
             <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-start gap-3 my-4"
            >
              <div className="flex-shrink-0 h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white">
                <Loader2 size={20} className="animate-spin" />
              </div>
              <div className="px-4 py-3 rounded-xl max-w-lg bg-gray-200 text-gray-800 rounded-bl-none">
                <p className="text-sm">Thinking...</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      
      {/* Message Input */}
      <div className="p-4 border-t bg-gray-50">
        <div className="relative">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about stocks, markets, or financial concepts..."
            className="w-full pl-4 pr-20 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 resize-none"
            rows="2"
            disabled={isLoading}
          />
          <button
            onClick={() => handleSendMessage()}
            disabled={!inputMessage.trim() || isLoading}
            className="absolute right-3 top-1/2 -translate-y-1/2 btn-primary p-2 h-10 w-14 flex items-center justify-center"
          >
            <Send size={18} />
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2 flex items-center">
          <CornerDownLeft size={12} className="mr-1" />
          Shift + Enter for new line.
        </p>
      </div>
    </div>
  );
};

export default Chatbot; 