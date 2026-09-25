export interface Repository {
    id: number;
    name: string;
    path: string;
    status: string;
}
export interface CreateRepositoryRequest {
    path: string;
}