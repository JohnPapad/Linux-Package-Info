import axios from 'axios';

const instance = axios.create({
    baseURL: 'http://' + IP + '/web_app/', 
    headers: {'Content-Type': 'application/json'}
});

export default instance;