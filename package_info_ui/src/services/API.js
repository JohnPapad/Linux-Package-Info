import axios from './axiosConfig';

export const API = {
    getPackages
};


function getPackages(query) {
    return axios.get('/package',
            {
                params: {
                    query: query
                }
            }
        ).then( response =>  response ? response.data : null)
        .catch( err => log.err(err));
}