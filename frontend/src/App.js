import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

// Components
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import WeeklyReportGenerator from './components/WeeklyReportGenerator';
import AutomationRequests from './components/AutomationRequests';
import AdminPanel from './components/AdminPanel';
import LoadingSpinner from './components/LoadingSpinner';

// Hooks & Utils
import { useAuth } from './hooks/useAuth';
import { authService } from './services/authService';

// Styles
import './App.css';

function App() {
  const { user, isAuthenticated, loading, login, logout } = useAuth();
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    // Check for existing session on app start
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem('session_token');
        if (token) {
          // Verify token is still valid
          const isValid = await authService.validateSession(token);
          if (!isValid) {
            localStorage.removeItem('session_token');
            localStorage.removeItem('user_data');
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        localStorage.removeItem('session_token');
        localStorage.removeItem('user_data');
      } finally {
        setIsInitializing(false);
      }
    };

    initializeAuth();
  }, []);

  if (isInitializing || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <div className="mt-6">
            <h2 className="text-2xl font-bold text-white mb-2">🎙️ Laude Agent</h2>
            <p className="text-blue-200">HSS Medicine Enterprise Platform</p>
            <div className="mt-4">
              <div className="inline-block animate-pulse">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1f2937',
              color: '#f9fafb',
              borderRadius: '8px',
              fontSize: '14px'
            },
            success: {
              iconTheme: {
                primary: '#10b981',
                secondary: '#f9fafb',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#f9fafb',
              },
            },
          }}
        />
        
        <Routes>
          {/* Public Routes */}
          <Route 
            path="/login" 
            element={
              !isAuthenticated ? (
                <Login onLogin={login} />
              ) : (
                <Navigate to="/dashboard" replace />
              )
            } 
          />
          
          {/* Protected Routes */}
          <Route 
            path="/dashboard" 
            element={
              isAuthenticated ? (
                <Dashboard user={user} onLogout={logout} />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          
          <Route 
            path="/reports" 
            element={
              isAuthenticated ? (
                <WeeklyReportGenerator user={user} onLogout={logout} />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          
          <Route 
            path="/automation" 
            element={
              isAuthenticated ? (
                <AutomationRequests user={user} onLogout={logout} />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          
          <Route 
            path="/admin" 
            element={
              isAuthenticated && user?.is_admin ? (
                <AdminPanel user={user} onLogout={logout} />
              ) : isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          
          {/* Default Route */}
          <Route 
            path="/" 
            element={
              <Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />
            } 
          />
          
          {/* Catch-all Route */}
          <Route 
            path="*" 
            element={
              <div className="min-h-screen bg-gray-100 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-6xl mb-4">🔍</div>
                  <h1 className="text-4xl font-bold text-gray-800 mb-2">404</h1>
                  <p className="text-gray-600 mb-8">Page not found</p>
                  <button 
                    onClick={() => window.location.href = '/'}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                  >
                    Go Home
                  </button>
                </div>
              </div>
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;