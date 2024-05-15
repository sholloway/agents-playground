from agents_playground.fp import Maybe, Nothing, Something
from agents_playground.fp.functions import identity


class TestMaybe:
    def test_maybe_can_be_something(self) -> None:
        maybe = Maybe.from_optional(5)
        assert isinstance(maybe, Something)

    def test_maybe_can_be_nothing(self) -> None:
        maybe = Maybe.from_optional(None)
        assert isinstance(maybe, Nothing)

    def test_maybe_is_a_functor(self) -> None:
        list_of_maybe_instances = [
            Maybe.from_optional(5),
            Something("abc"),
            Maybe.from_optional(None),
            Something(True),
            Nothing(),
        ]

        mapped_maybe_instances = [
            maybe.map(identity) for maybe in list_of_maybe_instances
        ]
        unwrapped_values = [maybe.unwrap() for maybe in mapped_maybe_instances]

        assert unwrapped_values == [5, "abc", None, True, None]
