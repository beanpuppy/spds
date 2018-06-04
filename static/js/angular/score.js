var app = angular.module('score', []);

app.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('{a');
    $interpolateProvider.endSymbol('a}');
}]);

app.controller("scoreCtrl", function($scope, $location, $http) {
    $scope.url = $location.absUrl().split('?')[1]
    $http({
        method : "GET",
        url : "analyse?" + $scope.url
    }).then(function(response) {
        $scope.callback = response.data;
    }, function(response) {
        $scope.callback = response.data;
    });
});
