// notifications.js
document.addEventListener('DOMContentLoaded', () => {
    const notificationHandler = {
        init() {
            console.log('Initializing notification handler');
            this.notificationUrl = document.body.dataset.notificationUrl;
            this.notifications = [];
            this.unreadCount = 0;
            this.processedNotifications = new Set(); // Add this to track processed notifications
            
            if (!this.notificationUrl) {
                console.error('Notification URL not found');
                return;
            }
            
            this.setupNotificationContainer();
            this.setupEventSource();
            this.setupAudioElement();
            this.setupMarkAllRead();
            this.loadNotifications(); 
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
                // Available notification sounds
                const NOTIFICATION_SOUNDS = {
                    SUBTLE: 'https://cdn.jsdelivr.net/gh/ferdium/ferdium-app/src/renderer/sounds/subtle.mp3',
                    DING: 'https://cdn.jsdelivr.net/gh/ferdium/ferdium-app/src/renderer/sounds/notification.mp3',
                    POP: 'https://cdn.jsdelivr.net/gh/ferdium/ferdium-app/src/renderer/sounds/pop.mp3',
                    BELL: 'https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3'
                };

                const audio = new Audio(NOTIFICATION_SOUNDS.DING);
                audio.id = 'notificationSound';
                audio.preload = 'auto';
                audio.volume = 0.5;

                audio.onerror = (e) => {
                    console.error('Audio loading error:', e);
                    // Fallback to another sound if the first one fails
                    audio.src = NOTIFICATION_SOUNDS.BELL;
                };

                this.audio = audio;
            } catch (error) {
                console.error('Error setting up audio:', error);
            }
        },

        async loadNotifications() {
            try {
                const response = await fetch('/api/notifications/');
                if (response.ok) {
                    const notifications = await response.json();
                    notifications.forEach(notification => {
                        this.addNotificationToInbox(notification, false);
                    });
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
            try {
                if (this.eventSource) {
                    this.eventSource.close();
                }

                const streamUrl = this.notificationUrl.replace(/\/$/, '');
                console.log('Connecting to EventSource at:', streamUrl);
                
                this.eventSource = new EventSource(streamUrl);
                
                this.eventSource.onmessage = (event) => {
                    console.log('Received message:', event.data);
                    try {
                        const data = JSON.parse(event.data);
                        if (data.ping) {
                            console.log('Received ping');
                            return;
                        }
                        if (!this.processedNotifications.has(data.id)) {
                            this.processedNotifications.add(data.id);
                            this.handleNewNotification(data);
                        }
                    } catch (error) {
                        console.error('Error processing message:', error);
                    }
                };
                this.eventSource.onerror = (error) => {
                    console.error('EventSource failed:', error);
                    if (this.eventSource) {
                        this.eventSource.close();
                        this.eventSource = null;
                    }
                    setTimeout(() => this.setupEventSource(), 5000);
                };

                this.eventSource.onopen = () => {
                    console.log('EventSource connection established');
                };
            } catch (error) {
                console.error('Error setting up EventSource:', error);
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
    };

notificationHandler.init();
}
);