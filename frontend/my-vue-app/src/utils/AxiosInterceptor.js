import axios from "axios";

// 状态管理
let isRefreshing = false;
let failedQueue = [];
const tokenStatus = { value: "初始化..." };

// 核心工具：生成 ValidationField (时间戳+随机盐 -> ASCII偏移 -> 反转 -> Base64)
const generateValidationField = () => {
  const timestamp = Date.now().toString();
  const salt = Math.floor(Math.random() * 10).toString();

  // 逻辑：时间戳+盐 -> ASCII + 1 -> 反转 -> Base64
  const processed = (timestamp + salt)
    .split("")
    .map((char) => String.fromCharCode(char.charCodeAt(0) + 1))
    .reverse()
    .join("");

  return btoa(processed); // 若在 Node 环境，请使用 Buffer.from(processed).toString('base64')
};

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
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
    // 1. 请求拦截器
    axios.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem("access_token");

        // 注入安全校验字段 ValidationField
        config.headers["ValidationField"] = generateValidationField();

        const isAuthUrl =
          config.url &&
          (config.url.includes("/login/") ||
            config.url.includes("/token/refresh/"));

        if (token && !isAuthUrl) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        if (config.url && config.url.includes("/token/refresh/")) {
          config.headers["Content-Type"] = "application/json";
          delete config.headers.Authorization;
        }

        return config;
      },
      (error) => Promise.reject(error),
    );

    // 2. 响应拦截器
    axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        const status = error.response ? error.response.status : null;

        if (status === 401 && !originalRequest._retry) {
          // 处理刷新接口自身的 401
          if (originalRequest.url.includes("/token/refresh/")) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            processQueue(error);
            return Promise.reject(error);
          }

          originalRequest._retry = true;
          const refreshToken = localStorage.getItem("refresh_token");

          if (!refreshToken) return Promise.reject(error);

          // 并发控制：队列处理
          if (isRefreshing) {
            return new Promise((resolve, reject) => {
              failedQueue.push({ resolve, reject });
            }).then((token) => {
              originalRequest.headers.Authorization = "Bearer " + token;
              return axios(originalRequest);
            });
          }

          // 执行刷新
          isRefreshing = true;
          try {
            const response = await axios.post(
              "http://127.0.0.1:8000/api/users/token/refresh/",
              {
                refresh: refreshToken,
              },
            );

            const newAccessToken = response.data.access;
            localStorage.setItem("access_token", newAccessToken);

            isRefreshing = false;
            processQueue(null, newAccessToken);

            originalRequest.headers.Authorization = "Bearer " + newAccessToken;
            return axios(originalRequest);
          } catch (refreshError) {
            isRefreshing = false;
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            processQueue(refreshError);
            return Promise.reject(refreshError);
          }
        }
        return Promise.reject(error);
      },
    );
  }
};

export { setupAxiosInterceptor, tokenStatus };

