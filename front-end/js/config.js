(function (exports) {
    exports.appConfiguration = {
        userPool: new AmazonCognitoIdentity.CognitoUserPool({
            UserPoolId: 'us-east-1_pcMj8UVXg',
            ClientId: '2rv366qfb95oeccr6rgi4kndt3'
        }),
        appUrl: 'https://muf30if8ji.execute-api.us-east-1.amazonaws.com/Prod'
    };
    
})(window);