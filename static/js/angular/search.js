var app = angular.module('searchPlaylists', []);

app.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('{a');
    $interpolateProvider.endSymbol('a}');
}]);

app.controller("playlistCtrl", function($scope) {
    $scope.store = false;
    $('#new-playlist').submit(function() {
        var playlist = $scope.playlist.split(/(\/|:)/);
        playlist     = playlist[playlist.length-1];
        window.location.href='/analyse?playlist='+playlist+'&store='+$scope.store;
    });
});
