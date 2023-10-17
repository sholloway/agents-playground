struct Camera {
  projection: mat4x4<f32>,
  view: mat4x4<f32>
};

struct DisplayConfig {
  edges: i32,
  faces: i32,
  vertices: i32
};

@group(0) @binding(0) 
var<uniform> camera: Camera;

@group(1) @binding(0) 
var<uniform> model: mat4x4<f32>;

@group(2) @binding(0) 
var<uniform> display_config: DisplayConfig;

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

let LIGHT_POSITION = vec3<f32>(0.25, 0.5, 1f);
let lightColor = vec3<f32>(1f, 1f, 1f);
let AMBIENT_COLOR = vec4<f32>(0.1, 0.1, 0.1, 1f);
let LINE_WIDTH = 0.5f;
let LINE_COLOR = vec4<f32>(0.7f, 0.7f, 0.7f, 1f); // Default, draw an edge.

fn edge_factor(coord: vec3<f32>) -> f32{
  /*
  Given a barycentric coordinate, find how close the point is to the edge.
  */
  let d: vec3<f32> = fwidth(coord); // How is the coordinate compared to the pixels around it?
  let f: vec3<f32> = step(d * LINE_WIDTH, coord); //Find A <= B? 1 : 0 per component
  return min(min(f.x, f.y), f.z);
}

@fragment
fn fs_main(input : VertexOutput) -> @location(0) vec4<f32> {
  var face_color: vec4<f32>;
  var surface_color: vec4<f32>;
  var selected_color: vec4<f32>;

  if display_config.faces == 1 {
    // Calculate the face color using a lightning model.
    let vert_normal = normalize(input.normal);
    let light_normal = normalize(LIGHT_POSITION);
    let relation_to_light = dot(vert_normal, light_normal);
    let specular_amount = max(relation_to_light, 0.0);
    surface_color = AMBIENT_COLOR + specular_amount;
  }else{
    // The face color is transparent.
    surface_color = vec4<f32>(0f, 0f, 0f, 0f);
  }

  if display_config.edges == 1 {
    let applied: f32 = edge_factor(input.barycentric); 
    let step_color = vec4<f32>(applied, applied, applied, 1f);
    face_color = vec4<f32>(surface_color.r*applied, surface_color.g*applied, surface_color.b*applied, surface_color.a);
    selected_color = min(face_color, LINE_COLOR);
  }else{
    selected_color = surface_color;
  }

  return selected_color;
}