function annotate(idx) {
    let sentence = idx < 0 ? 'N/A' : document.querySelectorAll('#targets .sentence')[idx].textContent;
    let encodedSentence = encodeURIComponent(sentence);
    let sentenceID = parseInt(location.pathname.split('/').reverse()[0])

    fetch('/write_annotation/' + sentenceID + '/' + encodedSentence)
        .then((r) => r.json())
        .then((o) => {
            console.log(o);
            if (o.status) {
                location.href = '/annotate/' + (++sentenceID);
            }
        });
}

document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('keyup', (e) => {
        let k = e.key.toLowerCase()

        for (let e of document.querySelectorAll('#targets .badge')) {
            if (e.textContent == k) {
                e.parentElement.click();
            }
        }

        if (e.code == 'Space' || e.code == 'Escape') {
            annotate(-1);
        }
    });
})

