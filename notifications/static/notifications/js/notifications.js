// notifications.js
document.addEventListener('DOMContentLoaded', () => {
    const notificationHandler = {
        NOTIFICATION_SOUNDS: {
            arrow: 'http://codeskulptor-demos.commondatastorage.googleapis.com/pang/arrow.mp3',
            metalplate: 'https://cdnjs.cloudflare.com/ajax/libs/ion-sound/3.0.7/sounds/metal_plate.mp3',
            melody: 'http://codeskulptor-demos.commondatastorage.googleapis.com/descent/gotitem.mp3',
            bell: 'https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3'
        },

        init() {
            // Initialize core functionality first
            this.setupAudioElement();
            this.loadSavedSettings();
            this.setupSettingsListeners();

            // Only setup notifications if URL is available
            this.notificationUrl = document.body.dataset.notificationUrl;
            if (this.notificationUrl) {
                this.setupNotificationContainer();
                this.setupEventSource();
                this.loadNotifications();
            }

            console.log('Notification handler initialized');
        },
        setupNotificationContainer() {
            if (!document.getElementById('notification-container')) {
                const container = document.createElement('div');
                container.id = 'notification-container';
                document.body.appendChild(container);
            }
        },

        setupAudioElement() {
            try {
                // Create audio element first
                const audio = new Audio();
                
                // Get saved sound preference with fallback
                const savedSound = localStorage.getItem('notificationSound') || 'bell';
                const soundUrl = this.NOTIFICATION_SOUNDS[savedSound];
                
                if (soundUrl) {
                    audio.src = soundUrl;
                } else {
                    audio.src = this.NOTIFICATION_SOUNDS.ding; // Fallback to default
                }
                
                audio.preload = 'auto';
                
                // Set initial volume with fallback
                const savedVolume = localStorage.getItem('notificationVolume');
                audio.volume = savedVolume ? parseFloat(savedVolume) / 100 : 0.5;
                
                this.audio = audio;
                
                console.log('Audio setup complete:', {
                    sound: savedSound,
                    volume: audio.volume,
                    url: audio.src
                });
            } catch (error) {
                console.error('Error setting up audio:', error);
            }
        },

        async loadNotifications() {
            try {
                const response = await fetch('/api/notifications/');
                if (response.ok) {
                    const notifications = await response.json();
                    // Reset count before loading
                    this.unreadCount = 0;
                    
                    notifications.forEach(notification => {
                        this.addNotificationToInbox(notification);
                    });
                    
                    // Update counter after loading all notifications
                    this.updateNotificationCounter();
                }
            } catch (error) {
                console.error('Error loading notifications:', error);
            }
        },

        setupMarkAllRead() {
            const markAllReadBtn = document.getElementById('markAllRead');
            if (markAllReadBtn) {
                markAllReadBtn.addEventListener('click', async (e) => {
                    e.preventDefault();
                    await this.markAllNotificationsAsRead();
                });
            }
        },

        updateNotificationCounter() {
            const counter = document.getElementById('notification-counter');
            if (counter) {
                if (this.unreadCount > 0) {
                    counter.textContent = this.unreadCount;
                    counter.style.display = 'block';
                } else {
                    counter.style.display = 'none';
                }
            }
        },

        async markAsRead(notificationId) {
            try {
                const response = await fetch(`/api/notifications/${notificationId}/read/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCsrfToken(),
                    }
                });
                return response.ok;
            } catch (error) {
                console.error('Error marking notification as read:', error);
                return false;
            }
        },

        async markAllNotificationsAsRead() {
            try {
                const response = await fetch('/api/notifications/mark-all-read/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCsrfToken(),
                    }
                });

                if (response.ok) {
                    const notificationItems = document.querySelectorAll('.notification-item.unread');
                    notificationItems.forEach(item => {
                        item.classList.remove('unread');
                    });
                    this.unreadCount = 0;
                    this.updateNotificationCounter();
                }
            } catch (error) {
                console.error('Error marking all notifications as read:', error);
            }
        },

        getCsrfToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]').value;
        },

        setupEventSource() {
            // Only setup EventSource if we have a URL
            if (!this.notificationUrl) {
                console.log('No notification URL available, skipping EventSource setup');
                return;
            }

            try {
                if (this.eventSource) {
                    this.eventSource.close();
                }

                console.log('Setting up EventSource...');
                this.eventSource = new EventSource(this.notificationUrl);

                this.eventSource.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        if (data.ping) return;
                        this.handleNewNotification(data);
                    } catch (error) {
                        console.error('Error processing message:', error);
                    }
                };

                this.eventSource.onerror = (error) => {
                    console.log('EventSource error - will retry connection');
                    if (this.eventSource) {
                        this.eventSource.close();
                        this.eventSource = null;
                    }
                    // Retry connection after 5 seconds
                    setTimeout(() => this.setupEventSource(), 5000);
                };

            } catch (error) {
                console.error('Error in setupEventSource:', error);
            }
        },

        handleNewNotification(data) {
            this.showNotification(data);
            this.addNotificationToInbox(data);
            this.playNotificationSound();
        },
        playNotificationSound() {
            if (this.audio) {
                this.audio.currentTime = 0;
                this.audio.play().catch(error => {
                    console.error('Could not play notification sound:', error);
                });
            }
        },

        setVolume(volume) {
            if (this.audio) {
                this.audio.volume = Math.max(0, Math.min(1, volume));
            }
        },

        formatTime(timestamp) {
            const date = new Date(timestamp);
            return date.toLocaleString();
        },

        addNotificationToInbox(notification) {
            const notificationList = document.getElementById('notificationItems');
            if (notificationList) {
                // Check if notification already exists
                if (document.querySelector(`[data-notification-id="${notification.id}"]`)) {
                    return;
                }

                const notificationItem = document.createElement('div');
                notificationItem.className = `notification-item${notification.is_read ? '' : ' unread'}`;
                notificationItem.setAttribute('data-notification-id', notification.id);
                notificationItem.innerHTML = `
                    <div class="notification-content">
                        ${notification.message}
                        <div class="notification-time">
                            ${this.formatTime(notification.created_at)}
                        </div>
                    </div>
                `;

                // Remove "No notifications" message if it exists
                const noNotificationsDiv = notificationList.querySelector('.no-notifications');
                if (noNotificationsDiv) {
                    noNotificationsDiv.remove();
                }

                notificationList.insertBefore(notificationItem, notificationList.firstChild);

                if (!notification.is_read) {
                    this.unreadCount++;
                    this.updateNotificationCounter();
                }
            }
        },

        showNotification(data) {
            const notification = document.createElement('div');
            notification.className = 'notification-toast';
            notification.innerHTML = `
                <div class="notification-header">
                    <i class="bi bi-bell"></i>
                    <span>New Notification</span>
                    <button onclick="this.parentElement.parentElement.remove()" class="close-btn">&times;</button>
                </div>
                <div class="notification-body">
                    ${data.message}
                </div>
                <div class="notification-footer">
                    <small>${this.formatTime(data.created_at)}</small>
                </div>
            `;

            const container = document.getElementById('notification-container');
            if (container) {
                container.appendChild(notification);

                setTimeout(() => {
                    notification.remove();
                }, 5000);
            }
        },
        loadSavedSettings() {
            try {
                const soundSelect = document.getElementById('notificationSound');
                const volumeInput = document.getElementById('notificationVolume');
                
                if (soundSelect) {
                    const savedSound = localStorage.getItem('notificationSound') || 'ding';
                    soundSelect.value = savedSound;
                }
                
                if (volumeInput) {
                    const savedVolume = localStorage.getItem('notificationVolume') || '50';
                    volumeInput.value = savedVolume;
                }
            } catch (error) {
                console.error('Error loading saved settings:', error);
            }
        },
        setupSettingsListeners() {
            // Test sound button
            const testButton = document.getElementById('testSound');
            if (testButton) {
                testButton.addEventListener('click', () => {
                    console.log('Testing sound...');
                    this.playTestSound();
                });
            }

            // Sound selection
            const soundSelect = document.getElementById('notificationSound');
            if (soundSelect) {
                soundSelect.addEventListener('change', (e) => {
                    const selectedSound = e.target.value;
                    console.log('Changing sound to:', selectedSound);
                    
                    const soundUrl = this.NOTIFICATION_SOUNDS[selectedSound];
                    if (soundUrl && this.audio) {
                        this.audio.src = soundUrl;
                        localStorage.setItem('notificationSound', selectedSound);
                        // Don't auto-play test sound on change
                    }
                });
            }
            const volumeControl = document.getElementById('notificationVolume');
            if (volumeControl) {
                volumeControl.addEventListener('input', (e) => {
                    const volumeValue = e.target.value;
                    const volume = volumeValue / 100;
                    
                    this.setVolume(volume);
                    localStorage.setItem('notificationVolume', volumeValue);
                });
            }
        },


        
        setVolume(volume) {
            if (this.audio) {
                this.audio.volume = Math.max(0, Math.min(1, volume));
            }
        },

        playTestSound() {
            if (this.audio && this.audio.src) {
                const testAudio = new Audio(this.audio.src);
                testAudio.volume = this.audio.volume;
                
                testAudio.play().catch(error => {
                    console.error('Could not play test sound:', error);
                });
            }
        },
        
        saveSettings() {
            try {
                const soundSelect = document.getElementById('notificationSound');
                const volumeInput = document.getElementById('notificationVolume');
        
                if (soundSelect && volumeInput) {
                    // Save to localStorage
                    localStorage.setItem('notificationSound', soundSelect.value);
                    localStorage.setItem('notificationVolume', volumeInput.value);
        
                    // Apply settings immediately
                    if (this.audio) {
                        this.audio.src = this.NOTIFICATION_SOUNDS[soundSelect.value];
                        this.audio.volume = volumeInput.value / 100;
                    }

                    // Show success message
                    this.showSettingsToast('Settings saved successfully!');
                }
            } catch (error) {
                console.error('Error saving settings:', error);
                this.showSettingsToast('Error saving settings', 'danger');
            }
        },

        showSettingsToast(message, type = 'success') {
            // Remove any existing toasts
            const existingToast = document.querySelector('.settings-toast');
            if (existingToast) {
                existingToast.remove();
            }

            // Create new toast
            const toast = document.createElement('div');
            toast.className = `settings-toast alert alert-${type} position-fixed bottom-0 end-0 m-3`;
            toast.style.zIndex = '1050';
            toast.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="bi bi-${type === 'success' ? 'check' : 'exclamation'}-circle me-2"></i>
                    ${message}
                </div>
            `;

            // Add toast to document
            document.body.appendChild(toast);

            // Remove toast after 3 seconds
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                }
            }, 3000);
        }
    };

    notificationHandler.init();
    window.notificationHandler = notificationHandler;
});