/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Response model for Databricks SQL execution.
 */
export type ExecuteDBSQLResponse = {
    success: boolean;
    data?: (Record<string, any> | null);
    error?: (string | null);
    row_count?: (number | null);
};

