/**
 * QHUN22 Mobile - Home Page JavaScript
 * Banner sliders, video handling, and auto-sliders
 */

// ==================== MAIN BANNER SLIDER (Video) ====================
const MainSlider = {
    slides: null,
    dots: null,
    prevBtn: null,
    nextBtn: null,
    currentSlide: 0,
    isTransitioning: false,
    totalSlides: 0,
    slideDuration: 8000, // 8 seconds
    autoSlideTimer: null,

    init() {
        this.slides = document.querySelectorAll('.banner-slide');
        this.dots = document.querySelectorAll('.dot-btn');
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.totalSlides = this.slides.length;

        if (this.totalSlides === 0) {
            console.warn('No slides found for MainSlider');
            return;
        }

        this.bindEvents();
        this.startAutoSlide();
        this.playCurrentVideo();
    },

    bindEvents() {
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.prevSlide();
            });
        }

        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.nextSlide();
            });
        }

        this.dots.forEach((dot, index) => {
            dot.addEventListener('click', (e) => {
                e.preventDefault();
                if (index !== this.currentSlide) {
                    this.goToSlide(index);
                }
            });
        });
    },

    getCurrentVideo() {
        return this.slides[this.currentSlide]?.querySelector('video');
    },

    playCurrentVideo() {
        const video = this.getCurrentVideo();
        if (video) {
            video.currentTime = 0;
            video.play().catch((e) => {
                console.warn('Video play error:', e);
            });
        }
    },

    playVideoAt(index) {
        const video = this.slides[index]?.querySelector('video');
        if (video) {
            video.currentTime = 0;
            video.play().catch((e) => {
                console.warn('Video play error at index ' + index + ':', e);
            });
        }
    },

    goToSlide(newIndex) {
        if (this.isTransitioning || newIndex === this.currentSlide) return;
        this.isTransitioning = true;

        const currentEl = this.slides[this.currentSlide];
        const nextEl = this.slides[newIndex];

        // Update dots
        this.dots[this.currentSlide].classList.remove('bg-white/90', 'active');
        this.dots[this.currentSlide].classList.add('bg-white/40');
        this.dots[newIndex].classList.remove('bg-white/40');
        this.dots[newIndex].classList.add('bg-white/90', 'active');

        // Fade transition
        currentEl.style.opacity = '0';

        setTimeout(() => {
            currentEl.classList.remove('opacity-100');
            currentEl.classList.add('opacity-0');
            nextEl.classList.remove('opacity-0');
            nextEl.classList.add('opacity-100');

            // Play new video
            this.playVideoAt(newIndex);

            setTimeout(() => {
                currentEl.style.opacity = '';
                this.isTransitioning = false;
                this.currentSlide = newIndex;
                this.resetAutoSlideTimer();
            }, 350);
        }, 350);
    },

    nextSlide() {
        const newIndex = (this.currentSlide + 1) % this.totalSlides;
        this.goToSlide(newIndex);
    },

    prevSlide() {
        const newIndex = (this.currentSlide - 1 + this.totalSlides) % this.totalSlides;
        this.goToSlide(newIndex);
    },

    startAutoSlide() {
        this.autoSlideTimer = setInterval(() => this.nextSlide(), this.slideDuration);
    },

    resetAutoSlideTimer() {
        clearInterval(this.autoSlideTimer);
        if (!this.isTransitioning) {
            this.startAutoSlide();
        }
    }
};

// ==================== AUTO BANNER SLIDER (Image) ====================
const AutoBannerSlider = {
    track: null,
    items: null,
    currentIndex: 0,
    realItemCount: 4, // 4 real banners
    slideDuration: 3000, // 3 seconds
    interval: null,

    init() {
        this.track = document.getElementById('autoSliderTrack');
        if (!this.track) return;

        this.items = this.track.querySelectorAll('.auto-slider-item');
        if (this.items.length === 0) return;

        this.startAutoSlide();
    },

    startAutoSlide() {
        this.interval = setInterval(() => this.nextSlide(), this.slideDuration);
    },

    nextSlide() {
        this.currentIndex++;

        // Calculate transform (each item is 50% width)
        const translateX = -(this.currentIndex * 50);
        this.track.style.transform = `translateX(${translateX}%)`;

        // Reset when reaching clone banners
        if (this.currentIndex >= this.realItemCount) {
            setTimeout(() => {
                this.track.style.transition = 'none';
                this.track.style.transform = 'translateX(0)';
                this.currentIndex = 0;

                setTimeout(() => {
                    this.track.style.transition = 'transform 0.5s ease-in-out';
                }, 50);
            }, 500);
        }
    }
};

// ==================== INITIALIZE ALL ====================
document.addEventListener('DOMContentLoaded', function() {
    // Debug: Log video elements
    const videoIds = ['video-iphone', 'video-samsung', 'video-xiaomi', 'video-oppo'];
    videoIds.forEach(id => {
        const video = document.getElementById(id);
        if (video) {
            console.log(`Video element found: ${id}`);
            // Add error handling
            video.addEventListener('error', (e) => {
                console.error(`Error loading video ${id}:`, e);
                console.error('Source:', video.querySelector('source')?.src);
            });
            video.addEventListener('canplaythrough', () => {
                console.log(`Video ready to play: ${id}`);
            });
        } else {
            console.warn(`Video element NOT found: ${id}`);
        }
    });

    MainSlider.init();
    AutoBannerSlider.init();
});
