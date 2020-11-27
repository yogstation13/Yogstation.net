const DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

window.addEventListener("load", function () {
	window.activity_tracker = new Vue({
		el: '#activity-tracker',
		data: {
			days_of_week: DAYS_OF_WEEK,
			week: new Array(7).fill(new Array(24).fill(0))
		},
		mounted: function() {
			$.getJSON(`/api/admin/activity`, function(data) {
				window.activity_tracker.week = data;
			})
		},
		methods: {
			color_from_amount_active(amount) { // Return color range of red to yellow to green based on number between 1-10
				value = Math.min(amount, 5) / 5
				var hue=((value)*120).toString(10);
				return ["hsl(",hue,",100%,50%)"].join("");
			} 
		}
	});
}, false);