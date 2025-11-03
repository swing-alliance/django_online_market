import axios from 'axios';

let isRefreshing = false;
let failedQueue = [];
const tokenStatus = { value: '初始化...' }; 

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

const setupAxiosInterceptor = () => {
    if (axios.interceptors.request.handlers.length === 0) {
        axios.interceptors.request.use(
            config => {
                const token = localStorage.getItem('access_token');
                const isAuthUrl = config.url.includes('/login/') || config.url.includes('/token/refresh/');
                
                if (token && !isAuthUrl) {
                    config.headers.Authorization = `Bearer ${token}`;
                    tokenStatus.value = 'Access Token 已设置';
                }
                return config;
            },
            error => {
                return Promise.reject(error);
            }
        );

        axios.interceptors.response.use(
            response => response,
            async (error) => {
                console.log('中断器调试Error response:', error.response); // 打印错误响应
                const originalRequest = error.config;
                if (error.response && error.response.status === 401 && !originalRequest._retry) {
                    console.log('token过期重试');
                    originalRequest._retry = true; // 标记已重试
                    const refreshToken = localStorage.getItem('refresh_token');
                    if (!refreshToken || isRefreshing) {
                        return new Promise(function(resolve, reject) {
                            failedQueue.push({ resolve, reject });
                        }).then(token => {
                            originalRequest.headers.Authorization = 'Bearer ' + token;
                            return axios(originalRequest);
                        }).catch(err => {
                            return Promise.reject(err);
                        });
                    }

                    if (!isRefreshing) {
                        isRefreshing = true;
                        tokenStatus.value = 'Access Token 过期，正在刷新...';

                        try {
                            console.log('开始发送刷新 token 请求');
                            const response = await axios.post('http://127.0.0.1:8000/api/users/token/refresh/', { 
                                refresh: refreshToken 
                            });
                            console.log('刷新 token 响应:', response.data); // 打印响应
                            const newAccessToken = response.data.access;
                            localStorage.setItem('access_token', newAccessToken);
                            isRefreshing = false;
                            processQueue(null, newAccessToken);
                            originalRequest.headers.Authorization = 'Bearer ' + newAccessToken;
                            tokenStatus.value = 'Token 刷新成功，已重发请求';
                            return axios(originalRequest);

                        } catch (refreshError) {
                            isRefreshing = false;
                            processQueue(refreshError);
                            localStorage.removeItem('access_token');
                            localStorage.removeItem('refresh_token');
                            tokenStatus.value = 'Refresh Token 失败，请重新登录';
                            console.error("Token Refresh Failed, redirect to login.");
                            return Promise.reject(refreshError);
                        }
                    }
                }
                return Promise.reject(error);
            }
        );
    }
};

export { setupAxiosInterceptor, tokenStatus };