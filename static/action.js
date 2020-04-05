/* Send a request to endpoint when button is clicked */

let requestor;
function extract() {
    requestor = new XMLHttpRequest();
    requestor.open('POST', 'http://127.0.0.1:5000/graphs', true);   // change this to point to appropriate endpoint
    requestor.setRequestHeader('Content-Type', 'application/json');
    requestor.send(JSON.stringify({
      'county': document.getElementById('county-id').value,
      'state': document.getElementById('state-id').value
    }));

    let response = {};

    requestor.addEventListener("readystatechange", function (event) {
      if (requestor.readyState == 4 && requestor.status == 200) {
          response = JSON.parse(requestor.responseText);  //response is a JSON object
          console.log(response);
      }
      else if (requestor.readyState == 4 && requestor.status == 400) {
          alert('Bad request');
      }
    }, false);

}