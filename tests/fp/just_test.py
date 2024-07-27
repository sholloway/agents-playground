from agents_playground.fp import Just


class TestJust:
    def test_unwrap_returns_inner_value(self) -> None:
        value: int = 5
        wrapped = Just(value)
        assert wrapped.unwrap() == value

    def test_just_equality(self) -> None:
        assert Just(5) == Just(5)
        assert Just(72.123) == Just(72.123)
        assert Just(7) == Just(7.0)
        assert Just("abc") == Just("abc")
        assert Just(True) == Just(True)
        assert Just(True) != Just(False)

    def test_just_is_a_monad(self) -> None:
        just_some_monads = [Just(7), Just(True), Just("abc")]

        results = [monad.bind(lambda i: Just(i)) for monad in just_some_monads]
        unwrapped_values = [maybe.unwrap() for maybe in results]
        assert unwrapped_values == [7, True, "abc"]
