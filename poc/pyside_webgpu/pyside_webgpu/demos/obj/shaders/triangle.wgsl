struct Camera {
  projection : mat4x4<f32>,
  view : mat4x4<f32>
};

@group(0) @binding(0) 
var<uniform> camera: Camera;

@group(1) @binding(0) 
var<uniform> model: mat4x4<f32>;

struct VertexInput {
  @location(0) position: vec4<f32>, 
  @location(1) texture: vec2<f32>,
  @location(2) normal: vec3<f32>,
  @location(3) barycentric: vec3<f32>
};

struct VertexOutput {
  @builtin(position) position : vec4<f32>,
  @location(0) normal : vec3<f32>,
  @location(1) barycentric: vec3<f32>
};

@vertex
fn vs_main(input : VertexInput) -> VertexOutput {
  var output : VertexOutput;
  output.position = camera.projection * camera.view * model * input.position;
  output.normal = normalize((camera.view * model * vec4<f32>(input.normal[0], input.normal[1], input.normal[2], 0f)).xyz);
  output.barycentric = input.barycentric;
  return output;
}

let lightDir = vec3<f32>(0.25, 0.5, 1f);
let lightColor = vec3<f32>(1f, 1f, 1f);
let ambientColor = vec3<f32>(0.1, 0.1, 0.1);
let LINE_WIDTH = 0.5f;

fn edge_factor(coord: vec3<f32>) -> f32{
  let d = fwidth(coord);
  let f = step(d * LINE_WIDTH, coord);
  return min(min(f.x, f.y), f.z);
}

@fragment
fn fs_main(input : VertexOutput) -> @location(0) vec4<f32> {
  var color = vec4<f32>(0.7f, 0.7f, 0.7f, 1f); // Default, draw an edge.
  // if (input.barycentric.x > LINE_WIDTH && input.barycentric.y > LINE_WIDTH && input.barycentric.z > LINE_WIDTH){
  //   // If we're not close to the edge then shade the triangle face.
  //   let N = normalize(input.normal);
  //   let L = normalize(lightDir);
  //   let NDotL = max(dot(N, L), 0.0);
  //   let surfaceColor = ambientColor + NDotL;
  //   color = vec4<f32>(surfaceColor[0], surfaceColor[1], surfaceColor[2], 1f);
  // }
  // return color;

  let applied = edge_factor(input.barycentric);
  let step_color = vec4<f32>(applied, applied, applied, 1f);
  let selected_color = min(step_color, color);
  return vec4<f32>(selected_color.r, selected_color.g, selected_color.b, 1f);
}