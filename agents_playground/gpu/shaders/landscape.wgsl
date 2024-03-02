struct Camera {
  projection: mat4x4<f32>,
  view: mat4x4<f32>
};

struct DisplayConfig {
  shading_mode: i32 // DEBUG:0, SIMPLE_SHADING: 1
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

const LIGHT_POSITION = vec3<f32>(0.25, 0.5, 1f);
const lightColor = vec3<f32>(1f, 1f, 1f);
const AMBIENT_COLOR = vec4<f32>(0.1, 0.1, 0.1, 1f);

const DEBUG_LINE_WIDTH = 0.5f;
const DEBUG_LINE_COLOR = vec4<f32>(0.7f, 0.7f, 0.7f, 1f); // Default, draw an edge.
const DEBUG_BASE_COLOR = vec4<f32>(1f, 1f, 1f, 1f); 

fn edge_factor(coord: vec3<f32>, line_width: f32) -> f32{
  /*
  Given a barycentric coordinate, find how close the point is to the edge.
  */
  let d: vec3<f32> = fwidth(coord); // How is the coordinate compared to the pixels around it?
  let f: vec3<f32> = step(d * line_width, coord); //Find A <= B? 1 : 0 per component
  return min(min(f.x, f.y), f.z);
}

fn debug_shading(base_color: vec4<f32>, edge_color:vec4<f32>, line_width: f32, barycentric_coord: vec3<f32>) -> vec4<f32>{
  let applied: f32 = edge_factor(barycentric_coord, line_width); 
  let step_color = vec4<f32>(applied, applied, applied, 1f);
  let face_color = vec4<f32>(base_color.r*applied, base_color.g*applied, base_color.b*applied, base_color.a);
  return min(face_color, edge_color);
}

fn simple_shading(light_pos: vec3<f32>, vert_normal: vec3<f32>, ambient_color: vec4<f32>) -> vec4<f32>{
  let vert_normal_unit = normalize(vert_normal); 
  let light_normal = normalize(light_pos);
  let relation_to_light = dot(vert_normal_unit, light_normal);
  let specular_amount = max(relation_to_light, 0.0);
  return ambient_color + specular_amount;
}

//const in vec3 L, const in vec3 N, const in vec3 V, float shininess
// WIP... Look at the wikipedia article.
fn blinn_phong(light_pos: vec3<f32>, vert_normal: vec3<f32>, vert_pos: vec4<f32>, shininess: f32) -> vec4<f32>{
    let half_vector = normalize(light_pos + vert_pos.xyz);
    let specular_amount = pow(max(0.0, dot(vert_normal, half_vector)), shininess);
    return vec4<f32>(0f,0f,0f,0f);
}

@fragment
fn fs_main(input : VertexOutput) -> @location(0) vec4<f32> {
  var surface_color: vec4<f32>;

  switch display_config.shading_mode{
    case 0{ //Note: Change this to use constants after upgrading wgpu-py.
      surface_color = debug_shading(DEBUG_BASE_COLOR, DEBUG_LINE_COLOR, DEBUG_LINE_WIDTH, input.barycentric);
    }
    case 1{
      surface_color = simple_shading(LIGHT_POSITION, input.normal, AMBIENT_COLOR);
    }
    default{
      surface_color = DEBUG_BASE_COLOR;
    }
  }

  return surface_color;
}