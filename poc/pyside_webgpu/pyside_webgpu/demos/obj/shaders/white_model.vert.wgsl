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

@vertex
fn main(input : VertexInput) -> VertexOutput {
  var output : VertexOutput;
  output.position = camera.projection * camera.view * model * vec4<f32>(input.position[0], input.position[1], input.position[2], input.position[3]);
  output.normal = normalize((camera.view * model * vec4<f32>(input.normal[0], input.normal[1], input.normal[2], 0f)).xyz);
  
  
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

Try:
- [] Get to were we can control the camera to verify we know what we're looking at.
*/