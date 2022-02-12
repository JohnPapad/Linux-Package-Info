import axios from './axiosConfig';

export const API = {
    getPackages,
    ratePackageVersion,
    changePackageVersionRating,
    getPackagesDockerfile,
    logIn,
    logOut,
    signUp
};

async function getPackages(query) {
    try {
        const response = await axios.get(`/packages/?${query}`)
        return response.data;
    }
    catch (error){
        console.error(error);
    }
}

async function getPackagesDockerfile(payload) {
    try {
        const response = await axios.post('/packages/dockerfile/', payload, { 
            headers: {
                'accept':'text/plain'
            }
        })
        return response.data;
    }
    catch (error){
        console.error(error);
    }
}

async function logIn(payload) {
    try {
        const response = await axios.post(`/users/login/`, payload)
        return response;
    }
    catch (error){
        if (error.response) {
            // Request made and server responded
            return error.response;
        }
        console.error(error);
    }
}

async function logOut(payload) {
    try {
        const response = await axios.post(`/users/logout/`, payload)
        return response;
    }
    catch (error){
        console.error(error);
    }
}

async function signUp(payload) {
    try {
        const response = await axios.post(`/users/register/`, payload)
        return response;
    }
    catch (error){
        if (error.response) {
            // Request made and server responded
            return error.response;
        }
        console.error(error);
    }
}

async function ratePackageVersion(payload) {
    try {
        const response = await axios.post(`/packages/versions/ratings/`, payload)
        return response;
    }
    catch (error){
        console.error(error);
    }
}

async function changePackageVersionRating(payload, ratingId) {
    try {
        const response = await axios.put(`/packages/versions/ratings/${ratingId}/`, payload)
        return response;
    }
    catch (error){
        console.error(error);
    }
}