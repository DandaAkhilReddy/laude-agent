import { useState, useEffect, useCallback } from 'react';
import { authService } from '../services/authService';
import toast from 'react-hot-toast';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Initialize auth state
  useEffect(() => {
    const initAuth = () => {
      try {
        const userData = authService.getCurrentUser();
        const isAuth = authService.isAuthenticated();
        
        if (isAuth && userData) {
          setUser(userData);
          setIsAuthenticated(true);
        } else {
          // Clear invalid data
          localStorage.removeItem('session_token');
          localStorage.removeItem('user_data');
          setUser(null);
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    initAuth();

    // Listen for storage changes (multi-tab sync)
    const handleStorageChange = (e) => {
      if (e.key === 'session_token' || e.key === 'user_data') {
        if (!e.newValue) {
          // Token/data was removed
          setUser(null);
          setIsAuthenticated(false);
        } else {
          // Token/data was added/updated
          initAuth();
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // Login function
  const login = useCallback(async (email, otpCode) => {
    setLoading(true);
    try {
      const result = await authService.verifyOTP(email, otpCode);
      
      if (result.success) {
        const userData = result.data.user_data;
        setUser(userData);
        setIsAuthenticated(true);
        
        toast.success(`Welcome back, ${userData.full_name.split(' ')[0]}! 👋`);
        
        return { success: true, data: userData };
      } else {
        toast.error(result.error);
        return { success: false, error: result.error };
      }
    } catch (error) {
      const errorMessage = 'Login failed. Please try again.';
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  // Logout function
  const logout = useCallback(async () => {
    setLoading(true);
    try {
      await authService.logout();
      setUser(null);
      setIsAuthenticated(false);
      toast.success('Logged out successfully');
    } catch (error) {
      console.error('Logout error:', error);
      // Still clear local state even if API call fails
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  }, []);

  // Update user data
  const updateUser = useCallback((userData) => {
    setUser(userData);
    localStorage.setItem('user_data', JSON.stringify(userData));
  }, []);

  // Session validation
  const validateSession = useCallback(async () => {
    const token = authService.getToken();
    if (!token) {
      setIsAuthenticated(false);
      setUser(null);
      return false;
    }

    const isValid = await authService.validateSession(token);
    if (!isValid) {
      setIsAuthenticated(false);
      setUser(null);
      localStorage.removeItem('session_token');
      localStorage.removeItem('user_data');
      return false;
    }

    return true;
  }, []);

  // Session warning for expiry
  useEffect(() => {
    if (!isAuthenticated || !user) return;

    const checkSessionExpiry = () => {
      try {
        const expiryDate = new Date(user.session_expires);
        const now = new Date();
        const timeUntilExpiry = expiryDate - now;
        
        // Show warning 5 minutes before expiry
        const warningTime = 5 * 60 * 1000; // 5 minutes in milliseconds
        
        if (timeUntilExpiry <= warningTime && timeUntilExpiry > 0) {
          toast((t) => (
            <div className="flex flex-col space-y-2">
              <div className="font-medium">⏰ Session Expiring Soon</div>
              <div className="text-sm text-gray-600">
                Your session will expire in {Math.ceil(timeUntilExpiry / 60000)} minutes.
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => {
                    window.location.reload(); // Refresh to extend session
                    toast.dismiss(t.id);
                  }}
                  className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
                >
                  Extend Session
                </button>
                <button
                  onClick={() => toast.dismiss(t.id)}
                  className="bg-gray-300 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-400"
                >
                  Dismiss
                </button>
              </div>
            </div>
          ), {
            duration: Infinity,
            id: 'session-warning'
          });
        } else if (timeUntilExpiry <= 0) {
          // Session expired
          logout();
          toast.error('Your session has expired. Please log in again.');
        }
      } catch (error) {
        console.error('Session expiry check error:', error);
      }
    };

    // Check immediately and then every minute
    checkSessionExpiry();
    const interval = setInterval(checkSessionExpiry, 60000);
    
    return () => clearInterval(interval);
  }, [isAuthenticated, user, logout]);

  return {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
    updateUser,
    validateSession,
  };
};

export default useAuth;