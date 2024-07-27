from __future__ import annotations

from agents_playground.spatial.matrix.matrix import (
    Matrix,
    MatrixError,
    NumericType,
    RowMajorNestedTuple,
)


def m2(
    m00: NumericType, m01: NumericType, m10: NumericType, m11: NumericType
) -> Matrix2x2[NumericType]:
    data = ((m00, m01), (m10, m11))
    return Matrix2x2(data)


# Note: This is a convenience function for the more involved algorithms.
# fmt: off
def det2(a: NumericType, b: NumericType, c: NumericType, d: NumericType) -> NumericType:
    """
    Calculate the determinate of a 2x2 matrix represented as 4 numbers.
    If there is a matrix A, [A] then there is a determinate of |A|.
    [A] = | a, b |
          | c, d |
    |A| = ad - bc
    """
    return a * d - b * c
# fmt: on


class Matrix2x2(Matrix[NumericType]):
    def __init__(self, data: RowMajorNestedTuple) -> None:
        super().__init__(data, 2, 2)

    @staticmethod
    def fill(value: NumericType) -> Matrix[NumericType]:
        return m2(value, value, value, value)

    @staticmethod
    def identity() -> Matrix2x2:
        return m2(1, 0, 0, 1)

    def new(self, *args: NumericType) -> Matrix[NumericType]:
        """Create a new matrix with the same shape but with the provided data."""
        return m2(*args)

    def __repr__(self) -> str:
        row_one = f"{','.join(map(str, self._data[0:2]))}"
        row_two = f"{','.join(map(str, self._data[2:4]))}"
        msg = f"Matrix2x2(\n\t{row_one}\n\t{row_two}\n)"
        return msg

    # fmt: off
    def det(self: Matrix[NumericType]) -> NumericType:
        """
        Calculate the determinate of the matrix.
        If there is a matrix A, [A] then there is a determinate of |A|.
        [A] = | a, b |
              | c, d |
        |A| = ad - bc
        """
        # return self.i(0,0) * self.i(1,1) - self.i(0,1)*self.i(1,0)
        return det2(*self._data)
    # fmt: on

    def adj(self) -> Matrix:
        """
        Calculates the adjugate of the matrix.

        The adjugate of a matrix is the transpose of its cofactor matrix.
        """
        return m2(self.i(1, 1), -self.i(0, 1), -self.i(1, 0), self.i(0, 0))

    def inverse(self: Matrix[NumericType]) -> Matrix[NumericType]:
        """
        Returns the inverse of the matrix as a new matrix.

        The inverse of matrix A is defined as 1/A or A^-1 where
          A*A^-1 = A^-1*A = I

        For I, the identity matrix.
        A^-1 = 1/det(A) * adj(A)

        Which means:
        - A matrix A is invertible (inverse of A exists) only when det(A) ≠ 0.
        """
        determinate: NumericType = self.det()
        if determinate == 0:
            raise MatrixError(
                "Cannot calculate the inverse of a matrix that has a determinate of 0."
            )
        return self.adj() * (1 / determinate)  # type: ignore

    def new_size_smaller(self, *args: NumericType) -> Matrix[NumericType]:
        """Provisions a matrix of a size smaller than the active matrix."""
        raise NotImplementedError()
