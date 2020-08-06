window.addEventListener("load", function () {
	window.set_loa_form_modal = new Vue({
		el: '#content',

		data: {
			loa_modal_is_active: false,
			loa_target_admin_ckey: null
		}
	});
}, false);