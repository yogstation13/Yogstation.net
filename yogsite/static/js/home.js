window.addEventListener("load", function () {

	window.frontpage = new Vue ({
		el: "#frontpage",

		data: {
			staff: {},
			server_stats: []
		},

		mounted: function() {
			load_frontpage_staff();
			load_server_stats_loop();
		}
	})

})

function load_frontpage_staff(round_id) {
	$.getJSON(`/api/frontpage_staff`, function(data) {
		window.frontpage.staff = data;
	})
}

function load_server_stats_loop() {
	$.getJSON(`/api/stats`, function(data) {
		window.frontpage.server_stats = data;
	})
	setTimeout(load_server_stats_loop, 10000)
}
