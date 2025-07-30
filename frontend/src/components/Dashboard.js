import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Mic, 
  FileText, 
  MessageSquare, 
  Settings, 
  LogOut, 
  Activity,
  Clock,
  Users,
  TrendingUp,
  Shield,
  Zap
} from 'lucide-react';
import toast from 'react-hot-toast';

import LoadingSpinner from './LoadingSpinner';
import { apiService } from '../services/apiService';

const Dashboard = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Update time every minute
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);
    return () => clearInterval(timer);
  }, []);

  // Load dashboard stats
  useEffect(() => {
    loadDashboardStats();
  }, []);

  const loadDashboardStats = async () => {
    try {
      setLoading(true);
      // In a real implementation, you'd have dashboard stats endpoint
      // For now, we'll use mock data
      setTimeout(() => {
        setStats({
          totalReports: 12,
          thisWeekReports: 3,
          automationRequests: 5,
          pendingRequests: 2,
          systemStatus: 'operational',
          lastReportDate: '2024-01-15T10:30:00Z',
        });
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Failed to load dashboard stats:', error);
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await onLogout();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const getGreeting = () => {
    const hour = currentTime.getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const getSessionExpiry = () => {
    if (!user?.session_expires) return '';
    try {
      const expiryDate = new Date(user.session_expires);
      return expiryDate.toLocaleTimeString('en-US', { 
        hour: 'numeric',
        minute: '2-digit',
        hour12: true 
      });
    } catch (error) {
      return '';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="healthcare-gradient shadow-medical-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex items-center mr-8">
                <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center mr-3">
                  <span className="text-2xl">🎙️</span>
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white">Laude Agent</h1>
                  <p className="text-white/80 text-sm">HSS Medicine Enterprise</p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-6">
              {/* User Info */}
              <div className="text-right">
                <p className="text-white font-medium">{user?.full_name}</p>
                <p className="text-white/80 text-sm">
                  {user?.department} • {user?.company_domain?.toUpperCase()}
                </p>
              </div>

              {/* Admin Badge */}
              {user?.is_admin && (
                <div className="bg-yellow-500/20 border border-yellow-400/30 rounded-lg px-3 py-1">
                  <span className="text-yellow-200 text-xs font-medium">Admin</span>
                </div>
              )}

              {/* Logout */}
              <button
                onClick={handleLogout}
                className="bg-red-500/20 hover:bg-red-500/30 border border-red-400/30 text-white px-4 py-2 rounded-lg transition-colors flex items-center"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="medical-card rounded-2xl p-8 mb-8 hover-lift">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-hss-primary mb-2">
                {getGreeting()}, {user?.full_name?.split(' ')[0]}! 👋
              </h2>
              <p className="text-gray-600 text-lg mb-4">
                Your AI-powered voice-to-email assistant is ready to help you create professional communications.
              </p>
              <div className="flex items-center text-sm text-gray-500">
                <Clock className="h-4 w-4 mr-2" />
                <span>
                  {currentTime.toLocaleDateString('en-US', { 
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </span>
              </div>
            </div>
            <div className="hidden lg:block">
              <div className="w-32 h-32 bg-gradient-to-br from-hss-light to-blue-100 rounded-full flex items-center justify-center">
                <span className="text-6xl">🚀</span>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
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
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="medical-card p-6 rounded-xl hover-lift">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <FileText className="h-6 w-6 text-green-600" />
                </div>
                <span className="text-2xl font-bold text-green-600">{stats?.totalReports || 0}</span>
              </div>
              <p className="text-gray-600 font-medium">Total Reports</p>
              <p className="text-sm text-gray-500">+{stats?.thisWeekReports || 0} this week</p>
            </div>

            <div className="medical-card p-6 rounded-xl hover-lift">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <MessageSquare className="h-6 w-6 text-blue-600" />
                </div>
                <span className="text-2xl font-bold text-blue-600">{stats?.automationRequests || 0}</span>
              </div>
              <p className="text-gray-600 font-medium">Automation Requests</p>
              <p className="text-sm text-gray-500">{stats?.pendingRequests || 0} pending</p>
            </div>

            <div className="medical-card p-6 rounded-xl hover-lift">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Activity className="h-6 w-6 text-purple-600" />
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse mr-2"></div>
                  <span className="text-sm font-medium text-green-600">Online</span>
                </div>
              </div>
              <p className="text-gray-600 font-medium">System Status</p>
              <p className="text-sm text-gray-500">All services operational</p>
            </div>

            <div className="medical-card p-6 rounded-xl hover-lift">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                  <Shield className="h-6 w-6 text-orange-600" />
                </div>
                <span className="text-xs font-medium text-orange-600">SECURE</span>
              </div>
              <p className="text-gray-600 font-medium">Session Active</p>
              <p className="text-sm text-gray-500">Expires at {getSessionExpiry()}</p>
            </div>
          </div>
        )}

        {/* Main Features */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Weekly Report Generator */}
          <Link
            to="/reports"
            className="medical-card p-8 rounded-2xl hover-lift transition-all duration-300 group"
          >
            <div className="flex items-start justify-between mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <Mic className="h-8 w-8 text-white" />
              </div>
              <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                <Zap className="h-6 w-6 text-blue-500" />
              </div>
            </div>
            <h3 className="text-xl font-bold text-hss-primary mb-3">
              🎙️ Weekly Report Generator
            </h3>
            <p className="text-gray-600 mb-4 leading-relaxed">
              Record your weekly updates using advanced voice recognition. Speak naturally and let AI transform your words into professional, polished reports.
            </p>
            <div className="flex items-center text-blue-600 font-medium">
              <span>Start Recording</span>
              <span className="ml-2 transform group-hover:translate-x-2 transition-transform">→</span>
            </div>
          </Link>

          {/* Request Automation */}
          <Link
            to="/automation"
            className="medical-card p-8 rounded-2xl hover-lift transition-all duration-300 group"
          >
            <div className="flex items-start justify-between mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <MessageSquare className="h-8 w-8 text-white" />
              </div>
              <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                <TrendingUp className="h-6 w-6 text-green-500" />
              </div>
            </div>
            <h3 className="text-xl font-bold text-hss-primary mb-3">
              🤖 Request Automation
            </h3>
            <p className="text-gray-600 mb-4 leading-relaxed">
              Submit automation requests using voice or text. Chat with our support team and track your requests through our integrated communication system.
            </p>
            <div className="flex items-center text-green-600 font-medium">
              <span>Create Request</span>
              <span className="ml-2 transform group-hover:translate-x-2 transition-transform">→</span>
            </div>
          </Link>
        </div>

        {/* Admin Panel Access */}
        {user?.is_admin && (
          <div className="medical-card p-6 rounded-2xl border-2 border-yellow-200 bg-gradient-to-r from-yellow-50 to-orange-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-yellow-500 rounded-xl flex items-center justify-center mr-4">
                  <Settings className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-yellow-800">Admin Panel</h3>
                  <p className="text-yellow-700">Manage automation requests and system administration</p>
                </div>
              </div>
              <Link
                to="/admin"
                className="bg-yellow-500 hover:bg-yellow-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                Access Admin Panel
              </Link>
            </div>
          </div>
        )}

        {/* System Status */}
        <div className="medical-card p-6 rounded-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse mr-3"></div>
              <span className="text-green-600 font-medium">🟢 System Online - All services operational</span>
            </div>
            <div className="text-sm text-gray-500">
              Last updated: {currentTime.toLocaleTimeString()}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;