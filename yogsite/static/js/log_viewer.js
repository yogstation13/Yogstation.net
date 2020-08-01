var category_color_classes = {
	"game": "is-primary",
	"attack": "is-warning",
	"runtime": "is-danger",
	"config_error": "is-danger is-light",
	"map_errors": "is-danger is-light",
	"telecomms": "is-success",
	"pda": "is-success is-light",
	"sql": "is-info",
	"tgui": "is-link",
	"hrefs": "is-link is-light",
	"job_debug": "is-warning is-light",
	"mecha": "is-warning is-light",
	"asset": "is-primary is-light",
	"manifest": "is-info is-light"
}

window.addEventListener("load", function () {

	window.log_viewer = new Vue ({
		el: "#log-viewer",

		data: {
			query: "",
			log_entries: [],
			enabled_categories: Object.keys(category_color_classes)
		},

		mounted: function() {
			load_logs(log_viewer_round_id);
		},

		computed: {
			filtered_log_entries() {
				return this.log_entries.filter(entry => {
					return	entry.content.toLowerCase().includes(this.query.toLowerCase()) &&
							this.enabled_categories.includes(entry.category);
				})
			}
		},

		methods: {
			format_datetime_local: format_datetime_local
		}
	})

})

function load_logs(round_id) {
	$.getJSON(`/api/rounds/${round_id}/logs`, function(data) {
		window.log_viewer.log_entries = data;
	})
}

