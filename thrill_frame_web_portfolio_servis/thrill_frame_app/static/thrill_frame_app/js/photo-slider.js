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

window.togglePhotoLike = function (event, photoId) {
    if (event) event.preventDefault();
    if (event) event.stopPropagation();

    const btn = event ? event.currentTarget : document.querySelector(`.like-btn[data-photo-id="${photoId}"]`);
    if (!btn) return;

    fetch(`/photos/${photoId}/like/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(res => res.json())
    .then(data => {
        const countEl = document.getElementById(`likes-count-${photoId}`);
        if (countEl) countEl.textContent = data.likes_count ?? 0;

        const icon = btn.querySelector('i');
        if (icon) {
            if (data.liked) {
                btn.classList.add('liked');
                icon.classList.remove('bi-heart');
                icon.classList.add('bi-heart-fill');
            } else {
                btn.classList.remove('liked');
                icon.classList.remove('bi-heart-fill');
                icon.classList.add('bi-heart');
            }
        }
    })
    .catch(err => console.error('Помилка лайка фото:', err));
};

window.submitPhotoComment = function (photoId) {
    const textInput = document.getElementById(`comment-text-${photoId}`);
    if (!textInput) return;

    const text = textInput.value.trim();
    if (!text) return;

    const formData = new FormData();
    formData.append('text', text);

    fetch(`/photos/${photoId}/comment/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(res => {
        if (!res.ok) throw new Error('Failed to submit comment');
        return res.json();
    })
    .then(data => {
        if (data.status === 'success') {
            textInput.value = '';

            const commentsList = document.getElementById(`comments-list-${photoId}`);
            if (commentsList) {
                const html = `
                    <div class="single-comment p-2 rounded-3" style="background: rgba(255, 255, 255, 0.03);">
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="user-gradient-name" style="font-size: 0.85rem;">${escapeHtml(data.username)}</span>
                            <small class="text-white" style="font-size: 0.75rem;">${escapeHtml(data.created_at)}</small>
                        </div>
                        <p class="text-white mb-1 mt-1" style="font-size: 0.9rem;">${escapeHtml(data.text)}</p>
                    </div>
                `;
                commentsList.insertAdjacentHTML('afterend', html);
            }

            const commentsCountEl = document.getElementById(`comments-count-${photoId}`);
            if (commentsCountEl) commentsCountEl.textContent = data.comment_count ?? 0;
        }
    })
    .catch(err => console.error('Помилка надсилання коментаря:', err));
};

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('photoSliderModal');
    const closeBtn = document.querySelector('.close-slider');
    const mainImage = document.getElementById('sliderMainImage');
    const sliderCurrent = document.getElementById('sliderCurrent');
    const sliderTotal = document.getElementById('sliderTotal');
    const prevBtn = document.getElementById('sliderPrev');
    const nextBtn = document.getElementById('sliderNext');

    if (!modal || !mainImage || !sliderCurrent || !sliderTotal || !prevBtn || !nextBtn) return;

    let currentPhotos = [];
    let currentIndex = 0;

    function updateSlider() {
        if (!currentPhotos.length) return;

        mainImage.src = currentPhotos[currentIndex];
        sliderCurrent.textContent = currentIndex + 1;
        sliderTotal.textContent = currentPhotos.length;

        prevBtn.style.visibility = currentIndex === 0 ? 'hidden' : 'visible';
        nextBtn.style.visibility = currentIndex === currentPhotos.length - 1 ? 'hidden' : 'visible';
    }

    function openSlider(images) {
        if (!images || !images.length) return;

        currentPhotos = images;
        currentIndex = 0;
        currentPhotos.forEach(imageUrl => {
            const image = new Image();
            image.src = imageUrl;
        });
        updateSlider();
        modal.style.display = 'block';
    }

    document.querySelectorAll('.photoshoot-slider-trigger').forEach(trigger => {
        trigger.addEventListener('click', function () {
            const images = JSON.parse(this.dataset.images || '[]');
            openSlider(images);
        });
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', function () {
            modal.style.display = 'none';
        });
    }

    prevBtn.addEventListener('click', function () {
        if (currentIndex > 0) {
            currentIndex -= 1;
            updateSlider();
        }
    });

    nextBtn.addEventListener('click', function () {
        if (currentIndex < currentPhotos.length - 1) {
            currentIndex += 1;
            updateSlider();
        }
    });

    window.addEventListener('keydown', function (event) {
        if (modal.style.display !== 'block') return;

        if (event.key === 'Escape') modal.style.display = 'none';
        if (event.key === 'ArrowLeft') {
            if (currentIndex > 0) {
                currentIndex -= 1;
                updateSlider();
            }
        }
        if (event.key === 'ArrowRight') {
            if (currentIndex < currentPhotos.length - 1) {
                currentIndex += 1;
                updateSlider();
            }
        }
    });

    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.dataset.photoId = btn.dataset.photoId || btn.getAttribute('data-photo-id') || btn.closest('[data-photo-id]')?.dataset.photoId || btn.id?.replace('likes-count-', '');
    });
});
