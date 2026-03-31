// ================= LOGIN FORM =================

document.getElementById("loginForm")?.addEventListener("submit", function(event){

event.preventDefault();

let id = document.getElementById("employeeId").value;
let password = document.getElementById("password").value;
let role = document.getElementById("role").value;

if(id === "" || password === "")
{
document.getElementById("error").innerText = "Please enter login details";
return;
}

fetch("/login", {
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
employee_id:id,
password:password
})
})
.then(res => res.json())
.then(data => {

if(data.status === "success")
{
localStorage.setItem("employee_id", id);

// IMPORTANT — Flask Routes
if(role === "admin")
{
window.location.href="/admin";
}
else
{
window.location.href="/employee";
}
}
else
{
document.getElementById("error").innerText="Invalid Credentials";
}

});

});



// ================= CREATE BRIEF =================

document.getElementById("briefForm")?.addEventListener("submit", function(event){

event.preventDefault();

let week = document.getElementById("weekNumber").value;
let airline = document.getElementById("airline").value;
let incident = document.getElementById("incident").value;
let circular = document.getElementById("circularLink").value;
let comment = document.getElementById("opsComment").value;
let conclusion = document.getElementById("conclusion").value;

fetch("/createBrief", {
method:"POST",
headers:{
"Content-Type":"application/json"
},
body: JSON.stringify({
week_number: week,
airline: airline,
incident: incident,
circular_link: circular,
ops_comment: comment,
conclusion: conclusion
})
})
.then(res => res.json())
.then(data => {

if(data.status === "success")
{
alert("Briefing Saved to Database");
}

});

});



// ================= LOAD LATEST BRIEF =================

let currentBriefID = null;

function loadLatestBrief(){

fetch("/latestBrief")
.then(res => res.json())
.then(data => {

if(data)
{
currentBriefID = data.brief_id;

document.getElementById("briefWeek").innerText =
"Weekly Briefing - " + data.week_number;

document.getElementById("briefAirline").innerText =
"Airline: " + data.airline;

document.getElementById("briefIncident").innerText =
"Incident: " + data.incident;

document.getElementById("briefComment").innerText =
data.ops_comment;

document.getElementById("briefConclusion").innerText =
data.conclusion;

document.getElementById("briefCircular").href =
data.circular_link;
}

});

}



// ================= ACKNOWLEDGE =================

function acknowledgeBrief(){

let employeeID = localStorage.getItem("employee_id");

fetch("/acknowledge", {
method:"POST",
headers:{
"Content-Type":"application/json"
},
body: JSON.stringify({
employee_id: employeeID,
brief_id: currentBriefID
})
})
.then(res => res.json())
.then(data => {

if(data.status === "success")
{
alert("Acknowledgement Recorded");
}
else if(data.status === "already")
{
alert("You have already acknowledged this briefing");
}

});

}



// ================= ADMIN DASHBOARD STATS =================

function loadStats(){

fetch("/stats")
.then(res => res.json())
.then(data => {

document.getElementById("totalEmployees").innerText = data.total_employees;
document.getElementById("readEmployees").innerText = data.read;
document.getElementById("pendingEmployees").innerText = data.pending;

});

}



// ================= LOAD ACKNOWLEDGEMENT TABLE =================

function loadAcknowledgements(){

fetch("/acknowledgementList")
.then(res => res.json())
.then(data => {

let table = document.getElementById("ackTable");

data.forEach(row => {

let tr = document.createElement("tr");

tr.innerHTML = `
<td>${row.name}</td>
<td>${row.department}</td>
<td class="${row.status === 'Read' ? 'read' : 'pending'}">
${row.status}
</td>
`;

table.appendChild(tr);

});

});

}



// ================= LOAD HISTORY =================

function loadHistory(){

fetch("/historyData")
.then(res => res.json())
.then(data => {

let table = document.getElementById("historyTable");

data.forEach(row => {

let tr = document.createElement("tr");

tr.innerHTML = `
<td>${row.week_number}</td>
<td>${row.airline}</td>
<td>${row.incident}</td>
<td><a href="${row.circular_link}" target="_blank">Link</a></td>
<td>${row.ops_comment}</td>
<td>${row.conclusion}</td>
<td>${row.created_at}</td>
`;

table.appendChild(tr);

});

});

}



// ================= LOGOUT =================

function logout(){
localStorage.removeItem("employee_id");
window.location.href = "/";
}