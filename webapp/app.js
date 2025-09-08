// Pickleball AI WebApp - Main Application

class PickleballApp {
    constructor() {
        // --- Configuration ---
        const serverIp = '0nex2fx18j42ro-8000.proxy.runpod.net'; // CHANGE THIS to your server laptop's IP address

        // Base URL for all standard HTTP API calls (fetch)
        this.apiUrl = `https://${serverIp}`;
        
        // URL for Socket.IO (WebSocket) connections ONLY, including the namespace
        this.socketUrl = `https://${serverIp}/webapp`;

        this.socket = null;
        this.currentTheme = 'default';
        this.isAdminLoggedIn = false;
        this.courts = {};
        this.currentFeed = null;
        this.currentMatch = null;
        this.matchHistory = [];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadSettings();
        this.loadMatchHistory();
        this.connectToServer();
        this.startStatusUpdates();
        this.setCurrentDate();
    }
    
    setupEventListeners() {
        // Admin panel
        document.getElementById('adminLoginBtn').addEventListener('click', () => this.showAdminPanel());
        document.getElementById('closeAdminPanel').addEventListener('click', () => this.hideAdminPanel());
        document.getElementById('loginBtn').addEventListener('click', () => this.handleLogin());
        document.getElementById('logoutBtn').addEventListener('click', () => this.handleLogout());
        
        // Settings panel
        document.getElementById('settingsBtn').addEventListener('click', () => this.showSettingsPanel());
        document.getElementById('closeSettingsPanel').addEventListener('click', () => this.hideSettingsPanel());
        document.getElementById('themeSelect').addEventListener('change', (e) => this.changeTheme(e.target.value));
        
        // Live feed panel
        document.getElementById('closeLiveFeed').addEventListener('click', () => this.hideLiveFeed());
        document.getElementById('replay5Btn').addEventListener('click', () => this.requestReplay(5));
        document.getElementById('replay10Btn').addEventListener('click', () => this.requestReplay(10));
        document.getElementById('zoomBtn').addEventListener('click', () => this.toggleZoom());
        
        // Scoring panel
        document.getElementById('closeScoringPanel').addEventListener('click', () => this.hideScoringPanel());
        document.getElementById('saveScoreBtn').addEventListener('click', () => this.saveScore());
        document.getElementById('resetScoreBtn').addEventListener('click', () => this.resetScore());
        document.getElementById('newMatchBtn').addEventListener('click', () => this.newMatch());
        
        // Admin controls
        document.getElementById('addCourtBtn').addEventListener('click', () => this.addCourt());
        document.getElementById('addCameraBtn').addEventListener('click', () => this.addCamera());
        
        // Overlay click to close panels
        document.getElementById('overlay').addEventListener('click', () => this.hideAllPanels());

        // Event delegation for delete buttons on the main grid
        document.getElementById('courtsGrid').addEventListener('click', (e) => {
            if (e.target.classList.contains('delete-court-btn')) {
                const courtCard = e.target.closest('.court-card');
                const courtId = courtCard.dataset.courtId;
                this.handleDeleteCourt(courtId);
            }
            if (e.target.classList.contains('delete-camera-btn')) {
                const cameraItem = e.target.closest('.camera-item');
                const courtId = cameraItem.dataset.courtId;
                const camId = cameraItem.dataset.camId;
                this.handleDeleteCamera(courtId, camId);
            }
        });
    }
    
    connectToServer() {
        try {
            this.socket = io(this.socketUrl);
            
            this.socket.on('connect', () => {
                console.log('Connected to the WebApp WebSocket namespace.');
                this.updateConnectionStatus(true);
            });
            
            this.socket.on('disconnect', () => {
                console.log('Disconnected from the WebApp WebSocket namespace.');
                this.updateConnectionStatus(false);
            });
            
            this.socket.on('decision', (data) => {
                this.handleDecision(data);
            });
            
            this.socket.on('replay_clip', (data) => {
                this.handleReplay(data);
            });

            this.socket.on('live_frame', (data) => {
                if (this.currentFeed && this.currentFeed.camId == data.cam_id) {
                    const feedElement = document.getElementById('cameraFeed');
                    feedElement.innerHTML = `<img src="data:image/jpeg;base64,${data.frame}" style="width:100%; height:100%; object-fit:contain;">`;
                }
            });
            
            this.socket.on('error', (data) => {
                console.error('Server error:', data);
                this.showNotification('Server Error: ' + data.msg, 'error');
            });
            
        } catch (error) {
            console.error('Failed to connect to server:', error);
            this.showNotification('Failed to connect to server', 'error');
        }
    }
    
    updateConnectionStatus(connected) {
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.status-text');
        
        if (statusDot && statusText) {
            if (connected) {
                statusDot.className = 'status-dot connected';
                statusText.textContent = 'Connected';
            } else {
                statusDot.className = 'status-dot disconnected';
                statusText.textContent = 'Disconnected';
            }
        }
    }
    
    async handleLogin() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await fetch(`${this.apiUrl}/admin/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (data.ok) {
                this.isAdminLoggedIn = true;
                this.showAdminControls();
                this.showNotification('Login successful', 'success');
                await this.loadCourts();
                this.populateCourtSelect();
            } else {
                this.showNotification('Login failed: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showNotification('Login failed', 'error');
        }
    }
    
    async handleLogout() {
        try {
            await fetch(`${this.apiUrl}/admin/logout`, {
                method: 'POST',
                credentials: 'include'
            });
            
            this.isAdminLoggedIn = false;
            this.hideAdminControls();
            this.showNotification('Logged out', 'info');
        } catch (error) {
            console.error('Logout error:', error);
        }
    }
    
    showAdminControls() {
        document.getElementById('loginForm').style.display = 'none';
        document.getElementById('adminControls').style.display = 'block';
        this.updateSystemStatus();
    }
    
    hideAdminControls() {
        document.getElementById('loginForm').style.display = 'block';
        document.getElementById('adminControls').style.display = 'none';
    }
    
    async addCourt() {
        const courtId = document.getElementById('newCourtId').value;
        const courtName = document.getElementById('newCourtName').value;
        
        if (!courtId || !courtName) {
            this.showNotification('Please fill in all fields', 'warning');
            return;
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/admin/courts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ court_id: courtId, court_name: courtName }),
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (data.ok) {
                this.showNotification('Court added successfully', 'success');
                // Await the new court list before updating the dropdown
                await this.loadCourts();
                this.populateCourtSelect();
                this.clearCourtForm();
            } else {
                this.showNotification('Failed to add court: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Add court error:', error);
            this.showNotification('Failed to add court', 'error');
        }
    }
    
    async addCamera() {
        const courtId = document.getElementById('cameraCourtId').value;
        const cameraId = parseInt(document.getElementById('newCameraId').value);
        const cameraName = document.getElementById('newCameraName').value;
        const position = document.getElementById('newCameraPosition').value;
        
        if (!courtId || !cameraId || !cameraName) {
            this.showNotification('Please fill in all fields', 'warning');
            return;
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/admin/cameras`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    court_id: courtId,
                    cam_id: cameraId,
                    cam_name: cameraName,
                    position: position
                }),
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (data.ok) {
                this.showNotification('Camera added successfully', 'success');
                await this.loadCourts();
                this.clearCameraForm();
            } else {
                this.showNotification('Failed to add camera: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Add camera error:', error);
            this.showNotification('Failed to add camera', 'error');
        }
    }

    async handleDeleteCourt(courtId) {
        if (!confirm(`Are you sure you want to delete court "${courtId}"? This will also delete all of its cameras.`)) {
            return;
        }

        try {
            const response = await fetch(`${this.apiUrl}/admin/courts/${courtId}`, {
                method: 'DELETE',
                credentials: 'include'
            });
            const data = await response.json();
            if (data.ok) {
                this.showNotification('Court deleted successfully', 'success');
                await this.loadCourts();
                this.populateCourtSelect();
            } else {
                this.showNotification(`Error: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showNotification('Failed to delete court.', 'error');
        }
    }

    async handleDeleteCamera(courtId, camId) {
        if (!confirm(`Are you sure you want to delete camera "${camId}" from court "${courtId}"?`)) {
            return;
        }

        try {
            const response = await fetch(`${this.apiUrl}/admin/cameras/${courtId}/${camId}`, {
                method: 'DELETE',
                credentials: 'include'
            });
            const data = await response.json();
            if (data.ok) {
                this.showNotification('Camera deleted successfully', 'success');
                await this.loadCourts();
            } else {
                this.showNotification(`Error: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showNotification('Failed to delete camera.', 'error');
        }
    }
    
    async loadCourts() {
        if (!this.isAdminLoggedIn) return;
        try {
            const response = await fetch(`${this.apiUrl}/admin/courts`, {
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.courts = data.courts || {};
                this.renderCourts();
            }
        } catch (error) {
            console.error('Failed to load courts:', error);
        }
    }
    
    renderCourts() {
        const courtsGrid = document.getElementById('courtsGrid');
        courtsGrid.innerHTML = '';
        
        if (Object.keys(this.courts).length === 0) {
            courtsGrid.innerHTML = '<div class="no-courts">No courts configured. Use Admin Panel to add courts.</div>';
            return;
        }
        
        Object.entries(this.courts).forEach(([courtId, court]) => {
            const courtElement = this.createCourtElement(courtId, court);
            courtsGrid.appendChild(courtElement);
        });
    }
    
    createCourtElement(courtId, court) {
        const template = document.getElementById('courtTemplate');
        const courtElement = template.content.cloneNode(true);
        const courtCard = courtElement.querySelector('.court-card');
        courtCard.dataset.courtId = courtId;
        
        const courtName = courtElement.querySelector('.court-name');
        const camerasGrid = courtElement.querySelector('.cameras-grid');
        
        courtName.textContent = court.name;
        
        Object.entries(court.cameras).forEach(([camId, camera]) => {
            const cameraElement = this.createCameraElement(courtId, camId, camera);
            camerasGrid.appendChild(cameraElement);
        });
        
        return courtElement;
    }
    
    createCameraElement(courtId, camId, camera) {
        const template = document.getElementById('cameraTemplate');
        const cameraElement = template.content.cloneNode(true);
        const cameraItem = cameraElement.querySelector('.camera-item');
        cameraItem.dataset.courtId = courtId;
        cameraItem.dataset.camId = camId;
        
        const cameraName = cameraElement.querySelector('.camera-name');
        const cameraPosition = cameraElement.querySelector('.camera-position');
        const statusIndicator = cameraElement.querySelector('.status-indicator');
        const statusText = cameraElement.querySelector('.status-text');
        const viewFeedBtn = cameraElement.querySelector('.view-feed-btn');
        
        cameraName.textContent = camera.name;
        cameraPosition.textContent = camera.position;
        statusIndicator.className = `status-indicator ${camera.status}`;
        statusText.textContent = camera.status;
        
        viewFeedBtn.addEventListener('click', () => this.viewCameraFeed(courtId, camId));
        
        return cameraElement;
    }
    
    viewCameraFeed(courtId, camId) {
        this.currentFeed = { courtId, camId };
        this.showLiveFeed();
        
        if (this.socket) {
            this.socket.emit('join_camera_feed', {
                court_id: courtId,
                cam_id: camId
            });
        }
    }
    
    showLiveFeed() {
        document.getElementById('liveFeedPanel').classList.add('active');
        document.getElementById('overlay').classList.add('active');
        document.getElementById('cameraFeed').innerHTML = '<div class="feed-placeholder">Connecting to camera feed...</div>';
        this.resetDecisionPanel();
    }
    
    hideLiveFeed() {
        document.getElementById('liveFeedPanel').classList.remove('active');
        document.getElementById('overlay').classList.remove('active');
        this.currentFeed = null;
    }
    
    resetDecisionPanel() {
        document.getElementById('decisionBadge').textContent = 'No Decision';
        document.getElementById('decisionBadge').className = 'decision-badge no-decision';
        document.getElementById('ballPosition').textContent = '-';
    }
    
    requestReplay(duration) {
        if (!this.currentFeed || !this.socket) return;
        this.socket.emit('request_replay', {
            court_id: this.currentFeed.courtId,
            cam_id: this.currentFeed.camId,
            duration: duration
        });
    }
    
    toggleZoom() {
        document.getElementById('cameraFeed').classList.toggle('zoomed');
    }
    
    handleDecision(data) {
        if (!this.currentFeed) return;
        if (this.currentFeed.courtId === data.court_id && this.currentFeed.camId === data.cam_id) {
            this.updateDecisionPanel(data);
        }
    }
    
    updateDecisionPanel(data) {
        document.getElementById('decisionBadge').textContent = data.decision || 'No Decision';
        document.getElementById('decisionBadge').className = `decision-badge ${data.decision ? data.decision.toLowerCase() : 'no-decision'}`;
        document.getElementById('ballPosition').textContent = data.ball_xy ? `(${data.ball_xy[0]}, ${data.ball_xy[1]})` : '-';
    }
    
    handleReplay(data) {
        if (data.frames && data.frames.length > 0) {
            this.playReplay(data.frames, data.fps);
        }
    }
    
    playReplay(frames, fps) {
        const feedElement = document.getElementById('cameraFeed');
        feedElement.innerHTML = '';
        let currentFrame = 0;
        const interval = 1000 / fps;

        const renderFrame = () => {
            if (currentFrame >= frames.length) {
                feedElement.innerHTML = '<div class="feed-placeholder">Replay finished</div>';
                return;
            }
            feedElement.innerHTML = `<img src="data:image/jpeg;base64,${frames[currentFrame]}" style="width:100%;height:100%;object-fit:contain;">`;
            currentFrame++;
            setTimeout(renderFrame, interval);
        };
        renderFrame();
    }
    
    // --- All other methods (scoring, settings, etc.) remain unchanged ---

    showScoringPanel(courtId) {
        this.currentMatch = { courtId, date: new Date().toISOString().split('T')[0] };
        document.getElementById('scoringPanel').classList.add('active');
        document.getElementById('overlay').classList.add('active');
        document.getElementById('matchDate').value = this.currentMatch.date;
        this.loadCurrentMatch();
    }
    
    hideScoringPanel() {
        document.getElementById('scoringPanel').classList.remove('active');
        document.getElementById('overlay').classList.remove('active');
        this.currentMatch = null;
    }
    
    loadCurrentMatch() {
        const savedMatch = localStorage.getItem(`match_${this.currentMatch.courtId}`);
        if (savedMatch) {
            const match = JSON.parse(savedMatch);
            document.getElementById('matchTitle').value = match.title || '';
            document.getElementById('teamASet1').value = match.teamA?.set1 || '';
            document.getElementById('teamASet2').value = match.teamA?.set2 || '';
            document.getElementById('teamASet3').value = match.teamA?.set3 || '';
            document.getElementById('teamBSet1').value = match.teamB?.set1 || '';
            document.getElementById('teamBSet2').value = match.teamB?.set2 || '';
            document.getElementById('teamBSet3').value = match.teamB?.set3 || '';
        }
    }
    
    saveScore() {
        if (!this.currentMatch) return;
        const matchData = {
            courtId: this.currentMatch.courtId,
            title: document.getElementById('matchTitle').value || 'Untitled Match',
            date: document.getElementById('matchDate').value,
            teamA: {
                set1: parseInt(document.getElementById('teamASet1').value) || 0,
                set2: parseInt(document.getElementById('teamASet2').value) || 0,
                set3: parseInt(document.getElementById('teamASet3').value) || 0
            },
            teamB: {
                set1: parseInt(document.getElementById('teamBSet1').value) || 0,
                set2: parseInt(document.getElementById('teamBSet2').value) || 0,
                set3: parseInt(document.getElementById('teamBSet3').value) || 0
            },
            timestamp: new Date().toISOString()
        };
        localStorage.setItem(`match_${this.currentMatch.courtId}`, JSON.stringify(matchData));
        this.addToHistory(matchData);
        this.showNotification('Score saved successfully', 'success');
    }
    
    resetScore() {
        if (confirm('Are you sure you want to reset the score?')) {
            document.getElementById('teamASet1').value = '';
            document.getElementById('teamASet2').value = '';
            document.getElementById('teamASet3').value = '';
            document.getElementById('teamBSet1').value = '';
            document.getElementById('teamBSet2').value = '';
            document.getElementById('teamBSet3').value = '';
            this.showNotification('Score reset', 'info');
        }
    }
    
    newMatch() {
        if (confirm('Start a new match? Current match will be saved.')) {
            this.saveScore();
            this.resetScore();
            document.getElementById('matchTitle').value = '';
            this.currentMatch.date = new Date().toISOString().split('T')[0];
            document.getElementById('matchDate').value = this.currentMatch.date;
            this.showNotification('New match started', 'info');
        }
    }
    
    addToHistory(matchData) {
        this.matchHistory.unshift(matchData);
        if (this.matchHistory.length > 50) {
            this.matchHistory = this.matchHistory.slice(0, 50);
        }
        localStorage.setItem('matchHistory', JSON.stringify(this.matchHistory));
        this.renderMatchHistory();
    }
    
    loadMatchHistory() {
        const saved = localStorage.getItem('matchHistory');
        if (saved) {
            this.matchHistory = JSON.parse(saved);
        }
        this.renderMatchHistory();
    }
    
    renderMatchHistory() {
        const historyList = document.getElementById('historyList');
        if (!historyList) return;
        historyList.innerHTML = '';
        if (this.matchHistory.length === 0) {
            historyList.innerHTML = '<div style="text-align: center; color: var(--secondary-color); padding: 1rem;">No matches recorded yet</div>';
            return;
        }
        this.matchHistory.forEach((match) => {
            const matchElement = document.createElement('div');
            matchElement.className = 'history-item';
            const teamAScore = (match.teamA.set1 || 0) + (match.teamA.set2 || 0) + (match.teamA.set3 || 0);
            const teamBScore = (match.teamB.set1 || 0) + (match.teamB.set2 || 0) + (match.teamB.set3 || 0);
            matchElement.innerHTML = `
                <div style="font-weight: 600;">${match.title}</div>
                <div style="font-size: 0.875rem; color: var(--secondary-color);">
                    ${new Date(match.date).toLocaleDateString()} - Court ${match.courtId}
                </div>
                <div>Team A: ${teamAScore} vs Team B: ${teamBScore}</div>`;
            historyList.appendChild(matchElement);
        });
    }
    
    setCurrentDate() {
        document.getElementById('matchDate').value = new Date().toISOString().split('T')[0];
    }
    
    showAdminPanel() {
        document.getElementById('adminPanel').classList.add('active');
        document.getElementById('overlay').classList.add('active');
    }
    
    hideAdminPanel() {
        document.getElementById('adminPanel').classList.remove('active');
        document.getElementById('overlay').classList.remove('active');
    }
    
    showSettingsPanel() {
        document.getElementById('settingsPanel').classList.add('active');
        document.getElementById('overlay').classList.add('active');
    }
    
    hideSettingsPanel() {
        document.getElementById('settingsPanel').classList.remove('active');
        document.getElementById('overlay').classList.remove('active');
    }
    
    hideAllPanels() {
        this.hideAdminPanel();
        this.hideSettingsPanel();
        this.hideLiveFeed();
        this.hideScoringPanel();
    }
    
    populateCourtSelect() {
        const select = document.getElementById('cameraCourtId');
        select.innerHTML = '';
        Object.entries(this.courts).forEach(([courtId, court]) => {
            const option = document.createElement('option');
            option.value = courtId;
            option.textContent = court.name;
            select.appendChild(option);
        });
    }
    
    async updateSystemStatus() {
        if (!this.isAdminLoggedIn) return;
        try {
            const response = await fetch(`${this.apiUrl}/status`, { credentials: 'include' });
            if (response.ok) {
                const data = await response.json();
                document.getElementById('totalCourts').textContent = data.courts;
                document.getElementById('activeStreams').textContent = data.active_streams;
                document.getElementById('totalCameras').textContent = data.total_cameras;
            }
        } catch (error) {
            console.error('Failed to update system status:', error);
        }
    }
    
    clearCourtForm() {
        document.getElementById('newCourtId').value = '';
        document.getElementById('newCourtName').value = '';
    }
    
    clearCameraForm() {
        document.getElementById('newCameraId').value = '';
        document.getElementById('newCameraName').value = '';
        document.getElementById('newCameraPosition').value = 'north';
    }
    
    changeTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        this.saveSettings();
    }
    
    loadSettings() {
        const settings = JSON.parse(localStorage.getItem('pickleball_settings'));
        if (settings) {
            this.changeTheme(settings.theme || 'default');
        }
    }
    
    saveSettings() {
        const settings = { theme: this.currentTheme };
        localStorage.setItem('pickleball_settings', JSON.stringify(settings));
    }
    
    startStatusUpdates() {
        // This interval now only fetches the lightweight system status.
        // It no longer fetches the entire court list, making it much more efficient.
        setInterval(() => {
            if (this.isAdminLoggedIn) {
                this.updateSystemStatus();
            }
        }, 10000); // Refresh status every 10 seconds
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.classList.add('show'), 100);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PickleballApp();
});