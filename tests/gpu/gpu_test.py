import pytest

import wgpu.utils;

class TestGPU:
    def test_adapter(self) -> None:
        # https://wgpu-py.readthedocs.io/en/stable/generated/wgpu.GPUAdapter.html#wgpu.GPUAdapter.info
        device = wgpu.utils.get_default_device()
        adapter = device.adapter
        # wgpu = "^0.13.0"