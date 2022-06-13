const SHORTENED_EL = document.getElementById("shortened");
const BTN_EL = document.getElementById("btn");
const LONG_URL_EL = document.getElementById("long-url");
const URL_BACK_EL = document.getElementById("url-back");

function makeid(length) {
  var result           = '';
  var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  var charactersLength = characters.length;
  for ( var i = 0; i < length; i++ ) {
    result += characters.charAt(Math.floor(Math.random() * 
  charactersLength));
  }
  return result;
}


URL_BACK_EL.value = makeid(10);

function onShortened() {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/shorten", true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4 && xhr.status == 200) {
      var response = JSON.parse(xhr.responseText);
      SHORTENED_EL.innerHTML = window.location.origin + "/" + response.id;
      SHORTENED_EL.style.color = "black";
    }

    else if (xhr.readyState == 4 && xhr.status == 409) {
      var response = JSON.parse(xhr.responseText);
      SHORTENED_EL.innerHTML = response.detail;
      SHORTENED_EL.style.color = "red";
    }
  }
  xhr.send(JSON.stringify({ url: LONG_URL_EL.value, id: URL_BACK_EL.value }));
}
