customSignIn = function (form) {
    var xmlhttp = new XMLHttpRequest();

    var timestamp = Date.now();



    var data = JSON.stringify({
        email: form.username.value,
        password: form.password.value,
        timestamp: timestamp
    });

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            localStorage.setItem("user_email", form.username.value);
            customSignInResponse(JSON.parse(xmlhttp.responseText));
        }
    };

    sendPOSTRequest(xmlhttp, "/signin/", data);
};

customSignInResponse = function (result) {
    if (result.success) {
        connectWebSocket();
        localStorage.setItem("user_token", result.data);
        changeView("profile");
    } else {
        document.getElementById("signinform").username.setCustomValidity(result.message);
    }
};

customSignUp = function (form) {
    var xmlhttp = new XMLHttpRequest();

    var data = JSON.stringify({
        city: form.city.value,
        country: form.country.value,
        email: form.email.value,
        familyname: form.lastname.value,
        firstname: form.firstname.value,
        gender: form.gender.value,
        password: form.password.value,
        repassword: form.repassword.value,
        timestamp: Date.now()
    });

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            customSignUpResponse(JSON.parse(xmlhttp.responseText));
        }
    };

    sendPOSTRequest(xmlhttp, "/signup/", data);
};

customSignUpResponse = function (result) {
    var form = document.getElementById("signupform");
    if (result.success) {
        form.email.setCustomValidity("");
        form.reset();
    } else {
        form.email.setCustomValidity(result.message);
    }
};

customSignOut = function () {
    var xmlhttp = new XMLHttpRequest();

    var timestamp = Date.now();

    var data_to_hash = JSON.stringify({
        timestamp: timestamp,
        token: localStorage.getItem("user_token")
    });

    var hashed_data = CryptoJS.SHA256("/signout/" + data_to_hash);

    var data = JSON.stringify({
        email: localStorage.getItem("user_email"),
        hash: hashed_data.toString(),
        timestamp: timestamp
    });

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            customSignOutResponse(JSON.parse(xmlhttp.responseText));
        }
    };

    sendPOSTRequest(xmlhttp, "/signout/", data)
};

customSignOutResponse = function (result) {
    if (result.success) {
        changeView("welcome");
    }
};

customChangePassword = function (form) {
    var xmlhttp = new XMLHttpRequest();

    var timestamp = Date.now();

    var data_to_hash = JSON.stringify({
        newpassword: form.newpassword.value,
        oldpassword: form.oldpassword.value,
        timestamp: timestamp,
        token: localStorage.getItem("user_token")
    });

    var hashed_data = CryptoJS.SHA256("/changepassword/" + data_to_hash);

    var data = JSON.stringify({
        newpassword: form.newpassword.value,
        oldpassword: form.oldpassword.value,
        email: localStorage.getItem("user_email"),
        hash: hashed_data.toString(),
        timestamp: timestamp
    });

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            customChangePasswordResponse(JSON.parse(xmlhttp.responseText));
        }
    };

    sendPOSTRequest(xmlhttp, "/changepassword/", data);
};

customChangePasswordResponse = function (result) {
    var form = document.getElementById("accountform");
    if (result.success) {
        form.oldpassword.setCustomValidity("");
        form.reset();
    }
    else {
        form.oldpassword.setCustomValidity(result.message);
    }
};

customPostMessage = function (form) {
    var xmlhttp = new XMLHttpRequest();

    var timestamp = Date.now();

    var data_to_hash = JSON.stringify({
        client_email: localStorage.getItem("user_email"),
        message: form.message.value,
        post_email: localStorage.getItem("post_email"),
        timestamp: timestamp,
        token: localStorage.getItem("user_token")
    });

    var hashed_data = CryptoJS.SHA256("/postmessage/" + data_to_hash);

    var data = JSON.stringify({
        message: form.message.value,
        post_email: localStorage.getItem("post_email"),
        client_email: localStorage.getItem("user_email"),
        hash: hashed_data.toString(),
        timestamp: timestamp
    });

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            customPostMessageResponse(JSON.parse(xmlhttp.responseText));
        }
    };

    sendPOSTRequest(xmlhttp, "/postmessage/", data);
};

customPostMessageResponse = function (result) {
    if (result.success) {
        getMessages();
        document.getElementById("postMessageForm").reset();
    }
};

showHomePanel = function () {
    var xmlhttp = new XMLHttpRequest();
    var hashed_data = CryptoJS.SHA256('/getuserdatabytoken/' +
        localStorage.getItem("user_token"));

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            showHomePanelResponse(JSON.parse(xmlhttp.responseText));
        }
    };

    sendGETRequest(xmlhttp, '/getuserdatabytoken/' +
        localStorage.getItem("user_email") + '/' + hashed_data);
};

showHomePanelResponse = function (result) {
if (result.success)
{
    localStorage.setItem("post_email", result.data.email);
    showPanel("home");
    getInfo(result.data.email);
    getMessages();
}
};

getInfo = function (email) {
    var xmlhttp = new XMLHttpRequest();
    var hashed_data = CryptoJS.SHA256('/getuserdatabyemail/' +
        localStorage.getItem("user_token") + '/' + email);

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            getInfoResponse(JSON.parse(xmlhttp.responseText));
        }
    };

    sendGETRequest(xmlhttp, '/getuserdatabyemail/' +
        localStorage.getItem("user_email") + '/' + email + '/' + hashed_data)
};

getInfoResponse = function (result) {
    document.getElementById("firstname").innerHTML = result.data.firstname;
    document.getElementById("lastname").innerHTML = result.data.familyname;
    document.getElementById("email").innerHTML = result.data.email;
    document.getElementById("city").innerHTML = result.data.city;
    document.getElementById("country").innerHTML = result.data.country;
    document.getElementById("gender").innerHTML = result.data.gender;
};

getMessages = function () {
    var xmlhttp = new XMLHttpRequest();

    var hashed_data = CryptoJS.SHA256('/getusermessagesbyemail/' +
        localStorage.getItem("user_token") + '/' +
        localStorage.getItem("post_email"));

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            getMessagesResponse(JSON.parse(xmlhttp.responseText));
        }
    };

    sendGETRequest(xmlhttp, '/getusermessagesbyemail/' +
        localStorage.getItem("user_email") + '/' +
        localStorage.getItem("post_email") + '/' + hashed_data);
};

getMessagesResponse = function (result) {
    var message_board = document.getElementById("message_board_self");
    message_board.value = "";
    if (result.success) {
        for (var i = result.data.length - 1; i >= 0; i--) {
            message_board.value += result.data[i].writer + " : " + result.data[i].content + "\n\n";
        }
    }
};

browseOtherUser = function (form) {
    var email = form.email.value;
    localStorage.setItem("post_email", email);

    var xmlhttp = new XMLHttpRequest();

    var hashed_data = CryptoJS.SHA256('/getuserdatabyemail/' +
        localStorage.getItem("user_token") + '/' + email);

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            browseOtherUserResponse(JSON.parse(xmlhttp.responseText));
        }
    };

    sendGETRequest(xmlhttp, '/getuserdatabyemail/' +
        localStorage.getItem("user_email") + '/' + email +
        '/' + hashed_data);
};

browseOtherUserResponse = function (result) {
    var form = document.getElementById("browseUserForm");
    if (result.success) {
        showPanel("home");
        getInfo(localStorage.getItem("post_email"));
        getMessages();
        form.reset();
    } else {
        form.email.setCustomValidity(result.message);
    }
};

validatePassword = function (password) {
    if (password.value.length < 8) {
        password.setCustomValidity("Password must be atleast 8 characters.");
    } else {
        password.setCustomValidity("");
    }
};

matchingPasswords = function (password, repassword) {
    if (password.value != repassword.value) {
        repassword.setCustomValidity("Passwords must match.");
    } else {
        repassword.setCustomValidity("");
    }
};

sendPOSTRequest = function (xmlhttp, url, data) {
    xmlhttp.open("POST", url, true);
    xmlhttp.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
    xmlhttp.send(data);
};

sendGETRequest = function (xmlhttp, url) {
    xmlhttp.open("GET", url, true);
    xmlhttp.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
    xmlhttp.send(null);
};

connectWebSocket = function () {
    var connection = new WebSocket('ws://' + window.location.hostname + ':5000/signin/' + localStorage.getItem("user_email"));

    connection.onclose = function () {
        connection.close();
        localStorage.setItem("user_token", "");
        localStorage.setItem("user_email", "");
        changeView("welcome");
    };

    connection.onmessage = function (event) {
        var data = JSON.parse(event.data);
        updateGraphs(data.messages,
        data.user_messages,
            data.signedin,
            data.signedup);
    }
};

changeView = function (name) {
    if (name === "welcome") {
        document.getElementById("content").innerHTML = document.getElementById("welcomeview").innerHTML;
    } else if (name == "profile") {
        document.getElementById("content").innerHTML = document.getElementById("profileview").innerHTML;
        showHomePanel();
        createGraphs();
    }
};

showPanel = function (name) {
    homePanel.style.display = "none";
    browsePanel.style.display = "none";
    accountPanel.style.display = "none";
    liveDataPanel.style.display = "none";

    if (name === "home") {
        homePanel.style.display = "block";
    } else if (name === "browse") {
        browsePanel.style.display = "block";
    } else if (name === "account") {
        accountPanel.style.display = "block";
    } else if (name == "liveData") {
        liveDataPanel.style.display = "block";
    }
};

var post_graph;
var user_graph;

createGraphs = function () {
createPostGraph();
createUserGraph();
};

createPostGraph = function() {
var ctx = document.getElementById("post_graph").getContext("2d");

    var data = {
                    labels: ["user posts", "total posts"],
        datasets: [
            {
                fillColor: "rgba(0,102,102,0.5)",
                strokeColor: "rgba(0,120,120,0.8)",
                highlightFill: "rgba(0,51,51,0.75)",
                highlightStroke: "rgba(0,60,60,1)",
                data: [0, 0]
            }]};



    var options = {
        responsive: true
    };

    post_graph = new Chart(ctx).Bar(data, options);
    };

createUserGraph = function() {
var ctx = document.getElementById("user_graph").getContext("2d");

    var data = {
            labels: ["signed in", "signed up"],
        datasets: [
            {
                fillColor: "rgba(0,102,102,0.5)",
                strokeColor: "rgba(0,120,120,0.8)",
                highlightFill: "rgba(0,51,51,0.75)",
                highlightStroke: "rgba(0,60,60,1)",
                data: [0, 0]
            }]
    };


    var options = {
        responsive: true
    };

    user_graph = new Chart(ctx).Bar(data, options);
    };

updateGraphs = function (total_messages, user_messages, signedin, signedup) {
updatePostGraph(user_messages, total_messages);
updateUserGraph(signedin, signedup);
};

updatePostGraph = function(user_messages, total_messages){
    post_graph.datasets[0].bars[0].value = user_messages;
    post_graph.datasets[0].bars[1].value = total_messages;
    post_graph.update();
}

updateUserGraph = function(signedin, signedup) {
    user_graph.datasets[0].bars[0].value = signedin;
    user_graph.datasets[0].bars[1].value = signedup;
    user_graph.update();
}

init = function () {
    changeView("welcome");
};

window.onload = function () {
    init();
};