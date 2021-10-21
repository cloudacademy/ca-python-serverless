/*global Vue, todoStorage */

(function (exports) {

	'use strict';

	var filters = {
		all: function (todos) {
			return todos;
		},
		active: function (todos) {
			return todos.filter(function (todo) {
				return !todo.completed;
			});
		},
		completed: function (todos) {
			return todos.filter(function (todo) {
				return todo.completed;
			});
		}
	};

	exports.applicationConfigSettings = new Vue({
		data: {
			appState: '',
			userPool: appConfiguration.userPool,
			token: '',
			appUrl: appConfiguration.appUrl
		},
		watch: {
			appState: function (val) {
				var apps = [exports.login, exports.register, exports.update, exports.app];

				for (var i = 0; i < apps.length; i++) {
					var app = apps[i];
					app.show = app.showForStates.indexOf(val) >= 0;
				}
			}
		}
	});

	// Set the initial state
	authTokenPromise(exports.applicationConfigSettings.userPool).then(function (token) {
		if (!token) {
			exports.applicationConfigSettings.appState = 'LOGGED_OUT';
			return;
		}
		exports.applicationConfigSettings.token = token;
		exports.applicationConfigSettings.appState = 'LOGGED_IN';

	}).catch(function (error) {
		alert(error);
	});



	exports.login = new Vue({
		el: '.login',
		data: {
			username: '',
			password: '',
			showForStates: ['LOGGED_OUT'],
			show: false
		},
		methods: {
			login: function () {
				var that = this;
				login(this.username, this.password, applicationConfigSettings.userPool,
					function (res) {
						applicationConfigSettings.appState = 'LOGGED_IN';
						that.username = '';
						that.password = '';

					},
					function (res) {
						if (res.code === 'UserNotConfirmedException') {
							applicationConfigSettings.appState = 'NEEDS_UPDATE';
						}
					}
				);
			}
		}
	});

	exports.register = new Vue({
		el: '.register',
		data: {
			username: '',
			password: '',
			showForStates: ['LOGGED_OUT'],
			show: false
		},
		methods: {
			register: function () {
				register(this.username, this.password, applicationConfigSettings.userPool, function (a) {
					if (!a.userConfirmed) {
						applicationConfigSettings.appState = 'NEEDS_UPDATE';
					}
				}, function (a) {
					console.error(a);
				});
			}
		}
	});

	exports.update = new Vue({
		el: '.update',
		data: {
			username: '',
			code: '',
			showForStates: ['NEEDS_UPDATE'],
			show: false
		},
		methods: {
			verify: function () {
				verify(this.username, this.code, applicationConfigSettings.userPool, function (a) {
					applicationConfigSettings.appState = 'LOGGED_OUT';
				}, function (e) {
					console.error(e);
					alert(e);
				});
			}
		}
	});


	exports.app = new Vue({

		// the root element that will be compiled
		el: '.todoapp',

		// app initial state
		data: {
			todos: [],
			newTodo: '',
			editedTodo: null,
			visibility: 'all',
			showForStates: ['LOGGED_IN'],
			show: false
		},

		// computed properties
		// http://vuejs.org/guide/computed.html
		computed: {
			filteredTodos: function () {
				return filters[this.visibility](this.todos);
			},
			remaining: function () {
				return filters.active(this.todos).length;
			},
			allDone: {
				get: function () {
					return this.remaining === 0;
				},
				set: function (value) {
					this.todos.forEach(function (todo) {
						todo.completed = value;
					});
				}
			}
		},

		watch: {
			// If this is set to show, then fetch the items.
			show: function (val) {
				if (val) {
					this.getAll();
				}
			}
		},
		// methods that implement data logic.
		// note there's no DOM manipulation here at all.
		methods: {
			signOut: function () {
				applicationConfigSettings.userPool.getCurrentUser().signOut();
				applicationConfigSettings.appState = 'LOGGED_OUT';
			},
			getAll: function () {
				var that = this;
				todoStorage.fetch(applicationConfigSettings.appUrl, applicationConfigSettings.token, function (res) {
					that.todos = res;
				}, function (e) {
					console.error(e);
					alert('Welcome! Please refresh the page to continue.');
				});

			},
			pluralize: function (word, count) {
				return word + (count === 1 ? '' : 's');
			},
			complete: function (todo) {
				todoStorage.update(applicationConfigSettings.appUrl, JSON.stringify(todo), applicationConfigSettings.token);
			},
			addTodo: function () {
				var that = this;
				var value = this.newTodo && this.newTodo.trim();
				if (!value) {
					return;
				}

				todoStorage.save(applicationConfigSettings.appUrl, JSON.stringify({ 'item': value }), applicationConfigSettings.token, function (res) {
					that.todos.push({ item: value, completed: false });
					that.newTodo = '';
				});

			},

			removeTodo: function (todo) {
				var that = this;
				todoStorage.remove(applicationConfigSettings.appUrl, todo.todoId, applicationConfigSettings.token, function (res) {
					var index = that.todos.indexOf(todo);
					that.todos.splice(index, 1);
				});

			},

			editTodo: function (todo) {
				this.beforeEditCache = todo.item;
				this.editedTodo = todo;
			},

			doneEdit: function (todo) {
				if (!this.editedTodo) {
					return;
				}
				this.editedTodo = null;
				todo.item = todo.item.trim();
				if (!todo.item) {
					this.removeTodo(todo);
				}
				todoStorage.update(applicationConfigSettings.appUrl, JSON.stringify(todo), applicationConfigSettings.token);
			},

			cancelEdit: function (todo) {
				this.editedTodo = null;
				todo.item = this.beforeEditCache;
			},

			removeCompleted: function () {
				this.todos = filters.active(this.todos);
			}
		},

		// a custom directive to wait for the DOM to be updated
		// before focusing on the input field.
		// http://vuejs.org/guide/custom-directive.html
		directives: {
			'todo-focus': function (el, binding) {
				if (binding.value) {
					el.focus();
				}
			}
		}
	});


	function register(email, password, userPool, onSuccess, onFailure) {
		var dataEmail = {
			Name: 'email',
			Value: email
		};
		var attributeEmail = new AmazonCognitoIdentity.CognitoUserAttribute(dataEmail);

		userPool.signUp(email, password, [attributeEmail], null,
			function signUpCallback(err, result) {
				if (!err) {
					onSuccess(result);
				} else {
					onFailure(err);
				}
			}
		);
	}

	function verify(email, code, userPool, onSuccess, onFailure) {
		var cogUser = new AmazonCognitoIdentity.CognitoUser({
			Username: email,
			Pool: userPool
		});

		cogUser.confirmRegistration(code, true, function (err, result) {
			if (!err) {
				onSuccess(result);
			} else {
				onFailure(err);
			}
		});
	}

	function login(email, password, userPool, onSuccess, onFailure) {
		var auth = new AmazonCognitoIdentity.AuthenticationDetails({
			Username: email,
			Password: password
		});

		var cogUser = new AmazonCognitoIdentity.CognitoUser({
			Username: email,
			Pool: userPool
		});

		cogUser.authenticateUser(auth, {
			onSuccess: onSuccess,
			onFailure: onFailure
		});
	}

	function authTokenPromise(userPool) {
		return new Promise(function (resolve, reject) {
			var cogUser = userPool.getCurrentUser();

			if (!cogUser) {
				return resolve(null);
			}

			cogUser.getSession(function (err, session) {
				if (err) {
					return reject(err);
				}

				if (!session.isValid()) {
					return resolve(null);
				}

				return resolve(session.getIdToken().getJwtToken());
			});
		});
	}

})(window);
