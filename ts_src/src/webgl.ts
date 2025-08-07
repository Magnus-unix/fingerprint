function shouldAvoidDebugRendererInfo(): boolean {
  return false; // 修改为始终允许，便于演示和调试
}

function shouldAvoidPolygonModeExtensions(): boolean {
  return false;
}

function isValidParameterGetter(gl: WebGLRenderingContext) {
  return typeof gl.getParameter === 'function';
}

function getShaderPrecision(gl: WebGLRenderingContext, shaderType: number, precisionType: number) {
  const shaderPrecision = gl.getShaderPrecisionFormat(shaderType, precisionType);
  return shaderPrecision
    ? [shaderPrecision.rangeMin, shaderPrecision.rangeMax, shaderPrecision.precision]
    : [];
}

function getConstantsFromPrototype(obj: any): string[] {
  return Object.keys(obj.__proto__).filter((key) => typeof key === 'string' && /^[A-Z0-9_x]+$/.test(key));
}

function getWebGLContext(): WebGLRenderingContext | null {
  const canvas = document.createElement('canvas');
  let context: WebGLRenderingContext | null = null;

  for (const type of ['webgl', 'experimental-webgl']) {
    try {
      context = canvas.getContext(type) as WebGLRenderingContext;
    } catch {
      continue;
    }
    if (context) break;
  }

  return context;
}

async function getWebGLFingerprint(): Promise<any> {
  const gl = getWebGLContext();
  if (!gl) return { error: 'no_context' };
  if (!isValidParameterGetter(gl)) return { error: 'invalid_getParameter' };

  const debugExt = shouldAvoidDebugRendererInfo() ? null : gl.getExtension('WEBGL_debug_renderer_info');

  const basicInfo = {
    version: gl.getParameter(gl.VERSION)?.toString() || '',
    vendor: gl.getParameter(gl.VENDOR)?.toString() || '',
    vendorUnmasked: debugExt ? gl.getParameter(debugExt.UNMASKED_VENDOR_WEBGL)?.toString() : '',
    renderer: gl.getParameter(gl.RENDERER)?.toString() || '',
    rendererUnmasked: debugExt ? gl.getParameter(debugExt.UNMASKED_RENDERER_WEBGL)?.toString() : '',
    shadingLanguageVersion: gl.getParameter(gl.SHADING_LANGUAGE_VERSION)?.toString() || '',
  };

  const constants = getConstantsFromPrototype(gl);
  const parameters: string[] = [];

  for (const constant of constants) {
    const code = (gl as any)[constant];
    if (typeof code === 'number') {
      try {
        const value = gl.getParameter(code);
        parameters.push(`${constant}(${code})=${value}`);
      } catch {
        parameters.push(`${constant}(${code})=error`);
      }
    }
  }

  const supportedExtensions = gl.getSupportedExtensions() || [];
  const shaderPrecisions: string[] = [];

  const shaderTypes = ['FRAGMENT_SHADER', 'VERTEX_SHADER'] as const;
  const precisionTypes = ['LOW_FLOAT', 'MEDIUM_FLOAT', 'HIGH_FLOAT', 'LOW_INT', 'MEDIUM_INT', 'HIGH_INT'] as const;

  for (const shader of shaderTypes) {
    for (const precision of precisionTypes) {
      const shaderTypeConst = (gl as any)[shader];
      const precisionConst = (gl as any)[precision];
      if (typeof shaderTypeConst === 'number' && typeof precisionConst === 'number') {
        const res = gl.getShaderPrecisionFormat(shaderTypeConst, precisionConst);
        if (res) {
          shaderPrecisions.push(`${shader}.${precision}=${res.rangeMin},${res.rangeMax},${res.precision}`);
        }
      }
    }
  }

  return {
    ...basicInfo,
    extensions: supportedExtensions,
    parameters,
    shaderPrecisions,
  };
}
