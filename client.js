
displayView = function() {
    //the code required to display a view
};

validatePassword = function(password) {
    if (password.value.length < 8) {
        password.setCustomValidity("Password must be atleast 8 characters.");
        password.checkValidity();
    } else {
        password.setCustomValidity("");
    }
};
matchingPasswords = function(password, repassword) {
    if (password.value != repassword.value) {
        repassword.setCustomValidity("Passwords must match.");
        repassword.checkValidity();
    } else {
        repassword.setCustomValidity("");
    }
}

custom_change_passwd = function(form) {
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

custom_sign_out = function() {
    var result = serverstub.signOut(localStorage.getItem("user_token"));
    if (result.success) {
        changeView("welcome");
    } else {

    }
}

custom_signin = function(form) {
    var result = serverstub.signIn(form.username.value, form.password.value);
    if (result.success) {
        localStorage.setItem("user_token", result.data);
        changeView("profile");

    } else {
    	form.username.setCustomValidity(result.message);
    }
};

show_home_panel = function(){
	var result = serverstub.getUserDataByToken(localStorage.getItem("user_token")).data;
	localStorage.setItem("post_email", result.email);
	showPanel("home");
	get_info(result.email);
    get_messages(document.getElementById("message_board_self"));

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
    var result = serverstub.signUp(input);
    if (result.success) {
    	  form.email.setCustomValidity("");
    	  form.clear();
    } else {
     	form.email.setCustomValidity(result.message);
     	form.email.checkValidity();
    }
    /*
    if(!result.success){
    	form.email.setCustomValidity(result.message);
    	form.email.checkValidity();
    }
    */
};

get_messages = function(message_board) {
    var result = serverstub.getUserMessagesByEmail(localStorage.getItem("user_token"), localStorage.getItem("post_email"));
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
    document.getElementById("email").innerHTML = result.email;
    document.getElementById("city").innerHTML = result.city;
    document.getElementById("country").innerHTML = result.country;
    document.getElementById("gender").innerHTML = result.gender;

};

browse_other_user = function(form) {
    var email = form.email.value;
    localStorage.setItem("post_email", email);
    var result = serverstub.getUserDataByEmail(localStorage.getItem("user_token"), email);
    if (result.success) {
        showPanel("home");
        get_info(email);
        get_messages(message_board_self);
        form.reset();
    } else {
    	form.email.setCustomValidity(result.message);
    }
};

custom_post_message = function(form) {
    var result = serverstub.postMessage(localStorage.getItem("user_token"), form.message.value, localStorage.getItem("post_email"));
    if (result.success) {
		get_messages(document.getElementById("message_board_self"));
		form.reset();
    } else {

    }
};

changeView = function(name) {
    if (name === "welcome") {
        document.getElementById("content").innerHTML = document.getElementById("welcomeview").innerHTML;
    } else if (name == "profile") {
        document.getElementById("content").innerHTML = document.getElementById("profileview").innerHTML;

        show_home_panel();
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