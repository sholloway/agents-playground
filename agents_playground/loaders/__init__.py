from abc import ABC, abstractmethod
import datetime as dt 
import json
import jsonschema as js
from jsonschema.protocols import Validator
import os
from pathlib import Path
from typing import Any, Protocol

from agents_playground.uom import DateTime

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f %Z"

def str_to_datetime(timestamp: str) -> DateTime:
  """Convert a string timestamp into a datetime instance."""
  return dt.datetime.strptime(timestamp, TIMESTAMP_FORMAT).replace(tzinfo=dt.timezone.utc)

def now_as_string() -> str:
  return dt.datetime.now(tz = dt.timezone.utc).strftime(TIMESTAMP_FORMAT)

_SEARCH_DIRECTORIES: dict[str, None] = {}

def set_search_directories(directories: list[str]) -> None:
  _SEARCH_DIRECTORIES.clear()
  for dir in directories:
    _SEARCH_DIRECTORIES[dir] = None 

def register_search_directory(path:str) -> None:
  _SEARCH_DIRECTORIES[path] = None

def search_directories() -> list[str]:
  """Returns a list of directories to search when trying to find scene related files."""
  return list(_SEARCH_DIRECTORIES)

def find_valid_path(file_path: str, search_directories: list[str]) -> tuple[bool,str]:
  consider_path = file_path
  file_found: bool = os.path.exists(consider_path)
  
  if not file_found:
    # The path may be relative. Attempt to make it a relative path.
    for dir in search_directories:
      consider_path = os.path.join(dir, consider_path)
      file_found = os.path.exists(consider_path)
      if file_found:
        break 
  return (file_found, consider_path)

class JSONFileLoaderStep(ABC):
  @abstractmethod
  def process(
    self, 
    context: dict[str, Any], 
    schema_path: str, 
    file_path: str, 
    search_directories: list[str]
  ) -> bool:
    """
    Runs a step in loading a file.

    Args:
      - context: Maintains the state between steps.
      - schema_path: The path to where schema is.
      - file_path: The path to where the file to load is.
    """    

class JSONFileLoaderStepException(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class ValidateSchemaExists(JSONFileLoaderStep):
  def process(
      self, 
      context: dict[str, Any], 
      schema_path: str, 
      file_path: str, 
      search_directories: list[str]
    ) -> bool: 
    if not os.path.exists(os.path.join(Path.cwd(), schema_path)):
      raise JSONFileLoaderStepException(f'Could not find the schema {schema_path}.')
    return True
  
class ValidateJSONFileExists(JSONFileLoaderStep):
  """Searches for a file.
  
  The search algorithm is:
  1. Try the path provided.
  2. If the provided path fails, then search for the file by joining the provided
     path with each of the provided search directories.
  """
  def process(
    self, 
    context: dict[str, Any], 
    schema_path: str, 
    file_path: str,
    search_directories: list[str]
  ) -> bool: 
    file_found, verified_path = find_valid_path(file_path, search_directories) 
    if file_found:
      context['json_file_path'] = verified_path
    else:
      raise JSONFileLoaderStepException(f'Could not find the JSON file at {file_path} or in {search_directories}.')
        
    return True
  
class LoadJSONIntoMemory(JSONFileLoaderStep):
  def process(
    self, 
    context: dict[str, Any], 
    schema_path: str, 
    file_path: str, 
    search_directories: list[str]
  ) -> bool: 
    with open(file = context['json_file_path'], mode = 'r', encoding="utf-8") as filereader:
      context['json_content'] = json.load(filereader)
    return True
  
class LoadSchemaIntoMemory(JSONFileLoaderStep):
  def process(
    self, 
    context: dict[str, Any], 
    schema_path: str, 
    file_path: str, 
    search_directories: list[str]
  ) -> bool: 
    with open(file = schema_path, mode = 'r', encoding="utf-8") as filereader:
      context['schema_content'] = json.load(filereader)
    return True
  
class ValidateSchema(JSONFileLoaderStep):
  def process(
    self, 
    context: dict[str, Any], 
    schema_path: str, 
    file_path: str, 
    search_directories: list[str]
  ) -> bool: 
    schema_content = context.get('schema_content')
    if schema_content is not None:
      # Raises a jsonschema.exceptions.SchemaError exception if the schema isn't valid.
      Validator.check_schema(schema_content)
    else:
      raise JSONFileLoaderStepException(f'The schema must be loaded into the context before attempting to validate it.')
    return True

class ValidateJSONWithSchema(JSONFileLoaderStep):
  def process(
    self, 
    context: dict[str, Any], 
    schema_path: str, 
    file_path: str, 
    search_directories: list[str]
  ) -> bool: 
    js.validate(
      instance = context['json_content'],
      schema = context['schema_content']
    )
    return True
  
class JSONFileLoader:
  def __init__(self):
    self._steps = [
      ValidateSchemaExists(),
      ValidateJSONFileExists(),
      LoadSchemaIntoMemory(),
      ValidateSchema(),
      LoadJSONIntoMemory(),
      ValidateJSONWithSchema()
    ]
  
  def load(self, context: dict[str, Any], schema_path: str, file_path: str, search_directories: list[str]) -> bool:
    return all([ r.process(context, schema_path, file_path, search_directories) for r in self._steps])