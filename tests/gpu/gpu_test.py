from typing import Any
import pytest

import array 
from array import array as create_array
from functools import reduce
from operator import mul

import wgpu.utils

"""
This test class is just to help work through the complexities of working with compute
shaders. It will be removed after building the render/compute graph system.
"""

@pytest.fixture
def gpu() -> tuple[wgpu.GPUDevice, wgpu.GPUAdapter]:
    """Returns the default GPU device and adapter."""
    device: wgpu.GPUDevice = wgpu.utils.get_default_device()
    adapter: wgpu.GPUAdapter = device.adapter
    return (device, adapter)

class TestGPU:
    def test_computing_doubles(self, gpu: tuple[wgpu.GPUDevice, wgpu.GPUAdapter]) -> None:
        # https://webgpufundamentals.org/webgpu/lessons/webgpu-fundamentals.html (Hello world compute shader)
        device, adapter = gpu

        # 2. Setup the Computer Shader
        kernel: str = f"""
            // Bound variable that can be written to and read from.
            @group(0) @binding(0) var<storage, read_write> data: array<f32>;
    
            @compute 
            @workgroup_size(1) 
            fn main(@builtin(global_invocation_id) id: vec3<u32>) {{
                // The ID value passed in is a 3D vector of three unsigned integers.
                // The vector contains:
                //  X: 
                //  Y: 
                //  Z: 

                //1. ?
                let i = id.x;
                
                // Look up the data at the location, multiply it by 2 and save it back to the buffer.
                data[i] = data[i] * 2.0;
            }}
        """

        # 3. Compile the compute shader.
        compute_shader: wgpu.GPUShaderModule = device.create_shader_module(label='Computer Shader', code=kernel)

        # 4. Set up the compute pipeline.
        pipeline = device.create_compute_pipeline(
            label = 'Compute Pipeline', 
            layout = wgpu.AutoLayoutMode.auto, # type: ignore
            compute={
                'module': compute_shader,
                'entry_point': 'main'
            } 
        )

        # 5. Create the input array and buffer
        original_input: tuple[float, ...] = (1,2,3)
        kernel_input: array.array = create_array('f', original_input)
        input_buffer_size: int = kernel_input.itemsize * len(kernel_input)
        work_buffer: wgpu.GPUBuffer = device.create_buffer(
            label = 'Work Buffer',
            size = input_buffer_size,
            usage = wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_SRC | wgpu.BufferUsage.COPY_DST # type: ignore
        )

        device.queue.write_buffer(work_buffer, 0, kernel_input)

        # 6. Create the results buffer for getting the output of the compute shader.
        result_buffer: wgpu.GPUBuffer = device.create_buffer(
            label = 'Result Buffer',
            size = input_buffer_size, 
            usage = wgpu.BufferUsage.MAP_READ | wgpu.BufferUsage.COPY_DST # type: ignore
        )

        # 7. Create a bind group for the compute shader's input.
        bind_group = device.create_bind_group(
            label = 'Bind group for input buffer',
            layout = pipeline.get_bind_group_layout(0),
            entries = [{
                'binding': 0,
                'resource': {
                    'buffer': work_buffer,
                    'offset': 0,
                    'size': input_buffer_size
                }
            }]
        )

        # 8. Encode commands to do the computation.
        encoder: wgpu.GPUCommandEncoder = device.create_command_encoder(label='Kernel Encoder')
        compute_pass: wgpu.GPUComputePassEncoder = encoder.begin_compute_pass(label='Kernel Compute Pass') 
        compute_pass.set_pipeline(pipeline)
        compute_pass.set_bind_group(0, bind_group)
        compute_pass.dispatch_workgroups(len(kernel_input))
        compute_pass.end()

        # 9. Encode a command to copy to the results to a mappable buffer.
        encoder.copy_buffer_to_buffer(
            source = work_buffer,
            source_offset = 0,
            destination = result_buffer,
            destination_offset = 0,
            size = input_buffer_size
        )

        # 10. Finish encoding
        compute_cmd_buffer: wgpu.GPUCommandBuffer = encoder.finish()

        # 11. Submit the encoded commands to the GPU.
        # This is when the GPU computation happens.
        device.queue.submit([compute_cmd_buffer])

        # 12. Read the results from the results buffer and return a memoryview.
        result_buffer.map(wgpu.MapMode.READ) # type: ignore
        output = result_buffer.read_mapped().cast('f').tolist()
        result_buffer.unmap()
        
        print(output)
        assert output == [2, 4, 6]
        

    """
    Resources 
    - https://wgpu-py.readthedocs.io/en/stable/generated/wgpu.GPUAdapter.html#wgpu.GPUAdapter.info

    
    To get the local limits:
    import wgpu.utils
    from pprint import pprint as pp

    pp(wgpu.utils.get_default_device().adapter.limits)
    """

    def test_test_limits(self, gpu: tuple[wgpu.GPUDevice, wgpu.GPUAdapter]) -> None:
        device, adapter = gpu
        # The defaults are specified in the below article.
        # https://webgpufundamentals.org/webgpu/lessons/webgpu-compute-shaders.html (Walks through workgroups.)
        limits: dict[str, int] = adapter.limits
        assert limits['max_compute_invocations_per_workgroup'] >= 256
        assert limits['max_compute_workgroup_size_x'] >= 256
        assert limits['max_compute_workgroup_size_y'] >= 256
        assert limits['max_compute_workgroup_size_z'] >= 64
        
    def test_workgroup_configuration(self, gpu: tuple[wgpu.GPUDevice, wgpu.GPUAdapter]) -> None:
        """
        # https://webgpufundamentals.org/webgpu/lessons/webgpu-compute-shaders.html (Walks through workgroups.)
        """
        device, adapter = gpu

        # 1. Setup the Computer Shader
        dispatch_count: tuple[int, ...] = (4, 3, 2)
        workgroup_size: tuple[int, ...] = (2, 3, 4)

        num_workgroups: int = reduce(mul, dispatch_count)
        num_threads_per_workgroup: int = reduce(mul, workgroup_size)
        num_results: int = num_workgroups * num_threads_per_workgroup
        input_buffer_size:int = num_results * 4 * 4 # vec3f * u32

        kernel: str = f"""
        // NOTE!: vec3u is padded to by 4 bytes
        @group(0) @binding(0) var<storage, read_write> workgroupResult: array<vec3u>;
        @group(0) @binding(1) var<storage, read_write> localResult: array<vec3u>;
        @group(0) @binding(2) var<storage, read_write> globalResult: array<vec3u>;

        @compute @workgroup_size{workgroup_size} fn main(
            @builtin(workgroup_id) workgroup_id : vec3<u32>,
            @builtin(local_invocation_id) local_invocation_id : vec3<u32>,
            @builtin(global_invocation_id) global_invocation_id : vec3<u32>,
            @builtin(local_invocation_index) local_invocation_index: u32,
            @builtin(num_workgroups) num_workgroups: vec3<u32>
        ) {{
            // workgroup_index is similar to local_invocation_index except for
            // workgroups, not threads inside a workgroup.
            // It is not a builtin so we compute it ourselves.

            let workgroup_index =  
                workgroup_id.x +
                workgroup_id.y * num_workgroups.x +
                workgroup_id.z * num_workgroups.x * num_workgroups.y;

            // global_invocation_index is like local_invocation_index
            // except linear across all invocations across all dispatched
            // workgroups. It is not a builtin so we compute it ourselves.

            let global_invocation_index =
                workgroup_index * {num_threads_per_workgroup} +
                local_invocation_index;

            // now we can write each of these builtins to our buffers.
            workgroupResult[global_invocation_index] = workgroup_id;
            localResult[global_invocation_index] = local_invocation_id;
            globalResult[global_invocation_index] = global_invocation_id;
        }}
        """

        # 2. Compile the compute shader.
        compute_shader: wgpu.GPUShaderModule = device.create_shader_module(label='Computer Shader', code=kernel)

        # 3. Set up the compute pipeline.
        pipeline = device.create_compute_pipeline(
            label = 'Compute Pipeline', 
            layout = wgpu.AutoLayoutMode.auto, # type: ignore
            compute={
                'module': compute_shader,
                'entry_point': 'main'
            } 
        )

        # 4. Create the input buffers.
        input_buffer_access_rights: int = wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_SRC # type: ignore
        workgroup_buffer: wgpu.GPUBuffer = device.create_buffer(
            label = 'Workgroup Buffer',
            size = input_buffer_size,
            usage = input_buffer_access_rights
        )
        
        local_buffer: wgpu.GPUBuffer = device.create_buffer(
            label = 'Workgroup Buffer',
            size = input_buffer_size,
            usage = input_buffer_access_rights
        )
        
        global_buffer: wgpu.GPUBuffer = device.create_buffer(
            label = 'Workgroup Buffer',
            size = input_buffer_size,
            usage = input_buffer_access_rights
        )
        

        # 5. Create the output buffers.
        output_buffer_access_rights: int = wgpu.BufferUsage.MAP_READ | wgpu.BufferUsage.COPY_DST # type: ignore
        
        workgroup_read_buffer: wgpu.GPUBuffer = device.create_buffer(
            label = 'Workgroup Buffer',
            size = input_buffer_size,
            usage = output_buffer_access_rights
        )
        
        local_read_buffer: wgpu.GPUBuffer = device.create_buffer(
            label = 'Local Read Buffer',
            size = input_buffer_size,
            usage = output_buffer_access_rights
        )
        
        global_read_buffer: wgpu.GPUBuffer = device.create_buffer(
            label = 'Global Read Buffer',
            size = input_buffer_size,
            usage = output_buffer_access_rights
        )

        # 6. Create bind group for the kernel.
        bind_group: wgpu.GPUBindGroup = device.create_bind_group(
            label='Kernel Bind Group', 
            layout = pipeline.get_bind_group_layout(0),
            entries = [
                {
                    'binding': 0,
                    'resource': {
                        'buffer': workgroup_buffer,
                        'offset': 0,
                        'size': input_buffer_size
                    }
                },
                {
                    'binding': 1,
                    'resource': {
                        'buffer': local_buffer,
                        'offset': 0,
                        'size': input_buffer_size
                    }
                },
                {
                    'binding': 2,
                    'resource': {
                        'buffer': global_buffer,
                        'offset': 0,
                        'size': input_buffer_size
                    }
                }
            ]
        )

        # 7. Encode commands to do the computation.
        encoder: wgpu.GPUCommandEncoder = device.create_command_encoder(label='Kernel Encoder')
        compute_pass: wgpu.GPUComputePassEncoder = encoder.begin_compute_pass(label='Kernel Compute Pass') 
        compute_pass.set_pipeline(pipeline)
        compute_pass.set_bind_group(0, bind_group)
        compute_pass.dispatch_workgroups(*dispatch_count)
        compute_pass.end()

        # 8. Encode a command to copy the results to a mappable buffer.
        encoder.copy_buffer_to_buffer(
            source = workgroup_buffer, 
            source_offset=0, 
            destination=workgroup_read_buffer, 
            destination_offset=0, 
            size=input_buffer_size
        )
        
        encoder.copy_buffer_to_buffer(
            source = local_buffer, 
            source_offset=0, 
            destination=local_read_buffer, 
            destination_offset=0, 
            size=input_buffer_size
        )
        
        encoder.copy_buffer_to_buffer(
            source = global_buffer, 
            source_offset=0, 
            destination=global_read_buffer, 
            destination_offset=0, 
            size=input_buffer_size
        )

        # 9. Finish encoding
        compute_cmd_buffer: wgpu.GPUCommandBuffer = encoder.finish()

        # 10. Submit the encoded commands to the GPU.
        # This is when the GPU computation happens.
        device.queue.submit([compute_cmd_buffer])

         # 12. Read the results from the results buffers.
        workgroup_read_buffer.map(wgpu.MapMode.READ) # type: ignore
        local_read_buffer.map(wgpu.MapMode.READ) # type: ignore
        global_read_buffer.map(wgpu.MapMode.READ) # type: ignore

        workgroup_ids = workgroup_read_buffer.read_mapped().cast('i').tolist()
        local_ids = local_read_buffer.read_mapped().cast('i').tolist()
        global_ids = global_read_buffer.read_mapped().cast('i').tolist()
        
        workgroup_read_buffer.unmap()
        local_read_buffer.unmap()
        global_read_buffer.unmap()

        # 13. Deal with the output...
        # Zip the three lists to make a table?
        table_format = "{:<8} {:<10} {:<10} {:<10}"
        for i in range(num_results):
            dispatch_instance: int = i % num_threads_per_workgroup
            if dispatch_instance == 0:
                header = f"""
---------------------------------------
global                 local     global   dispatch: {dispatch_instance}
invoc.    workgroup    invoc.    invoc.
index     id           id        id
---------------------------------------
                """
                print(header)
            
            offset = i * 4
            workgroup_id = ','.join(map(str, workgroup_ids[offset:offset+3]))
            local_invoc_id = ','.join(map(str,local_ids[offset:offset+3]))
            global_invoc_id = ','.join(map(str,global_ids[offset:offset+3]))

            print(table_format.format(i, workgroup_id, local_invoc_id, global_invoc_id))
    
        assert False