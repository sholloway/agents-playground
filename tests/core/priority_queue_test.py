import pytest

from agents_playground.core.priority_queue import PriorityQueue


class TestPriorityQueue:
    def test_building_a_queue(self):
        queue = PriorityQueue()
        assert len(queue) == 0

        queue.push("p1", 1, 2).push("p4", 2, 7).push("p2", 3, 4).push("p3", 4, 5)

        assert len(queue) == 4

        p1 = queue.pop()
        p2 = queue.pop()
        p3 = queue.pop()
        p4 = queue.pop()

        assert len(queue) == 0

        assert p1[0] == 2 and p1[1] == "p1"
        assert p2[0] == 4 and p2[1] == "p2"
        assert p3[0] == 5 and p3[1] == "p3"
        assert p4[0] == 7 and p4[1] == "p4"

    def test_popping_on_empty_raises(self):
        queue = PriorityQueue()
        assert len(queue) == 0

        with pytest.raises(KeyError) as error:
            queue.pop()

        assert "Cannot pop from an empty priority queue." in str(error.value)

    def test_adding_multiple_times(self):
        # IDs are unique in the queue, not the items.
        # Here we initial add the same item twice using different IDs
        queue = PriorityQueue()
        reused_id = 42
        queue.push("p1", reused_id, 2)
        queue.push("p1", 2, 4)
        assert len(queue) == 2
        assert len(queue._index) == 2

        # If an ID is reused, then that entry is marked for removal and the ID
        # is used for a new entry.
        queue.push("p2", reused_id, 5)
        assert len(queue) == 3
        assert len(queue._index) == 2

        # By inspecting the queue's index we can see that the item stored under
        # the ID has changed.
        item_decorator = queue.index(reused_id)
        assert item_decorator is not None
        assert item_decorator.item == "p2"

    def test_in_clause(self):
        queue = PriorityQueue()
        assert len(queue) == 0

        int_id = 14
        str_id = "abc"
        tuple_id = (14, "abc")
        float_id = 14.7
        queue.push("p1", int_id, 2).push("p4", str_id, 7).push("p2", tuple_id, 4).push(
            "p3", float_id, 5
        )

        assert int_id in queue
        assert str_id in queue
        assert tuple_id in queue
        assert float_id in queue

    def test_priority_tie_breaker(self):
        # When there is a tie among queued items, the order of insertion is used as
        # a tie breaker. The older node (lower count) has higher priority.
        queue = PriorityQueue()
        queue.push("p1", 1, 72).push("p2", 2, 72).push("p3", 3, 72).push("p4", 4, 72)

        # Should pop in order they where added since the priority is all the same.
        p1 = queue.pop()
        p2 = queue.pop()
        p3 = queue.pop()
        p4 = queue.pop()

        assert p1[0] == 72 and p1[1] == "p1"
        assert p2[0] == 72 and p2[1] == "p2"
        assert p3[0] == 72 and p3[1] == "p3"
        assert p4[0] == 72 and p4[1] == "p4"

    def test_removing_items(self):
        queue = PriorityQueue()
        queue.push("p1", 1, 2).push("p4", 2, 104).push("p2", 3, 14).push("p3", 4, 72)

        assert len(queue) == 4
        assert len(queue._index) == 4

        queue.remove(3)  # Remove p2

        assert len(queue) == 4
        assert len(queue._index) == 3

        p1 = queue.pop()
        p3 = queue.pop()
        p4 = queue.pop()

        assert p1[0] == 2 and p1[1] == "p1"
        assert p3[0] == 72 and p3[1] == "p3"
        assert p4[0] == 104 and p4[1] == "p4"

        assert len(queue) == 0
        assert len(queue._index) == 0

    def test_update_priority(self):
        queue = PriorityQueue()
        queue.push("p1", 1, 2).push("p4", 2, 104).push("p2", 3, 14).push("p3", 4, 72)

        # Update p3 to be at the highest priority.
        queue.push("p3", 4, 1)

        assert len(queue) == 5  # Includes the removed item
        assert len(queue._index) == 4  # The four indexed items

        p3 = queue.pop()
        assert p3[0] == 1 and p3[1] == "p3"

    def test_storing_callables(self):
        f1 = lambda d: 4
        f2 = lambda d: "abc"
        f3 = lambda d: True

        queue = PriorityQueue()
        queue.push(f3, 1, 1478)
        queue.push(f2, 2, 766)
        queue.push(f1, 3, 14)

        p1 = queue.pop()
        p2 = queue.pop()
        p3 = queue.pop()

        assert p1[1](None) == 4
        assert p2[1](None) == "abc"
        assert p3[1](None) == True

    def test_str_dunder(self):
        queue = PriorityQueue()
        queue.push("a", 1)
        output = queue.__str__()
        expected = "[PriorityItemDecorator(priority=0, count=0, id=1, item='a', item_data=None)]"
        assert output == expected

    def test_peak_always_returns_highest_priority(self):
        EMPTY_ITEM = None
        queue = PriorityQueue()
        queue.push(EMPTY_ITEM, 1, 200).push(EMPTY_ITEM, 2, 104).push(
            EMPTY_ITEM, 3, 14
        ).push(EMPTY_ITEM, 4, 72)

        assert queue.peek() == (14, 3)

        queue.push(EMPTY_ITEM, 5, 13)
        assert queue.peek() == (13, 5)

        # Verify that removing an item doesn't break peek().
        queue.remove(5)
        queue.remove(3)
        assert queue.peek() == (72, 4)

    def test_peek_returns_none_when_queue_is_empty(self):
        queue = PriorityQueue()
        assert queue.peek() is None


"""
import random
from agents_playground.core.priority_queue import PriorityQueue
q = PriorityQueue()
for i in range(10):
  q.push("SET", i, random.randrange(1, 100000))
q.top()
"""
