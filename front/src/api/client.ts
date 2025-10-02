import axios from 'axios';

// URL base do seu servidor FastAPI
const API_BASE_URL = 'http://127.0.0.1:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Isso é um "interceptor". Ele executa antes de cada requisição.
// Ele pega o token que salvamos no login e o anexa no cabeçalho.
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