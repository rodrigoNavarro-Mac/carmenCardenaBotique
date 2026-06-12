(function () {
  function closestSubmitter(event) {
    return event.submitter || document.activeElement;
  }

  document.addEventListener("submit", function (event) {
    const form = event.target;
    const submitter = closestSubmitter(event);
    const confirmMessage = submitter && submitter.getAttribute("data-confirm");

    if (confirmMessage && !window.confirm(confirmMessage)) {
      event.preventDefault();
      return;
    }

    if (form.matches("[data-prevent-double-submit]")) {
      form.querySelectorAll('button[type="submit"]').forEach(function (button) {
        button.disabled = true;
        button.classList.add("is-loading");
      });
    }
  });

  document.addEventListener("htmx:beforeRequest", function (event) {
    const element = event.detail.elt;
    if (element) {
      element.classList.add("is-loading");
    }
  });

  document.addEventListener("htmx:afterRequest", function (event) {
    const element = event.detail.elt;
    if (element) {
      element.classList.remove("is-loading");
    }
  });
})();
