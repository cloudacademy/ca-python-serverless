/*jshint unused:false */

(function (exports, $) {

	'use strict';
	
	function fetch(endpoint, token, onSuccess, onFailure) {
		$.ajax({
            method: 'GET',
            url: endpoint + '/todo',
            headers: {
                Authorization: token
            },            
            contentType: 'application/json',
            success: onSuccess,
            error: onFailure
        });
	}

	function save(endpoint, item, token, onSuccess, onFailure) {
		$.ajax({
            method: 'POST',
            url: endpoint + '/todo',
            headers: {
                Authorization: token
			},  
			data: item, 
            contentType: 'application/json',
            success: onSuccess,
            error: onFailure
        });
	}
		
	function update(endpoint, item, token, onSuccess, onFailure) {
		$.ajax({
            method: 'PUT',
            url: endpoint + '/todo',
            headers: {
                Authorization: token
			},  
			data: item, 
            contentType: 'application/json',
            success: onSuccess,
            error: onFailure
        });
	}
		
	function remove(endpoint, id, token, onSuccess, onFailure) {
		$.ajax({
            method: 'DELETE',
            url: endpoint + '/todo?id=' + id,
            headers: {
                Authorization: token
			},  
            contentType: 'application/json',
            success: onSuccess,
            error: onFailure
        });
	}
	exports.todoStorage = {
		fetch: fetch,
		save: save,
		update: update,
		remove: remove
	};

})(window, jQuery);
