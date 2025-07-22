"""Tools router demonstrating MCP tool creation with Databricks SDK integration."""

import os
from typing import Any, Dict, Optional

from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import DatabricksError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class ExecuteDBSQLRequest(BaseModel):
  """Request model for executing Databricks SQL."""

  query: str
  warehouse_id: Optional[str] = None
  catalog: Optional[str] = None
  schema: Optional[str] = None
  limit: Optional[int] = 100


class ExecuteDBSQLResponse(BaseModel):
  """Response model for Databricks SQL execution."""

  success: bool
  data: Optional[Dict[str, Any]] = None
  error: Optional[str] = None
  row_count: Optional[int] = None


@router.post('/execute_dbsql', response_model=ExecuteDBSQLResponse)
async def execute_dbsql(request: ExecuteDBSQLRequest) -> ExecuteDBSQLResponse:
  """Execute SQL query using Databricks SDK with PAT authentication.

  This endpoint demonstrates how to create MCP tools that interact with
  Databricks services using the SDK and Personal Access Token (PAT).

  Args:
      request: SQL execution request with query and optional parameters

  Returns:
      ExecuteDBSQLResponse with query results or error message
  """
  try:
    # Initialize Databricks SDK with PAT from environment
    w = WorkspaceClient(
      host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
    )

    # Get warehouse ID from request or environment
    warehouse_id = request.warehouse_id or os.environ.get('DATABRICKS_SQL_WAREHOUSE_ID')
    if not warehouse_id:
      raise ValueError(
        'No SQL warehouse ID provided. Set DATABRICKS_SQL_WAREHOUSE_ID or pass warehouse_id.'
      )

    # Build the full query with catalog/schema if provided
    query = request.query
    if request.catalog and request.schema:
      # Prepend USE statements if catalog/schema specified
      query = f'USE CATALOG {request.catalog}; USE SCHEMA {request.schema}; {query}'

    # Execute the query
    print(f'🔧 Executing SQL on warehouse {warehouse_id}: {query[:100]}...')

    # Use the SQL execution API
    result = w.statement_execution.execute_statement(
      warehouse_id=warehouse_id,
      statement=query,
      wait_timeout='30s',  # Wait up to 30 seconds for results
    )

    # Process results
    if result.result and result.result.data_array:
      # Convert data array to list of dicts
      columns = [col.name for col in result.manifest.schema.columns]
      data = []

      for row in result.result.data_array[: request.limit]:
        row_dict = {}
        for i, col in enumerate(columns):
          row_dict[col] = row[i]
        data.append(row_dict)

      return ExecuteDBSQLResponse(
        success=True, data={'columns': columns, 'rows': data}, row_count=len(data)
      )
    else:
      # Query executed but no results (e.g., DDL statement)
      return ExecuteDBSQLResponse(
        success=True, data={'message': 'Query executed successfully with no results'}, row_count=0
      )

  except DatabricksError as e:
    print(f'❌ Databricks error: {str(e)}')
    return ExecuteDBSQLResponse(success=False, error=f'Databricks error: {str(e)}')
  except Exception as e:
    print(f'❌ Error executing SQL: {str(e)}')
    return ExecuteDBSQLResponse(success=False, error=f'Error: {str(e)}')


@router.get('/list_warehouses')
async def list_warehouses() -> Dict[str, Any]:
  """List available SQL warehouses using Databricks SDK.

  This endpoint demonstrates how to list resources using the SDK.

  Returns:
      Dictionary containing list of SQL warehouses
  """
  try:
    # Initialize Databricks SDK
    w = WorkspaceClient(
      host=os.environ.get('DATABRICKS_HOST'), token=os.environ.get('DATABRICKS_TOKEN')
    )

    # List SQL warehouses
    warehouses = []
    for warehouse in w.warehouses.list():
      warehouses.append(
        {
          'id': warehouse.id,
          'name': warehouse.name,
          'state': warehouse.state.value if warehouse.state else 'UNKNOWN',
          'size': warehouse.cluster_size,
          'type': warehouse.warehouse_type.value if warehouse.warehouse_type else 'UNKNOWN',
        }
      )

    return {'success': True, 'warehouses': warehouses, 'count': len(warehouses)}

  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
