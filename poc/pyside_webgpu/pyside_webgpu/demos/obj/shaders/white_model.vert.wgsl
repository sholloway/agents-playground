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
fn main(input : VertexInput) -> VertexOutput {
  var output : VertexOutput;
  // Original
  // output.position = camera.projection * camera.view * model * vec4<f32>(input.position[0], input.position[1], input.position[2], input.position[3]);
  // output.normal = normalize((camera.view * model * vec4<f32>(input.normal[0], input.normal[1], input.normal[2], 0f)).xyz);
  
  // Ignoring the projection Matrix
  output.position = camera.view * model * vec4<f32>(input.position[0], input.position[1], input.position[2], input.position[3]);
  output.normal = normalize((camera.view * model * vec4<f32>(input.normal[0], input.normal[1], input.normal[2], 0f)).xyz);
  
  // Using the shader defined view matrix.
  // output.position = view_matrix * vec4<f32>(input.position[0], input.position[1], input.position[2], input.position[3]);
  // output.normal = (view_matrix * vec4<f32>(input.normal[0], input.normal[1], input.normal[2], 0f)).xyz;
  
  // Pass Through
  // output.position = input.position; 
  // output.normal = input.normal;
  return output;
}
/*
The Issue:
The Skull isn't rendering correctly. 

Why?
- It could be that the camera is inside the model.
- Culling could be off.
- There may be an issue with how the VBO is being accessed by the shader.
- There could be a bug in the parser. 
- The normals could be wrong.

- Need to controll the aspect ratio of what's being rendered independently of the canvas size.
  Right now if the canvas is resized it skews the rendered frame.

Try:
- [] Get to where we can control the camera to verify we know what we're looking at.
*/