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
                'controls': 0,
                'rel': 0,
                'showinfo': 0,
                'modestbranding': 1,
                'mute': 1,
                'playsinline': 1,
                'loop': 1,
                'playlist': videoId,
                'iv_load_policy': 3,
                'fs': 0,
                'disablekb': 1
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
        sliderInterval = setInterval(nextSlide, 30000);
    }
}

function nextSlide() {
    if (totalSlides <= 1) return;

    if (players[currentSlide] && typeof players[currentSlide].pauseVideo === 'function') {
        players[currentSlide].pauseVideo();
    }
    slideElements[currentSlide].classList.remove('active');

    currentSlide = (currentSlide + 1) % totalSlides;

    slideElements[currentSlide].classList.add('active');
    if (players[currentSlide] && typeof players[currentSlide].playVideo === 'function') {
        players[currentSlide].playVideo();
    }
}

window.onYouTubeIframeAPIReady = initYouTubePlayers;

if (window.YT && window.YT.Player) {
    initYouTubePlayers();
} else if (!document.querySelector('script[src*="youtube.com/iframe_api"]')) {
    const tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    const firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
}

document.addEventListener('DOMContentLoaded', function () {
    const videoModalElement = document.getElementById('videoModal');
    const youtubePlayer = document.getElementById('youtubePlayer');
    const videoModalTitle = document.getElementById('videoModalTitle');

    if (videoModalElement && youtubePlayer) {
        const bsModal = new bootstrap.Modal(videoModalElement);

        document.querySelectorAll('.video-play-trigger, .release-card').forEach(card => {
            card.addEventListener('click', function (e) {
                e.stopPropagation();
                const videoId = this.getAttribute('data-video-id');
                const videoTitle = this.getAttribute('data-video-title') || '';

                if (videoId && videoId.trim() !== '' && videoId !== 'None') {
                    if (videoModalTitle) videoModalTitle.textContent = videoTitle;
                    youtubePlayer.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`;
                    bsModal.show();
                } else {
                    console.error('Не вдалося витягти YouTube ID. Перевірте атрибут data-video-id.');
                }
            });
        });

        videoModalElement.addEventListener('hidden.bs.modal', function () {
            youtubePlayer.src = '';
        });
    }

    const radioButtons = document.querySelectorAll('input[name="contact_method"]');
    const dynamicLabel = document.getElementById("dynamic_username_label");

    if (radioButtons.length > 0 && dynamicLabel) {
        radioButtons.forEach(radio => {
            radio.addEventListener("change", function() {
                if (this.value === 'telegram') {
                    dynamicLabel.innerText = "Введіть Telegram нік";
                } else if (this.value === 'instagram') {
                    dynamicLabel.innerText = "Введіть Instagram нік";
                }
            });
        });
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function toggleLike(event, videoId) {
    if (event) event.stopPropagation();

    const btn = event.currentTarget;

    fetch(`/video/${videoId}/like/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.total_likes !== undefined) {
            const likesCountEl = document.getElementById(`likes-count-${videoId}`);
            if (likesCountEl) likesCountEl.innerText = data.total_likes;

            if (data.liked) {
                btn.classList.add('liked');
            } else {
                btn.classList.remove('liked');
            }
        }
    })
    .catch(err => console.error('Помилка при відправці лайка:', err));
}

function toggleReplyInput(commentId) {
    const form = document.getElementById(`reply-form-${commentId}`);
    if (form) form.classList.toggle('d-none');
}

function submitComment(videoId, parentId = null) {
    const textInput = parentId
        ? document.getElementById(`reply-text-${parentId}`)
        : document.getElementById(`comment-text-${videoId}`);

    if (!textInput) return;

    const text = textInput.value.trim();
    if (!text) return;

    const formData = new FormData();
    formData.append('text', text);
    if (parentId) formData.append('parent_id', parentId);

    fetch(`/video/${videoId}/comment/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            textInput.value = '';

            const commentHtml = `
                <div class="single-comment p-2 rounded-3 mt-2" style="background: rgba(255, 255, 255, 0.03);">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="user-gradient-name" style="font-size: 0.85rem;">${data.username}</span>
                        <small class="text-white" style="font-size: 0.75rem;">${data.created_at}</small>
                    </div>
                    <p class="text-white mb-1 mt-1" style="font-size: 0.9rem;">${data.text}</p>
                </div>
            `;

            if (parentId) {
                const repliesContainer = document.getElementById(`replies-${parentId}`);
                if (repliesContainer) repliesContainer.insertAdjacentHTML('beforeend', commentHtml);

                const replyForm = document.getElementById(`reply-form-${parentId}`);
                if (replyForm) replyForm.classList.add('d-none');
            } else {
                const commentsList = document.getElementById(`comments-list-${videoId}`);
                if (commentsList) commentsList.insertAdjacentHTML('afterbegin', commentHtml);
            }

            const commentsCountEl = document.getElementById(`comments-count-${videoId}`);
            if (commentsCountEl) {
                if (data.comments_count !== undefined) {
                    commentsCountEl.innerText = data.comments_count;
                } else {
                    let currentCount = parseInt(commentsCountEl.innerText) || 0;
                    commentsCountEl.innerText = currentCount + 1;
                }
            }
        }
    })
    .catch(err => console.error('Помилка надсилання коментаря:', err));
}

function copyShareLink(videoId) {
    const linkInput = document.getElementById(`shareLink-${videoId}`);
    if (!linkInput) return;

    linkInput.select();
    navigator.clipboard.writeText(linkInput.value)
        .then(() => alert('Посилання скопійовано!'))
        .catch(err => console.error('Не вдалося скопіювати:', err));
}

document.addEventListener('DOMContentLoaded', function() {
    const GOOGLE_API_KEY = 'YOUR_GOOGLE_DRIVE_API_KEY';

    const modal = document.getElementById('photoSliderModal');
    const closeBtn = document.querySelector('.close-slider');
    const mainImage = document.getElementById('sliderMainImage');
    const counter = document.getElementById('sliderCounter');
    const prevBtn = document.getElementById('sliderPrev');
    const nextBtn = document.getElementById('sliderNext');

    let currentPhotos = [];
    let currentIndex = 0;

    document.querySelectorAll('.photo-thumbnail-container').forEach(container => {
        container.addEventListener('click', async function() {
            const folderId = this.dataset.folderId;
            const coverUrl = this.dataset.coverUrl;

            currentPhotos = [coverUrl];
            currentIndex = 0;
            updateSlider();
            modal.style.display = 'block';

            if (folderId && GOOGLE_API_KEY !== 'YOUR_GOOGLE_DRIVE_API_KEY') {
                try {
                    const response = await fetch(`https://www.googleapis.com/drive/v3/files?q='${folderId}'+in+parents+and+mimeType+contains+'image/'&key=${GOOGLE_API_KEY}&fields=files(id)`);
                    const data = await response.json();
                    if (data.files) {
                        const fetchedPhotos = data.files.map(file => `https://drive.google.com/uc?id=${file.id}`);
                        currentPhotos = [coverUrl, ...fetchedPhotos];
                        updateSlider();
                    }
                } catch (error) {
                    console.error('Помилка завантаження фото з Google Drive:', error);
                }
            }
        });
    });

    closeBtn.addEventListener('click', () => modal.style.display = 'none');

    prevBtn.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateSlider();
        }
    });

    nextBtn.addEventListener('click', () => {
        if (currentIndex < currentPhotos.length - 1) {
            currentIndex++;
            updateSlider();
        }
    });

    function updateSlider() {
        mainImage.src = currentPhotos[currentIndex];
        counter.textContent = `${currentIndex + 1} / ${currentPhotos.length}`;

        prevBtn.style.visibility = currentIndex === 0 ? 'hidden' : 'visible';
        nextBtn.style.visibility = currentIndex === currentPhotos.length - 1 ? 'hidden' : 'visible';
    }

    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const photoId = this.dataset.id;
            fetch(`/photos/${photoId}/like/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(res => res.json())
            .then(data => {
                this.querySelector('.likes-count').textContent = data.likes_count;
                const icon = this.querySelector('i');
                if (data.liked) {
                    icon.classList.remove('bi-heart');
                    icon.classList.add('bi-heart-fill');
                } else {
                    icon.classList.remove('bi-heart-fill');
                    icon.classList.add('bi-heart');
                }
            });
        });
    });

    document.querySelectorAll('.share-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const url = this.dataset.url;
            navigator.clipboard.writeText(url).then(() => {
                alert('Посилання скопійовано!');
            });
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
