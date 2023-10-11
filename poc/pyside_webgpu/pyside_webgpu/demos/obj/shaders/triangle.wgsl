struct Camera {
  projection : mat4x4<f32>,
  view : mat4x4<f32>
};

@group(0) @binding(0) 
var<uniform> camera: Camera;

@group(1) @binding(0) 
var<uniform> model: mat4x4<f32>;

struct VertexInput {
  @location(0) position : vec4<f32>, 
  @location(1) normal : vec3<f32>,
};

struct VertexOutput {
  @builtin(position) position : vec4<f32>,
  @location(0) normal : vec3<f32>,
};

// Manual View Matrix for Debugging
let view_matrix = mat4x4<f32>(
  vec4<f32>(1f, 0f, 0f, 0f),   // Column 1: Right Axis
  vec4<f32>(0f, 1f, 0f, 0f),   // Column 2: Up Axis
  vec4<f32>(0f, 0f, 1f, 0f),   // Column 3: Facing Axis
  vec4<f32>(0f, 0f, 0f, 1f)    // Column 4: Eye Position.
);

@vertex
fn vs_main(input : VertexInput) -> VertexOutput {
  var output : VertexOutput;
  // Original
  // output.position = camera.projection * camera.view * model * vec4<f32>(input.position[0], input.position[1], input.position[2], input.position[3]);
  // output.normal = normalize((camera.view * model * vec4<f32>(input.normal[0], input.normal[1], input.normal[2], 0f)).xyz);
  
  // Ignoring the projection Matrix
  output.position = camera.view * model * input.position;
  output.normal = normalize((camera.view * model * vec4<f32>(input.normal[0], input.normal[1], input.normal[2], 0f)).xyz);
  
  // Using the shader defined view matrix.
  // output.position = view_matrix * vec4<f32>(input.position[0], input.position[1], input.position[2], input.position[3]);
  // output.normal = (view_matrix * vec4<f32>(input.normal[0], input.normal[1], input.normal[2], 0f)).xyz;
  
  // Pass Through
  // output.position = input.position; 
  // output.normal = input.normal;
  return output;
}

let lightDir = vec3<f32>(0.25, 0.5, 1f);
let lightColor = vec3<f32>(1f, 1f, 1f);
let ambientColor = vec3<f32>(0.1, 0.1, 0.1);

@fragment
fn fs_main(input : VertexOutput) -> @location(0) vec4<f32> {
  // An extremely simple directional lighting model, just to give our model some shape.
  let N = normalize(input.normal);
  let L = normalize(lightDir);
  let NDotL = max(dot(N, L), 0.0);
  let surfaceColor = ambientColor + NDotL;
  return vec4<f32>(surfaceColor[0], surfaceColor[1], surfaceColor[2], 1f);
}