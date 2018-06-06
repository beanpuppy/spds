var app = angular.module('score', []);

app.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('{a');
    $interpolateProvider.endSymbol('a}');
}]);

app.controller("scoreCtrl", function($scope, $location, $http) {
    $scope.url      = $location.absUrl().split('?')[1]
    $scope.page_url = $location.absUrl().split('?')[1].split('&')[0]
    $scope.loaded   = false;

    $http({
        method : "GET",
        url    : "analyse?" + $scope.url
    }).then(function(response) {
        $scope.callback = response.data;
        $scope.loaded   = true;
    });
});

app.directive('loading', ['$http', function($http) {
    return {
        restrict: 'A',
        link: function(scope, elm, attrs) {
            scope.loading = function () {
                return $http.pendingRequests.length > 0;
            };
            scope.$watch(scope.loading, function(v) {
                if(v) {
                    elm.show();
                } else {
                    elm.hide();
                }
            });
        }
    };
}]);
