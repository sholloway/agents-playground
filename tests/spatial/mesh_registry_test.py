import pytest
from agents_playground.spatial.mesh import MeshData, MeshRegistry, MeshRegistryError


@pytest.fixture
def registry() -> MeshRegistry:
    return MeshRegistry()


class TestMeshRegistry:
    def test_initialize_empty(self, registry: MeshRegistry) -> None:
        assert len(registry) == 0

    def test_add_mesh(self, registry: MeshRegistry) -> None:
        registry["my_mesh"] = MeshData("my_mesh")
        assert len(registry) == 1

        registry.add_mesh(MeshData("my_other_mesh"))
        assert len(registry) == 2

        assert registry["my_mesh"].alias == "my_mesh"
        assert registry["my_other_mesh"].alias == "my_other_mesh"

    def test_cannot_assign_alias_twice(self, registry: MeshRegistry) -> None:
        registry["my_mesh"] = MeshData("my_mesh")

        with pytest.raises(MeshRegistryError):
            registry["my_mesh"] = MeshData("my_mesh")

    def test_tagging(self, registry: MeshRegistry) -> None:
        registry["my_mesh"] = MeshData("my_mesh")
        registry["my_other_mesh"] = MeshData("my_other_mesh")
        registry["my_other_other_mesh"] = MeshData("my_other_other_mesh")

        registry.tag("my_mesh", "cool_mesh")
        cool_meshes: list[MeshData] = registry.filter("cool_mesh")
        assert len(cool_meshes) == 1
        assert cool_meshes[0].alias == "my_mesh"

    def test_tag_when_adding(self, registry: MeshRegistry) -> None:
        registry.add_mesh(MeshData("Agent Model"), tags=["agent"])
        registry.add_mesh(
            MeshData("Animated Agent Model"), tags=["agent", "display_normals"]
        )
        registry.add_mesh(MeshData("my_other_other_mesh"), tags=["display_normals"])

        assert len(registry.filter("agent")) == 2
        assert len(registry.filter("display_normals")) == 2

    def test_remove_tag_from_mesh(self, registry: MeshRegistry) -> None:
        registry.add_mesh(MeshData("Agent Model"), tags=["agent"])
        registry.add_mesh(
            MeshData("Animated Agent Model"), tags=["agent", "display_normals"]
        )
        registry.add_mesh(MeshData("my_other_other_mesh"), tags=["display_normals"])
        assert len(registry.filter("display_normals")) == 2

        registry.remove_tag("Animated Agent Model", "display_normals")
        assert len(registry.filter("display_normals")) == 1

    def test_remove_tag_from_registry(self, registry: MeshRegistry) -> None:
        registry.add_mesh(MeshData("Agent Model"), tags=["agent"])
        registry.add_mesh(
            MeshData("Animated Agent Model"), tags=["agent", "display_normals"]
        )
        registry.add_mesh(MeshData("my_other_other_mesh"), tags=["display_normals"])
        assert len(registry.filter("display_normals")) == 2

        registry.delete_tag("display_normals")
        assert len(registry.filter("display_normals")) == 0

    def test_clear_the_registry(self, registry: MeshRegistry) -> None:
        registry.add_mesh(MeshData("Agent Model"), tags=["agent"])
        registry.add_mesh(
            MeshData("Animated Agent Model"), tags=["agent", "display_normals"]
        )
        registry.add_mesh(MeshData("my_other_other_mesh"), tags=["display_normals"])
        assert len(registry) == 3
        registry.clear()
        assert len(registry) == 0
