import router from '@/router';
function isTokenExit() {
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    const tokenExists = accessToken !== null && refreshToken !== null;
    return tokenExists;
}

async function simplelogout() {
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    console.log('Token 已清除');
    const success = accessToken !== null && refreshToken !== null;
    await router.push({ path: '/login' }); 
    return success; 
}

export default {isTokenExit, simplelogout};