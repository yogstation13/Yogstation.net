function int2ip (ipInt) {
    return ( (ipInt>>>24) +'.' + (ipInt>>16 & 255) +'.' + (ipInt>>8 & 255) +'.' + (ipInt & 255) );
}

$(document).ready(function() {
	$("#get-recent-ip-button").click(function() {
		var ckey = $("#form_ban_edit-ckey").val()
		if (!ckey) {return}

		$.getJSON(`/api/last_ip_cid?ckey=${ckey}`, function(data) {
			if (data["success"]) {
				$("#form_ban_edit-ip").val(int2ip(data["data"]["ip"]))
			}
		})
	})

	$("#get-recent-computerid-button").click(function() {
		var ckey = $("#form_ban_edit-ckey").val()
		if (!ckey) {return}

		$.getJSON(`/api/last_ip_cid?ckey=${ckey}`, function(data) {
			if (data["success"]) {
				$("#form_ban_edit-computerid").val(data["data"]["computerid"])
			}
		})
	})
})