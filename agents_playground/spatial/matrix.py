from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from functools import singledispatchmethod, wraps
import more_itertools
from typing import Callable, Generic, List, Sequence, Tuple, TypeVar, cast

from agents_playground.spatial.vector import Vector
from agents_playground.spatial.vector2d import Vector2d
from agents_playground.spatial.vector3d import Vector3d
from agents_playground.spatial.vector4d import Vector4d

MatrixType = TypeVar('MatrixType', int, float)
RowMajorNestedTuple = Tuple[Tuple[MatrixType, ...], ...]

def vector(*args) -> Vector:
  """Given a set of arguments, create a vector of the appropriate size."""
  match len(args):
    case 2:
      return Vector2d(*args)
    case 3:
      return Vector3d(*args)
    case 4:
      return Vector4d(*args)
    case _:
      raise NotImplementedError(f'Cannot create a vector with {len(args)} dimensions.')
    

class MatrixOrder(Enum):
  Row = 0
  Column = 1

def flatten(data: RowMajorNestedTuple, major: MatrixOrder) -> Tuple[MatrixType, ...]:
  match major:
    case MatrixOrder.Row:
      return tuple(more_itertools.flatten(data))
    case MatrixOrder.Column:
      return ( 
        data[0][0], data[0][1], data[2][0], data[3][0], 
        data[0][1], data[1][1], data[2][1], data[3][1], 
        data[0][2], data[1][2], data[2][2], data[3][2], 
        data[0][3], data[1][3], data[2][3], data[3][3], 
      )
    
def expand(data: Sequence[MatrixType], width, height) -> RowMajorNestedTuple:
  """Does the opposite of expand. Given a flat list builds a RowMajorNestedTuple."""
  rows: List[Tuple[MatrixType, ...]] = []
  for row in range(height):
    start = row * width + 0
    stop = start + width
    rows.append(tuple(data[start:stop]))
  # Convert the outer list to a tuple.
  return tuple(rows)
    
class MatrixError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

def guard_indices(func):
  """A decorator that enforces the range i,j are in."""
  error_msg = "The guard_indices decorator supports guarding functions with parameters named i,j or row, col."
  @wraps(func)
  def _guard(*args, **kwargs):
    self = args[0]
    if len(args) >= 3:
      # Support the convention of functions specifying self, i,j as the first two parameters
      i = args[1]
      j = args[2]
    else: 
      # Does the function use named parameters
      # Support the convention (i,j) or (row, col)
      if 'i' in kwargs:
        i = kwargs['i']  
      elif 'row' in kwargs:
        i = kwargs['row'] 
      else:
        raise MatrixError(error_msg)
      
      if 'j' in kwargs:
        j = kwargs['j']  
      elif 'col' in kwargs:
        j = kwargs['col'] 
      else:
        raise MatrixError(error_msg)
      
    if i >= 0 and i < self.width and j >= 0 and j < self.height:
      return func(*args, **kwargs)
    else:
      general_msg = 'Attempted to access an element in a Matrix at an invalid index.'
      usage_msg = f'matrix.i(row, col) only accepts values in the range [0, ({self.width} | {self.height})].'
      found_msg = f'found matrix.i(row={i}, col={j})'
      msg = f'{general_msg}\n{usage_msg}\n{found_msg}'
      raise MatrixError(msg)
  return _guard

def enforce_matrix_size(func):
  """A decorator that guards against using another matrix of a different size."""
  @wraps(func)
  def _guard(*args, **kwargs):
    self: Matrix = args[0]
    other: Matrix = args[1]
    if self.width == other.width and self.height == other.height:
      return func(*args, **kwargs)
    else:
      error_msg = f"Cannot perform this operation on matrices that are of different sizes."
      raise MatrixError(error_msg)
  return _guard

# TODO: Consider making this an abstract class.
# That would enable consistency in storage and there are some methods that could be pulled up.
# The application of the guard_index may be able to just stay in this module.
class Matrix(Generic[MatrixType], ABC):
  def __init__(self, data: RowMajorNestedTuple, width: int, height: int) -> None:
    self._data = flatten(data, MatrixOrder.Row)
    self._width = width
    self._height = height

  @abstractmethod
  def new(self, *args: MatrixType) -> Matrix[MatrixType]:
    """Create a new matrix with the same shape but with the provided data."""

  @property
  def width(self) -> int:
    """Returns the width of the matrix"""
    return self._width

  @property
  def height(self) -> int:
    """Returns the height of the matrix"""
    return self._height
  
  def __eq__(self, other: object) -> bool:
    if isinstance(other, Matrix):
      return self._data.__eq__(other._data)
    else:
      raise MatrixError(f'Cannot compare a Matrix{self.width}x{self.height} to a {type(other)}')

  @guard_indices
  def i(self, row: int, col: int) -> MatrixType:
    """Finds the stored value in the matrix at matrix[i][j] using row-major convention."""
    # https://en.wikipedia.org/wiki/Row-_and_column-major_order
    return self._data[row * self.width + col]

  def flatten(self, major: MatrixOrder) -> Tuple[MatrixType, ...]:
    """
    Flattens the matrix into a tuple.

    Args:
      - major (MatrixOrder): Determines if the returned tuple will be in row-major
        or column-major order. The default is MatrixOrder.Column.

    Returns 
    The flattened tuple is either of the form:
    For the matrix:
      | m00, m01 |
      | m10, m11 |
  
    Row-Major
    (m00, m01, m02, m03)

    Column-Major
    (m00, m10, m20, m30)
    """
    match major:
      case MatrixOrder.Row:
        return self._data
      case MatrixOrder.Column:
        new_order: List[MatrixType] = []
        for j in range(self.height):
          for i in range(self.width):
            new_order.append(self.i(i,j))
        return tuple(new_order)
  
  def transpose(self) -> Matrix[MatrixType]:
    """
    Returns the transpose of the matrix along its diagonal as a new matrix.

      For the matrix:
      | m00, m01, m02, m03 |
      | m10, m11, m12, m13 |
      | m20, m21, m22, m23 |
      | m30, m31, m32, m33 |

    Returns:
      | m00, m10, m20, m30 |
      | m01, m11, m21, m31 |
      | m02, m12, m22, m32 |
      | m03, m13, m23, m33 |
    """
    col_order = self.flatten(MatrixOrder.Column)
    return self.new(*col_order)

  def to_vectors(self, major: MatrixOrder) -> Tuple[Vector, ...]:
    """
    Returns the rows or columns of the matrix as a series of vectors.

    Args:
      - major (MatrixOrder): Determines the orientation of the vectors.
    """
    rows = []
    match major:
      case MatrixOrder.Row:
        for row in range(self.height):
          start = row * self.width + 0
          stop = start + self.width
          rows.append(vector(*self._data[start:stop]))
        return tuple(rows)
      case MatrixOrder.Column:
        return self.transpose().to_vectors(MatrixOrder.Row)
      
  @enforce_matrix_size
  def __add__(self, other: Matrix) -> Matrix:
    """Returns the results of adding this with another matrix of the same size."""
    new_values = []
    for i in range(self.width):
      for j in range(self.height):
        new_values.append(self.i(i,j) + other.i(i,j))
    return self.new(*new_values)
  
  @enforce_matrix_size
  def __sub__(self, other: Matrix) -> Matrix:
    new_values = []
    for i in range(self.width):
      for j in range(self.height):
        new_values.append(self.i(i,j) - other.i(i,j))
    return self.new(*new_values)
  
  def map(self, func: Callable[[MatrixType], MatrixType]) -> Matrix[MatrixType]:
    """Creates a new matrix by applying a function to every element in the matrix."""
    return self.new(*[func(item) for item in self._data])
  
  @guard_indices
  def sub_matrix(self, row: int, col:int) -> Matrix[MatrixType]:
    """
    Given a location in a matrix, return the sub-matrix created by removing the
    row/column that intersect at the row/col location.

    A 4x4 will return a 3x3. A 3x3 will return a 2x2. A 2x2 will throw an error.
    """
    indices = tuple(range(self.width))
    filtered_rows = tuple(filter(lambda i: i != row, indices))
    filtered_cols = tuple(filter(lambda i: i != col, indices))
    sub_matrix_data = []
    for i in filtered_rows:
      for j in filtered_cols:
        sub_matrix_data.append(self.i(i,j))
    return self.new_size_smaller(*sub_matrix_data)
  
  @abstractmethod
  def new_size_smaller(self,  *args: MatrixType) -> Matrix[MatrixType]:
    """Provisions a matrix of a size smaller than the active matrix."""
          
  @abstractmethod
  def det(self) -> float:
    """
    Calculate the determinate of the matrix.
	  If there is a matrix A, [A] then there is a determinate of |A|.
    [A] = | a, b | 
			    | c, d |
	  |A| = ad - bc
    """

  @abstractmethod
  def adj(self) -> Matrix:
    """
    Calculates the adjugate of the matrix.

    The adjugate of a matrix is the transpose of its cofactor matrix.
    """

  @abstractmethod
  def inverse(self) -> Matrix[MatrixType]:
    """
    Returns the inverse of the matrix as a new matrix.
    
    The inverse of matrix A is defined as 1/A or A^-1 where
      A*A^-1 = A^-1*A = I
    
    For I, the identity matrix.
    A^-1 = 1/det(A) * adj(A)

    Which means:
    - A matrix A is invertible (inverse of A exists) only when det(A) ≠ 0.
    """

@singledispatchmethod
def __mul__(self, other) -> Matrix:
  """
  Multiply this matrix by another matrix, scalar, or vector. 

  Returns
    this * other
  """
  error_msg = f"Cannot multiply an instance of Matrix{self.width}x{self.height} by an instance of {type(other)}"
  raise MatrixError(error_msg)

@__mul__.register
@enforce_matrix_size
def _(self, other: Matrix) -> Matrix:
  # A new matrix is created by multiplying the rows of this matrix by 
  # the columns of the other matrix. So for C = A*B
  # Cij = Ai * Bj
  # So, Cij is the dot product of row Ai and column Bj.
  r = self.to_vectors(MatrixOrder.Row)
  c = other.to_vectors(MatrixOrder.Column)
  new_values = []
  for i in range(self.width):
    for j in range(self.height):
      new_values.append(r[i]*c[j])
  return cast(Matrix, self.new(*new_values))
      
@__mul__.register
def _(self, other: int | float) -> Matrix:
  new_values = [other * x for x in self._data]
  return cast(Matrix, self.new(*new_values))

Matrix.__mul__ = __mul__ # type: ignore