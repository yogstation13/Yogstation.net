var default_donate_ammount = 7;


function get_benefit_message(amount) {
	if (amount < 7) {
		return "You will not receive any donor benefits."
	}

	if (amount < 14) {
		return "You will receive ONE month of donor benefits."
	}

	return "You will receive THREE months of donor benefits."
}

window.addEventListener("load", function () {
	window.donate_form = new Vue({
		el: '#donate-form',
		data: {
			donate_amount: default_donate_ammount,
			benefit_message: get_benefit_message(default_donate_ammount)
		},

		watch: {
			donate_amount: {
				handler: function(val, old_val) {
					window.donate_form.benefit_message = get_benefit_message(val)
				}
			}
		}
	});
}, false);