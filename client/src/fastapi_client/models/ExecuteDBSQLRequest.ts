/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Request model for executing Databricks SQL.
 */
export type ExecuteDBSQLRequest = {
    query: string;
    warehouse_id?: (string | null);
    catalog?: (string | null);
    schema?: (string | null);
    limit?: (number | null);
};

