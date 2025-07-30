import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Plus, 
  MessageSquare, 
  Send, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  User,
  Bot,
  Filter,
  Search,
  MoreHorizontal,
  Edit,
  Trash2,
  Eye
} from 'lucide-react';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

import { apiService } from '../services/apiService';
import LoadingSpinner from './LoadingSpinner';

const AutomationRequests = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('requests'); // 'requests' or 'create'
  const [requests, setRequests] = useState([]);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  
  // Create new request form
  const [newRequest, setNewRequest] = useState({
    title: '',
    description: '',
    priority: 'medium'
  });

  // Chat system
  const [chatMessages, setChatMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [sendingMessage, setSendingMessage] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadRequests();
  }, []);

  useEffect(() => {
    if (selectedRequest) {
      loadChatMessages(selectedRequest._id);
    }
  }, [selectedRequest]);

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadRequests = async () => {
    try {
      setLoading(true);
      // For demo, we'll use mock data
      // In production: const result = await apiService.automation.getRequests();
      
      setTimeout(() => {
        const mockRequests = [
          {
            _id: '1',
            title: 'Automated Patient Intake Process',
            description: 'Need automation for patient intake forms and initial screening workflow',
            priority: 'high',
            status: 'in_progress',
            created_at: '2024-01-15T09:00:00Z',
            updated_at: '2024-01-16T14:30:00Z',
            user_id: user?.user_id,
            user_name: user?.full_name,
            admin_notes: 'Working on initial requirements gathering'
          },
          {
            _id: '2', 
            title: 'Insurance Verification Automation',
            description: 'Automate the insurance verification process to reduce manual work',
            priority: 'medium',
            status: 'pending',
            created_at: '2024-01-14T11:15:00Z',
            updated_at: '2024-01-14T11:15:00Z',
            user_id: user?.user_id,
            user_name: user?.full_name,
            admin_notes: null
          },
          {
            _id: '3',
            title: 'Appointment Reminder System',
            description: 'Set up automated appointment reminders via SMS and email',
            priority: 'low',
            status: 'completed',
            created_at: '2024-01-10T08:45:00Z',
            updated_at: '2024-01-13T16:20:00Z',
            user_id: user?.user_id,
            user_name: user?.full_name,
            admin_notes: 'Successfully implemented and tested'
          }
        ];
        
        setRequests(mockRequests);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Failed to load requests:', error);
      toast.error('Failed to load automation requests');
      setLoading(false);
    }
  };

  const loadChatMessages = async (requestId) => {
    try {
      // Mock chat messages for demo
      const mockMessages = [
        {
          _id: '1',
          message: 'Hi! I submitted a request for automating our patient intake process. Can you help me with the requirements?',
          sender_type: 'user',
          sender_name: user?.full_name,
          created_at: '2024-01-15T09:30:00Z'
        },
        {
          _id: '2',
          message: 'Hello! Thanks for your automation request. I\'ve reviewed the details and have a few questions: 1) What specific forms need to be automated? 2) Do you need integration with existing EMR systems? 3) What\'s your preferred timeline?',
          sender_type: 'admin',
          sender_name: 'Admin Support',
          created_at: '2024-01-15T10:15:00Z'
        },
        {
          _id: '3',
          message: 'Great questions! 1) We need to automate the initial patient information form, insurance details, and medical history. 2) Yes, we use Epic EMR system. 3) Ideally within 2-3 weeks if possible.',
          sender_type: 'user',
          sender_name: user?.full_name,
          created_at: '2024-01-15T14:20:00Z'
        },
        {
          _id: '4',
          message: 'Perfect! Epic integration is definitely possible. I\'ll prepare a detailed implementation plan and timeline. Expect an update by tomorrow with the technical specifications and project roadmap.',
          sender_type: 'admin',
          sender_name: 'Admin Support',
          created_at: '2024-01-16T09:45:00Z'
        }
      ];
      
      setChatMessages(mockMessages);
    } catch (error) {
      console.error('Failed to load chat messages:', error);
      toast.error('Failed to load chat messages');
    }
  };

  const createRequest = async (e) => {
    e.preventDefault();
    
    if (!newRequest.title.trim() || !newRequest.description.trim()) {
      toast.error('Please fill in all required fields');
      return;
    }

    setCreating(true);
    try {
      // In production: const result = await apiService.automation.createRequest(newRequest);
      
      // Mock successful creation
      setTimeout(() => {
        const mockNewRequest = {
          _id: Date.now().toString(),
          ...newRequest,
          status: 'pending',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          user_id: user?.user_id,
          user_name: user?.full_name,
          admin_notes: null
        };
        
        setRequests(prev => [mockNewRequest, ...prev]);
        setNewRequest({ title: '', description: '', priority: 'medium' });
        setActiveTab('requests');
        toast.success('Automation request created successfully! 🚀');
        setCreating(false);
      }, 1500);
    } catch (error) {
      console.error('Failed to create request:', error);
      toast.error('Failed to create automation request');
      setCreating(false);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim() || !selectedRequest) return;

    setSendingMessage(true);
    try {
      const message = {
        _id: Date.now().toString(),
        message: newMessage.trim(),
        sender_type: 'user',
        sender_name: user?.full_name,
        created_at: new Date().toISOString()
      };

      setChatMessages(prev => [...prev, message]);
      setNewMessage('');
      
      // Simulate admin response after delay
      setTimeout(() => {
        const adminResponse = {
          _id: (Date.now() + 1).toString(),
          message: 'Thanks for your message! I\'ll review this and get back to you shortly with an update.',
          sender_type: 'admin',
          sender_name: 'Admin Support',
          created_at: new Date().toISOString()
        };
        setChatMessages(prev => [...prev, adminResponse]);
      }, 2000);

      toast.success('Message sent!');
    } catch (error) {
      console.error('Failed to send message:', error);
      toast.error('Failed to send message');
    } finally {
      setSendingMessage(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'in_progress': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'completed': return 'bg-green-100 text-green-800 border-green-200';
      case 'cancelled': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const filteredRequests = requests.filter(request => {
    const matchesSearch = request.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         request.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || request.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="healthcare-gradient shadow-medical-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Link
                to="/dashboard"
                className="bg-white/20 hover:bg-white/30 text-white p-2 rounded-lg mr-4 transition-colors"
              >
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <div>
                <h1 className="text-xl font-bold text-white">🤖 Automation Requests</h1>
                <p className="text-white/80 text-sm">Request and track automation projects</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-white/80">{user?.full_name}</span>
              <button
                onClick={onLogout}
                className="bg-red-500/20 hover:bg-red-500/30 border border-red-400/30 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="medical-card p-1 rounded-xl mb-8 inline-flex">
          <button
            onClick={() => setActiveTab('requests')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              activeTab === 'requests'
                ? 'bg-hss-primary text-white shadow-md'
                : 'text-gray-600 hover:text-hss-primary'
            }`}
          >
            My Requests ({requests.length})
          </button>
          <button
            onClick={() => setActiveTab('create')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              activeTab === 'create'
                ? 'bg-hss-primary text-white shadow-md'
                : 'text-gray-600 hover:text-hss-primary'
            }`}
          >
            Create New Request
          </button>
        </div>

        {/* Requests List Tab */}
        {activeTab === 'requests' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Requests List */}
            <div className="lg:col-span-2">
              {/* Search and Filter */}
              <div className="medical-card p-6 rounded-xl mb-6">
                <div className="flex flex-col sm:flex-row gap-4">
                  <div className="flex-1 relative">
                    <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search requests..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hss-primary focus:border-transparent"
                    />
                  </div>
                  <div className="relative">
                    <Filter className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                    <select
                      value={filterStatus}
                      onChange={(e) => setFilterStatus(e.target.value)}
                      className="pl-10 pr-8 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hss-primary focus:border-transparent"
                    >
                      <option value="all">All Status</option>
                      <option value="pending">Pending</option>
                      <option value="in_progress">In Progress</option>
                      <option value="completed">Completed</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Requests */}
              {loading ? (
                <div className="space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="medical-card p-6 rounded-xl">
                      <div className="animate-pulse">
                        <div className="h-4 bg-gray-200 rounded mb-3"></div>
                        <div className="h-6 bg-gray-200 rounded mb-4"></div>
                        <div className="flex space-x-2 mb-4">
                          <div className="h-6 w-20 bg-gray-200 rounded"></div>
                          <div className="h-6 w-16 bg-gray-200 rounded"></div>
                        </div>
                        <div className="h-4 bg-gray-200 rounded"></div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : filteredRequests.length === 0 ? (
                <div className="medical-card p-12 rounded-xl text-center">
                  <MessageSquare className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-600 mb-2">No Requests Found</h3>
                  <p className="text-gray-500 mb-6">
                    {searchTerm || filterStatus !== 'all' 
                      ? 'No requests match your search criteria.'
                      : 'You haven\'t created any automation requests yet.'
                    }
                  </p>
                  <button
                    onClick={() => setActiveTab('create')}
                    className="medical-button px-6 py-3 text-white font-medium rounded-lg"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Create First Request
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredRequests.map((request) => (
                    <div
                      key={request._id}
                      className={`medical-card p-6 rounded-xl hover-lift cursor-pointer transition-all ${
                        selectedRequest?._id === request._id ? 'ring-2 ring-hss-primary' : ''
                      }`}
                      onClick={() => setSelectedRequest(request)}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <h3 className="text-lg font-semibold text-hss-primary">{request.title}</h3>
                        <div className="flex items-center space-x-2">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(request.status)}`}>
                            {request.status.replace('_', ' ').toUpperCase()}
                          </span>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getPriorityColor(request.priority)}`}>
                            {request.priority.toUpperCase()}
                          </span>
                        </div>
                      </div>
                      
                      <p className="text-gray-600 mb-4 line-clamp-2">{request.description}</p>
                      
                      <div className="flex items-center justify-between text-sm text-gray-500">
                        <div className="flex items-center">
                          <Clock className="h-4 w-4 mr-1" />
                          Created {format(new Date(request.created_at), 'MMM d, yyyy')}
                        </div>
                        {selectedRequest?._id === request._id && (
                          <span className="text-hss-primary font-medium">Click to view chat →</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Chat Panel */}
            <div className="lg:col-span-1">
              {selectedRequest ? (
                <div className="medical-card rounded-xl overflow-hidden h-fit lg:sticky lg:top-8">
                  {/* Chat Header */}
                  <div className="bg-hss-primary text-white p-4">
                    <h3 className="font-semibold mb-1">💬 Support Chat</h3>
                    <p className="text-sm opacity-90">{selectedRequest.title}</p>
                  </div>

                  {/* Chat Messages */}
                  <div className="h-96 overflow-y-auto p-4 space-y-4 custom-scrollbar">
                    {chatMessages.map((message) => (
                      <div
                        key={message._id}
                        className={`flex ${message.sender_type === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`max-w-xs lg:max-w-sm px-4 py-3 rounded-2xl ${
                          message.sender_type === 'user'
                            ? 'chat-bubble-user'
                            : 'chat-bubble-admin'
                        }`}>
                          <div className="flex items-center mb-1">
                            {message.sender_type === 'user' ? (
                              <User className="h-3 w-3 mr-1" />
                            ) : (
                              <Bot className="h-3 w-3 mr-1" />
                            )}
                            <span className="text-xs font-medium opacity-75">
                              {message.sender_name}
                            </span>
                          </div>
                          <p className="text-sm leading-relaxed">{message.message}</p>
                          <p className="text-xs opacity-60 mt-1">
                            {format(new Date(message.created_at), 'MMM d, HH:mm')}
                          </p>
                        </div>
                      </div>
                    ))}
                    <div ref={messagesEndRef} />
                  </div>

                  {/* Chat Input */}
                  <form onSubmit={sendMessage} className="p-4 border-t border-gray-200">
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        placeholder="Type your message..."
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hss-primary focus:border-transparent"
                        disabled={sendingMessage}
                      />
                      <button
                        type="submit"
                        disabled={!newMessage.trim() || sendingMessage}
                        className="medical-button px-4 py-2 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {sendingMessage ? (
                          <LoadingSpinner size="sm" color="white" />
                        ) : (
                          <Send className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </form>
                </div>
              ) : (
                <div className="medical-card p-8 rounded-xl text-center h-fit lg:sticky lg:top-8">
                  <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-600 mb-2">Select a Request</h3>
                  <p className="text-gray-500">
                    Click on any request to view details and start chatting with support.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Create Request Tab */}
        {activeTab === 'create' && (
          <div className="max-w-2xl mx-auto">
            <div className="medical-card p-8 rounded-xl">
              <div className="text-center mb-8">
                <div className="w-16 h-16 bg-green-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Plus className="h-8 w-8 text-green-600" />
                </div>
                <h2 className="text-2xl font-bold text-hss-primary mb-2">Create Automation Request</h2>
                <p className="text-gray-600">
                  Describe the process you'd like to automate and our team will help you implement it.
                </p>
              </div>

              <form onSubmit={createRequest} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Request Title *
                  </label>
                  <input
                    type="text"
                    value={newRequest.title}
                    onChange={(e) => setNewRequest(prev => ({ ...prev, title: e.target.value }))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hss-primary focus:border-transparent"
                    placeholder="e.g., Automated Patient Intake Process"
                    required
                    disabled={creating}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Detailed Description *
                  </label>
                  <textarea
                    value={newRequest.description}
                    onChange={(e) => setNewRequest(prev => ({ ...prev, description: e.target.value }))}
                    rows={6}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hss-primary focus:border-transparent resize-none"
                    placeholder="Describe the current process, what you'd like to automate, and any specific requirements..."
                    required
                    disabled={creating}
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    Be as detailed as possible to help us understand your needs.
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Priority Level
                  </label>
                  <select
                    value={newRequest.priority}
                    onChange={(e) => setNewRequest(prev => ({ ...prev, priority: e.target.value }))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hss-primary focus:border-transparent"
                    disabled={creating}
                  >
                    <option value="low">Low - Nice to have</option>
                    <option value="medium">Medium - Important for efficiency</option>
                    <option value="high">High - Critical for operations</option>
                  </select>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium text-blue-800 mb-2">💡 What happens next?</h4>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• Your request will be reviewed by our automation team</li>
                    <li>• We'll reach out via chat with questions and updates</li>
                    <li>• You'll receive a detailed implementation plan</li>
                    <li>• Track progress through the chat system</li>
                  </ul>
                </div>

                <div className="flex items-center justify-between pt-6">
                  <button
                    type="button"
                    onClick={() => setActiveTab('requests')}
                    className="flex items-center text-gray-600 hover:text-hss-primary transition-colors"
                    disabled={creating}
                  >
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back to Requests
                  </button>
                  
                  <button
                    type="submit"
                    disabled={creating || !newRequest.title.trim() || !newRequest.description.trim()}
                    className="medical-button px-8 py-3 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    {creating ? (
                      <>
                        <LoadingSpinner size="sm" color="white" className="mr-2" />
                        Creating Request...
                      </>
                    ) : (
                      <>
                        <Plus className="h-4 w-4 mr-2" />
                        Create Request
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AutomationRequests;