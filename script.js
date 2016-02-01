"use strict";

function request(method, url, data, onload, onerror) {
	const request = new XMLHttpRequest();
	request.open(method, url, true);
	request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
	request.onerror = function(e) {
		if(onerror) {
			onerror("HTTP request failed");
		}
	}
	request.onload = function(e) {
		if( request.status == 200 ){
			onload(JSON.parse(request.responseText))
		} else {
			if(onerror) {
				onerror(request.statusText);
			}
		}
	}
	let encoded = "";
	if(typeof data !== null) {
		for (var key in data) {
			if (data.hasOwnProperty(key)) {
				if(encoded) {
					encoded += "&";
				}
				encoded += encodeURIComponent(key)+"="+encodeURIComponent(data[key]);
			}
		}
	}
	request.send(encoded);
}

function post(url, data, onload, onerror) {
	return request('POST', url, data, onload, onerror)
}

function get(url, onload, onerror) {
	return request('GET', url, null, onload, onerror)
}

function addComments(comments) {
	for(const c of comments){
		if(!document.getElementById(c.id)) {
			const line = document.getElementById(c.left_id) || document.getElementById(c.right_id)
			if(!line) {
				console.error("missing source for: "+JSON.stringify(c));
				continue;
			}
			const target = line.parentElement.children[2]
			const comment = document.createElement('div');
			comment.id = c.id;
			comment.innerText = c.message;
			comment.className = 'comment';
			target.appendChild(comment);
		}
	}
}

function createCommentEditor(review_id, left_id, right_id) {
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
		const data = {
			"review_id": review_id,
			"left_id": left_id,
			"right_id": right_id,
			"message": text.value,
		};
		post('/comment/create', data, function(response) {
			const parent = form.parentElement;
			form.remove();
			addComments(response)
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
		form.remove();
	});
	form.appendChild(cancel);
	form.appendChild(errorText);
	return form;
}

function initComments(review_id) {
	function onCommentClick(e){
		if(e.target.parentElement == this) {
			this.children[2].appendChild(createCommentEditor(review_id, this.children[0].id, this.children[1].id));
		}
	}
	const commentable = document.getElementsByClassName('c')
	for(var i=0; i<commentable.length;i++) {
		commentable[i].addEventListener("click", onCommentClick);
	}
	get('/comments/' + review_id, addComments, null);
}

