/**
 * level3.js
 *
 * This module provides Level 3 bot detection signals based on environmental and behavioral analysis.
 * It aims to identify headless browsers, particularly those using stealth plugins like playwright-extra-plugin-stealth,
 * by checking for inconsistencies that are difficult to spoof.
 */

/**
 * Checks for the presence of Chrome DevTools-related objects in the window.
 * Playwright might inject these objects if DevTools is not properly disabled.
 * @returns {boolean} - True if DevTools-related objects are found, false otherwise.
 */
function checkDevTools() {
    try {
        // Check for common DevTools hooks
        if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || window.devtools) {
            return true;
        }
    } catch (e) {
        // Ignore potential errors in restricted environments
    }
    return false;
}

/**
 * Performs a WebGL fingerprinting check to identify software-based renderers like SwiftShader,
 * which are commonly used in headless environments.
 * @returns {object} - An object containing the WebGL vendor and renderer strings.
 */
function getWebGLFingerprint() {
    try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        if (gl) {
            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
            const vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
            const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
            return { vendor, renderer };
        }
    } catch (e) {
        // WebGL may not be supported or could be blocked
    }
    return { vendor: 'unknown', renderer: 'unknown' };
}

/**
 * Checks for the presence of specific APIs that are often incomplete or missing in headless environments.
 * @returns {object} - An object indicating the presence of various APIs.
 */
function checkApiIntegrity() {
    const signals = {
        hasSpeechSynthesis: 'speechSynthesis' in window,
        hasTouchEvents: 'TouchEvent' in window,
        hasPointerEvents: 'PointerEvent' in window,
        hasRequestIdleCallback: 'requestIdleCallback' in window,
    };
    return signals;
}

/**
 * A simple heuristic to check the number of available fonts. Headless browsers often have a very limited set.
 * This is an asynchronous check as font loading can be slow.
 * @returns {Promise<number>} - A promise that resolves with the number of detected fonts.
 */
async function getFontCount() {
    try {
        if (!document.fonts || !document.fonts.ready) {
            return -1; // Font loading API not supported
        }
        await document.fonts.ready;
        return document.fonts.size;
    } catch (e) {
        return -1;
    }
}


/**
 * Gathers all Level 3 signals.
 * This function combines various checks to build a comprehensive profile of potential bot-like behavior.
 * @returns {Promise<object>} - A promise that resolves to an object containing all Level 3 signals.
 */
export async function getLevel3Signals() {
    try {
        const webgl = getWebGLFingerprint();
        const hasDevTools = checkDevTools();
        const apiIntegrity = checkApiIntegrity();
        const fontCount = await getFontCount();

        return {
            // Returns true if the renderer is SwiftShader, a strong indicator of a headless environment.
            isSwiftShader: webgl.renderer.includes('SwiftShader'),
            webglVendor: webgl.vendor,
            webglRenderer: webgl.renderer,
            // True if DevTools hooks are detected.
            hasDevTools,
            // A collection of boolean flags for API presence.
            apiIntegrity,
            // A count of available fonts. A very low number can be suspicious.
            fontCount,
        };
    } catch (error) {
        console.error('Error collecting Level 3 signals:', error);
        return {
            error: true,
            message: error.message,
        };
    }
}
