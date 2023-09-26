from __future__ import annotations

from enum import Enum
from functools import wraps
import more_itertools
from typing import Generic, Protocol, Tuple, TypeVar
from agents_playground.spatial.vector2d import Vector2d

from agents_playground.spatial.vector3d import Vector3d
from agents_playground.spatial.vector4d import Vector4d

MatrixType = TypeVar('MatrixType', int, float)
RowMajorNestedTuple = Tuple[Tuple[MatrixType, ...], ...]

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

class Matrix(Protocol):
  ...

class MatrixError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

def guard_indices(width: int, height: int):
  def decorate(func):
    """A decorator that enforces the range i,j are in."""
    error_msg = "The guard_indices decorator supports guarding functions with parameters named i,j or row, col."
    @wraps(func)
    def _guard(*args, **kwargs):
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
        
      if i >= 0 and i < width and j >= 0 and j < height:
        return func(*args, **kwargs)
      else:
        general_msg = 'Attempted to access an element in a Matrix at an invalid index.'
        usage_msg = f'matrix.i(row, col) only accepts values in the range [0,{width}].'
        found_msg = f'found matrix.i(row={i}, col={j})'
        msg = f'{general_msg}\n{usage_msg}\n{found_msg}'
        raise MatrixError(msg)
    return _guard
  return decorate