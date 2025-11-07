import axios from 'axios';

let isRefreshing = false;
let failedQueue = [];
// tokenStatus 状态跟踪，在 Vue 组件中使用时需要是响应式引用 (e.g., ref)
const tokenStatus = { value: '初始化...' }; 

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error); // 刷新失败，拒绝挂起的请求
        } else {
            prom.resolve(token); // 刷新成功，解决挂起的请求
        }
    });
    failedQueue = [];
};

const setupAxiosInterceptor = () => {
    if (axios.interceptors.request.handlers.length === 0) {
        axios.interceptors.request.use(
            config => {
                const token = localStorage.getItem('access_token');
                const refreshToken = localStorage.getItem('refresh_token'); // 🔑 新增：获取 Refresh Token
                console.log('--- Axios Request Debug ---');
                console.log('Access Token (ls):', token ? 'Found' : 'Missing');
                console.log('Refresh Token (ls):', refreshToken ? 'Found' : 'Missing');
                console.log('---------------------------');
                const isAuthUrl = config.url && (
                    config.url.includes('/login/') || 
                    config.url.includes('/token/refresh/')
                );
                if (token && !isAuthUrl) {
                    config.headers.Authorization = `Bearer ${token}`;
                    tokenStatus.value = 'Access Token 已设置';
                }
                if (config.url && config.url.includes('/token/refresh/')) {
                    config.headers['Content-Type'] = 'application/json';
                    delete config.headers.Authorization; 
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
                console.log('中断器调试 Error response:', error.response); // 打印错误响应
                const originalRequest = error.config;
                const status = error.response ? error.response.status : null;
                if (status === 401 && !originalRequest._retry) {
                    console.log('token过期重试');
                    if (originalRequest.url.includes('/token/refresh/')) {
                        console.error('拦截器警告：刷新 Token 请求自身收到了 401 错误！');
                        // 刷新失败，强制用户重新登录
                        localStorage.removeItem('access_token');
                        localStorage.removeItem('refresh_token');
                        tokenStatus.value = 'Refresh Token 失败，请重新登录';
                        processQueue(error); // 拒绝队列中的所有请求
                        return Promise.reject(error); 
                    }
                    
                    originalRequest._retry = true; // 标记已重试
                    const refreshToken = localStorage.getItem('refresh_token');

                    if (!refreshToken) {
                        console.error('拦截器发现 401 错误，但无 Refresh Token，终止自动刷新。');
                        return Promise.reject(error); 
                    }
                    if (isRefreshing) {
                        console.log('执行失败队列 (等待刷新完成)');
                        return new Promise((resolve, reject) => {
                            failedQueue.push({ resolve, reject });
                        }).then(token => {
                            originalRequest.headers.Authorization = 'Bearer ' + token;
                            return axios(originalRequest);
                        }).catch(err => {
                            return Promise.reject(err);
                        });
                    }
                    
                    // 4. 如果是第一个 401 错误，且不在刷新中，则开始刷新
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
                            // 刷新失败（例如，Refresh Token 也过期了）
                            isRefreshing = false;
                            
                            localStorage.removeItem('access_token');
                            localStorage.removeItem('refresh_token');
                            tokenStatus.value = 'Refresh Token 失败，请重新登录';
                            console.error("Token Refresh Failed, redirect to login.");
                            
                            processQueue(refreshError);
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