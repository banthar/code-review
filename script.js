"use strict";

function post(url, data, onload, onerror) {
	const request = new XMLHttpRequest();
	request.open("POST", url, true);
	request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
	request.onerror = function(e) {
		onerror("Unable to send request");
	}
	request.onload = function(e) {
		if( request.status != 200 ){
			onerror(request.status+" "+request.statusText);
		} else {
			onload(request.responseText)
		}
	}

	let encoded = "";
	for (var key in data) {
		if (data.hasOwnProperty(key)) {
			encoded += encodeURIComponent(key)+"="+encodeURIComponent(data[key]);
		}
	}

	request.send(encoded);
}

const commentable = document.getElementsByClassName('c')
for(var i=0; i<commentable.length;i++) {
	function createForm(mainElement) {
		const form = document.createElement("form");
		const errorText = document.createElement("span");


		const text = document.createElement("textarea");
		text.style.width='500px';
		text.style.height='100px';
		form.appendChild(text);

		form.appendChild(document.createElement("br"));

		const save = document.createElement("input");
		save.type = 'button';
		save.value = "Save";
		save.addEventListener("click", function() {
			errorText.innerText = 'Sending ...';
			errorText.style.color = null;
			post('/comment/create', {"message": text.value}, function(response) {
				const parent = form.parentElement;
				form.remove();
				const comment = document.createElement('div');
				comment.innerText = response;
				comment.className = 'comment';
				parent.appendChild(comment);
			}, function(error) {
				errorText.innerText = error;
				errorText.style.color = 'red';
			});
		});
		form.appendChild(save);

		const cancel = document.createElement("input");
		cancel.type = 'button';
		cancel.value = "Cancel";
		cancel.addEventListener("click", function() {
			mainElement.remove();
		});
		form.appendChild(cancel);

		form.appendChild(errorText);

		return form;
	}
	const addCommentEditor = function(){
		const td = document.createElement("td");
		td.colSpan = 10;
		const tr = document.createElement("tr");
		td.appendChild(createForm(tr));
		tr.appendChild(td);
		const parent = this.parentElement;
		parent.insertBefore(tr, this.nextSibling);
	};
	commentable[i].addEventListener("click", addCommentEditor);
}

