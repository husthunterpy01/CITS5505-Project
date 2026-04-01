function loadComponent(id, file) {
  $.get(file)
    .done(function (html) {
      $("#" + id).html(html);
    })
    .fail(function () {
      console.error("Could not load " + file);
    });
}

const routes = {
  "#home": "./pages/WelcomePage/welcomepage.html",
  "#signin": "./pages/SignInPage/signinpage.html",
  "#about": "./pages/AboutPage/about.html",
  "#signup": "./pages/SignUpPage/signuppage.html",
};

function toggleLayoutByHash(hash) {
  const isAuth = hash === "#signin" || hash === "#signup";
  // Show header only on non-auth pages
  $("#header").toggle(!isAuth);
}

function renderByHash() {
  const hash = window.location.hash || "#home";
  const page = routes[hash] || routes["#home"];
  loadComponent("main-content", page);
  toggleLayoutByHash(hash);
}

$(document).ready(function () {
  loadComponent("header", "./components/header.html");
  loadComponent("footer", "./components/footer.html");

  renderByHash();
  $(window).on("hashchange", renderByHash);
});
