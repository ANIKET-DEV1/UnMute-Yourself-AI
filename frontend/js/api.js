const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
  ? 'http://localhost:5000/api'
  : '/api';

// Auth State Management
const Auth = {
  getToken: () => localStorage.getItem('unmute_token'),
  setToken: (token) => localStorage.setItem('unmute_token', token),
  getUser: () => {
    try {
      const u = localStorage.getItem('unmute_user');
      return u ? JSON.parse(u) : null;
    } catch (e) {
      return null;
    }
  },
  setUser: (user) => localStorage.setItem('unmute_user', JSON.stringify(user)),
  logout: () => {
    localStorage.removeItem('unmute_token');
    localStorage.removeItem('unmute_user');
    window.location.href = 'login.html';
  },
  isLoggedIn: () => !!localStorage.getItem('unmute_token'),
};

// Generic Fetch Wrapper
async function request(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const token = Auth.getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers,
  };

  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, config);
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.message || 'API request failed');
    }
    return data;
  } catch (err) {
    console.error(`API Error [${endpoint}]:`, err);
    throw err;
  }
}

// API Endpoints
const API = {
  // Authentication APIs
  auth: {
    register: async (name, email, password) => {
      const data = await request('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ name, email, password }),
      });
      if (data.token) {
        Auth.setToken(data.token);
        Auth.setUser(data.user);
      }
      return data;
    },

    login: async (email, password) => {
      const data = await request('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      if (data.token) {
        Auth.setToken(data.token);
        Auth.setUser(data.user);
      }
      return data;
    },

    getMe: async () => {
      return await request('/auth/me', { method: 'GET' });
    },
  },

  // Session Management APIs
  sessions: {
    createSession: async (mode = 'GROUP_DISCUSSION', topic = 'General Practice', durationMins = 20) => {
      return await request('/sessions/create', {
        method: 'POST',
        body: JSON.stringify({ mode, topic, durationMins }),
      });
    },

    getSession: async (sessionId) => {
      return await request(`/sessions/${sessionId}`, { method: 'GET' });
    },

    getMySessions: async () => {
      return await request('/sessions/my-sessions', { method: 'GET' });
    },

    saveReport: async (sessionId, report, transcript = []) => {
      return await request(`/sessions/${sessionId}/report`, {
        method: 'POST',
        body: JSON.stringify({ report, transcript, status: 'COMPLETED' }),
      });
    },
  },
};

// UI Helper to update user badge in Navbar across pages
function initNavbarUser() {
  const user = Auth.getUser();
  const navContainer = document.querySelector('.header-nav-links') || document.querySelector('.nav-right');
  
  if (navContainer && user) {
    // Check if user element already added
    if (!document.getElementById('user-nav-badge')) {
      const userBadge = document.createElement('div');
      userBadge.id = 'user-nav-badge';
      userBadge.style.cssText = 'display: flex; align-items: center; gap: 10px; font-size: 13px; font-weight: 600; color: #1e104a;';
      userBadge.innerHTML = `
        <span style="background: rgba(110,70,235,0.1); padding: 4px 10px; border-radius: 20px; color: #6e46eb;">👤 ${user.name}</span>
        <button onclick="Auth.logout()" style="background: none; border: 1px solid #e2e8f0; padding: 4px 10px; border-radius: 8px; cursor: pointer; font-size: 12px; color: #64748b;">Logout</button>
      `;
      navContainer.appendChild(userBadge);
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  initNavbarUser();
});
