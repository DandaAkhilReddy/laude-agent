import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('session_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('session_token');
      localStorage.removeItem('user_data');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  /**
   * Register a new user
   */
  async register(userData) {
    try {
      const response = await api.post('/api/auth/register', userData);
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed',
      };
    }
  },

  /**
   * Generate OTP for email
   */
  async generateOTP(email) {
    try {
      const response = await api.post('/api/auth/generate-otp', { email });
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Failed to generate OTP',
      };
    }
  },

  /**
   * Verify OTP and login
   */
  async verifyOTP(email, otpCode) {
    try {
      const response = await api.post('/api/auth/verify-otp', {
        email,
        otp_code: otpCode,
      });
      
      if (response.data.success) {
        // Store session data
        localStorage.setItem('session_token', response.data.session_token);
        localStorage.setItem('user_data', JSON.stringify(response.data.user_data));
      }
      
      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'OTP verification failed',
      };
    }
  },

  /**
   * Logout user
   */
  async logout() {
    try {
      await api.post('/api/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Always clear local storage
      localStorage.removeItem('session_token');
      localStorage.removeItem('user_data');
    }
  },

  /**
   * Validate current session
   */
  async validateSession(token) {
    try {
      const response = await api.get('/api/auth/validate', {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data.success;
    } catch (error) {
      return false;
    }
  },

  /**
   * Get current user data from localStorage
   */
  getCurrentUser() {
    try {
      const userData = localStorage.getItem('user_data');
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Error parsing user data:', error);
      return null;
    }
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    const token = localStorage.getItem('session_token');
    const userData = this.getCurrentUser();
    
    if (!token || !userData) {
      return false;
    }

    // Check if session is expired
    try {
      const expiryDate = new Date(userData.session_expires);
      return expiryDate > new Date();
    } catch (error) {
      return false;
    }
  },

  /**
   * Get session token
   */
  getToken() {
    return localStorage.getItem('session_token');
  },
};

export default authService;