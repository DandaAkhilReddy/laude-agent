import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Users, 
  MessageSquare, 
  Settings, 
  TrendingUp,
  Search,
  Filter,
  Eye,
  CheckCircle,
  Clock,
  AlertCircle,
  Download,
  MoreHorizontal,
  User,
  Bot,
  Send
} from 'lucide-react';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

import { apiService } from '../services/apiService';
import LoadingSpinner from './LoadingSpinner';

const AdminPanel = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('requests'); // 'requests', 'users', 'stats'
  const [requests, setRequests] = useState([]);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [stats, setStats] = useState(null);
  
  // Chat system
  const [chatMessages, setChatMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [sendingMessage, setSendingMessage] = useState(false);
  const [updatingStatus, setUpdatingStatus] = useState(false);

  useEffect(() => {
    loadData();
  }, [activeTab]);

  useEffect(() => {
    if (selectedRequest) {
      loadChatMessages(selectedRequest._id);
    }
  }, [selectedRequest]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'requests') {
        await loadAllRequests();
      } else if (activeTab === 'stats') {
        await loadStats();
      }
    } catch (error) {
      console.error('Failed to load data:', error);
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const loadAllRequests = async () => {
    // Mock data for demo
    const mockRequests = [
      {
        _id: '1',
        title: 'Automated Patient Intake Process',
        description: 'Need automation for patient intake forms and initial screening workflow',
        priority: 'high',
        status: 'in_progress',
        created_at: '2024-01-15T09:00:00Z',
        updated_at: '2024-01-16T14:30:00Z',
        user_id: 'user_1',
        user_name: 'Dr. Sarah Johnson',
        user_email: 'sarah.johnson@hssmedicine.com',
        user_department: 'Emergency Medicine',
        admin_notes: 'Working on initial requirements gathering'
      },
      {
        _id: '2',
        title: 'Insurance Verification Automation',
        description: 'Automate the insurance verification process to reduce manual work for billing department',
        priority: 'medium',
        status: 'pending',
        created_at: '2024-01-14T11:15:00Z',
        updated_at: '2024-01-14T11:15:00Z',
        user_id: 'user_2',
        user_name: 'Mark Thompson',
        user_email: 'mark.thompson@hssmedicine.com',
        user_department: 'Billing Department',
        admin_notes: null
      },
      {
        _id: '3',
        title: 'Appointment Reminder System',
        description: 'Set up automated appointment reminders via SMS and email to reduce no-shows',
        priority: 'low',
        status: 'completed',
        created_at: '2024-01-10T08:45:00Z',
        updated_at: '2024-01-13T16:20:00Z',
        user_id: 'user_3',
        user_name: 'Lisa Chen',
        user_email: 'lisa.chen@hssmedicine.com',
        user_department: 'Patient Services',
        admin_notes: 'Successfully implemented and tested - 40% reduction in no-shows'
      },
      {
        _id: '4',
        title: 'Lab Report Distribution',
        description: 'Automated distribution of lab reports to physicians and patients through secure portal',
        priority: 'high',
        status: 'pending',
        created_at: '2024-01-16T10:30:00Z',
        updated_at: '2024-01-16T10:30:00Z',
        user_id: 'user_4',
        user_name: 'Dr. Michael Rodriguez',
        user_email: 'michael.rodriguez@hssmedicine.com',
        user_department: 'Laboratory',
        admin_notes: null
      }
    ];
    
    setRequests(mockRequests);
  };

  const loadStats = async () => {
    // Mock stats data
    const mockStats = {
      totalRequests: 24,
      pendingRequests: 8,
      inProgressRequests: 6,
      completedRequests: 10,
      totalUsers: 45,
      activeUsers: 38,
      avgResponseTime: '2.4 hours',
      completionRate: 85,
      requestsByDepartment: [
        { department: 'Emergency Medicine', count: 8 },
        { department: 'Billing Department', count: 6 },
        { department: 'Patient Services', count: 5 },
        { department: 'Laboratory', count: 3 },
        { department: 'Radiology', count: 2 }
      ],
      recentActivity: [
        { action: 'Request completed', user: 'Lisa Chen', time: '2 hours ago' },
        { action: 'New request created', user: 'Dr. Michael Rodriguez', time: '4 hours ago' },
        { action: 'Status updated', user: 'Admin', time: '6 hours ago' },
        { action: 'Message sent', user: 'Mark Thompson', time: '8 hours ago' }
      ]
    };
    
    setStats(mockStats);
  };

  const loadChatMessages = async (requestId) => {
    // Mock chat messages
    const mockMessages = [
      {
        _id: '1',
        message: 'Hi! I submitted a request for automating our patient intake process. This is a high priority for our emergency department.',
        sender_type: 'user',
        sender_name: 'Dr. Sarah Johnson',
        created_at: '2024-01-15T09:30:00Z'
      },
      {
        _id: '2',
        message: 'Hello Dr. Johnson! Thanks for your automation request. I understand the urgency for the emergency department. I have a few questions: 1) What specific forms need to be automated? 2) Do you need integration with Epic EMR? 3) What\'s your ideal timeline?',
        sender_type: 'admin',
        sender_name: 'Admin Support',
        created_at: '2024-01-15T10:15:00Z'
      },
      {
        _id: '3',
        message: 'Great questions! 1) We need to automate patient information forms, insurance verification, triage assessment, and medical history intake. 2) Yes, Epic integration is essential. 3) We\'d like to have this implemented within 3 weeks if possible, as we\'re seeing increased patient volume.',
        sender_type: 'user',
        sender_name: 'Dr. Sarah Johnson',
        created_at: '2024-01-15T14:20:00Z'
      },
      {
        _id: '4',
        message: 'Perfect! I\'ve reviewed the requirements and Epic integration is definitely achievable. Given the complexity and your timeline, I\'ll assign our senior developer to this project. I\'ll have a detailed technical specification and project timeline ready by tomorrow morning. We should be able to complete this within your 3-week deadline.',
        sender_type: 'admin',
        sender_name: 'Admin Support',
        created_at: '2024-01-16T09:45:00Z'
      }
    ];
    
    setChatMessages(mockMessages);
  };

  const updateRequestStatus = async (requestId, newStatus, adminNotes = '') => {
    setUpdatingStatus(true);
    try {
      // Mock status update
      setRequests(prev => prev.map(req => 
        req._id === requestId 
          ? { ...req, status: newStatus, admin_notes: adminNotes, updated_at: new Date().toISOString() }
          : req
      ));
      
      if (selectedRequest?._id === requestId) {
        setSelectedRequest(prev => ({ 
          ...prev, 
          status: newStatus, 
          admin_notes: adminNotes,
          updated_at: new Date().toISOString()
        }));
      }
      
      toast.success('Request status updated successfully!');
    } catch (error) {
      console.error('Failed to update status:', error);
      toast.error('Failed to update request status');
    } finally {
      setUpdatingStatus(false);
    }
  };

  const sendAdminMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim() || !selectedRequest) return;

    setSendingMessage(true);
    try {
      const message = {
        _id: Date.now().toString(),
        message: newMessage.trim(),
        sender_type: 'admin',
        sender_name: user?.full_name || 'Admin Support',
        created_at: new Date().toISOString()
      };

      setChatMessages(prev => [...prev, message]);
      setNewMessage('');
      toast.success('Message sent!');
    } catch (error) {
      console.error('Failed to send message:', error);
      toast.error('Failed to send message');
    } finally {
      setSendingMessage(false);
    }
  };

  const exportRequests = () => {
    const csvContent = [
      ['Title', 'Status', 'Priority', 'User', 'Department', 'Created', 'Updated'],
      ...filteredRequests.map(req => [
        req.title,
        req.status,
        req.priority,
        req.user_name,
        req.user_department,
        format(new Date(req.created_at), 'yyyy-MM-dd'),
        format(new Date(req.updated_at), 'yyyy-MM-dd')
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `automation-requests-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Requests exported successfully!');
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
                         request.user_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         request.user_department.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || request.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-yellow-600 via-orange-600 to-red-600 shadow-medical-lg">
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
                <h1 className="text-xl font-bold text-white">⚙️ Admin Panel</h1>
                <p className="text-white/80 text-sm">Manage automation requests and system administration</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="bg-yellow-500/20 border border-yellow-400/30 rounded-lg px-3 py-1">
                <span className="text-yellow-200 text-xs font-medium">ADMIN ACCESS</span>
              </div>
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

      {/* Tab Navigation */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { key: 'requests', label: 'Automation Requests', icon: MessageSquare },
              { key: 'stats', label: 'Analytics', icon: TrendingUp },
              { key: 'users', label: 'User Management', icon: Users }
            ].map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`flex items-center px-3 py-4 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.key
                      ? 'border-hss-primary text-hss-primary'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Requests Tab */}
        {activeTab === 'requests' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Requests List */}
            <div className="lg:col-span-2">
              {/* Search and Controls */}
              <div className="medical-card p-6 rounded-xl mb-6">
                <div className="flex flex-col sm:flex-row gap-4 mb-4">
                  <div className="flex-1 relative">
                    <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search requests, users, departments..."
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
                
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-600">
                    Showing {filteredRequests.length} of {requests.length} requests
                  </div>
                  <button
                    onClick={exportRequests}
                    className="flex items-center text-hss-primary hover:text-hss-secondary transition-colors"
                  >
                    <Download className="h-4 w-4 mr-1" />
                    Export CSV
                  </button>
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
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-hss-primary mb-1">{request.title}</h3>
                          <div className="flex items-center text-sm text-gray-600 space-x-4">
                            <span className="flex items-center">
                              <User className="h-4 w-4 mr-1" />
                              {request.user_name}
                            </span>
                            <span>{request.user_department}</span>
                            <span>{request.user_email}</span>
                          </div>
                        </div>
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
                      
                      {request.admin_notes && (
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                          <p className="text-sm text-blue-800">
                            <strong>Admin Notes:</strong> {request.admin_notes}
                          </p>
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between text-sm text-gray-500">
                        <div className="flex items-center">
                          <Clock className="h-4 w-4 mr-1" />
                          Created {format(new Date(request.created_at), 'MMM d, yyyy')} • 
                          Updated {format(new Date(request.updated_at), 'MMM d, yyyy')}
                        </div>
                        {selectedRequest?._id === request._id && (
                          <span className="text-hss-primary font-medium">Selected →</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Request Detail & Chat Panel */}
            <div className="lg:col-span-1">
              {selectedRequest ? (
                <div className="medical-card rounded-xl overflow-hidden h-fit lg:sticky lg:top-8">
                  {/* Request Header */}
                  <div className="bg-hss-primary text-white p-4">
                    <h3 className="font-semibold mb-1">Request Details</h3>
                    <p className="text-sm opacity-90">{selectedRequest.title}</p>
                  </div>

                  {/* Status Update */}
                  <div className="p-4 border-b border-gray-200">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Update Status
                    </label>
                    <div className="flex space-x-2">
                      <select
                        value={selectedRequest.status}
                        onChange={(e) => updateRequestStatus(selectedRequest._id, e.target.value)}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hss-primary focus:border-transparent text-sm"
                        disabled={updatingStatus}
                      >
                        <option value="pending">Pending</option>
                        <option value="in_progress">In Progress</option>
                        <option value="completed">Completed</option>
                        <option value="cancelled">Cancelled</option>
                      </select>
                      {updatingStatus && (
                        <LoadingSpinner size="sm" color="hss" />
                      )}
                    </div>
                  </div>

                  {/* Chat Messages */}
                  <div className="h-64 overflow-y-auto p-4 space-y-3 custom-scrollbar">
                    {chatMessages.map((message) => (
                      <div
                        key={message._id}
                        className={`flex ${message.sender_type === 'admin' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`max-w-xs px-3 py-2 rounded-2xl text-sm ${
                          message.sender_type === 'admin'
                            ? 'bg-hss-primary text-white'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          <div className="flex items-center mb-1">
                            {message.sender_type === 'admin' ? (
                              <Bot className="h-3 w-3 mr-1" />
                            ) : (
                              <User className="h-3 w-3 mr-1" />
                            )}
                            <span className="text-xs font-medium opacity-75">
                              {message.sender_name}
                            </span>
                          </div>
                          <p className="leading-relaxed">{message.message}</p>
                          <p className="text-xs opacity-60 mt-1">
                            {format(new Date(message.created_at), 'MMM d, HH:mm')}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Admin Chat Input */}
                  <form onSubmit={sendAdminMessage} className="p-4 border-t border-gray-200">
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        placeholder="Type admin response..."
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hss-primary focus:border-transparent text-sm"
                        disabled={sendingMessage}
                      />
                      <button
                        type="submit"
                        disabled={!newMessage.trim() || sendingMessage}
                        className="medical-button px-3 py-2 text-white text-sm rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
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
                  <Eye className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-600 mb-2">Select a Request</h3>
                  <p className="text-gray-500">
                    Click on any request to view details, update status, and chat with the user.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Stats Tab */}
        {activeTab === 'stats' && (
          <div className="space-y-8">
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="medical-card p-6 rounded-xl">
                    <div className="animate-pulse">
                      <div className="w-12 h-12 bg-gray-200 rounded-lg mb-4"></div>
                      <div className="h-4 bg-gray-200 rounded mb-2"></div>
                      <div className="h-6 bg-gray-200 rounded"></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <>
                {/* Overview Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="medical-card p-6 rounded-xl hover-lift">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <MessageSquare className="h-6 w-6 text-blue-600" />
                      </div>
                      <span className="text-2xl font-bold text-blue-600">{stats?.totalRequests}</span>
                    </div>
                    <p className="text-gray-600 font-medium">Total Requests</p>
                    <p className="text-sm text-gray-500">All time</p>
                  </div>

                  <div className="medical-card p-6 rounded-xl hover-lift">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                        <Clock className="h-6 w-6 text-yellow-600" />
                      </div>
                      <span className="text-2xl font-bold text-yellow-600">{stats?.pendingRequests}</span>
                    </div>
                    <p className="text-gray-600 font-medium">Pending</p>
                    <p className="text-sm text-gray-500">Needs attention</p>
                  </div>

                  <div className="medical-card p-6 rounded-xl hover-lift">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                        <CheckCircle className="h-6 w-6 text-green-600" />
                      </div>
                      <span className="text-2xl font-bold text-green-600">{stats?.completedRequests}</span>
                    </div>
                    <p className="text-gray-600 font-medium">Completed</p>
                    <p className="text-sm text-gray-500">{stats?.completionRate}% rate</p>
                  </div>

                  <div className="medical-card p-6 rounded-xl hover-lift">
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                        <Users className="h-6 w-6 text-purple-600" />
                      </div>
                      <span className="text-2xl font-bold text-purple-600">{stats?.activeUsers}</span>
                    </div>
                    <p className="text-gray-600 font-medium">Active Users</p>
                    <p className="text-sm text-gray-500">This month</p>
                  </div>
                </div>

                {/* Department Breakdown */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <div className="medical-card p-6 rounded-xl">
                    <h3 className="text-lg font-semibold text-hss-primary mb-4">Requests by Department</h3>
                    <div className="space-y-3">
                      {stats?.requestsByDepartment.map((dept, index) => (
                        <div key={index} className="flex items-center justify-between">
                          <span className="text-gray-700">{dept.department}</span>
                          <div className="flex items-center">
                            <div className="w-24 h-2 bg-gray-200 rounded-full mr-3">
                              <div 
                                className="h-2 bg-hss-primary rounded-full" 
                                style={{ width: `${(dept.count / stats.totalRequests) * 100}%` }}
                              ></div>
                            </div>
                            <span className="text-sm font-medium text-gray-600">{dept.count}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="medical-card p-6 rounded-xl">
                    <h3 className="text-lg font-semibold text-hss-primary mb-4">Recent Activity</h3>
                    <div className="space-y-3">
                      {stats?.recentActivity.map((activity, index) => (
                        <div key={index} className="flex items-start space-x-3">
                          <div className="w-2 h-2 bg-hss-primary rounded-full mt-2"></div>
                          <div className="flex-1">
                            <p className="text-sm text-gray-700">{activity.action}</p>
                            <p className="text-xs text-gray-500">{activity.user} • {activity.time}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="medical-card p-8 rounded-xl text-center">
            <Users className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-600 mb-2">User Management</h3>
            <p className="text-gray-500 mb-6">
              User management features will be available in the next update.
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-800">
                💡 <strong>Coming Soon:</strong> View all users, manage permissions, track activity, and more.
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AdminPanel;