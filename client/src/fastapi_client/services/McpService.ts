/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class McpService {
    /**
     * Get Mcp Info
     * Get MCP server information including URL and capabilities.
     *
     * Returns:
     * Dictionary with MCP server details
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getMcpInfoApiMcpInfoInfoGet(): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/mcp_info/info',
        });
    }
    /**
     * Get Mcp Discovery
     * Get MCP discovery information including prompts and tools.
     *
     * This endpoint dynamically discovers available prompts and tools
     * from the FastMCP server instance.
     *
     * Returns:
     * Dictionary with prompts and tools lists
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getMcpDiscoveryApiMcpInfoDiscoveryGet(): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/mcp_info/discovery',
        });
    }
}
