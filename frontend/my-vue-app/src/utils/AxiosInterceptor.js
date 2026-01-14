import axios from 'axios';
//此文件用于设置axios的请求和响应拦截器，处理Token的自动刷新逻辑
// 1. 自动身份注入 (Request Interceptor)
// 权限绑定：在每次发起请求（非登录/刷新请求）时，自动从 localStorage 读取 access_token 并添加到 HTTP Header 的 Authorization: Bearer <token> 中。
// 智能避让：自动识别登录和刷新接口，避免在这些请求中重复添加旧 Token 或错误的 Content-Type。
// 2. 401 错误拦截与自愈 (Response Interceptor)
// 过期检测：当后端返回 401 Unauthorized 状态码时，拦截器不会立即报错，而是判定为 access_token 过期，并触发自动修复机制。
// 自动刷新：拦截器会自动使用本地的 refresh_token 向后端请求新的 access_token，无需用户手动重新登录。
// 3. 请求并发控制（队列机制）
// 防止重复刷新：通过 isRefreshing 开关，确保在多个请求同时过期时，只发送一次刷新 Token 的请求，避免资源浪费。
// 请求挂起与重发：在 Token 刷新期间产生的其他请求会被推入 failedQueue 队列中暂存。一旦新 Token 获取成功，队列中的所有请求会带着新 Token 自动重新发起，用户感知不到中断。
// 4. 异常处理与强制下线
// 刷新失败保护：如果 refresh_token 也过期了（刷新接口返回 401），拦截器会清除本地所有 Token 缓存，并将状态设为“请重新登录”，引导用户回到登录页。
// 死循环防止：通过 _retry 标记位，确保一个请求最多只尝试刷新一次，防止因逻辑错误导致前端不停地请求接口。
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