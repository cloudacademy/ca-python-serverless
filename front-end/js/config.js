(function (exports) {
    exports.appConfiguration = {
        userPool: new AmazonCognitoIdentity.CognitoUserPool({
            UserPoolId: '',
            ClientId: ''
        }),
        appUrl: ''
    };
    
})(window);