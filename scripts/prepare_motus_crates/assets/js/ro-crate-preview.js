function containsText(anchor, text) {
    return anchor.textContent.includes(text);
}

function handleClick(event) {
    if (window.self === window.top) {
        // We're not in an iframe, so we allow the links to work normally
        return;
    }
    event.preventDefault();
    const anchor = event.target;
    const anchorText = anchor.textContent;
    window.parent.postMessage(anchor.id, "*");
}

document.addEventListener("DOMContentLoaded", function () {
    const anchorTags = document.querySelectorAll("a");
    anchorTags.forEach(anchor => {
        const anchorText = anchor.textContent;
        if (containsText(anchor, "multiqc_report") || containsText(anchor, "krona")) {
            anchor.addEventListener("click", handleClick);
        }
    });
});