let savedUser = localStorage.getItem("puterUser");
const possibleIds = ["account1", "account2", "account3", "account4"];
let accountElem = null;

// Find the first existing account element
for (let id of possibleIds) {
    let elem = document.getElementById(id);
    if (elem) {
        accountElem = elem;
        break;
    }
}

// If an element exists, set the stored value before the page loads
if (accountElem) {
    accountElem.innerHTML = savedUser ? savedUser : "Sign In";
    accountElem.href = savedUser ? "account.html" : "#";
}


document.addEventListener("DOMContentLoaded", function () {
    
    const possibleIds = ["account1", "account2", "account3", "account4"];
    let accountElem = null;

    // Find which element exists on this page
    for (let id of possibleIds) {
        let elem = document.getElementById(id);
        if (elem) {
            accountElem = elem;
            break; // Stop once we find the first existing element
        }
    }
    
    if (accountElem) {
        accountElem.innerHTML = savedUser ? savedUser : "Sign In";
        accountElem.href = savedUser ? "account.html" : "#";
    }

    let userName = "Sign In";

    if (puter.auth.isSignedIn()) {
        puter.auth.getUser().then(function (user) {
            localStorage.setItem("puterUser", userName);
            userName = user.username;
            if (accountElem) {
                accountElem.innerHTML = userName; // Update DOM
                accountElem.href = "account.html";
            }
        }).catch(error => alert("Error fetching user:", error));
    } else {
        if (accountElem) {
            accountElem.innerHTML = userName; // Update DOM immediately
            accountElem.href = "#";
        }
    }
});

