const DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

window.addEventListener("load", function () {
	window.activity_tracker = new Vue({
		el: '#activity-tracker',
		data: {
			days_of_week: DAYS_OF_WEEK,
			week: new Array(7).fill(new Array(24).fill(null)),

			start_date: new Date(new Date().setDate(new Date().getDate() - 27)).toISOString().split("T")[0], // Simply amazing, javascript
			end_date: new Date().toISOString().split("T")[0],
			filter_rank: "All"
		},
		mounted: function() {
			this.update_week_from_api();
		},
		methods: {
			update_week_from_api() {
				$.getJSON(`/api/admin/activity?start_date=${this.start_date}&end_date=${this.end_date}&rank_filter=${this.filter_rank}`, function(data) {
					window.activity_tracker.week = data;
				})
			},
			color_from_amount_active(amount) { // Return color range of red to yellow to green based on number between 1-10
				if (amount == null) {
					console.log("h");
					return "#888";
				}
				value = Math.min(amount, 5) / 5
				var hue=((value)*120).toString(10);
				return ["hsl(",hue,",100%,50%)"].join("");
			} 
		}
	});
}, false);