var app = angular.module('search', []);

app.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('{a');
    $interpolateProvider.endSymbol('a}');
}]);

app.controller("searchCtrl", function($scope) {
    $scope.store = false;
    $('#new-playlist').submit(function() {
        var playlist = $scope.playlist.split(/(\/|:)/);
        playlist     = playlist[playlist.length-1];
        window.location.href='/score?playlist='+playlist+'&store='+$scope.store;
    });
});
