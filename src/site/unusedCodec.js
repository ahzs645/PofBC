// Stand-in for the Node built-ins that @firstform/json-url's unused codecs reach for.
//
// json-url's registry references every codec it knows about, including the ones backed by
// node:zlib and lzma. The share engine enables only `lz` and `raw`, so those paths are never
// taken — but Vite still has to resolve the imports, and without this it replaces them with its
// own silent stub and prints a warning about it on every build.
//
// Being explicit is better: the build stays quiet, and anything that did somehow reach one of
// these gets an error that says what happened instead of a vague `undefined is not a function`.

const unavailable = () => {
  throw new Error(
    'This json-url codec is not bundled. The share engine enables only "lz" and "raw"; ' +
    'add the codec to src/site/shareLink.js and drop the alias in vite.config.js to use another.'
  )
}

export default new Proxy({}, { get: () => unavailable })
