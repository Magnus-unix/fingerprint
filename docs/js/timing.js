let startTime = null;
let endTime = null;

export function markStartTime() {
    startTime = performance.now();
}

export function markEndTime() {
    endTime = performance.now();
    return {
        startTime,
        endTime,
        duration: endTime - startTime  // 单位：毫秒
    };
}
