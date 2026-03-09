/**
 * API Service - Axios client for backend communication
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Customers
export const getCustomers = (skip = 0, limit = 100) => 
  apiClient.get(`/customers?skip=${skip}&limit=${limit}`);

export const getCustomerDetails = (customerId) => 
  apiClient.get(`/customers/${customerId}`);

export const uploadCustomerData = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.post('/customers/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

// Analytics
export const getDashboardMetrics = () => 
  apiClient.get('/analytics/dashboard');

export const getRFMAnalysis = (recalculate = false) => 
  apiClient.get(`/analytics/rfm?recalculate=${recalculate}`);

export const getRFMSegments = () => 
  apiClient.get('/analytics/rfm/segments');

export const getChurnAnalysis = (recalculate = false) => 
  apiClient.get(`/analytics/churn?recalculate=${recalculate}`);

export const getChurnSummary = () => 
  apiClient.get('/analytics/churn/summary');

export const getCLVAnalysis = (recalculate = false) => 
  apiClient.get(`/analytics/clv?recalculate=${recalculate}`);

export const getCLVSummary = () => 
  apiClient.get('/analytics/clv/summary');

// Models
export const trainModels = (modelType = 'all') => 
  apiClient.post(`/models/train?model_type=${modelType}`);

export const getModelPerformance = () => 
  apiClient.get('/models/performance');

// Recommendations
export const getRecommendations = (segment = null, limit = 50) => 
  apiClient.get(`/recommendations?${segment ? `segment=${segment}&` : ''}limit=${limit}`);

export const getRetentionStrategies = () => 
  apiClient.get('/recommendations/strategies');

export const getCustomerRecommendation = (customerId) => 
  apiClient.get(`/recommendations/customer/${customerId}`);

// Export
export const exportCustomers = (format = 'csv') => 
  apiClient.get(`/export/customers?format=${format}`, { responseType: 'blob' });

export const exportAnalytics = (reportType = 'full', format = 'csv') => 
  apiClient.get(`/export/analytics?report_type=${reportType}&format=${format}`, { responseType: 'blob' });

// Stats
export const getStatsOverview = () => 
  apiClient.get('/stats/overview');

// Data management
export const resetAllData = () =>
  apiClient.delete('/data/reset');

export default apiClient;
