var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
const getParameterEnums = [
    gl.VERSION,
    gl.VENDOR,
    gl.RENDERER,
    gl.SHADING_LANGUAGE_VERSION,
    gl.MAX_TEXTURE_SIZE,
    gl.MAX_CUBE_MAP_TEXTURE_SIZE,
    gl.MAX_RENDERBUFFER_SIZE,
    gl.MAX_VERTEX_ATTRIBS,
    gl.MAX_VERTEX_TEXTURE_IMAGE_UNITS,
    gl.MAX_TEXTURE_IMAGE_UNITS,
    gl.MAX_COMBINED_TEXTURE_IMAGE_UNITS,
    gl.MAX_FRAGMENT_UNIFORM_VECTORS,
    gl.MAX_VERTEX_UNIFORM_VECTORS,
    gl.MAX_VARYING_VECTORS
];

function shouldAvoidDebugRendererInfo() {
    return false; // 修改为始终允许，便于演示和调试
}
function shouldAvoidPolygonModeExtensions() {
    return false;
}
function isValidParameterGetter(gl) {
    return typeof gl.getParameter === 'function';
}
function getShaderPrecision(gl, shaderType, precisionType) {
    var shaderPrecision = gl.getShaderPrecisionFormat(shaderType, precisionType);
    return shaderPrecision
        ? [shaderPrecision.rangeMin, shaderPrecision.rangeMax, shaderPrecision.precision]
        : [];
}
function getConstantsFromPrototype(obj) {
    return Object.keys(obj.__proto__).filter(function (key) { return typeof key === 'string' && /^[A-Z0-9_x]+$/.test(key); });
}
function getWebGLContext() {
    var canvas = document.createElement('canvas');
    var context = null;
    for (var _i = 0, _a = ['webgl', 'experimental-webgl']; _i < _a.length; _i++) {
        var type = _a[_i];
        try {
            context = canvas.getContext(type);
        }
        catch (_b) {
            continue;
        }
        if (context)
            break;
    }
    return context;
}
export function getWebGLFingerprint() {
    return __awaiter(this, void 0, void 0, function () {
        var gl, debugExt, basicInfo, constants, parameters, _i, constants_1, constant, code, value, supportedExtensions, shaderPrecisions, shaderTypes, precisionTypes, _a, shaderTypes_1, shader, _b, precisionTypes_1, precision, shaderTypeConst, precisionConst, res;
        var _c, _d, _e, _f, _g, _h;
        return __generator(this, function (_j) {
            gl = getWebGLContext();
            if (!gl)
                return [2 /*return*/, { error: 'no_context' }];
            if (!isValidParameterGetter(gl))
                return [2 /*return*/, { error: 'invalid_getParameter' }];
            debugExt = shouldAvoidDebugRendererInfo() ? null : gl.getExtension('WEBGL_debug_renderer_info');
            basicInfo = {
                version: ((_c = gl.getParameter(gl.VERSION)) === null || _c === void 0 ? void 0 : _c.toString()) || '',
                vendor: ((_d = gl.getParameter(gl.VENDOR)) === null || _d === void 0 ? void 0 : _d.toString()) || '',
                vendorUnmasked: debugExt ? (_e = gl.getParameter(debugExt.UNMASKED_VENDOR_WEBGL)) === null || _e === void 0 ? void 0 : _e.toString() : '',
                renderer: ((_f = gl.getParameter(gl.RENDERER)) === null || _f === void 0 ? void 0 : _f.toString()) || '',
                rendererUnmasked: debugExt ? (_g = gl.getParameter(debugExt.UNMASKED_RENDERER_WEBGL)) === null || _g === void 0 ? void 0 : _g.toString() : '',
                shadingLanguageVersion: ((_h = gl.getParameter(gl.SHADING_LANGUAGE_VERSION)) === null || _h === void 0 ? void 0 : _h.toString()) || '',
            };
            constants = getConstantsFromPrototype(gl);
            parameters = [];
            for (_i = 0, constants_1 = constants; _i < constants_1.length; _i++) {
                constant = constants_1[_i];
                code = gl[constant];
                if (typeof code === 'number' && getParameterEnums.includes(code)) {
                    try {
                        value = gl.getParameter(code);
                        parameters.push(`${constant}(${code})=${value}`);
                    } catch (_k) {
                        parameters.push(`${constant}(${code})=error`);
                    }
                }                   
            }
            supportedExtensions = gl.getSupportedExtensions() || [];
            shaderPrecisions = [];
            shaderTypes = ['FRAGMENT_SHADER', 'VERTEX_SHADER'];
            precisionTypes = ['LOW_FLOAT', 'MEDIUM_FLOAT', 'HIGH_FLOAT', 'LOW_INT', 'MEDIUM_INT', 'HIGH_INT'];
            for (_a = 0, shaderTypes_1 = shaderTypes; _a < shaderTypes_1.length; _a++) {
                shader = shaderTypes_1[_a];
                for (_b = 0, precisionTypes_1 = precisionTypes; _b < precisionTypes_1.length; _b++) {
                    precision = precisionTypes_1[_b];
                    shaderTypeConst = gl[shader];
                    precisionConst = gl[precision];
                    if (typeof shaderTypeConst === 'number' && typeof precisionConst === 'number') {
                        res = gl.getShaderPrecisionFormat(shaderTypeConst, precisionConst);
                        if (res) {
                            shaderPrecisions.push("".concat(shader, ".").concat(precision, "=").concat(res.rangeMin, ",").concat(res.rangeMax, ",").concat(res.precision));
                        }
                    }
                }
            }
            return [2 /*return*/, __assign(__assign({}, basicInfo), { extensions: supportedExtensions, parameters: parameters, shaderPrecisions: shaderPrecisions })];
        });
    });
}
