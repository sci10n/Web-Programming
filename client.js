displayView = function() {
    //the code required to display a view
};

validatePassword = function(password) {
    if (password.value.length < 8) {
        password.setCustomValidity("Password must be atleast 8 characters.");
        password.reportValidity();
    } else {
        password.setCustomValidity("");
    }
};
matchingPasswords = function(password, repassword) {
    if (password.value != repassword.value) {
        repassword.setCustomValidity("Passwords must match.");
        repassword.reportValidity();
    } else {
        repassword.setCustomValidity("");
    }
}

custom_change_passwd = function(form) {
    var result = serverstub.changePassword(localStorage.getItem("user_token"), form.oldpassword.value, form.newpassword.value);
    window.alert(result.message);
};

custom_sign_out = function() {
    var result = serverstub.signOut(localStorage.getItem("user_token"));
    window.alert(result.message);
    if (result.success) {
        changeView("welcome");
    } else {

    }
}

custom_signin = function(form) {
    var result = serverstub.signIn(form.username.value, form.password.value);
    window.alert(result.message + " " + result.data);
    if (result.success) {
        localStorage.setItem("user_token", result.data);
        changeView("profile");
    } else {

    }
};

showPanel = function(name) {
    homePanel.style.display = "none";
    browsePanel.style.display = "none";
    accountPanel.style.display = "none";
    if (name === "home") {
        homePanel.style.display = "block";
        get_info(serverstub.getUserDataByToken(localStorage.getItem("user_token")).data.email);
        get_messages_self(document.getElementById("message_board_self"));

    } else if (name === "browse") {
        browsePanel.style.display = "block";
    } else if (name === "account") {
        accountPanel.style.display = "block";
    }

};


custom_signup = function(form) {
    var input = {
        email: form.email.value,
        password: form.password.value,
        firstname: form.firstname.value,
        familyname: form.lastname.value,
        gender: form.gender.value,
        city: form.city.value,
        country: form.country.value
    };
    window.alert(input.email);
    var result = serverstub.signUp(input);
    window.alert(result.message);
    if (result.success) {

    } else {

    }
    /*
    if(!result.success){
    	form.email.setCustomValidity(result.message);
    	form.email.checkValidity();
    }
    */
};

get_messages_self = function(message_board) {
    var result = serverstub.getUserDataByToken(localStorage.getItem("user_token"));
    get_messages(message_board, result.data.email);
};

get_messages = function(message_board, email) {
    var result = serverstub.getUserMessagesByEmail(localStorage.getItem("user_token"), email);
    message_board.value = "";
    if (result.success) {
        for (var i = result.data.length - 1; i >= 0; i--) {
            message_board.value += result.data[i].writer + " : " + result.data[i].content + "\n\n";
        }
    }
};

get_info = function(email) {
    var result = serverstub.getUserDataByEmail(localStorage.getItem("user_token"), email).data;
    document.getElementById("firstname").innerHTML = result.firstname;
    document.getElementById("lastname").innerHTML = result.familyname;


};

browse_other_user = function(form) {
    var email = form.email.value;
    var result = serverstub.getUserDataByEmail(localStorage.getItem("user_token"), email);
    if (result.success) {
        showPanel("home");
        get_info(email);
        get_messages(message_board_self, email);
    } else {
        window.alert(result.message);

    }
};

custom_post_message = function(form) {
    var result = serverstub.postMessage(localStorage.getItem("user_token"), form.message.value, form.email.value);
    if (result.success) {

    } else {

    }
};

changeView = function(name) {
    if (name === "welcome") {
        document.getElementById("content").innerHTML = document.getElementById("welcomeview").innerHTML;
    } else if (name == "profile") {
        document.getElementById("content").innerHTML = document.getElementById("profileview").innerHTML;

        showPanel("home");
    }
}

window.onload = function() {
    //code that is executed as the page is loaded.
    //You shall put your own custom code here.
    //window.alert("Hello TDDD97");
    //document.getElementById("homePanel").style.opacity = "0";
    //document.getElementById("browsePanel").style.opacity = "0";
    //document.getElementById("accountPanel").style.opacity = "0";
    changeView("welcome");
};