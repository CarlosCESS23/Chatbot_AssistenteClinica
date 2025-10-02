import axios from 'axios';

// URL base do seu servidor FastAPI
const API_BASE_URL = 'http://127.0.0.1:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Este "interceptor" é executado antes de cada requisição.
// Ele pega o token que guardámos no login e anexa-o ao cabeçalho.
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default apiClient;