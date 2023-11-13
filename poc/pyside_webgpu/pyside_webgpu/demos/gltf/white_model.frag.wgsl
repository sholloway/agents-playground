// Some hardcoded lighting
const lightDir = vec3f(0.25, 0.5, 1);
const lightColor = vec3f(1);
const ambientColor = vec3f(0.1);

@fragment
fn fragmentMain(input : VertexOutput) -> @location(0) vec4f {
  // An extremely simple directional lighting model, just to give our model some shape.
  let N = normalize(input.normal);
  let L = normalize(lightDir);
  let NDotL = max(dot(N, L), 0.0);
  let surfaceColor = ambientColor + NDotL;

  return vec4f(surfaceColor, 1);
}