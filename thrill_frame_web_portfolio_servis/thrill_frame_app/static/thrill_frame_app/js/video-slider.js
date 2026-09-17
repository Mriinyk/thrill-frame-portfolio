let players = [];
let currentSlide = 0;
let totalSlides = 0;
let slideElements = [];
let sliderInterval = null;

function extractYouTubeID(urlOrId) {
    if (!urlOrId) return '';
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = urlOrId.trim().match(regExp);
    return (match && match[2].length === 11) ? match[2] : urlOrId.trim();
}

function initYouTubePlayers() {
    slideElements = Array.from(document.querySelectorAll('.hero-slide'));
    totalSlides = slideElements.length;

    if (totalSlides === 0) return;

    slideElements.forEach((slide, index) => {
        const rawId = slide.dataset.youtubeId;
        const videoId = extractYouTubeID(rawId);
        const playerContainer = slide.querySelector(`[id="player${index}"]`);

        if (!videoId || !playerContainer) return;

        players[index] = new YT.Player(playerContainer.id, {
            videoId: videoId,
            playerVars: {
                'origin': window.location.origin,
                'enablejsapi': 1,
                'autoplay': index === 0 ? 1 : 0,
                'controls': 0,         // Приховує панель керування
                'rel': 0,              // Не показує схожі відео
                'showinfo': 0,         // Приховує заголовок
                'modestbranding': 1,   // Приховує великий логотип YouTube
                'mute': 1,             // Автовідтворення вимагає mute
                'playsinline': 1,
                'loop': 1,
                'playlist': videoId,
                'iv_load_policy': 3,   // Вимикає анотації та підказки
                'fs': 0,               // Вимикає кнопку повного екрана
                'disablekb': 1         // Вимикає керування клавіатурою
            },
            events: {
                'onReady': (event) => {
                    event.target.mute();
                    if (index === 0) {
                        event.target.playVideo();
                        startSlider();
                    }
                }
            }
        });
    });
}

function startSlider() {
    if (totalSlides > 1 && !sliderInterval) {
        sliderInterval = setInterval(nextSlide, 30000); // Перемикання кожні 30 секунд
    }
}

function nextSlide() {
    if (totalSlides <= 1) return;

    // 1. Ставимо на паузу поточне відео (без seekTo, щоб зберегти позицію)
    if (players[currentSlide] && typeof players[currentSlide].pauseVideo === 'function') {
        players[currentSlide].pauseVideo();
    }
    slideElements[currentSlide].classList.remove('active');

    // 2. Індекс наступного слайду
    currentSlide = (currentSlide + 1) % totalSlides;

    // 3. Активуємо та продовжуємо грати з місця зупинки
    slideElements[currentSlide].classList.add('active');
    if (players[currentSlide] && typeof players[currentSlide].playVideo === 'function') {
        players[currentSlide].playVideo();
    }
}

// Ініціалізація
window.onYouTubeIframeAPIReady = initYouTubePlayers;

if (window.YT && window.YT.Player) {
    initYouTubePlayers();
} else if (!document.querySelector('script[src*="youtube.com/iframe_api"]')) {
    const tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    const firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
}

// Блок новинок
document.addEventListener('DOMContentLoaded', function () {
    const videoModalElement = document.getElementById('videoModal');
    const youtubePlayer = document.getElementById('youtubePlayer');
    const videoModalTitle = document.getElementById('videoModalTitle');

    if (!videoModalElement || !youtubePlayer) return;

    const bsModal = new bootstrap.Modal(videoModalElement);

    document.querySelectorAll('.release-card').forEach(card => {
        card.addEventListener('click', function () {
            const videoId = this.getAttribute('data-video-id');
            const videoTitle = this.getAttribute('data-video-title') || '';

            if (videoId && videoId.trim() !== '') {
                videoModalTitle.textContent = videoTitle;
                youtubePlayer.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`;
                bsModal.show();
            } else {
                console.error('Не вдалося витягти YouTube ID. Перевірте посилання в адмінці.');
            }
        });
    });

    videoModalElement.addEventListener('hidden.bs.modal', function () {
        youtubePlayer.src = '';
    });
});
