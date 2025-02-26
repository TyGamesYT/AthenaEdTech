function logout() {
    puter.auth.signOut().then(() => {
        localStorage.removeItem("puterUser");
        location.reload(); // Reload to reflect the change immediately
    });
}