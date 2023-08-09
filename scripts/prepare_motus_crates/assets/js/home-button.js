function goHome(event) {
  if (window.self === window.top) {
    // We're not in an iframe, so we allow the links to work normally
    return;
  }
  event.preventDefault();
  window.parent.postMessage('ro-crate-preview.html', "*");
}

document.addEventListener("DOMContentLoaded", function() {
  const homeButton = document.createElement("a");
  homeButton.textContent = "Home";
  homeButton.href = "ro-crate-preview.html";
  homeButton.classList.add('home-button');
  homeButton.addEventListener("click", goHome);
  document.body.insertBefore(homeButton, document.body.firstChild);

  window.addEventListener("scroll", function() {
    const homeButton = document.querySelector(".home-button");

    if (window.scrollY > 0) {
      homeButton.classList.add("transparent");
    } else {
      homeButton.classList.remove("transparent");
    }
  });
});
