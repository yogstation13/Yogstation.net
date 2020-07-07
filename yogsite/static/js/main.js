Vue.options.delimiters = ['${', '}'];


window.onload = function () {
	var nav = new Vue({
		el: '#navbar',
		data: {
			nav_open: false
		}
	});
}