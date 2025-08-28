function safeGet(gl, pname) {
    try {
        if (typeof pname === 'number' || (pname in gl)) {
            return gl.getParameter(pname);
        }
    } catch (e) {}
    return null;
}

function getWebGLContext() {
    const canvas = document.createElement('canvas');
    return (
        canvas.getContext('webgl') ||
        canvas.getContext('experimental-webgl') ||
        null
    );
}

export async function getWebGLFingerprint() {
    try {
        const gl = getWebGLContext();
        if (!gl) return { supported: false };

        // 扩展：厂商和渲染器
        const dbgRendererInfo = gl.getExtension('WEBGL_debug_renderer_info');
        const vendorUnmasked = dbgRendererInfo
            ? safeGet(gl, dbgRendererInfo.UNMASKED_VENDOR_WEBGL)
            : null;
        const rendererUnmasked = dbgRendererInfo
            ? safeGet(gl, dbgRendererInfo.UNMASKED_RENDERER_WEBGL)
            : null;

        // 基础信息
        const basicInfo = {
            supported: true,
            version: safeGet(gl, gl.VERSION) || '',
            shadingLanguageVersion: safeGet(gl, gl.SHADING_LANGUAGE_VERSION) || '',
            vendor: safeGet(gl, gl.VENDOR) || '',
            renderer: safeGet(gl, gl.RENDERER) || '',
            vendorUnmasked: vendorUnmasked || '',
            rendererUnmasked: rendererUnmasked || '',
        };

        // 常用参数
        const parameters = {
            aliasedLineWidthRange: safeGet(gl, gl.ALIASED_LINE_WIDTH_RANGE),
            aliasedPointSizeRange: safeGet(gl, gl.ALIASED_POINT_SIZE_RANGE),
            alphaBits: safeGet(gl, gl.ALPHA_BITS),
            depthBits: safeGet(gl, gl.DEPTH_BITS),
            stencilBits: safeGet(gl, gl.STENCIL_BITS),
            maxRenderbufferSize: safeGet(gl, gl.MAX_RENDERBUFFER_SIZE),
            maxTextureSize: safeGet(gl, gl.MAX_TEXTURE_SIZE),
        };

        // 扩展列表
        const extensions = gl.getSupportedExtensions() || [];

        // 着色器精度
        const shaderPrecisions = [];
        const shaderTypes = ['FRAGMENT_SHADER', 'VERTEX_SHADER'];
        const precisionTypes = [
            'LOW_FLOAT',
            'MEDIUM_FLOAT',
            'HIGH_FLOAT',
            'LOW_INT',
            'MEDIUM_INT',
            'HIGH_INT',
        ];

        for (const shader of shaderTypes) {
            for (const precision of precisionTypes) {
                const shaderTypeConst = gl[shader];
                const precisionConst = gl[precision];
                if (typeof shaderTypeConst === 'number' && typeof precisionConst === 'number') {
                    try {
                        const res = gl.getShaderPrecisionFormat(shaderTypeConst, precisionConst);
                        if (res) {
                            shaderPrecisions.push(
                                `${shader}.${precision}=${res.rangeMin},${res.rangeMax},${res.precision}`
                            );
                        }
                    } catch (e) {
                        // 某些设备/浏览器不支持
                    }
                }
            }
        }

        return {
            ...basicInfo,
            parameters,
            extensions,
            shaderPrecisions,
        };
    } catch (e) {
        return { supported: false, error: e.message || 'webgl_error' };
    }
}
