validatePassword = function (password) {
    if (password.value.length < 8) {
        password.setCustomValidity("Password must be atleast 8 characters.");
    } else {
        password.setCustomValidity("");
    }
    password.checkValidity();
};

matchingPasswords = function (password, repassword) {
    if (password.value != repassword.value) {
        repassword.setCustomValidity("Passwords must match.");
    } else {
        repassword.setCustomValidity("");
    }
    repassword.checkValidity();
};

customChangePassword = function (form) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", '/changepassword', true);

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            customChangePasswordResponse(JSON.parse(xmlhttp.responseText));
        }
    };

    xmlhttp.setRequestHeader("Content-Type", "application/json; charset=UTF-8");

    var data = {
        token: localStorage.getItem("user_token"),
        oldpassword: form.oldpassword.value,
        newpassword: form.newpassword.value
    };

    xmlhttp.send(JSON.stringify(data));
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

customSignOut = function () {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", '/signout', true);

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            customSignOutResponse(JSON.parse(xmlhttp.responseText));
        }
    };

    xmlhttp.setRequestHeader("Content-Type", "application/json; charset=UTF-8");

    var data = {
        token: localStorage.getItem("user_token")
    };

    xmlhttp.send(JSON.stringify(data));
};

customSignOutResponse = function (result) {
    if (result.success) {
        changeView("welcome");
    }
};

customSignIn = function (form) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", '/signin', true);

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            customSignInResponse(JSON.parse(xmlhttp.responseText));
        }
    };

    xmlhttp.setRequestHeader("Content-Type", "application/json; charset=UTF-8");

    var data = {
        email: form.username.value,
        password: form.password.value,
    };

    xmlhttp.send(JSON.stringify(data));
};

customSignInResponse = function (result) {
    if (result.success) {
        localStorage.setItem("user_token", result.data);
        changeView("profile");
    } else {
        document.getElementById("signinform").username.setCustomValidity(result.message);
    }
};

showHomePanel = function (message_board) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", '/getuserdatabytoken/' +
        localStorage.getItem("user_token"), true);

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            showHomePanelResponse(JSON.parse(xmlhttp.responseText));
        }
    };

    xmlhttp.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
    xmlhttp.send(null);
};

showHomePanelResponse = function (result) {
    localStorage.setItem("post_email", result.data.email);
    showPanel("home");
    getInfo(result.data.email);
    getMessages(document.getElementById("message_board_self"));
};

showPanel = function (name) {
    homePanel.style.display = "none";
    browsePanel.style.display = "none";
    accountPanel.style.display = "none";
    if (name === "home") {
        homePanel.style.display = "block";
    } else if (name === "browse") {
        browsePanel.style.display = "block";
    } else if (name === "account") {
        accountPanel.style.display = "block";
    }
};

customSignUp = function (form) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", '/signup', true);

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            customSignUpResponse(JSON.parse(xmlhttp.responseText));
        }
    };

    xmlhttp.setRequestHeader("Content-Type", "application/json; charset=UTF-8");

    var data = {
        email: form.email.value,
        password: form.password.value,
        firstname: form.firstname.value,
        familyname: form.lastname.value,
        gender: form.gender.value,
        city: form.city.value,
        country: form.country.value
    };

    xmlhttp.send(JSON.stringify(data));
};

customSignUpResponse = function (result) {
    var form = document.getElementById("signupform");
    if (result.success) {
        form.email.setCustomValidity("");
        form.reset();
    } else {
        form.email.setCustomValidity(result.message);
        form.email.checkValidity();
    }
};

getMessages = function (message_board) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", '/getusermessagesbyemail/' +
        localStorage.getItem("user_token") + '/' +
        localStorage.getItem("post_email"), true);

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            getMessagesResponse(JSON.parse(xmlhttp.responseText));
        }
    };

    xmlhttp.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
    xmlhttp.send(null);
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

customSignUpResponse = function (result) {
    var form = document.getElementById("signupform");
    if (result.success) {
        form.email.setCustomValidity("");
        form.reset();
    } else {
        form.email.setCustomValidity(result.message);
        form.email.checkValidity();
    }
};

getInfo = function (email) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", '/getuserdatabyemail/' +
        localStorage.getItem("user_token") + '/' + email, true);

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            getInfoResponse(JSON.parse(xmlhttp.responseText));
        }
    };

    xmlhttp.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
    xmlhttp.send(null);
};

getInfoResponse = function (result) {
    document.getElementById("firstname").innerHTML = result.data.firstname;
    document.getElementById("lastname").innerHTML = result.data.familyname;
    document.getElementById("email").innerHTML = result.data.email;
    document.getElementById("city").innerHTML = result.data.city;
    document.getElementById("country").innerHTML = result.data.country;
    document.getElementById("gender").innerHTML = result.data.gender;
};

browseOtherUser = function (form) {
    var email = form.email.value;
    localStorage.setItem("post_email", email);

    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", '/getuserdatabyemail/' +
        localStorage.getItem("user_token") + '/' + email, true);

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            browseOtherUserResponse(JSON.parse(xmlhttp.responseText));
        }
    };

    xmlhttp.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
    xmlhttp.send(null);
};

browseOtherUserResponse = function (result) {
    var form = document.getElementById("browseUserForm");
    if (result.success) {
        showPanel("home");
        getInfo(localStorage.getItem("post_email"));
        getMessages(message_board_self);
        form.reset();
    } else {
        form.email.setCustomValidity(result.message);
    }
};

customPostMessage = function (form) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", '/postmessage', true);

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            customPostMessageResponse(JSON.parse(xmlhttp.responseText));
        }
    };

    xmlhttp.setRequestHeader("Content-Type", "application/json; charset=UTF-8");

    var data = {
        token: localStorage.getItem("user_token"),
        message: form.message.value,
        email: localStorage.getItem("post_email")
    };

    xmlhttp.send(JSON.stringify(data));
};

customPostMessageResponse = function (result) {
    if (result.success) {
        getMessages(document.getElementById("message_board_self"));
        document.getElementById("postMessageForm").reset();
    }
};

changeView = function (name) {
    if (name === "welcome") {
        document.getElementById("content").innerHTML = document.getElementById("welcomeview").innerHTML;
    } else if (name == "profile") {
        document.getElementById("content").innerHTML = document.getElementById("profileview").innerHTML;
        showHomePanel();
    }
};

init = function () {
    changeView("welcome");
};

window.onload = function () {
    init();
};
