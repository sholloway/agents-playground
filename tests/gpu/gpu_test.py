import pytest

import array 
from array import array as create_array
from functools import reduce
from operator import mul

import wgpu.utils


class TestGPU:
    """
    Resources 
    - https://webgpufundamentals.org/webgpu/lessons/webgpu-fundamentals.html (Hello world compute shader)
    - https://webgpufundamentals.org/webgpu/lessons/webgpu-compute-shaders.html (Walks through workgroups.)
    - https://wgpu-py.readthedocs.io/en/stable/generated/wgpu.GPUAdapter.html#wgpu.GPUAdapter.info

    Default Workgroup Limits
    - maxComputeInvocationsPerWorkgroup: 256
    - maxComputeWorkgroupSizeX: 256
    - maxComputeWorkgroupSizeY: 256
    - maxComputeWorkgroupSizeZ: 64
    
    To get the local limits:
    import wgpu.utils
    from pprint import pprint as pp

    pp(wgpu.utils.get_default_device().adapter.limits)
    """

    
    def test_computing_doubles(self) -> None:
        # 1. Get the device and adapter for working with the GPU.
        device: wgpu.GPUDevice = wgpu.utils.get_default_device()
        adapter: wgpu.GPUAdapter = device.adapter

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
        


    def test_blah(self) -> None:
        """
        Do the second tutorial here.
        """
        # 1. Get the device and adapter for working with the GPU.
        device: wgpu.GPUDevice = wgpu.utils.get_default_device()
        adapter: wgpu.GPUAdapter = device.adapter

        dispatch_count: tuple[int, ...] = (4, 3, 2)
        workgroup_size: tuple[int, ...] = (2, 3, 4)

        # 2. Setup the Computer Shader
        num_workgroups: int = reduce(mul, dispatch_count)
        num_threads_per_workgroup: int = reduce(mul, workgroup_size)
        num_results: int = num_workgroups * num_threads_per_workgroup
        input_buffer_size:int = num_results * 4 * 4 # vec3f * u32

        kernel: str = f"""
            
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

        # 5. Create the buffers.
        # usage = wgpu.GPUBuf
        workgroup_buffer: wgpu.GPUBuffer = device.create_buffer(
            label = 'Workgroup Buffer',
            size = input_buffer_size,
            usage = wgpu.BufferUsage.STORAGE | wgpu.BufferUsage.COPY_SRC # type: ignore
        )
