// Front relief inferred from the catalogue artwork. R is elevation, G is the exposed field,
// and B identifies the smooth number plate. Preserve strokes, holes and clipping paths.
const surfaceMap = (root) => {
  for (const shape of root.querySelectorAll('path, rect, circle, ellipse, polygon, polyline, line, use')) {
    if (shape.closest('defs, clipPath, mask')) continue
    const plaque = shape.closest('[data-component="serial-plaque"]')
    const field = shape.id === 'inner-rim' || (shape.matches('[data-role="border"]') && !shape.hasAttribute('data-component'))
    const caption = shape.closest('[data-caption]')?.getAttribute('data-caption') ?? ''
    const digits = /^\d+$/.test(caption)
    // The photographed Warden drawing separates the letter ridge from its face,
    // and the leaf blade from its raised veins.
    const highRelief = shape.matches('[data-role="letter-face"]') ||
      shape.closest('#maple-leaf-principal-veins, #maple-leaf-secondary-veins, #maple-leaf-midrib')
    const face = highRelief ? '#e00000' : plaque ? '#9400ff' : field ? '#40ff00' : digits ? '#160000' : '#ac0000'
    // The badge library uses SVG presentation attributes, including inherited fill and stroke.
    for (const attr of ['fill', 'stroke']) {
      const paint = shape.closest(`[${attr}]`)?.getAttribute(attr) ?? (attr === 'fill' ? 'black' : 'none')
      shape.setAttribute(attr, paint === 'none' ? 'none' : attr === 'stroke' && field ? '#aa0000' : face)
    }
  }
  return new XMLSerializer().serializeToString(root)
}

const vertex = `#version 300 es
precision highp float;
uniform sampler2D surface;
uniform vec2 aspect;
uniform float yaw;
out vec2 uv;
const int grid = 112;
const vec2 corners[6] = vec2[6](vec2(0,0),vec2(1,0),vec2(1,1),vec2(0,0),vec2(1,1),vec2(0,1));
void main() {
  int cell = gl_VertexID / 6;
  uv = (vec2(cell % grid, cell / grid) + corners[gl_VertexID % 6]) / float(grid);
  vec2 p = (uv * 2.0 - 1.0) * aspect;
  float z = 0.055 * max(0.0, 1.0-dot(p,p)) + 0.013 * texture(surface, uv).r;
  float x = cos(yaw)*p.x + sin(yaw)*z;
  float depth = -sin(yaw)*p.x + cos(yaw)*z;
  float w = 1.0 - depth*0.20;
  gl_Position = vec4(0.91 * vec2(x, -p.y) / aspect, -depth*0.3, w);
}`

const fragment = `#version 300 es
precision highp float;
uniform sampler2D art;
uniform sampler2D surface;
uniform vec2 pixel;
uniform float yaw;
uniform float grain;
uniform float copper;
uniform float bronze;
uniform float darkPlate;
in vec2 uv;
out vec4 colour;
float hash(vec2 p) {
  vec3 q = fract(vec3(p.xyx) * 0.1031);
  q += dot(q, q.yzx + 33.33);
  return fract((q.x+q.y)*q.z);
}
float noise(vec2 p) {
  vec2 i=floor(p), f=fract(p);
  f=f*f*(3.0-2.0*f);
  return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+1.0),f.x),f.y);
}
float heightAt(vec2 p) {
  vec4 m=texture(surface,p);
  return m.r + grain*m.g*(noise(p/pixel*0.33)-0.5);
}
void main() {
  vec4 src=texture(art,uv);
  if(src.a<0.005) discard;
  vec3 m=texture(surface,uv).rgb;
  vec2 d=pixel*1.5;
  vec2 slope=vec2(heightAt(uv+vec2(d.x,0))-heightAt(uv-vec2(d.x,0)),
                  heightAt(uv+vec2(0,d.y))-heightAt(uv-vec2(0,d.y)));
  vec3 n=normalize(vec3(-slope.x*2.6, slope.y*2.6,1.0) + vec3((uv.x-.5)*.23,(.5-uv.y)*.23,0));
  n=vec3(cos(yaw)*n.x+sin(yaw)*n.z,n.y,-sin(yaw)*n.x+cos(yaw)*n.z);
  vec3 light=normalize(vec3(-.55,.66,.78));
  float diffuse=max(0.0,dot(n,light));
  float spec=pow(max(0.0,dot(n,normalize(light+vec3(0,0,1)))),mix(29.0,16.0,copper));
  float lum=dot(src.rgb,vec3(.299,.587,.114));
  // Preserve green enamel. Silver on the numbered shields is neutral, and the dark
  // fields on the Forest Service ovals read as brown patina in the photographs.
  float green=smoothstep(.08,.22,src.g-src.r);
  vec3 silver=mix(vec3(lum)*vec3(1.00,1.01,1.02),src.rgb,green);
  vec3 patina=mix(src.rgb,vec3(.28,.19,.11),m.g*.83);
  vec3 base=mix(mix(silver,patina,bronze),src.rgb,copper);
  base*=1.0-darkPlate*m.b*.53;
  float reflection=dot(reflect(vec3(0,0,-1),n),normalize(vec3(-.65,.35,.65)));
  float band=smoothstep(.25,.82,reflection);
  vec3 metal=base*(.38+.45*diffuse+.45*band) + vec3(.48*spec+.045*band);
  vec3 copperFace=base*(.60+.39*diffuse+.29*band)+vec3(.35,.23,.17)*spec;
  colour=vec4(mix(metal,copperFace,copper),src.a);
}`

const raster = async (url, width, height) => {
  const image = new Image()
  image.src = url
  await image.decode()
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  canvas.getContext('2d').drawImage(image, 0, 0, width, height)
  return canvas
}

const compile = (gl, type, source) => {
  const shader = gl.createShader(type)
  gl.shaderSource(shader, source)
  gl.compileShader(shader)
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(shader))
  return shader
}

// The caller owns this canvas and its context for one selected badge.
export async function prepareRelief (gl, drawing, patch, isActive) {
  const root = new DOMParser().parseFromString(drawing.text, 'image/svg+xml').documentElement
  const { width, height } = root.viewBox.baseVal
  const scale = 896 / Math.max(width, height)
  const w = Math.max(1, Math.round(scale * width))
  const h = Math.max(1, Math.round(scale * height))
  const maskUrl = URL.createObjectURL(new Blob([surfaceMap(root)], { type: 'image/svg+xml' }))
  let maps
  try {
    maps = await Promise.all([drawing.url, maskUrl].map((url) => raster(url, w, h)))
  } finally {
    URL.revokeObjectURL(maskUrl)
  }
  if (!isActive()) return null
  const program = gl.createProgram()
  for (const [type, source] of [[gl.VERTEX_SHADER, vertex], [gl.FRAGMENT_SHADER, fragment]]) {
    const shader = compile(gl, type, source)
    gl.attachShader(program, shader)
    gl.deleteShader(shader)
  }
  gl.linkProgram(program)
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program))
  gl.useProgram(program)
  const uniform = (key) => gl.getUniformLocation(program, key)
  maps.forEach((map, index) => {
    gl.activeTexture(gl.TEXTURE0 + index)
    gl.bindTexture(gl.TEXTURE_2D, gl.createTexture())
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, map)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE)
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE)
    gl.uniform1i(uniform(index ? 'surface' : 'art'), index)
  })
  gl.canvas.width = w
  gl.canvas.height = h
  gl.viewport(0, 0, w, h)
  gl.uniform2f(uniform('aspect'), w / Math.max(w,h), h / Math.max(w,h))
  gl.uniform2f(uniform('pixel'), 1/w, 1/h)
  const stippled = ['S11-O01', 'S12-O01', 'S17-O01', 'S20-O01'].includes(patch.id)
  const copper = /copper/i.test(patch.finish ?? '')
  gl.uniform1f(uniform('grain'), stippled ? .64 : copper ? .16 : .07)
  gl.uniform1f(uniform('copper'), Number(copper))
  gl.uniform1f(uniform('bronze'), Number(['S07-O01', 'S21-O01', 'S51-O01'].includes(patch.id)))
  gl.uniform1f(uniform('darkPlate'), Number(['S11-O01', 'S17-O01', 'S20-O01'].includes(patch.id)))
  const yaw = uniform('yaw')
  return (angle) => {
    gl.uniform1f(yaw, angle * Math.PI / 180)
    gl.clear(gl.COLOR_BUFFER_BIT)
    gl.drawArrays(gl.TRIANGLES, 0, 112 * 112 * 6)
  }
}
