
struct VertexOutput {
  @builtin(position) position : vec4<f32>,
  @location(0) normal : vec3<f32>,
};

let lightDir = vec3<f32>(0.25, 0.5, 1f);
let lightColor = vec3<f32>(1f, 1f, 1f);
let ambientColor = vec3<f32>(0.1, 0.1, 0.1);

@fragment
fn main(input : VertexOutput) -> @location(0) vec4<f32> {
  // An extremely simple directional lighting model, just to give our model some shape.
  let N = normalize(input.normal);
  let L = normalize(lightDir);
  let NDotL = max(dot(N, L), 0.0);
  let surfaceColor = ambientColor + NDotL;
  return vec4<f32>(surfaceColor[0], surfaceColor[1], surfaceColor[2], 1f);
}