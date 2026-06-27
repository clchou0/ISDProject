const roleSelect = document.getElementById("role");
if (roleSelect) {
	const customerFields = document.getElementById("customer-fields");
	const staffFields = document.getElementById("staff-fields");

	roleSelect.addEventListener("change", () => {
		const isStaff = roleSelect.value === "staff";
		customerFields.hidden = isStaff;
		staffFields.hidden = !isStaff;
	});
}

function editDeviceRecord(button) {
	let row = button.closest("tr");
	const copy = row.cloneNode(true);
	row.dataset.revertContent = copy.innerHTML;

	row.children[0].innerHTML = `<input name="name" value="${row.children[0].innerHTML}">`;
	row.children[1].innerHTML = `<input name="type" value="${row.children[1].innerHTML}">`;
	const cents = row.children[2].innerHTML.replace("$", "").replace(".", "").trim()
	row.children[2].innerHTML = `<input type="number" name="price" value="${cents}">`;
	row.children[3].innerHTML = `<input name="stock" type=number value="${row.children[3].innerHTML.replace(/\D/g, '')}">`;
	
	row.children[4].querySelector(".catalogue-staff-tools").style.display = "none";
	row.children[4].querySelector(".catalogue-edit-modal").style.display = "";
}

function revertEdit(button) {
	const row = button.closest("tr");

	row.innerHTML = row.dataset.revertContent;
}

function toggleActions() {
	const showActions = document.getElementById('show-actions').checked;
	
	document.querySelectorAll('.action-content').forEach(el => el.style.display = showActions ? 'block' : 'none');
	document.querySelectorAll('.status-content').forEach(el => el.style.display = showActions ? 'none' : 'block');
	document.getElementById('actions-header').textContent = showActions ? 'Actions' : 'Status';
  }

