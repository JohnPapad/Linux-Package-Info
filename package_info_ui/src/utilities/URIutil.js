export const createQueryParams = params => 
    Object.entries(params).map(kv => kv.map(encodeURIComponent).join("=")).join("&");


export const getQueryParams = (URLsearch) => {
    let queryParams = {};
    const query = new URLSearchParams(URLsearch);
    for (const param of query.entries()) {
        queryParams[param[0]] = param[1];
    }

    return queryParams;
}