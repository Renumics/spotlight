// Play videos when they scroll into view, pause them when they leave.
(function () {
    var observer = null;

    function setup() {
        if (!('IntersectionObserver' in window)) return;
        if (observer) observer.disconnect();

        observer = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    var video = entry.target;
                    if (entry.isIntersecting) {
                        var playing = video.play();
                        if (playing && playing.catch) playing.catch(function () {});
                    } else {
                        video.pause();
                    }
                });
            },
            { threshold: 0.25 }
        );

        document.querySelectorAll('.md-content video').forEach(function (video) {
            video.muted = true; // required for programmatic play without a user gesture
            observer.observe(video);
        });
    }

    // Material provides `document$`, which also re-fires on instant navigation.
    if (window.document$ && typeof window.document$.subscribe === 'function') {
        window.document$.subscribe(setup);
    } else if (document.readyState !== 'loading') {
        setup();
    } else {
        document.addEventListener('DOMContentLoaded', setup);
    }
})();
