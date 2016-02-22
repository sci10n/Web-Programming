validatePassword = function(password) {
    if (password.value.length < 8) {
        password.setCustomValidity("Password must be atleast 8 characters.");
    } else {
        password.setCustomValidity("");
    }
    password.checkValidity();
};

matchingPasswords = function(password, repassword) {
    if (password.value != repassword.value) {
        repassword.setCustomValidity("Passwords must match.");
    } else {
        repassword.setCustomValidity("");
    }
    repassword.checkValidity();
}

customChangePassword = function(form) {
    var result = serverstub.changePassword(localStorage.getItem("user_token"), form.oldpassword.value, form.newpassword.value);
    if(result.success){
    	form.oldpassword.setCustomValidity("");
    	form.reset();
    }
    else{
    	form.oldpassword.setCustomValidity(result.message);
    }
    form.oldpassword.checkValidity();
};

customSignOut = function() {
    var result = serverstub.signOut(localStorage.getItem("user_token"));
    if (result.success) {
        changeView("welcome");
    }
}

customSignIn = function(form) {
window.alertalert("customSignIn Begin");
var xmlhttp = new XMLHttpRequest();

xmlhttp.onreadystatechange = function () {
    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
        customSignInResponse(JSON.parse(xmlhttp.responseText));
     }
};

xmlhttp.setRequestHeader("Content-Type", "application/json");

xmlhttp.open("POST", '/signin', true);
xmlhttp.send(JSON.stringify(form.serializeArray()));
}

customSignInResponse = function(result) {
alert("customSignInResponse Begin");
    if (result.success) {
        localStorage.setItem("user_token", result.data);
        changeView("profile");
    } else {
    	form.username.setCustomValidity(result.message);
    }
};

showHomePanel = function(){
    var result = serverstub.getUserDataByToken(localStorage.getItem("user_token")).data;
    localStorage.setItem("post_email", result.email);
    showPanel("home");
    getInfo(result.email);
    getMessages(document.getElementById("message_board_self"));
}

showPanel = function(name) {
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

customSignUp = function(form) {
    var input = {
        email: form.email.value,
        password: form.password.value,
        firstname: form.firstname.value,
        familyname: form.lastname.value,
        gender: form.gender.value,
        city: form.city.value,
        country: form.country.value
    };
    var result = serverstub.signUp(input);

    if (result.success) {
    	form.email.setCustomValidity("");
    	form.clear();
    } else {
     	form.email.setCustomValidity(result.message);
     	form.email.checkValidity();
    }
};

getMessages = function(message_board) {
    var result = serverstub.getUserMessagesByEmail(localStorage.getItem("user_token"), localStorage.getItem("post_email"));
    message_board.value = "";
    if (result.success) {
        for (var i = result.data.length - 1; i >= 0; i--) {
            message_board.value += result.data[i].writer + " : " + result.data[i].content + "\n\n";
        }
    }
};

getInfo = function(email) {
    var result = serverstub.getUserDataByEmail(localStorage.getItem("user_token"), email).data;
    document.getElementById("firstname").innerHTML = result.firstname;
    document.getElementById("lastname").innerHTML = result.familyname;
    document.getElementById("email").innerHTML = result.email;
    document.getElementById("city").innerHTML = result.city;
    document.getElementById("country").innerHTML = result.country;
    document.getElementById("gender").innerHTML = result.gender;
};

browseOtherUser = function(form) {
    var email = form.email.value;
    localStorage.setItem("post_email", email);
    var result = serverstub.getUserDataByEmail(localStorage.getItem("user_token"), email);
    if (result.success) {
        showPanel("home");
        getInfo(email);
        getMessages(message_board_self);
        form.reset();
    } else {
    	form.email.setCustomValidity(result.message);
    }
};

customPostMessage = function(form) {
    var result = serverstub.postMessage(localStorage.getItem("user_token"), form.message.value, localStorage.getItem("post_email"));
    if (result.success) {
	getMessages(document.getElementById("message_board_self"));
	form.reset();
    } 
};

changeView = function(name) {
    if (name === "welcome") {
        document.getElementById("content").innerHTML = document.getElementById("welcomeview").innerHTML;
    } else if (name == "profile") {
        document.getElementById("content").innerHTML = document.getElementById("profileview").innerHTML;
        showHomePanel();
    }
}

init = function() {
    changeView("welcome");
}

window.onload = function() {
    init();
};
