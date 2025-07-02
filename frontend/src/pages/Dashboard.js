import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  TrendingUp, 
  MessageSquare, 
  CheckSquare, 
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  Users,
  DollarSign,
  Target,
  ListChecks,
  CheckCircle,
  Loader2
} from 'lucide-react';
import { motion } from 'framer-motion';
import apiClient from '../api';
import toast from 'react-hot-toast';

const StatCard = ({ icon, title, value, isLoading }) => (
  <motion.div 
    className="card"
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
  >
    <div className="flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <div className="bg-primary-100 p-3 rounded-full">
          {icon}
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          {isLoading ? (
            <Loader2 className="h-6 w-6 animate-spin text-primary-600" />
          ) : (
            <p className="text-2xl font-semibold text-gray-900">{value}</p>
          )}
        </div>
      </div>
    </div>
  </motion.div>
);

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalPredictions: 0,
    activeChats: 0,
    pendingTasks: 0,
    modelAccuracy: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      setIsLoading(true);
      try {
        const response = await apiClient.get('/stats');
        setStats(response.data);
      } catch (error) {
        console.error("Failed to fetch dashboard stats", error);
        toast.error('Could not load dashboard statistics.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  const quickActions = [
    {
      title: 'Predict Stock Price',
      description: 'Get AI-powered stock price predictions',
      icon: TrendingUp,
      href: '/predictor',
      color: 'bg-blue-500',
      textColor: 'text-blue-500'
    },
    {
      title: 'Chat with AI',
      description: 'Ask questions about stocks and markets',
      icon: MessageSquare,
      href: '/chatbot',
      color: 'bg-green-500',
      textColor: 'text-green-500'
    },
    {
      title: 'Manage Tasks',
      description: 'Organize and prioritize your tasks',
      icon: CheckSquare,
      href: '/tasks',
      color: 'bg-purple-500',
      textColor: 'text-purple-500'
    }
  ];

  const recentActivity = [
    {
      type: 'prediction',
      message: 'Predicted AAPL price for next week',
      time: '2 minutes ago',
      icon: TrendingUp,
      color: 'text-blue-500'
    },
    {
      type: 'chat',
      message: 'Chat session started with AI assistant',
      time: '5 minutes ago',
      icon: MessageSquare,
      color: 'text-green-500'
    },
    {
      type: 'task',
      message: 'New task created: Review portfolio',
      time: '10 minutes ago',
      icon: CheckSquare,
      color: 'text-purple-500'
    }
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">AI Platform Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome back! Here's a snapshot of your AI-powered activities.
        </p>
      </div>
      
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          icon={<TrendingUp className="h-6 w-6 text-primary-600" />}
          title="Total Predictions"
          value={stats.totalPredictions}
          isLoading={isLoading}
        />
        <StatCard
          icon={<MessageSquare className="h-6 w-6 text-primary-600" />}
          title="Active Chats"
          value={stats.activeChats}
          isLoading={isLoading}
        />
        <StatCard
          icon={<ListChecks className="h-6 w-6 text-primary-600" />}
          title="Pending Tasks"
          value={stats.pendingTasks}
          isLoading={isLoading}
        />
        <StatCard
          icon={<CheckCircle className="h-6 w-6 text-primary-600" />}
          title="Model Accuracy"
          value={`${stats.modelAccuracy.toFixed(1)}%`}
          isLoading={isLoading}
        />
      </div>

      {/* Placeholder for more charts and recent activity */}
      <div className="card">
         <h2 className="text-lg font-semibold text-gray-900 mb-4">Activity Overview</h2>
         <div className="text-center py-12">
            <p className="text-gray-500">More charts and activity feeds coming soon!</p>
         </div>
      </div>
    </div>
  );
};

export default Dashboard; 