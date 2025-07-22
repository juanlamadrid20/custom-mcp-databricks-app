/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ExecuteDBSQLRequest } from '../models/ExecuteDBSQLRequest';
import type { ExecuteDBSQLResponse } from '../models/ExecuteDBSQLResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ToolsService {
    /**
     * Execute Dbsql
     * Execute SQL query using Databricks SDK with PAT authentication.
     *
     * This endpoint demonstrates how to create MCP tools that interact with
     * Databricks services using the SDK and Personal Access Token (PAT).
     *
     * Args:
     * request: SQL execution request with query and optional parameters
     *
     * Returns:
     * ExecuteDBSQLResponse with query results or error message
     * @param requestBody
     * @returns ExecuteDBSQLResponse Successful Response
     * @throws ApiError
     */
    public static executeDbsqlApiToolsExecuteDbsqlPost(
        requestBody: ExecuteDBSQLRequest,
    ): CancelablePromise<ExecuteDBSQLResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/tools/execute_dbsql',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Warehouses
     * List available SQL warehouses using Databricks SDK.
     *
     * This endpoint demonstrates how to list resources using the SDK.
     *
     * Returns:
     * Dictionary containing list of SQL warehouses
     * @returns any Successful Response
     * @throws ApiError
     */
    public static listWarehousesApiToolsListWarehousesGet(): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/tools/list_warehouses',
        });
    }
}
