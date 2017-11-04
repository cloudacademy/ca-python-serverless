(function (exports) {
    exports.appConfiguration = {
        userPool: new AmazonCognitoIdentity.CognitoUserPool({
            UserPoolId: 'us-west-2_pcMj8UVXg',
            ClientId: '2rv366qfb95oeccr6rgi4kndt3'
        }),
        appUrl: 'https://muf30if8ji.execute-api.us-west-2.amazonaws.com/Prod'
    };
    
})(window);