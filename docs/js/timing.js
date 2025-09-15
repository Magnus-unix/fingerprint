let startTime = null;
let endTime = null;

function markStartTime() {
    startTime = performance.now();
}

function markEndTime() {
    endTime = performance.now();
    return {
        startTime,
        endTime,
        duration: endTime - startTime  // 单位：毫秒
    };
}

// 挂到全局
window.markStartTime = markStartTime;
window.markEndTime = markEndTime;
