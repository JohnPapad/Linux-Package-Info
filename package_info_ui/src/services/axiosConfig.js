import axios from 'axios';

const backendAPIbaseURL = "http://0.0.0.0:8000/api/v1/";

const axiosInstance = axios.create({
    baseURL: backendAPIbaseURL,
    timeout: 5000,
    headers: {
		'Authorization': localStorage.getItem('access_token')
			? 'Bearer ' + localStorage.getItem('access_token')
			: null,
		'Content-Type': 'application/json',
		'accept': 'application/json',
	}, 
});

axiosInstance.interceptors.response.use(
	(response) => {
		return response;
	},
	async function (error) {
		const originalRequest = error.config;

		if (typeof error.response === 'undefined') {
			alert('A server/network error occurred...');
			return Promise.reject(error);
		}

		if (error.response.status === 403 && originalRequest.url === backendAPIbaseURL + 'users/login/token/refresh/') {
			alert("Please login again");
			return Promise.reject(error);
		}

		if (error.response.data.code === 'token_not_valid' && error.response.status === 403 && error.response.statusText === 'Forbidden') {
			const refreshToken = localStorage.getItem('refresh_token');

			if (refreshToken) {
				const tokenParts = JSON.parse(atob(refreshToken.split('.')[1]));

				// exp date in token is expressed in seconds, while now() returns milliseconds:
				const now = Math.ceil(Date.now() / 1000);
				// console.log(tokenParts.exp);

				if (tokenParts.exp > now) {
					return axiosInstance
						.post('/users/login/token/refresh/', { refresh: refreshToken })
						.then((response) => {
							localStorage.setItem('access_token', response.data.access);
							localStorage.setItem('refresh_token', response.data.refresh);

							axiosInstance.defaults.headers['Authorization'] =
								'Bearer ' + response.data.access;
							originalRequest.headers['Authorization'] =
								'Bearer ' + response.data.access;

							return axiosInstance(originalRequest);
						})
						.catch((err) => {
							console.error(err);
						});
				} else {
					console.log('Refresh token is expired', tokenParts.exp, now);
					alert("Please login again");
				}
			} else {
				console.log('Refresh token not available.');
				alert("Please login again");
			}
		}

		return Promise.reject(error);
	}
);

export default axiosInstance;