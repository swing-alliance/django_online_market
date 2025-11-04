function isTokenExit() {
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    const tokenExists = accessToken !== null && refreshToken !== null;
    return tokenExists;
}

function simplelogout() {
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    if (accessToken !== null && refreshToken !== null) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        return true; 
    }
    return false;
}

export default {isTokenExit, simplelogout};