Vue.options.delimiters = ['${', '}'];


window.addEventListener("load", function () {
	var nav = new Vue({
		el: '#navbar',
		data: {
			nav_open: false
		}
	});
}, false);


function setTwoNumberDecimal(event) {
    this.value = parseFloat(this.value).toFixed(2);
}

function format_datetime_local(dt, format) {
	return new moment.unix(dt).format("YYYY-MM-DD HH:mm:ss.SSS");
}
