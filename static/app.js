function annotate(idx) {
    let sentence = idx < 0 ? 'No match' : document.querySelectorAll('#targets .sentence')[idx].textContent;
    let encodedSentence = encodeURIComponent(sentence);

    let fragments = location.pathname.split('/')
    let project = fragments[2]
    let sentenceID = parseInt(fragments[fragments.length - 1])

    fetch(`/write_annotation/${project}/${sentenceID}/${encodedSentence}`)
        .then((r) => r.json())
        .then((o) => {
            console.log(o);
            if (o.status) {
                location.href = `/annotate/${project}/${++sentenceID}`;
            }
        });
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('main').style.marginTop = (document.querySelector('.site-header').offsetHeight) + 'px'

    document.addEventListener('keyup', (e) => {
        let k = e.key.toLowerCase()

        for (let e of document.querySelectorAll('#targets .badge')) {
            if (e.textContent == k) {
                e.parentElement.click();
            }
        }

        if (e.code == 'Escape') {
            annotate(-1);
        }
    });
})

