from agents_playground.spatial.aabbox import AABBox2d
from agents_playground.spatial.vertex import Vertex2d


class TestAABBox:
    def test_overlapping_boxes(self) -> None:
        box_a = AABBox2d(center=Vertex2d(x=5.0, y=5.0), half_width=2, half_height=2)

        down = AABBox2d(center=Vertex2d(x=5.0, y=6.0), half_width=2, half_height=2)
        lower_corner = AABBox2d(center=Vertex2d(x=6.0, y=6.0), half_width=2, half_height=2)
        to_right = AABBox2d(center=Vertex2d(x=6.0, y=5.0), half_width=2, half_height=2)
        upper_right = AABBox2d(center=Vertex2d(x=6.0, y=4.0), half_width=2, half_height=2)
        up = AABBox2d(center=Vertex2d(x=5.0, y=4.0), half_width=2, half_height=2)
        upper_left = AABBox2d(center=Vertex2d(x=4.0, y=4.0), half_width=2, half_height=2)
        left = AABBox2d(center=Vertex2d(x=4.0, y=5.0), half_width=2, half_height=2)
        lower_left = AABBox2d(center=Vertex2d(x=5.0, y=5.0), half_width=2, half_height=2)
        surrounding = AABBox2d(center=Vertex2d(x=4.0, y=5.0), half_width=12, half_height=12)

        assert box_a.intersect(down), "Expected the two boxes to intersect."
        assert box_a.intersect(lower_corner), "Expected the two boxes to intersect."
        assert box_a.intersect(to_right), "Expected the two boxes to intersect."
        assert box_a.intersect(upper_right), "Expected the two boxes to intersect."
        assert box_a.intersect(up), "Expected the two boxes to intersect."
        assert box_a.intersect(upper_left), "Expected the two boxes to intersect."
        assert box_a.intersect(left), "Expected the two boxes to intersect."
        assert box_a.intersect(lower_left), "Expected the two boxes to intersect."

        assert box_a.intersect(box_a), "Expected the box to intersect itself."
        assert box_a.intersect(surrounding), "Expected nested boxes to intersect."

    def test_non_overlapping_boxes(self) -> None:
        box_a = AABBox2d(center=Vertex2d(x=5.0, y=5.0), half_width=2, half_height=2)

        down = AABBox2d(center=Vertex2d(x=5.0, y=16.0), half_width=2, half_height=2)
        lower_corner = AABBox2d(
            center=Vertex2d(x=16.0, y=16.0), half_width=2, half_height=2
        )
        to_right = AABBox2d(center=Vertex2d(x=16.0, y=5.0), half_width=2, half_height=2)
        upper_right = AABBox2d(center=Vertex2d(x=16.0, y=0.0), half_width=2, half_height=2)
        up = AABBox2d(center=Vertex2d(x=5.0, y=0.0), half_width=2, half_height=2)
        upper_left = AABBox2d(center=Vertex2d(x=0.0, y=0.0), half_width=2, half_height=2)
        left = AABBox2d(center=Vertex2d(x=0.0, y=5.0), half_width=2, half_height=2)
        lower_left = AABBox2d(center=Vertex2d(x=0.0, y=16.0), half_width=2, half_height=2)

        assert not box_a.intersect(down)
        assert not box_a.intersect(lower_corner)
        assert not box_a.intersect(to_right)
        assert not box_a.intersect(upper_right)
        assert not box_a.intersect(up)
        assert not box_a.intersect(upper_left)
        assert not box_a.intersect(left)
        assert not box_a.intersect(lower_left)
