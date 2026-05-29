

function confuseStringBySalt(arg, salt) {
    if (typeof arg !== 'string') return "";
    let flipArg = []; 
    for (let i = arg.length - 1; i >= 0; i--) {
        flipArg.push(arg[i]);
    }
    let shifted = flipArg.map(char => {
        return String.fromCharCode(char.charCodeAt(0) + salt);
    }).join('');
    return btoa(encodeURIComponent(shifted));
}

function restoreStringBySalt(encodedStr, salt) {
    try {
        let decoded = decodeURIComponent(atob(encodedStr));
        let originalArray = [];
        for (let i = decoded.length - 1; i >= 0; i--) {
            let charCode = decoded.charCodeAt(i);
            originalArray.push(String.fromCharCode(charCode - salt));
        }
        return originalArray.join('');
    } catch (e) {
        return "还原失败";
    }
}

// 调试 confusionattr
function confusionattr(arg1, arg2) {
    // 修正随机数生成方案 (1-100)
    let salt = Math.floor(Math.random() * 100) + 1;
    
    console.log("--- 开始调试 ---");
    console.log("当前使用的盐值 (Salt):", salt);

    if (typeof arg1 === "string" && typeof arg2 === "string") {
        // 混淆阶段
        const confused1 = confuseStringBySalt(arg1, salt);
        const confused2 = confuseStringBySalt(arg2, salt);
        
        console.log("混淆结果1:", confused1);
        console.log("混淆结果2:", confused2);

        // 还原阶段
        const restored1 = restoreStringBySalt(confused1, salt);
        const restored2 = restoreStringBySalt(confused2, salt);
        
        console.log("还原对比1:", arg1 === restored1 ? "✅ 匹配" : "❌ 失败", "(" + restored1 + ")");
        console.log("还原对比2:", arg2 === restored2 ? "✅ 匹配" : "❌ 失败", "(" + restored2 + ")");
        
        return {
            salt: salt,
            data: [confused1, confused2]
        };
    } else {
        console.error("错误：传入的参数不是字符串");
        return false;
    }
}


export default {confuseStringBySalt, restoreStringBySalt, confusionattr};