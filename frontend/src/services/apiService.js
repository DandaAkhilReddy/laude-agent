import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for file uploads
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('session_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('session_token');
      localStorage.removeItem('user_data');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // Reports API
  reports: {
    async generate(transcript) {
      try {
        const response = await api.post('/api/reports/generate', {
          transcript,
          user_id: JSON.parse(localStorage.getItem('user_data'))?.user_id,
        });
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to generate report',
        };
      }
    },

    async getHistory() {
      try {
        const response = await api.get('/api/reports/history');
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to fetch report history',
        };
      }
    },

    async getReport(reportId) {
      try {
        const response = await api.get(`/api/reports/${reportId}`);
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to fetch report',
        };
      }
    },
  },

  // Automation Requests API
  automation: {
    async createRequest(requestData) {
      try {
        const response = await api.post('/api/automation/requests', {
          ...requestData,
          user_id: JSON.parse(localStorage.getItem('user_data'))?.user_id,
        });
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to create automation request',
        };
      }
    },

    async getRequests() {
      try {
        const response = await api.get('/api/automation/requests');
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to fetch automation requests',
        };
      }
    },

    async updateRequest(requestId, updateData) {
      try {
        const response = await api.put(`/api/automation/requests/${requestId}`, updateData);
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to update request',
        };
      }
    },

    async addMessage(requestId, message) {
      try {
        const response = await api.post(`/api/automation/requests/${requestId}/messages`, {
          message,
          sender_type: 'user',
          user_id: JSON.parse(localStorage.getItem('user_data'))?.user_id,
        });
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to send message',
        };
      }
    },

    async getMessages(requestId) {
      try {
        const response = await api.get(`/api/automation/requests/${requestId}/messages`);
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to fetch messages',
        };
      }
    },
  },

  // Admin API
  admin: {
    async getAllRequests() {
      try {
        const response = await api.get('/api/admin/requests');
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to fetch requests',
        };
      }
    },

    async updateRequestStatus(requestId, status, adminNotes = '') {
      try {
        const response = await api.put(`/api/admin/requests/${requestId}/status`, {
          status,
          admin_notes: adminNotes,
        });
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to update request status',
        };
      }
    },

    async getStats() {
      try {
        const response = await api.get('/api/admin/stats');
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to fetch stats',
        };
      }
    },

    async getUserStats() {
      try {
        const response = await api.get('/api/admin/users/stats');
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to fetch user stats',
        };
      }
    },
  },

  // File Upload API
  files: {
    async uploadAudio(file, onProgress) {
      try {
        const formData = new FormData();
        formData.append('audio_file', file);
        formData.append('user_id', JSON.parse(localStorage.getItem('user_data'))?.user_id);

        const response = await api.post('/api/files/upload-audio', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (onProgress) {
              const percentCompleted = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              onProgress(percentCompleted);
            }
          },
        });

        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to upload audio file',
        };
      }
    },

    async transcribeAudio(fileId) {
      try {
        const response = await api.post(`/api/files/transcribe/${fileId}`);
        return { success: true, data: response.data };
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.detail || 'Failed to transcribe audio',
        };
      }
    },
  },

  // General API utilities
  async healthCheck() {
    try {
      const response = await api.get('/');
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: 'API health check failed',
      };
    }
  },

  // Error handling helper
  handleError(error, defaultMessage = 'An error occurred') {
    const message = error.response?.data?.detail || error.message || defaultMessage;
    toast.error(message);
    console.error('API Error:', error);
    return message;
  },
};

export default apiService;