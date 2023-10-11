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
  @location(1) color: vec4<f32>
};

let black = vec4<f32>(0f, 0f, 0f, 1f);
let white = vec4<f32>(1f, 1f, 1f, 1f);

@vertex
fn vs_main(input : VertexInput) -> VertexOutput {
  /*
  It seems that everything with a position Z coordination of less than 0 is getting clipped.
  Try shifting [-0.5,0.5] to [0,1]
  */

  var output : VertexOutput;
  output.position = camera.projection * camera.view * model * input.position;
  
  // var temp_p = camera.projection * camera.view * model * input.position;
  // var temp_p = camera.projection * model * input.position;
  // output.position =vec4<f32>(temp_p[0], temp_p[1], 0f, 1f);
  output.normal = normalize((camera.view * model * vec4<f32>(input.normal[0], input.normal[1], input.normal[2], 0f)).xyz);

  // output.position = vec4<f32>(input.position.x , input.position.y , 0f, 1f);
  // output.normal = input.normal;
  output.color = black;
  return output;
}

let lightDir = vec3<f32>(0.25, 0.5, 1f);
let lightColor = vec3<f32>(1f, 1f, 1f);
let ambientColor = vec3<f32>(0.1, 0.1, 0.1);

@fragment
fn fs_main(input : VertexOutput) -> @location(0) vec4<f32> {
  //Return black for where a line should be...
  return input.color;
}