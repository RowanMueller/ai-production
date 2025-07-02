import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Filter, 
  Search, 
  Calendar,
  Clock,
  Flag,
  CheckCircle,
  Circle,
  AlertCircle,
  MoreVertical,
  Edit,
  Trash2,
  Sparkles,
  Loader2,
  CheckSquare,
  Square
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import apiClient from '../api';

const TaskManager = () => {
  const [tasks, setTasks] = useState([]);
  const [showAddTask, setShowAddTask] = useState(false);
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('priority');
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(true);

  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    priority: '',
    category: '',
    dueDate: '',
    estimatedTime: ''
  });

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    setIsFetching(true);
    try {
      const response = await apiClient.get('/tasks');
      setTasks(response.data.tasks);
    } catch (error) {
      console.error("Failed to fetch tasks", error);
    } finally {
      setIsFetching(false);
    }
  };

  const handleAddTask = async () => {
    if (!newTask.title.trim()) {
      toast.error('Task title is required');
      return;
    }

    setIsLoading(true);
    try {
      const response = await apiClient.post('/tasks', { ...newTask });
      const createdTask = response.data;
      setTasks(prev => [createdTask, ...prev].sort((a, b) => b.priority - a.priority));
      setNewTask({
        title: '',
        description: '',
        priority: '',
        category: '',
        dueDate: '',
        estimatedTime: ''
      });
      setShowAddTask(false);
      toast.success('Task added and prioritized successfully!');
    } catch (error) {
      console.error('Failed to create task:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateTask = async (id, updates) => {
    const originalTasks = [...tasks];
    const updatedTasks = tasks.map(t => t.id === id ? { ...t, ...updates } : t);
    setTasks(updatedTasks);

    try {
      await apiClient.put(`/tasks/${id}`, updates);
      toast.success('Task updated!');
    } catch (error) {
      setTasks(originalTasks);
      console.error('Failed to update task:', error);
    }
  };

  const handleDeleteTask = async (id) => {
    const originalTasks = [...tasks];
    setTasks(tasks.filter(t => t.id !== id));
    
    try {
      await apiClient.delete(`/tasks/${id}`);
      toast.success('Task deleted successfully');
    } catch (error) {
      setTasks(originalTasks);
      console.error('Failed to delete task', error);
    }
  };

  const getPriorityColor = (priority) => {
    if (priority > 7) return 'text-red-600 bg-red-100';
    if (priority > 4) return 'text-orange-600 bg-orange-100';
    return 'text-green-600 bg-green-100';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'in_progress': return 'text-blue-600 bg-blue-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4" />;
      case 'in_progress': return <AlertCircle className="h-4 w-4" />;
      case 'pending': return <Circle className="h-4 w-4" />;
      default: return <Circle className="h-4 w-4" />;
    }
  };

  const filteredTasks = tasks
    .filter(task => {
      if (filter !== 'all' && task.status !== filter) return false;
      if (searchTerm && !task.title.toLowerCase().includes(searchTerm.toLowerCase())) return false;
      return true;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'priority':
          return b.priority - a.priority;
        case 'dueDate':
          return new Date(a.dueDate || '9999-12-31') - new Date(b.dueDate || '9999-12-31');
        case 'createdAt':
          return new Date(b.createdAt) - new Date(a.createdAt);
        default:
          return b.priority - a.priority;
      }
    });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">AI-Powered Task Manager</h1>
        <p className="mt-2 text-gray-600">
          Your tasks are automatically prioritized by our AI to maximize your productivity.
        </p>
      </div>

      {/* Controls */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div className="flex flex-col sm:flex-row gap-4 flex-1">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search tasks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input pl-10"
              />
            </div>

            {/* Filter */}
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="input"
            >
              <option value="all">All Tasks</option>
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
            </select>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="input"
            >
              <option value="priority">Sort by Priority</option>
              <option value="dueDate">Sort by Due Date</option>
              <option value="createdAt">Sort by Created</option>
            </select>
          </div>

          <button
            onClick={() => setShowAddTask(true)}
            className="btn-primary flex items-center"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Task
          </button>
        </div>
      </motion.div>

      {/* Add Task Modal */}
      <AnimatePresence>
        {showAddTask && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowAddTask(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="card w-full max-w-md"
              onClick={(e) => e.stopPropagation()}
            >
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Add New Task</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Title *
                  </label>
                  <input
                    type="text"
                    value={newTask.title}
                    onChange={(e) => setNewTask(prev => ({ ...prev, title: e.target.value }))}
                    className="input"
                    placeholder="Enter task title"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={newTask.description}
                    onChange={(e) => setNewTask(prev => ({ ...prev, description: e.target.value }))}
                    className="input"
                    rows="3"
                    placeholder="Enter task description"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Category
                    </label>
                    <select
                      value={newTask.category}
                      onChange={(e) => setNewTask(prev => ({ ...prev, category: e.target.value }))}
                      className="input"
                    >
                      <option value="">Select category</option>
                      <option value="work">Work</option>
                      <option value="personal">Personal</option>
                      <option value="financial">Financial</option>
                      <option value="learning">Learning</option>
                      <option value="research">Research</option>
                      <option value="strategy">Strategy</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Due Date
                    </label>
                    <input
                      type="date"
                      value={newTask.dueDate}
                      onChange={(e) => setNewTask(prev => ({ ...prev, dueDate: e.target.value }))}
                      className="input"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Estimated Time (hours)
                  </label>
                  <input
                    type="number"
                    value={newTask.estimatedTime}
                    onChange={(e) => setNewTask(prev => ({ ...prev, estimatedTime: e.target.value }))}
                    className="input"
                    placeholder="2"
                    min="0"
                    step="0.5"
                  />
                </div>

                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Sparkles className="h-4 w-4 text-primary-600" />
                  <span>AI will automatically assign priority based on content</span>
                </div>
              </div>

              <div className="flex space-x-3 mt-6">
                <button
                  onClick={() => setShowAddTask(false)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddTask}
                  disabled={isLoading || !newTask.title.trim()}
                  className="btn-primary flex-1 flex items-center justify-center"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <Plus className="h-4 w-4 mr-2" />
                  )}
                  {isLoading ? 'Creating...' : 'Create Task'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Tasks List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-4"
      >
        {isFetching ? (
          <div className="text-center py-8">
            <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary-600" />
            <p className="mt-2 text-gray-500">Loading tasks...</p>
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="card text-center py-12">
            <Circle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No tasks found</h3>
            <p className="text-gray-500">
              {searchTerm ? 'Try adjusting your search terms' : 'Create your first task to get started'}
            </p>
          </div>
        ) : (
          filteredTasks.map((task) => (
            <motion.div
              key={task.id}
              layout
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className={`flex items-center justify-between p-4 rounded-lg border ${
                task.status === 'completed' ? 'bg-gray-100' : 'bg-white'
              }`}
            >
              <div className="flex items-center gap-4">
                <button onClick={() => handleUpdateTask(task.id, { status: task.status === 'completed' ? 'pending' : 'completed' })}>
                  {task.status === 'completed' ? <CheckSquare className="h-6 w-6 text-green-500" /> : <Square className="h-6 w-6 text-gray-400" />}
                </button>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-2">
                    <h3 className={`text-lg font-medium ${
                      task.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-900'
                    }`}>
                      {task.title}
                    </h3>
                    <span className={`badge ${getPriorityColor(task.priority)}`}>
                      P{task.priority}
                    </span>
                    <span className={`badge ${getStatusColor(task.status)}`}>
                      {task.status.replace('_', ' ')}
                    </span>
                  </div>
                  
                  {task.description && (
                    <p className="text-gray-600 mb-3">{task.description}</p>
                  )}
                  
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    {task.category && (
                      <span className="capitalize">{task.category}</span>
                    )}
                    {task.dueDate && (
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 mr-1" />
                        {new Date(task.dueDate).toLocaleDateString()}
                      </div>
                    )}
                    {task.estimatedTime && (
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {task.estimatedTime}h
                      </div>
                    )}
                  </div>
                  
                  {task.aiReasoning && (
                    <div className="mt-3 p-2 bg-primary-50 rounded-lg">
                      <div className="flex items-start space-x-2">
                        <Sparkles className="h-4 w-4 text-primary-600 mt-0.5 flex-shrink-0" />
                        <p className="text-sm text-primary-800">{task.aiReasoning}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-4">
                <button
                  onClick={() => handleDeleteTask(task.id)}
                  className="text-gray-400 hover:text-red-500"
                  title="Delete task"
                >
                  <Trash2 className="h-5 w-5" />
                </button>
              </div>
            </motion.div>
          ))
        )}
      </motion.div>
    </div>
  );
};

export default TaskManager; 