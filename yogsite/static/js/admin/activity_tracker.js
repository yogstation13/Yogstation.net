window.addEventListener("load", function () {
	window.activity_tracker = new Vue({
		el: '#activity-tracker',
		data: {
			leaderboard: [],
			enabled_ranks: [],
			included_ckeys: "",
			start_date: new Date(new Date().setDate(new Date().getDate() - 27)).toISOString().split("T")[0], // Simply amazing, javascript
			end_date: new Date().toISOString().split("T")[0],

			loading: false
		},
		methods: {
			get_leaderboard_from_api() {
				this.loading = true;
				$.ajax(
					{
						url: `/api/admin/activity`,
						dataType: "json",
						data: {
							start_date: this.start_date,
							end_date: this.end_date,
							enabled_ranks: this.enabled_ranks,
							included_ckeys: this.included_ckeys.split(/\s+/)
						},
						success : function(result) {
							console.log(result)
							window.activity_tracker.leaderboard = result;
							window.activity_tracker.loading = false;
						}
					}
				);
			}
		}
	});
}, false);