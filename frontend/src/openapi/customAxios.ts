import Axios, { AxiosError, AxiosRequestConfig } from 'axios';

export const AXIOS_INSTANCE = Axios.create({
     baseURL: '',
     paramsSerializer: {
          indexes: null, // This will serialize arrays as ids=1&ids=2 instead of ids[]=1&ids[]=2
     },
     withCredentials: true, // Enable sending cookies with requests
}); // use your own URL here or environment variable

export const customAxios = <T>(config: AxiosRequestConfig): Promise<T> => {
     const source = Axios.CancelToken.source();

     const enhancedConfig = {
          ...config,
          cancelToken: source.token,
     };

     const promise = AXIOS_INSTANCE({
          ...enhancedConfig,
     })
          .then(({ data }) => data)
          .catch((error: AxiosError) => {
               if (error.code === 'ERR_CANCELED') {
                    return;
               }

               // If we have a 401 unauthorized error, raise an error
               // We let this be handled in the AuthProvider
               if (error.response?.status === 401) {
                    throw error;
               }
          });

     return promise;
};
