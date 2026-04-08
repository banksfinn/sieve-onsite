export default {
    fullstack_api: {
        input: {
            target: '../../../backend/tools/openapi/generated/openapi.json',
        },
        output: {
            target: '.',
            outputFile: 'fullstackAPI.ts',
            client: 'react-query',
            baseUrl: '',
            mode: 'single',
            prettier: true,
            tsconfig: '../../tsconfig.json',
            eslint: true,
            override: {
                paramsSerializerOptions: {
                    qs: {
                        arrayFormat: 'repeat',
                    },
                },
                mutator: {
                    path: './customAxios.ts',
                    name: 'customAxios',
                },
            },
        },
    },
};

